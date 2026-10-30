from pathlib import Path
import asyncio,csv,json,platform,time
import numpy as np
from mas_system import Coordinator,single_pipeline
from train_intent import Router
ROOT=Path(__file__).resolve().parents[1]
CASES=[('portable',100,'normal','ok',['p2','p4']),('unknown',100,'normal','no_results',[]),
 ('',100,'normal','no_results',[]),('portable',0,'normal','no_results',[]),
 ('sports',100,'normal','no_results',[]),('study',200,'normal','ok',['p5']),
 ('portable',100,'timeout','timeout',[]),('portable',100,'malformed','contract_error',[]),
 ('portable',100,'stale','availability_unverified',[]),('portable',100,'forged','contract_error',[]),
 ('portable',-1,'normal','invalid_input',[])]

async def run(out=ROOT/'results/tutorial',repetitions=20):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);router=Router(out);rows=[];trace=[]
    for system in ['B0_single','B1_rule_MAS','B2_learned_MAS','B3_no_validation']:
        coordinator=Coordinator(validate=system!='B3_no_validation')
        for rep in range(repetitions):
            for idx,(q,b,scenario,status,ids) in enumerate(CASES):
                start=time.perf_counter();coordinator.trace=[]
                if system=='B0_single':result=single_pipeline(q,b,scenario)
                else:
                    if system=='B2_learned_MAS':
                        intent=router.route('t\u00ecm mua laptop cho t\u00f4i')
                        if intent['intent']!='ecommerce':result={'status':'clarify','items':[]}
                        else:result=await coordinator.shop(q,b,scenario,f'{system}:{rep}:{idx}')
                    else:result=await coordinator.shop(q,b,scenario,f'{system}:{rep}:{idx}')
                latency=(time.perf_counter()-start)*1000
                success=result['status']==status and [i['id'] for i in result['items']]==ids
                violation=any(i['price']>b or i['id'] not in ['p1','p2','p3','p4','p5'] or scenario=='stale' for i in result['items'])
                rows.append({'system':system,'repeat':rep,'case':idx,'scenario':scenario,'status':result['status'],
                    'success':int(success),'violation':int(violation),'latency_ms':latency,'messages':2*len(coordinator.trace)})
                if rep==0:trace.append({'system':system,'case':idx,'result':result,'trace':list(coordinator.trace)})
    summary=[]
    for s in sorted(set(r['system'] for r in rows)):
        rr=[r for r in rows if r['system']==s];lat=[r['latency_ms'] for r in rr]
        summary.append({'system':s,'requests':len(rr),'success_rate':float(np.mean([r['success'] for r in rr])),
          'p50_ms':float(np.median(lat)),'p95_ms':float(np.percentile(lat,95)),
          'messages_mean':float(np.mean([r['messages'] for r in rr])),
          'violation_rate':float(np.mean([r['violation'] for r in rr]))})
    for filename,rr in [('mas_benchmark_raw.csv',rows),('mas_benchmark.csv',summary)]:
        with open(out/filename,'w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
    (out/'mas_traces.json').write_text(json.dumps(trace,ensure_ascii=False,indent=2))
    (out/'mas_metrics.json').write_text(json.dumps({'summary':summary,'case_count':len(CASES),'repetitions':repetitions,
        'python':platform.python_version(),'note':'Local synthetic services; single baseline injects declared service error outcomes synchronously; its timeout latency is not comparable to real wait_for deadline.'},indent=2))
    print(json.dumps(summary,indent=2));return summary
if __name__=='__main__':asyncio.run(run())
