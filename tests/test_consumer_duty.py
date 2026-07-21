"""
Behavioural tests for the Consumer Duty MI rules.

These assert the classification boundaries and the aggregation arithmetic
against hand-computed expected values, and they import the production rules
rather than re-implementing them, so a change to a threshold in
src/consumer_duty_rules.py fails a test here instead of passing silently.
"""

import os
import unittest

import pandas as pd

from src.consumer_duty_rules import (
    apply_rag,
    book_level_metrics,
    classify_acceptance,
    classify_complaints,
    overall_rag,
)
from src.generate_mi_report import build_markdown_table, load_data

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestAcceptanceBoundaries(unittest.TestCase):
    """The band edges are where a misclassification would actually happen."""

    def test_green_boundary(self):
        self.assertEqual(classify_acceptance(85.0), 'GREEN')
        self.assertEqual(classify_acceptance(84.99), 'AMBER')

    def test_amber_boundary(self):
        self.assertEqual(classify_acceptance(75.0), 'AMBER')
        self.assertEqual(classify_acceptance(74.99), 'RED')

    def test_travel_at_79_is_amber_not_red(self):
        # Regression guard: the published README table once reported this as RED.
        self.assertEqual(classify_acceptance(79.0), 'AMBER')


class TestComplaintsBoundaries(unittest.TestCase):

    def test_green_boundary(self):
        self.assertEqual(classify_complaints(2.99), 'GREEN')
        self.assertEqual(classify_complaints(3.0), 'AMBER')

    def test_amber_boundary(self):
        self.assertEqual(classify_complaints(5.0), 'AMBER')
        self.assertEqual(classify_complaints(5.01), 'RED')


class TestOverallRag(unittest.TestCase):

    def test_worst_of_wins(self):
        self.assertEqual(overall_rag('GREEN', 'RED'), 'RED')
        self.assertEqual(overall_rag('GREEN', 'AMBER'), 'AMBER')
        self.assertEqual(overall_rag('GREEN', 'GREEN'), 'GREEN')

    def test_unknown_value_raises(self):
        with self.assertRaises(ValueError):
            overall_rag('PURPLE')


class TestExposureFloor(unittest.TestCase):

    def test_thin_book_is_not_rated(self):
        thin = pd.Series({
            'claims_submitted': 40,
            'claims_acceptance_rate_pct': 50.0,
            'complaints_per_1k': 99.0,
        })
        from src.consumer_duty_rules import rate_product_line
        result = rate_product_line(thin)
        self.assertEqual(result['regulatory_rag'], 'INSUFFICIENT_EXPOSURE')


class TestBookLevelMetrics(unittest.TestCase):
    """
    Exposure weighting is the fix for a real defect: the console previously
    reported an unweighted mean of per-product ratios.
    """

    def setUp(self):
        self.df = load_data(os.path.join(BASE_DIR, 'data', 'consumer_duty_dataset.csv'))

    def test_acceptance_rate_uses_claim_counts(self):
        book = book_level_metrics(self.df)
        # 9,313 accepted / 10,400 submitted = 89.5481%
        self.assertAlmostEqual(book['claims_acceptance_rate_pct'], 89.5481, places=3)

    def test_weighted_differs_from_naive_mean(self):
        book = book_level_metrics(self.df)
        naive = self.df['claims_acceptance_rate_pct'].mean()
        self.assertAlmostEqual(naive, 87.5, places=3)
        self.assertGreater(book['claims_acceptance_rate_pct'] - naive, 2.0)

    def test_complaints_per_1k_uses_policy_counts(self):
        book = book_level_metrics(self.df)
        # 361 complaints / 120,000 policies * 1000 = 3.00833
        self.assertAlmostEqual(book['complaints_per_1k'], 3.00833, places=4)


class TestPublishedTableMatchesData(unittest.TestCase):
    """
    The README table is generated from the rated frame. This asserts the
    committed README still matches, so the published numbers cannot drift
    away from the shipped data again.
    """

    def test_readme_table_matches_generated_table(self):
        df = load_data(os.path.join(BASE_DIR, 'data', 'consumer_duty_dataset.csv'))
        expected = build_markdown_table(apply_rag(df))

        with open(os.path.join(BASE_DIR, 'README.md')) as handle:
            readme = handle.read()

        for line in expected.splitlines():
            self.assertIn(
                line.strip(),
                readme,
                msg=f"README.md is out of date. Missing row:\n  {line.strip()}\n"
                    "Re-run: python3 -m src.generate_mi_report",
            )


if __name__ == '__main__':
    unittest.main()
