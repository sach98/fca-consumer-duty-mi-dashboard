import os
import unittest
import pandas as pd
from src.generate_mi_report import load_data

class TestConsumerDutyMI(unittest.TestCase):

    def setUp(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.dataset_path = os.path.join(base_dir, 'data', 'consumer_duty_dataset.csv')

    def test_data_loading(self):
        df = load_data(self.dataset_path)
        self.assertFalse(df.empty)
        self.assertIn('product_line', df.columns)
        self.assertIn('claims_acceptance_rate_pct', df.columns)
        self.assertIn('fair_value_score', df.columns)

    def test_rag_rules(self):
        df = load_data(self.dataset_path)
        rag = df['claims_acceptance_rate_pct'].apply(
            lambda x: 'GREEN' if x >= 85 else ('AMBER' if x >= 75 else 'RED')
        )
        self.assertEqual(len(rag), len(df))
        self.assertTrue(set(rag).issubset({'GREEN', 'AMBER', 'RED'}))

if __name__ == '__main__':
    unittest.main()
