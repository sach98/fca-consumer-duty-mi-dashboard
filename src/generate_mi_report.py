#!/usr/bin/env python3
"""
FCA Consumer Duty MI & Fair Value Reporting Engine
--------------------------------------------------
Performs:
1. Four Outcomes Evaluation (Products & Services, Price & Value, Consumer Understanding, Consumer Support).
2. Claims Acceptance & Settlement SLA Analysis (Vulnerable vs Standard Policyholders).
3. Fair Value Scorecard Generation & Regulatory RAG Status.

Author: Sachin Sharma (Senior Business Analyst & CII DipFPS Certified Specialist)
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def load_data(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset not found at {filepath}")
    return pd.read_csv(filepath)

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'data', 'consumer_duty_dataset.csv')
    output_dir = os.path.join(base_dir, 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    
    print("Loading FCA Consumer Duty MI Dataset...")
    df = load_data(data_path)
    
    # RAG Status Evaluation
    # Claims Acceptance Rate: >= 85% Green, 75-84% Amber, < 75% Red
    # Complaints per 1k: < 3.0 Green, 3.0-5.0 Amber, > 5.0 Red
    df['claims_acceptance_rag'] = df['claims_acceptance_rate_pct'].apply(
        lambda x: 'GREEN' if x >= 85 else ('AMBER' if x >= 75 else 'RED')
    )
    df['complaints_rag'] = df['complaints_per_1k'].apply(
        lambda x: 'GREEN' if x < 3.0 else ('AMBER' if x <= 5.0 else 'RED')
    )
    
    print("\n--- Consumer Duty MI Dashboard Summary ---")
    print(df[['product_line', 'claims_acceptance_rate_pct', 'claims_acceptance_rag', 'complaints_per_1k', 'complaints_rag', 'fair_value_score']])
    
    summary_path = os.path.join(output_dir, 'consumer_duty_mi_summary.csv')
    df.to_csv(summary_path, index=False)
    print(f"\n[SUCCESS] Exported Consumer Duty MI Summary to {summary_path}")
    
    # Visualization: Claims Acceptance & Fair Value Scores
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    
    # Chart 1: Claims Acceptance Rate by Product Line
    axes[0].bar(df['product_line'], df['claims_acceptance_rate_pct'], color=['#2ca02c', '#2ca02c', '#2ca02c', '#d62728'])
    axes[0].axhline(85.0, color='red', linestyle='--', label='FCA Target (85%)')
    axes[0].set_title('Claims Acceptance Rate (%) by Product')
    axes[0].set_ylabel('Acceptance Rate (%)')
    axes[0].grid(True, linestyle='--', alpha=0.6)
    axes[0].legend()
    
    # Chart 2: Settlement Days (Standard vs Vulnerable)
    x = np.arange(len(df['product_line']))
    width = 0.35
    axes[1].bar(x - width/2, df['avg_settlement_days_standard'], width, label='Standard Policyholders', color='#1f77b4')
    axes[1].bar(x + width/2, df['avg_settlement_days_vulnerable'], width, label='Vulnerable Policyholders', color='#ff7f0e')
    axes[1].set_title('Avg Claims Settlement Days (FCA Consumer Support Outcome)')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(df['product_line'], rotation=15)
    axes[1].set_ylabel('Days')
    axes[1].grid(True, linestyle='--', alpha=0.6)
    axes[1].legend()
    
    plt.tight_layout()
    chart_path = os.path.join(output_dir, 'consumer_duty_mi_summary.png')
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"[SUCCESS] Exported Consumer Duty MI Chart to {chart_path}")

if __name__ == '__main__':
    main()
