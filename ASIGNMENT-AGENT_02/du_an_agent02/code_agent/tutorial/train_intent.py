"""Train a real classifier on a transparent synthetic, group-split Vietnamese dataset.
No raw clinical data; healthcare class means administrative scheduling only.
"""
from pathlib import Path
import csv,json,re,unicodedata
import numpy as np
import torch
from torch import nn
ROOT=Path(__file__).resolve().parents[2]
LABELS=['ecommerce','tourism','healthcare_admin']
VERBS=[['tìm mua','chọn mua','cần mua','tư vấn mua','muốn đặt mua','đề xuất mua','giúp chọn','gợi ý mua'],
 ['lên lịch tham quan','lập chuyến đi','tìm điểm du lịch','sắp xếp hành trình','muốn khám phá','tư vấn du lịch','gợi ý tham quan','lập lịch trình'],
 ['đặt lịch khám','hẹn gặp bác sĩ','tìm lịch phòng khám','chuẩn bị khám','hỏi giờ bệnh viện','xem lịch khám','hướng dẫn đặt hẹn','sắp xếp khám']]
OBJECTS=[['laptop','chuột máy tính','ba lô','giày thể thao','máy tính bảng','tai nghe'],
 ['bảo tàng','phố cổ','bãi biển','công viên','khu di tích','vườn thực vật'],
 ['quầy tiếp nhận','thủ tục đăng ký','giấy tờ bảo hiểm','lịch chuyên khoa','hồ sơ hẹn','giờ tiếp nhận']]
SUFFIX=['cho tôi','vào ngày mai','theo nhu cầu của tôi']

def normalize(text):
    text=unicodedata.normalize('NFD',text.lower()).replace('đ','d')
    return re.findall('[a-z]+',''.join(c for c in text if not unicodedata.combining(c)))

def generate_dataset():
    """Generate the synthetic reference data if it needs to be rebuilt."""
    rows=[]
    for y in range(3):
        for g,verb in enumerate(VERBS[y]):
            split='train' if g<5 else ('validation' if g==5 else 'test')
            for obj in OBJECTS[y]:
                for suffix in SUFFIX:
                    rows.append({'text':f'{verb} {obj} {suffix}','label':y,'class':LABELS[y],
                                 'group':f'{y}:{g}','split':split})
    assert len({r['text'] for r in rows})==len(rows)
    return rows

def dataset():
    """Load the prepared dataset and preserve the predefined group splits."""
    path = ROOT / 'dataset' / 'intent_dataset.csv'
    with path.open(encoding='utf-8', newline='') as file:
        rows = list(csv.DictReader(file))
    for row in rows:
        row['label'] = int(row['label'])
    return rows

class IntentNet(nn.Module):
    def __init__(self,n):super().__init__();self.net=nn.Sequential(nn.Linear(n,32),nn.ReLU(),nn.Linear(32,3))
    def forward(self,x):return self.net(x)

def features(texts,vocab):
    x=torch.zeros((len(texts),len(vocab)))
    for i,text in enumerate(texts):
        for token in set(normalize(text)):
            if token in vocab:x[i,vocab[token]]=1
    return x

def metrics(y,p):
    cm=np.zeros((3,3),dtype=int)
    for a,b in zip(y,p):cm[a,b]+=1
    pr=np.diag(cm)/np.maximum(cm.sum(0),1);rc=np.diag(cm)/np.maximum(cm.sum(1),1)
    f=2*pr*rc/np.maximum(pr+rc,1e-12)
    return {'accuracy':float(np.trace(cm)/cm.sum()),'macro_f1':float(f.mean()),'precision':pr.tolist(),
            'recall':rc.tolist(),'f1':f.tolist(),'confusion_matrix':cm.tolist()}

class Router:
    def __init__(self,path=ROOT/'ket_qua/tutorial'):
        ck=torch.load(Path(path)/'intent_model.pt',map_location='cpu',weights_only=True)
        self.vocab=ck['vocab'];self.threshold=ck['threshold'];self.model=IntentNet(len(self.vocab))
        self.model.load_state_dict(ck['state_dict']);self.model.eval()
        # This lexicon is defined before inspecting test/OOD outputs.
        domain=[*sum(OBJECTS,[]),*sum(VERBS,[])]
        self.domain_tokens=set(sum([normalize(s) for s in domain],[]))-set(normalize('cho toi vao ngay mai theo nhu cau cua toi tim can muon giup goi y'))
    def route(self,text):
        with torch.inference_mode():probs=self.model(features([text],self.vocab)).softmax(1)[0]
        confidence=float(probs.max());label=int(probs.argmax())
        known=bool(set(normalize(text)) & self.domain_tokens)
        return {'intent':LABELS[label] if known and confidence>=self.threshold else 'clarify','confidence':confidence}

