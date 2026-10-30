"""AGENT02 reproducible experiment. Run from any directory; no API or GPU.
Preserves reference reward/action dynamics; separates demand and sales RNG streams.
Training keeps the reference local observation and terminal update deliberately.
Evaluation uses common random numbers, frozen Q, and deterministic tie breaking.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict, replace
from pathlib import Path
import argparse, csv, json, platform, time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
SEEDS = [11, 22, 33, 44, 55]

@dataclass(frozen=True)
class Config:
    episodes: int = 5000
    horizon: int = 20
    evaluation_episodes: int = 500
    alpha: float = .1
    gamma: float = .9
    epsilon_start: float = .2
    epsilon_min: float = .02
    epsilon_decay: float = .995
    price: float = 10.
    cost: float = 5.
    discount: float = .2

def conversion(d, a, b):
    return np.clip(.30 + .25*d + .15*a - .10*b, .05, .95)

def expected_profit(cfg, d, a, b):
    return (10 + 10*d) * conversion(d,a,b) * (cfg.price*(1-cfg.discount*a)-cfg.cost)

class Environment:
    def __init__(self, cfg=Config(), seed=42):
        self.cfg = cfg
        sd, ss = np.random.SeedSequence(seed).spawn(2)
        self.demand_rng, self.sales_rng = np.random.default_rng(sd), np.random.default_rng(ss)
        self.d = 0
        self.previous = [0,0]
    def observations(self):
        return [(self.d,self.previous[1]), (self.d,self.previous[0])]
    def reset(self):
        self.d = int(self.demand_rng.integers(2)); self.previous = [0,0]
        return self.observations()
    def step(self, actions):
        if len(actions)!=2 or any(a not in (0,1) for a in actions):
            raise ValueError('Exactly two binary actions are required')
        n = 10 + 10*self.d
        p = [float(conversion(self.d, actions[i], actions[1-i])) for i in (0,1)]
        sales = [int(self.sales_rng.binomial(n,x)) for x in p]
        rewards = [sales[i]*(self.cfg.price*(1-self.cfg.discount*actions[i])-self.cfg.cost) for i in (0,1)]
        self.previous = list(actions); self.d = int(self.demand_rng.integers(2))
        return self.observations(), rewards, {'sales':sales,'conversion':p,'customers':n}

class QLearningAgent:
    def __init__(self, cfg=Config(), seed=10042):
        self.cfg=cfg; self.q=np.zeros((2,2,2)); self.rng=np.random.default_rng(seed)
    def act(self, state, epsilon=0.):
        if epsilon and self.rng.random()<epsilon: return int(self.rng.integers(2))
        q0,q1 = self.q[state]
        if epsilon and q0==q1: return int(self.rng.integers(2))
        return int(q1>q0)
    def learn(self,s,a,r,ns,terminal=False):
        target = r if terminal else r+self.cfg.gamma*float(max(self.q[ns]))
        idx=(*s,a); self.q[idx] += self.cfg.alpha*(target-self.q[idx])

class RuleBasedAgent:
    def act(self,state): return int(state[0]==1 and state[1]==1)

def train(cfg,seed,selfplay=False):
    # Pre-sample independent demand stream to avoid policy-dependent random draws.
    sd,ss,sa,sb=np.random.SeedSequence(seed).spawn(4)
    d=np.random.default_rng(sd).integers(2,size=(cfg.episodes,cfg.horizon+1))
    sales_rng=np.random.default_rng(ss)
    learner=QLearningAgent(cfg); learner.rng=np.random.default_rng(sa)
    other=QLearningAgent(cfg); other.rng=np.random.default_rng(sb)
    rows=[]; counts=np.zeros((2,2),dtype=int)
    for ep in range(cfg.episodes):
        prev=[0,0]; total=[0.,0.]
        eps=max(cfg.epsilon_min,cfg.epsilon_start*cfg.epsilon_decay**ep)
        for t in range(cfg.horizon):
            demand=int(d[ep,t]); states=[(demand,prev[1]),(demand,prev[0])]
            a=learner.act(states[0],eps)
            b=other.act(states[1],eps) if selfplay else int(demand and prev[0])
            acts=[a,b]; n=10+10*demand
            rewards=[]
            for i in (0,1):
                # In all supplied settings p lies within clipping bounds.
                p=.30+.25*demand+.15*acts[i]-.10*acts[1-i]
                s=int(sales_rng.binomial(n,p))
                rewards.append(s*(cfg.price*(1-cfg.discount*acts[i])-cfg.cost))
                total[i]+=rewards[i]; counts[i,acts[i]]+=1
            nxt=[(int(d[ep,t+1]),b),(int(d[ep,t+1]),a)]
            learner.learn(states[0],a,rewards[0],nxt[0],t==cfg.horizon-1)
            if selfplay: other.learn(states[1],b,rewards[1],nxt[1],t==cfg.horizon-1)
            prev=acts
        rows.append({'episode':ep+1,'rl_total':total[0],'opponent_total':total[1],
                     'rl_mean':total[0]/cfg.horizon,'opponent_mean':total[1]/cfg.horizon,'epsilon':eps})
    return learner,other,rows,counts

def exact_best_response(cfg):
    """Finite-horizon DP on full Markov state (d, own_prev, opponent_prev).
    The fixed opponent's current action is d * own_prev; current actions simultaneous.
    """
    V=np.zeros((cfg.horizon+1,2,2,2)); policy=np.zeros((cfg.horizon,2,2,2),dtype=int)
    for t in range(cfg.horizon-1,-1,-1):
        for d in (0,1):
            for own in (0,1):
                for opp in (0,1):
                    b=d*own
                    values=[expected_profit(cfg,d,a,b)+cfg.gamma*np.mean(V[t+1,:,a,b]) for a in (0,1)]
                    policy[t,d,own,opp]=int(np.argmax(values)); V[t,d,own,opp]=max(values)
    return policy,V

def evaluate(cfg,policy='rule',opponent='rule',seed=800011):
    """500 episodes vectorized; demand and Bernoulli sales shared across policies.
    Q arrays are read-only inputs; np.argmax breaks exact ties toward action 0.
    """
    sd,ss=np.random.SeedSequence(seed).spawn(2)
    E,H=cfg.evaluation_episodes,cfg.horizon
    d=np.random.default_rng(sd).integers(2,size=(E,H))
    uniforms=np.random.default_rng(ss).random((E,H,2,20))
    prev=np.zeros((2,E),dtype=int); totals=np.zeros((2,E)); counts=np.zeros((2,2),dtype=int)
    def actions(p,idx,t):
        if isinstance(p,str):
            if p=='rule': return d[:,t]*prev[1-idx]
            if p=='never': return np.zeros(E,dtype=int)
            if p=='always': return np.ones(E,dtype=int)
            raise ValueError(p)
        if p.ndim==4: return p[t,d[:,t],prev[idx],prev[1-idx]]
        return np.argmax(p[d[:,t],prev[1-idx]],axis=-1)
    for t in range(H):
        acts=np.stack([actions(policy,0,t),actions(opponent,1,t)])
        for i in (0,1):
            p=conversion(d[:,t],acts[i],acts[1-i]); n=10+10*d[:,t]
            sales=((uniforms[:,t,i,:]<p[:,None]) & (np.arange(20)[None,:]<n[:,None])).sum(1)
            totals[i]+=sales*(cfg.price*(1-cfg.discount*acts[i])-cfg.cost)
            counts[i,1]+=int(acts[i].sum()); counts[i,0]+=int(E-acts[i].sum())
        prev=acts
    summary=[{'agent':name,'total_reward':float(totals[i].sum()),'mean_reward':float(totals[i].mean()/H),
              'episode_sd':float((totals[i]/H).std(ddof=1)), 'no_discount':int(counts[i,0]),
              'discount':int(counts[i,1]),'discount_rate':float(counts[i,1]/(E*H))} for i,name in enumerate(['focal','opponent'])]
    episodes=[{'episode':j+1,'focal_total':totals[0,j],'opponent_total':totals[1,j]} for j in range(E)]
    return summary,episodes

def write_csv(path,rows):
    if not rows:return
    with open(path,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def smooth(rows,key='rl_mean',window=100):
    return np.convolve([r[key] for r in rows],np.ones(window)/window,'valid')

def run(output=ROOT/'ket_qua/assignment',episodes=5000):
    out=Path(output);out.mkdir(parents=True,exist_ok=True); started=time.time();cfg=Config(episodes=episodes)
    configs={'baseline':cfg,'alpha_001':replace(cfg,alpha=.01),'alpha_050':replace(cfg,alpha=.5),
             'epsilon_005':replace(cfg,epsilon_start=.05,epsilon_min=.05,epsilon_decay=1.),
             'epsilon_030':replace(cfg,epsilon_start=.30,epsilon_min=.30,epsilon_decay=1.)}
    all_rows=[]; learning={}; policies={};baseline=None
    for label,c in configs.items():
        curves=[]
        for seed in SEEDS:
            agent,_,rows,counts=train(c,seed);curves.append(smooth(rows));frozen=agent.q.copy()
            ev,ep=evaluate(c,agent.q,seed=800000+seed)
            assert np.array_equal(frozen,agent.q)
            r={'configuration':label,'seed':seed,**ev[0], 'opponent_mean':ev[1]['mean_reward'],
               'train_mean':float(np.mean([x['rl_mean'] for x in rows])),
               'train_first_500':float(np.mean([x['rl_mean'] for x in rows[:500]])),
               'train_last_500':float(np.mean([x['rl_mean'] for x in rows[-500:]])),
               'train_discount_rate':float(counts[0,1]/(c.episodes*c.horizon))}
            all_rows.append(r);policies[f'{label}_{seed}']=agent.q.tolist()
            write_csv(out/f'{label}_{seed}_training.csv',rows);write_csv(out/f'{label}_{seed}_evaluation.csv',ep)
        learning[label]=np.array(curves)
        print(label,'done',flush=True)
    a,_,rows,counts=train(cfg,42);baseline={'q':a.q.tolist(),'training_counts':counts.tolist()}
    ev,ep=evaluate(cfg,a.q,seed=500042);baseline['evaluation']=ev
    write_csv(out/'baseline_42_training.csv',rows);write_csv(out/'baseline_42_evaluation.csv',ep)
    write_csv(out/'baseline_42_summary.csv',ev);np.save(out/'baseline_42_q.npy',a.q)
    # Fair comparisons: same fixed opponent and evaluation tapes for every focal policy.
    fair=[];robust=[];selfplay=[];policy,_=exact_best_response(cfg)
    for seed in SEEDS:
        q=np.array(policies[f'baseline_{seed}'])
        for name,p in [('RL',q),('Rule','rule'),('Never','never'),('Always','always'),('DP',policy)]:
            ev,_=evaluate(cfg,p,seed=800000+seed);fair.append({'policy':name,'seed':seed,**ev[0]})
        c=replace(cfg,discount=.40)
        a,_,tr,_=train(c,seed)
        for name,p in [('frozen_RL',q),('retrained_RL',a.q),('Rule','rule'),('DP',exact_best_response(c)[0])]:
            ev,_=evaluate(c,p,seed=800000+seed);robust.append({'policy':name,'seed':seed,**ev[0]})
        # Both learners update; fixed held-out joint evaluation after training.
        a,b,tr,_=train(cfg,seed,selfplay=True)
        ev,_=evaluate(cfg,a.q,b.q,seed=900000+seed)
        for i,r in enumerate(ev):selfplay.append({'seed':seed,'learner':i,**r})
        write_csv(out/f'selfplay_{seed}_training.csv',tr)
        print('extensions seed',seed,'done',flush=True)
    write_csv(out/'configurations.csv',all_rows);write_csv(out/'fair_comparison.csv',fair)
    write_csv(out/'robustness_discount40.csv',robust);write_csv(out/'selfplay_summary.csv',selfplay)
    aggregates=[]
    for label in configs:
        rr=[r for r in all_rows if r['configuration']==label];v=np.array([r['mean_reward'] for r in rr])
        aggregates.append({'configuration':label,'mean':float(v.mean()),'sd':float(v.std(ddof=1)),
                           'ci95_half_t4':float(2.776*v.std(ddof=1)/np.sqrt(5)),
                           'discount_rate':float(np.mean([r['discount_rate'] for r in rr])),
                           'train_mean':float(np.mean([r['train_mean'] for r in rr])),
                           'first500':float(np.mean([r['train_first_500'] for r in rr])),
                           'last500':float(np.mean([r['train_last_500'] for r in rr]))})
    write_csv(out/'aggregate.csv',aggregates)
    plt.rcParams.update({'figure.dpi':150,'font.size':10})
    for keys,name,title in [(['baseline'],'learning_curve','Baseline training'),
                            (['alpha_001','baseline','alpha_050'],'learning_rates','Learning rate'),
                            (['baseline','epsilon_005','epsilon_030'],'exploration','Exploration')]:
        fig,ax=plt.subplots(figsize=(9,4))
        for k in keys:
            z=learning[k];x=np.arange(100,100+z.shape[1]);m=z.mean(0);s=z.std(0,ddof=1)
            ax.plot(x,m,label=k);ax.fill_between(x,m-s,m+s,alpha=.13)
        ax.set(xlabel='Episode (100-episode moving average)',ylabel='Profit / step',title=title+'; mean +/- 1 SD across 5 seeds')
        ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(out/(name+'.png'));plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,4));ax.bar([r['configuration'] for r in aggregates],[r['mean'] for r in aggregates],
        yerr=[r['sd'] for r in aggregates],capsize=4);ax.axhline(35,color='red',linestyle='--',label='Analytic never-discount expectation')
    ax.set(ylabel='Evaluation profit / step',title='Frozen policy; bars show 1 SD across 5 training/evaluation seeds');ax.tick_params(axis='x',rotation=15);ax.legend();fig.tight_layout();fig.savefig(out/'evaluation.png');plt.close(fig)
    fig,axs=plt.subplots(1,2,figsize=(9,3.5));q=np.array(baseline['q']).reshape(4,2);im=axs[0].imshow(q,cmap='Blues')
    for i in range(4):
        for j in range(2):axs[0].text(j,i,f'{q[i,j]:.1f}',ha='center',va='center')
    axs[0].set(xticks=[0,1],xticklabels=['No discount','Discount'],yticks=range(4),yticklabels=['(0,0)','(0,1)','(1,0)','(1,1)'],title='Q table, seed 42')
    grid=np.arange(0,.51,.01)
    for d in (0,1):
        axs[1].plot(grid,[expected_profit(replace(cfg,discount=float(x)),d,1,0)-expected_profit(cfg,d,0,0) for x in grid],label=f'demand={d}')
    axs[1].axhline(0,color='black',lw=.8);axs[1].set(xlabel='Discount fraction',ylabel='Expected advantage of discount',title='Immediate profit; competitor action=0');axs[1].legend();fig.tight_layout();fig.savefig(out/'q_and_sensitivity.png');plt.close(fig)
    metadata={'config':asdict(cfg),'seeds':SEEDS,'baseline':baseline,'aggregates':aggregates,'q_tables':policies,
              'python':platform.python_version(),'numpy':np.__version__,'matplotlib':matplotlib.__version__,
              'elapsed_seconds':time.time()-started,'protocol':'5 independent training seeds; paired evaluation seed=800000+seed; fixed opponent; frozen Q; epsilon=0; DP uses full state and time'}
    (out/'summary.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    print(json.dumps({'elapsed':metadata['elapsed_seconds'],'aggregate':aggregates},indent=2),flush=True)
    return metadata

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--episodes',type=int,default=5000);p.add_argument('--output',type=Path,default=ROOT/'ket_qua/assignment');a=p.parse_args();run(a.output,a.episodes)
