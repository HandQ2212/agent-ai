import asyncio,unittest
from mas_system import *
from train_intent import dataset, Router

class TutorialTests(unittest.IsolatedAsyncioTestCase):
    async def test_tag_retrieval(self):
        r=await Coordinator().shop('portable',100);self.assertEqual([p['id'] for p in r['items']],['p2','p4'])
    async def test_budget(self):
        r=await Coordinator().shop('portable',30);self.assertTrue(all(p['price']<=30 for p in r['items']))
    async def test_unknown(self):self.assertEqual((await Coordinator().shop('zzz',100))['status'],'no_results')
    async def test_empty(self):self.assertEqual((await Coordinator().shop('',100))['items'],[])
    async def test_out_of_stock(self):self.assertEqual((await Coordinator().shop('sports',100))['items'],[])
    async def test_negative_budget(self):self.assertEqual((await Coordinator().shop('portable',-1))['status'],'invalid_input')
    async def test_nan_budget(self):self.assertEqual((await Coordinator().shop('portable',float('nan')))['status'],'invalid_input')
    async def test_timeout(self):self.assertEqual((await Coordinator().shop('portable',100,'timeout'))['status'],'timeout')
    async def test_malformed(self):self.assertEqual((await Coordinator().shop('portable',100,'malformed'))['status'],'contract_error')
    async def test_stale(self):self.assertEqual((await Coordinator().shop('portable',100,'stale'))['status'],'availability_unverified')
    async def test_forged(self):self.assertEqual((await Coordinator().shop('portable',100,'forged'))['status'],'contract_error')
    async def test_message_receiver(self):
        with self.assertRaises(ValueError):await CatalogAgent().handle(Message('a','x','wrong','SEARCH',{'query':'x'}))
    async def test_correlation(self):
        class Bad:
            name='bad'
            async def handle(self,m):return Message('other','bad','coordinator','OK',{})
        with self.assertRaises(ValueError):await Coordinator().call(Bad(),Message('a','coordinator','bad','X',{}),'OK')
    async def test_trace(self):
        s=Coordinator();await s.shop('portable',100,task_id='trace-1');self.assertEqual(len(s.trace),4)
        self.assertTrue(all(t['task_id']=='trace-1' for t in s.trace))
    async def test_split_groups(self):
        r=dataset();groups={s:{x['group'] for x in r if x['split']==s} for s in ['train','validation','test']}
        self.assertFalse(groups['train'] & groups['test']);self.assertFalse(groups['validation'] & groups['test'])
    async def test_ood_abstention(self):self.assertEqual(Router().route('abc xyz')['intent'],'clarify')
    async def test_normal_equivalence(self):
        for q in ['portable','study','unknown','sports','']:
            for b in [0,30,100,1000]:self.assertEqual(await Coordinator().shop(q,b),single_pipeline(q,b))
if __name__=='__main__':unittest.main(verbosity=2)
