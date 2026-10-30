"""Local teaching MAS. All catalog/inventory data are synthetic, prices in toy units."""
from __future__ import annotations
import asyncio, math, time
from dataclasses import dataclass, asdict
from typing import Any

@dataclass(frozen=True)
class Product:
    id: str
    name: str
    category: str
    price: float
    tags: tuple[str,...]

PRODUCTS=(Product('p1','Lightweight laptop','electronics',850,('portable','study')),
 Product('p2','Wireless mouse','electronics',25,('portable','accessory')),
 Product('p3','Running shoes','sports',70,('fitness','outdoor')),
 Product('p4','Travel backpack','travel',55,('portable','travel')),
 Product('p5','Study tablet','electronics',150,('study','portable')))
STOCK={'p1':2,'p2':5,'p3':0,'p4':3,'p5':1}

@dataclass(frozen=True)
class Message:
    task_id: str
    sender: str
    receiver: str
    kind: str
    payload: dict[str,Any]
    def validate(self,receiver,kind):
        if not self.task_id or self.receiver!=receiver or self.kind!=kind or not isinstance(self.payload,dict):
            raise ValueError('Invalid message envelope')

class CatalogAgent:
    name='catalog'
    async def handle(self,m):
        m.validate(self.name,'SEARCH');q=m.payload['query'].strip().lower()
        ids=[p.id for p in PRODUCTS if q and any(q in s.lower() for s in (p.name,p.category,*p.tags))]
        if m.payload.get('scenario')=='forged':ids+=['p99','p1']
        return Message(m.task_id,self.name,m.sender,'CANDIDATES',{'ids':ids})

class RecommendationAgent:
    name='recommender'
    async def handle(self,m):
        m.validate(self.name,'RANK'); products={p.id:p for p in PRODUCTS}
        ids=m.payload['ids'];budget=m.payload['budget']
        ranked=sorted((i for i in ids if i in products and products[i].price<=budget),key=lambda i:products[i].price)
        return Message(m.task_id,self.name,m.sender,'RANKED',{'ids':ranked[:3]})

class InventoryAgent:
    name='inventory'
    async def handle(self,m):
        m.validate(self.name,'CHECK');scenario=m.payload.get('scenario','normal')
        if scenario=='timeout':await asyncio.sleep(.05)
        if scenario=='malformed':return {'ids':m.payload['ids']}
        age=3600. if scenario=='stale' else 0.
        return Message(m.task_id,self.name,m.sender,'AVAILABILITY',
            {'stock':{i:STOCK.get(i,0) for i in m.payload['ids']},'age_seconds':age})

class PolicyAgent:
    name='policy'
    async def handle(self,m):
        m.validate(self.name,'VALIDATE');lookup={p.id:p for p in PRODUCTS}
        ids=m.payload['ids'];allowed=set(m.payload['candidates']);budget=m.payload['budget']
        if any(i not in lookup or i not in allowed or lookup[i].price>budget for i in ids):
            raise ValueError('Candidate provenance/budget violation')
        return Message(m.task_id,self.name,m.sender,'VALIDATED',{'ids':ids})

class Coordinator:
    def __init__(self,validate=True,deadline=.01):
        self.catalog=CatalogAgent();self.recommender=RecommendationAgent();self.inventory=InventoryAgent()
        self.policy=PolicyAgent();self.validate=validate;self.deadline=deadline;self.trace=[]
    async def call(self,agent,m,expected):
        start=time.perf_counter(); status='error'
        try:
            result=await asyncio.wait_for(agent.handle(m),timeout=self.deadline)
            if not isinstance(result,Message):raise TypeError('Malformed response')
            if result.task_id!=m.task_id or result.receiver!=m.sender or result.sender!=agent.name or result.kind!=expected:
                raise ValueError('Response correlation/type violation')
            status='ok';return result
        except (TimeoutError,asyncio.TimeoutError,ValueError,TypeError,KeyError):
            status='error';raise
        finally:
            self.trace.append({'task_id':m.task_id,'agent':agent.name,'kind':m.kind,
                'status':status,'milliseconds':(time.perf_counter()-start)*1000})
    async def shop(self,query,budget,scenario='normal',task_id='demo'):
        self.trace=[]
        if not isinstance(query,str) or not isinstance(budget,(int,float)) or not math.isfinite(budget) or budget<0:
            return {'status':'invalid_input','items':[]}
        def msg(receiver,kind,payload):return Message(task_id,'coordinator',receiver,kind,payload)
        try:
            c=await self.call(self.catalog,msg('catalog','SEARCH',{'query':query,'scenario':scenario}),'CANDIDATES')
            candidates=c.payload['ids']
            if not candidates:return {'status':'no_results','items':[]}
            r=await self.call(self.recommender,msg('recommender','RANK',{'ids':candidates,'budget':budget}),'RANKED')
            ids=r.payload['ids']
            # Deliberate adversarial component output, to test coordinator validation.
            if scenario=='forged':ids=['p99','p1']+ids
            if self.validate:
                p=await self.call(self.policy,msg('policy','VALIDATE',{'ids':ids,'candidates':candidates,'budget':budget}),'VALIDATED')
                ids=p.payload['ids']
            inv=await self.call(self.inventory,msg('inventory','CHECK',{'ids':ids,'scenario':scenario}),'AVAILABILITY')
            if self.validate and (not isinstance(inv.payload.get('age_seconds'),(int,float)) or not 0<=inv.payload['age_seconds']<=60):
                return {'status':'availability_unverified','items':[]}
            stocks=inv.payload['stock']
            if self.validate and (set(stocks)!=set(ids) or any(type(n) is not int or n<0 for n in stocks.values())):
                raise ValueError('Invalid stock schema')
            lookup={p.id:p for p in PRODUCTS}
            items=[{'id':i,'price':lookup[i].price if i in lookup else 0,'availability':'verified'}
                   for i in ids if stocks.get(i,0)>0 or not self.validate]
            return {'status':'ok' if items else 'no_results','items':items}
        except (TimeoutError,asyncio.TimeoutError):return {'status':'timeout','items':[]}
        except (ValueError,TypeError,KeyError):return {'status':'contract_error','items':[]}

def single_pipeline(query,budget,scenario='normal'):
    """B0: same factual checks in one component, no messaging."""
    if not isinstance(query,str) or not isinstance(budget,(int,float)) or not math.isfinite(budget) or budget<0:
        return {'status':'invalid_input','items':[]}
    q=query.strip().lower()
    candidates=[p for p in PRODUCTS if q and any(q in s.lower() for s in (p.name,p.category,*p.tags))]
    if not candidates:return {'status':'no_results','items':[]}
    eligible=sorted([p for p in candidates if p.price<=budget],key=lambda p:p.price)[:3]
    if scenario=='forged':return {'status':'contract_error','items':[]}
    if scenario=='timeout':return {'status':'timeout','items':[]}
    if scenario=='malformed':return {'status':'contract_error','items':[]}
    if scenario=='stale':return {'status':'availability_unverified','items':[]}
    items=[{'id':p.id,'price':p.price,'availability':'verified'} for p in eligible if STOCK[p.id]>0]
    return {'status':'ok' if items else 'no_results','items':items}

async def demo():
    s=Coordinator()
    for scenario in ['normal','timeout','malformed','stale','forged']:
        result=await s.shop('portable',100,scenario,task_id=scenario)
        print(scenario,result)
    return s
if __name__=='__main__':asyncio.run(demo())
