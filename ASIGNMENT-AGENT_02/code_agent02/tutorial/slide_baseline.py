"""Executable transcription of Units 7-9 of the supplied teaching slide.
This baseline intentionally has no inventory/freshness/timeout controls.
The extended implementation is in mas_system.py.
"""
from dataclasses import dataclass
from typing import Any
from pathlib import Path
import json

@dataclass
class Message:
    sender: str
    receiver: str
    kind: str
    payload: dict[str, Any]

class Agent:
    def __init__(self,name):self.name=name
    def handle(self,message):raise NotImplementedError

PRODUCTS=[{'id':'p1','name':'Lightweight laptop','category':'electronics','price':850,'tags':['portable','study']},
          {'id':'p2','name':'Wireless mouse','category':'electronics','price':25,'tags':['portable','accessory']},
          {'id':'p3','name':'Running shoes','category':'sports','price':70,'tags':['fitness','outdoor']},
          {'id':'p4','name':'Travel backpack','category':'travel','price':55,'tags':['portable','travel']}]

class CatalogAgent(Agent):
    def __init__(self,products):super().__init__('catalog');self.products=products
    def handle(self,message):
        query=message.payload.get('query','').strip().lower()
        def matches(item):
            fields=[item['name'],item['category']]+item.get('tags',[])
            return any(query in str(value).lower() for value in fields)
        items=[item for item in self.products if query and matches(item)]
        return Message(self.name,message.sender,'SEARCH_RESULTS',{'items':items})

class RecommendationAgent(Agent):
    def __init__(self):super().__init__('recommender')
    def handle(self,message):
        budget=float(message.payload.get('budget',0));items=message.payload.get('items',[])
        candidates=[item for item in items if item['price']<=budget]
        ranked=sorted(candidates,key=lambda item:('portable' not in item['tags'],item['price']))
        return Message(self.name,message.sender,'RECOMMENDATIONS',{'items':ranked[:3]})

class Coordinator(Agent):
    def __init__(self,catalog,recommender):super().__init__('coordinator');self.catalog=catalog;self.recommender=recommender
    def shop(self,query,budget):
        search=Message(self.name,'catalog','SEARCH',{'query':query})
        found=self.catalog.handle(search)
        rank=Message(self.name,'recommender','RANK',{'items':found.payload['items'],'budget':budget})
        return self.recommender.handle(rank).payload['items']

def run_baseline():
    system=Coordinator(CatalogAgent(PRODUCTS),RecommendationAgent())
    items=system.shop('portable',100)
    assert [p['id'] for p in items]==['p2','p4']
    assert all(p['price']<=100 for p in items)
    assert not system.shop('unknown-query',100)
    assert not system.shop('',100)
    candidates={p['id'] for p in CatalogAgent(PRODUCTS).handle(Message('x','catalog','SEARCH',{'query':'portable'})).payload['items']}
    assert all(p['id'] in candidates for p in items)
    result={'query':'portable','budget':100,'items':items,'checks_passed':5,'source':'Teaching slide Units 7-9; original four-product baseline'}
    out=Path(__file__).resolve().parents[1]/'results/tutorial/slide_baseline.json'
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,indent=2));return result
if __name__=='__main__':run_baseline()
