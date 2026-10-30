import unittest
from dataclasses import replace
import numpy as np
from agent02_experiment import *
class AssignmentTests(unittest.TestCase):
    def test_update_example(self):
        a=QLearningAgent();a.q[0,0,0]=4;a.q[1,1]=[5,2];a.learn((0,0),0,6,(1,1));self.assertAlmostEqual(a.q[0,0,0],4.65)
    def test_terminal_no_bootstrap(self):
        a=QLearningAgent();a.q[1,1]=[100,200];a.learn((0,0),0,6,(1,1),True);self.assertAlmostEqual(a.q[0,0,0],.6)
    def test_simultaneous_observations(self):
        e=Environment(seed=1);e.reset();obs,_,_=e.step([1,0]);self.assertEqual(obs[0][1],0);self.assertEqual(obs[1][1],1)
    def test_invalid_actions(self):
        for a in [[1],[0,2],[0,1,1]]:
            with self.assertRaises(ValueError):Environment().step(a)
    def test_margin(self):self.assertEqual(Config().price*(1-.2)-Config().cost,3)
    def test_rule(self):self.assertEqual([RuleBasedAgent().act(s) for s in [(0,0),(0,1),(1,0),(1,1)]],[0,0,0,1])
    def test_freeze(self):
        a=QLearningAgent();q=a.q.copy();evaluate(replace(Config(),evaluation_episodes=10),a.q);np.testing.assert_array_equal(q,a.q)
    def test_evaluation_counts(self):
        r,_=evaluate(replace(Config(),evaluation_episodes=10),'never');self.assertEqual(r[0]['no_discount']+r[0]['discount'],200)
    def test_common_demand(self):
        c=replace(Config(),evaluation_episodes=25);a,_=evaluate(c,'never',seed=7);b,_=evaluate(c,'never',seed=7);self.assertEqual(a,b)
    def test_dp_baseline(self):
        p,v=exact_best_response(Config());self.assertTrue((p==0).all());self.assertTrue((v[-1]==0).all())
    def test_seed_reproduction(self):
        c=replace(Config(),episodes=10);a,_,r,_=train(c,7);b,_,s,_=train(c,7);np.testing.assert_array_equal(a.q,b.q);self.assertEqual(r,s)
    def test_symmetric_never(self):
        c=replace(Config(),evaluation_episodes=5000);r,_=evaluate(c,'never');self.assertLess(abs(r[0]['mean_reward']-35),.3)
if __name__=='__main__':unittest.main(verbosity=2)