def run(out=ROOT/'ket_qua/tutorial'):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);torch.set_num_threads(1);torch.manual_seed(42)
    rows=dataset();splits={s:[r for r in rows if r['split']==s] for s in ['train','validation','test']}
    vocab={w:i for i,w in enumerate(sorted(set(sum([normalize(r['text']) for r in splits['train']],[]))))}
    data={s:(features([r['text'] for r in rr],vocab),torch.tensor([r['label'] for r in rr])) for s,rr in splits.items()}
    model=IntentNet(len(vocab));optim=torch.optim.Adam(model.parameters(),lr=.02);lossfn=nn.CrossEntropyLoss()
    history=[];best_loss=float('inf');best=None
    for epoch in range(120):
        model.train();optim.zero_grad();loss=lossfn(model(data['train'][0]),data['train'][1]);loss.backward();optim.step()
        model.eval()
        with torch.inference_mode():val=float(lossfn(model(data['validation'][0]),data['validation'][1]))
        history.append({'epoch':epoch+1,'train_loss':float(loss.detach()),'validation_loss':val})
        if val<best_loss:best_loss=val;best={k:v.detach().clone() for k,v in model.state_dict().items()};best_epoch=epoch+1
    model.load_state_dict(best);model.eval()
    with torch.inference_mode():
        pv=model(data['validation'][0]).softmax(1).numpy();pt=model(data['test'][0]).softmax(1).numpy()
    # Maximize coverage subject to zero observed validation routing error (small toy set).
    choices=[]
    for threshold in [.5,.6,.7,.8,.9,.95,.99]:
        accept=pv.max(1)>=threshold
        if accept.any() and np.all(pv.argmax(1)[accept]==data['validation'][1].numpy()[accept]):choices.append((int(accept.sum()),threshold))
    threshold=max(choices,key=lambda x:(x[0],-x[1]))[1] if choices else 1.
    ck={'state_dict':best,'vocab':vocab,'threshold':threshold};torch.save(ck,out/'intent_model.pt')
    y=data['test'][1].numpy();pred=pt.argmax(1);result=metrics(y,pred);accepted=pt.max(1)>=threshold
    result.update({'splits':{s:len(rr) for s,rr in splits.items()},'threshold':threshold,'selected_epoch':best_epoch,
                   'test_coverage':float(accepted.mean()),'selective_accuracy':float(np.mean(y[accepted]==pred[accepted])) if accepted.any() else None,
                   'vocabulary_size':len(vocab),'seed':42,'torch':torch.__version__,
                   'limitation':'Synthetic template dataset; group split by verb family, objects shared. Not evidence of real-world NLU.'})
    router=Router(out);ood=['xin chào','thời tiết hôm nay thế nào','viết thơ cho tôi','giải phương trình','cảm ơn bạn','abc xyz']
    result['ood']=[{'text':s,**router.route(s)} for s in ood]
    for name,rr in [('intent_training.csv',history),('intent_test_predictions.csv',[
        {'text':r['text'],'label':r['label'],'predicted':int(p),'confidence':float(probs.max()),'accepted':bool(probs.max()>=threshold)}
        for r,p,probs in zip(splits['test'],pred,pt)])]:
        with open(out/name,'w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
    (out/'intent_metrics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(1,2,figsize=(9,3.5));ax[0].plot([r['train_loss'] for r in history],label='train');ax[0].plot([r['validation_loss'] for r in history],label='validation');ax[0].set(xlabel='Epoch',ylabel='Cross entropy');ax[0].legend()
    cm=np.array(result['confusion_matrix']);ax[1].imshow(cm,cmap='Blues');ax[1].set(xticks=range(3),yticks=range(3),xticklabels=['shop','tourism','admin'],yticklabels=['shop','tourism','admin'],xlabel='Prediction',ylabel='True label')
    for i in range(3):
        for j in range(3):ax[1].text(j,i,str(cm[i,j]),ha='center',va='center',color='white' if cm[i,j]>cm.max()/2 else 'black')
    fig.tight_layout();fig.savefig(out/'intent_training.png',dpi=160);plt.close(fig)
    print(json.dumps(result,ensure_ascii=False,indent=2));return result
if __name__=='__main__':run()
