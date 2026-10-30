"""Focused tests for the web adapter and its interaction with the Python agents."""
import unittest
from concurrent.futures import ThreadPoolExecutor
from server import recommend, classify, overview, catalog

class WebAdapterTests(unittest.TestCase):
    def test_search_returns_verified_catalog_items(self):
        data = recommend({'query': 'portable', 'budget': 100})
        self.assertEqual(data['status'], 'ok')
        self.assertEqual([p['id'] for p in data['items']], ['p2', 'p4'])
        self.assertTrue(all(p['price'] <= 100 and p['availability'] == 'verified' for p in data['items']))
        self.assertEqual([x['agent'] for x in data['trace']], ['catalog', 'recommender', 'policy', 'inventory'])

    def test_unknown_and_budget(self):
        self.assertEqual(recommend({'query': 'unknown', 'budget': 100})['status'], 'no_results')
        self.assertEqual(recommend({'query': 'portable', 'budget': -1})['status'], 'invalid_input')
        self.assertEqual(recommend({'query': 'sports', 'budget': 100})['items'], [])

    def test_failure_scenarios_do_not_return_products(self):
        expected = {'timeout': 'timeout', 'malformed': 'contract_error',
                    'stale': 'availability_unverified', 'forged': 'contract_error'}
        for scenario, status in expected.items():
            with self.subTest(scenario=scenario):
                result = recommend({'query': 'portable', 'budget': 100, 'scenario': scenario})
                self.assertEqual(result['status'], status)
                self.assertEqual(result['items'], [])

    def test_invalid_requests(self):
        for payload in (None, {}, {'query': 3, 'budget': 10}, {'query': 'x', 'budget': True},
                        {'query': 'x', 'budget': 10, 'scenario': 'other'}):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                recommend(payload)
        with self.assertRaises(ValueError):
            classify({'text': ''})

    def test_overview_uses_saved_experiment(self):
        data = overview()
        self.assertEqual(data['catalog_count'], 5)
        self.assertEqual(data['intent']['splits']['test'], 108)
        self.assertEqual(data['episodes'], 5000)
        self.assertEqual(len(data['assignment']), 5)
        self.assertEqual(len(catalog()), 5)

    def test_classifier_uses_trained_model_and_abstains(self):
        self.assertEqual(classify({'text': 'tìm mua laptop cho tôi'})['intent'], 'ecommerce')
        self.assertEqual(classify({'text': 'abc xyz'})['intent'], 'clarify')

    def test_parallel_requests_have_isolated_traces(self):
        inputs = [{'query': 'portable', 'budget': 100}, {'query': 'unknown', 'budget': 100}]
        with ThreadPoolExecutor(max_workers=2) as pool:
            first, second = list(pool.map(recommend, inputs))
        self.assertEqual([t['agent'] for t in first['trace']], ['catalog', 'recommender', 'policy', 'inventory'])
        self.assertEqual([t['agent'] for t in second['trace']], ['catalog'])

if __name__ == '__main__':
    unittest.main(verbosity=2)
