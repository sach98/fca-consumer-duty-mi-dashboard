import pandas as pd
import numpy as np

data = [
    {
        'product_line': 'Motor Insurance',
        'active_policies': 45000,
        'claims_submitted': 3200,
        'claims_accepted': 2880,
        'claims_acceptance_rate_pct': 90.0,
        'avg_settlement_days_standard': 8.5,
        'avg_settlement_days_vulnerable': 7.2,
        'complaints_count': 140,
        'complaints_per_1k': 3.11,
        'fair_value_score': 8.4,
        'vulnerable_satisfaction_score': 8.8
    },
    {
        'product_line': 'Home Insurance',
        'active_policies': 38000,
        'claims_submitted': 1900,
        'claims_accepted': 1672,
        'claims_acceptance_rate_pct': 88.0,
        'avg_settlement_days_standard': 12.0,
        'avg_settlement_days_vulnerable': 10.5,
        'complaints_count': 95,
        'complaints_per_1k': 2.50,
        'fair_value_score': 8.1,
        'vulnerable_satisfaction_score': 8.6
    },
    {
        'product_line': 'Pet Insurance',
        'active_policies': 22000,
        'claims_submitted': 4100,
        'claims_accepted': 3813,
        'claims_acceptance_rate_pct': 93.0,
        'avg_settlement_days_standard': 4.2,
        'avg_settlement_days_vulnerable': 3.8,
        'complaints_count': 44,
        'complaints_per_1k': 2.00,
        'fair_value_score': 8.9,
        'vulnerable_satisfaction_score': 9.1
    },
    {
        'product_line': 'Travel Insurance',
        'active_policies': 15000,
        'claims_submitted': 1200,
        'claims_accepted': 948,
        'claims_acceptance_rate_pct': 79.0,
        'avg_settlement_days_standard': 15.4,
        'avg_settlement_days_vulnerable': 14.1,
        'complaints_count': 82,
        'complaints_per_1k': 5.47,
        'fair_value_score': 7.2,
        'vulnerable_satisfaction_score': 7.5
    }
]

df = pd.DataFrame(data)
df.to_csv('/Users/sachin/JobHunt/github-work/build/fca-consumer-duty-mi-dashboard/data/consumer_duty_dataset.csv', index=False)
print("Generated FCA Consumer Duty dataset successfully.")
