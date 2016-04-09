import sys
import search
from inverted_index import Dictionary
import unittest

class SearchTest(unittest.TestCase):
    def are_lists_equal(self, a, b):
        return ','.join(a) == ','.join(b)

    def test_get_ltc(self):
        N = 1000000
        dic = Dictionary({
            'auto': {'frequency': 5000},
            'best': {'frequency': 50000},
            'car': {'frequency': 10000},
            'insurance': {'frequency': 1000},
            })
        tokens = ['best', 'car', 'insurance']
        ltc = search.get_ltc(tokens, dic, N)
        self.assertEqual(ltc['best'], 0.34)
        self.assertEqual(ltc['car'], 0.52)
        self.assertEqual(ltc['insurance'], 0.78)

    def test_negative_get_ltc(self):
        N = 1000000
        dic = Dictionary({
            'auto': {'frequency': 5000},
            'best': {'frequency': 50000},
            'car': {'frequency': 10000},
            'insurance': {'frequency': 1000},
            })
        tokens = ['foo', 'bar']
        ltc = search.get_ltc(tokens, dic, N)
        self.assertEqual(ltc, None)


    def test_scoring(self):
        scores = search.Scores()
        scores.add_product('5', 0)
        scores.add_product('6', 0.44)
        scores.add_product('5', 0)
        scores.add_product('5', 0.27)
        scores.add_product('5', 0.53)
        self.assertEqual(scores.get_score('5'), 0.8)
        self.assertEqual(scores.get_score('6'), 0.44)

    def test_get_top_k_results(self):
        scores = search.Scores()
        scores.add_product('3', 1.6)             
        scores.add_product('6', 0.44)     
        scores.add_product('9', 0.8)
        scores.add_product('5', 0.8)
        scores.add_product('7', 0.8)
        scores.add_product('2', 1.5)
        # correct order: 3, 2, 5, 7, 9, 6

        results = scores.get_top_results(6)
        self.assertTrue(self.are_lists_equal(results, ['3','2','5','7','9','6']))

        results = scores.get_top_results(1)
        self.assertTrue(self.are_lists_equal(results, ['3']))

        results = scores.get_top_results(0)
        self.assertTrue(self.are_lists_equal(results, []))

        results = scores.get_top_results(3)
        self.assertTrue(self.are_lists_equal(results, ['3','2','5']))

        results = scores.get_top_results(10)
        self.assertTrue(self.are_lists_equal(results, ['3','2','5','7','9','6']))   