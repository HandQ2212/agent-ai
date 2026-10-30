"""Train a real classifier on a transparent synthetic, group-split Vietnamese dataset.
No raw clinical data; healthcare class means administrative scheduling only.
"""
from pathlib import Path
import csv,json,re,unicodedata
import numpy as np
import torch
from torch import nn
ROOT=Path(__file__).resolve().parents[1]
LABELS=['ecommerce','tourism','healthcare_admin']
VERBS=[['t\u00ecm mua','ch\u1ecdn mua','c\u1ea7n mua','t\u01b0 v\u1ea5n mua','mu\u1ed1n \u0111\u1eb7t mua','\u0111\u1ec1 xu\u1ea5t mua','gi\u00fap ch\u1ecdn','g\u1ee3i \u00fd mua'],
 ['l\u00ean l\u1ecbch tham quan','l\u1eadp chuy\u1ebfn \u0111i','t\u00ecm \u0111i\u1ec3m du l\u1ecbch','s\u1eafp x\u1ebfp h\u00e0nh tr\u00ecnh','mu\u1ed1n kh\u00e1m ph\u00e1','t\u01b0 v\u1ea5n du l\u1ecbch','g\u1ee3i \u00fd tham quan','l\u1eadp l\u1ecbch tr\u00ecnh'],
 ['\u0111\u1eb7t l\u1ecbch kh\u00e1m','h\u1eb9n g\u1eb7p b\u00e1c s\u0129','t\u00ecm l\u1ecbch ph\u00f2ng kh\u00e1m','chu\u1ea9n b\u1ecb kh\u00e1m','h\u1ecfi gi\u1edd b\u1ec7nh vi\u1ec7n','xem l\u1ecbch kh\u00e1m','h\u01b0\u1edbng d\u1eabn \u0111\u1eb7t h\u1eb9n','s\u1eafp x\u1ebfp kh\u00e1m']]
OBJECTS=[['laptop','chu\u1ed9t m\u00e1y t\u00ednh','ba l\u00f4','gi\u00e0y th\u1ec3 thao','m\u00e1y t\u00ednh b\u1ea3ng','tai nghe'],
 ['b\u1ea3o t\u00e0ng','ph\u1ed1 c\u1ed5','b\u00e3i bi\u1ec3n','c\u00f4ng vi\u00ean','khu di t\u00edch','v\u01b0\u1eddn th\u1ef1c v\u1eadt'],
 ['qu\u1ea7y ti\u1ebfp nh\u1eadn','th\u1ee7 t\u1ee5c \u0111\u0103ng k\u00fd','gi\u1ea5y t\u1edd b\u1ea3o hi\u1ec3m','l\u1ecbch chuy\u00ean khoa','h\u1ed3 s\u01a1 h\u1eb9n','gi\u1edd ti\u1ebfp nh\u1eadn']]
SUFFIX=['cho t\u00f4i','v\u00e0o ng\u00e0y mai','theo nhu c\u1ea7u c\u1ee7a t\u00f4i']

def normalize(text):
    text=unicodedata.normalize('NFD',text.lower()).replace('\u0111','d')
    return re.findall('[a-z]+',''.join(c for c in text if not unicodedata.combining(c)))

def dataset():
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
    def __init__(self,path=ROOT/'results/tutorial'):
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

def run(out=ROOT/'results/tutorial'):
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
    router=Router(out);ood=['xin ch\u00e0o','th\u1eddi ti\u1ebft h\u00f4m nay th\u1ebf n\u00e0o','vi\u1ebft th\u01a1 cho t\u00f4i','gi\u1ea3i ph\u01b0\u01a1ng tr\u00ecnh','c\u1ea3m \u01a1n b\u1ea1n','abc xyz']
    result['ood']=[{'text':s,**router.route(s)} for s in ood]
    for name,rr in [('intent_dataset.csv',rows),('intent_training.csv',history),('intent_test_predictions.csv',[
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
