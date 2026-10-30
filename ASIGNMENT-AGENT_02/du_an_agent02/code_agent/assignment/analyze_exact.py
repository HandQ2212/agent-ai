"""Exact occupancy evaluation of frozen deterministic policies, without sampling."""
from pathlib import Path
import json,csv
import numpy as np
from agent02_experiment import Config, expected_profit, write_csv
ROOT=Path(__file__).resolve().parents[2]

def exact_mean(cfg,q):
    mu=np.zeros((2,2,2));mu[:,0,0]=.5;total=0.;rows=[]
    for t in range(cfg.horizon):
        nxt=np.zeros_like(mu);r=0.;discount=0.
        for d in (0,1):
            for u in (0,1):
                for v in (0,1):
                    mass=mu[d,u,v]
                    a=int(np.argmax(q[d,v]));b=d*u
                    r+=mass*expected_profit(cfg,d,a,b);discount+=mass*a
                    nxt[:,a,b]+=mass*.5
        total+=r;rows.append({'step':t+1,'expected_reward':float(r),'discount_probability':float(discount)})
        mu=nxt
    return float(total/cfg.horizon),rows

def run():
    out=ROOT/'ket_qua/assignment';data=json.loads((out/'summary.json').read_text());rr=[]
    measured=list(csv.DictReader((out/'configurations.csv').open()))
    for key,values in data['q_tables'].items():
        label,seed=key.rsplit('_',1);exact,_=exact_mean(Config(),np.array(values))
        sampled=next(float(r['mean_reward']) for r in measured if r['configuration']==label and r['seed']==seed)
        rr.append({'configuration':label,'seed':int(seed),'exact_mean':exact,'sampled_mean':sampled,'sample_error':sampled-exact,
            'policy_bits':''.join(map(str,np.argmax(np.array(values),axis=-1).ravel().tolist()))})
    write_csv(out/'exact_policy_values.csv',rr)
    value,steps=exact_mean(Config(),np.array(data['baseline']['q']));write_csv(out/'baseline42_exact_steps.csv',steps)
    (out/'exact_analysis.json').write_text(json.dumps({'baseline42_exact':value,
      'method':'Forward occupancy on full state (d, own_prev, opponent_prev), H=20, reward undiscounted, fixed rule opponent; no simulation or fitted model.'},indent=2))
    print('Exact analysis done; seed42 expected profit/step:',value)
if __name__=='__main__':run()
