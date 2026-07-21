#!/usr/bin/env python3
"""
FCA Consumer Duty MI & Fair Value Reporting Engine
--------------------------------------------------
Performs:
1. Four Outcomes Evaluation (Products & Services, Price & Value, Consumer Understanding, Consumer Support).
2. Claims Acceptance & Settlement SLA Analysis (Vulnerable vs Standard Policyholders).
3. Fair Value Scorecard Generation & Regulatory RAG Status.

All RAG thresholds and aggregations live in src/consumer_duty_rules.py so that
this report, the Streamlit console and the tests cannot disagree.

Author: Sachin Sharma
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.consumer_duty_rules import (
    ACCEPTANCE_GREEN_MIN,
    apply_rag,
    book_level_metrics,
    check_vulnerable_sla,
)

RAG_COLOURS = {
    'GREEN': '#2ca02c',
    'AMBER': '#ff7f0e',
    'RED': '#d62728',
    'INSUFFICIENT_EXPOSURE': '#7f7f7f',
}

AS_AT_DATE = '2026-07-22'


def load_data(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset not found at {filepath}")
    return pd.read_csv(filepath)


def build_markdown_table(rated):
    """
    Render the executive MI table as markdown, straight from the rated frame.

    README.md embeds the output of this function. It is generated rather than
    hand-typed so the published table can never contradict the shipped CSV.
    """
    header = (
        "| Product Line | Active Policies | Claims Acceptance (%) | Acceptance RAG "
        "| Complaints per 1k | Complaints RAG | Overall RAG | Fair Value Score (out of 10) |"
    )
    divider = "|---|---|---|---|---|---|---|---|"
    rows = [header, divider]
    for _, row in rated.iterrows():
        rows.append(
            f"| **{row['product_line']}** "
            f"| {row['active_policies']:,} "
            f"| **{row['claims_acceptance_rate_pct']:.1f}%** "
            f"| {row['claims_acceptance_rag']} "
            f"| **{row['complaints_per_1k']:.2f}** "
            f"| {row['complaints_rag']} "
            f"| {row['regulatory_rag']} "
            f"| **{row['fair_value_score']:.1f}** |"
        )
    return "\n".join(rows)


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'data', 'consumer_duty_dataset.csv')
    output_dir = os.path.join(base_dir, 'outputs')
    os.makedirs(output_dir, exist_ok=True)

    print("Loading FCA Consumer Duty MI Dataset...")
    df = load_data(data_path)
    rated = apply_rag(df)

    print("\n--- Consumer Duty MI Dashboard Summary ---")
    print(rated[['product_line', 'claims_acceptance_rate_pct', 'claims_acceptance_rag',
                 'complaints_per_1k', 'complaints_rag', 'regulatory_rag', 'fair_value_score']])

    book = book_level_metrics(df)
    print("\n--- Book-Level Position (exposure-weighted) ---")
    print(f"Claims acceptance rate : {book['claims_acceptance_rate_pct']:.2f}% "
          f"({book['claims_accepted']:,} accepted / {book['claims_submitted']:,} submitted)")
    print(f"Complaints per 1k      : {book['complaints_per_1k']:.2f} "
          f"across {book['active_policies']:,} policies")
    print(f"Fair value score       : {book['fair_value_score']:.2f} / 10")

    sla = check_vulnerable_sla(df)
    breaches = sla[sla['br02_breach']]
    print("\n--- BR-02 Vulnerable Customer SLA Check ---")
    if breaches.empty:
        print(f"PASS: vulnerable settlement is at or faster than standard on all "
              f"{len(sla)} product lines (smallest margin "
              f"{sla['sla_gap_days'].min():.1f} days).")
    else:
        print(f"BREACH on {len(breaches)} product line(s):")
        print(breaches[['product_line', 'sla_gap_days']].to_string(index=False))

    sla_path = os.path.join(output_dir, 'vulnerable_sla_check.csv')
    sla.to_csv(sla_path, index=False)
    print(f"[SUCCESS] Exported BR-02 SLA check to {sla_path}")

    summary_path = os.path.join(output_dir, 'consumer_duty_mi_summary.csv')
    rated.to_csv(summary_path, index=False)
    print(f"\n[SUCCESS] Exported Consumer Duty MI Summary to {summary_path}")

    table_path = os.path.join(output_dir, 'consumer_duty_mi_table.md')
    with open(table_path, 'w') as handle:
        handle.write(build_markdown_table(rated) + "\n")
    print(f"[SUCCESS] Exported README MI table to {table_path}")

    # Visualization: Claims Acceptance & Settlement Equity
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Chart 1: Claims acceptance rate, coloured by its own RAG rather than by
    # row position, so re-ordering the dataset cannot mislabel a bar.
    bar_colours = [RAG_COLOURS[rag] for rag in rated['claims_acceptance_rag']]
    axes[0].bar(rated['product_line'], rated['claims_acceptance_rate_pct'], color=bar_colours)
    axes[0].axhline(
        ACCEPTANCE_GREEN_MIN,
        color='black',
        linestyle='--',
        linewidth=1,
        label=f'Internal review trigger ({ACCEPTANCE_GREEN_MIN:.0f}%)',
    )
    axes[0].axhline(
        book['claims_acceptance_rate_pct'],
        color='#1f77b4',
        linestyle=':',
        linewidth=2,
        label=f"Book average ({book['claims_acceptance_rate_pct']:.1f}%)",
    )
    # Labels sit inside the bar tops so they cannot collide with the book-average line.
    for idx, value in enumerate(rated['claims_acceptance_rate_pct']):
        axes[0].text(idx, value - 4.0, f'{value:.1f}%', ha='center', va='top',
                     fontsize=10, color='white', fontweight='bold')
    axes[0].set_title(
        f"Travel is the only line below the {ACCEPTANCE_GREEN_MIN:.0f}% review trigger"
    )
    axes[0].set_ylabel('Claims acceptance rate (%)')
    axes[0].set_ylim(0, 105)
    axes[0].tick_params(axis='x', rotation=15)
    axes[0].grid(True, linestyle='--', alpha=0.6)
    axes[0].legend(fontsize=8)

    # Chart 2: Settlement Days (Standard vs Vulnerable)
    x = np.arange(len(rated['product_line']))
    width = 0.35
    axes[1].bar(x - width / 2, rated['avg_settlement_days_standard'], width,
                label='Standard policyholders', color='#1f77b4')
    axes[1].bar(x + width / 2, rated['avg_settlement_days_vulnerable'], width,
                label='Vulnerable policyholders', color='#ff7f0e')
    axes[1].set_title('Vulnerable customers settle faster on every line')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(rated['product_line'], rotation=15)
    axes[1].set_ylabel('Average settlement time (days)')
    axes[1].grid(True, linestyle='--', alpha=0.6)
    axes[1].legend(fontsize=8)

    plt.tight_layout(rect=[0, 0.06, 1, 1])
    fig.text(
        0.5, 0.02,
        'Source: synthetic illustrative dataset (data/consumer_duty_dataset.csv) | '
        f"as at {AS_AT_DATE} | {book['active_policies']:,} active policies | "
        'RAG bands are internal review triggers, not FCA limits',
        ha='center',
        fontsize=8,
        color='#444444',
    )
    chart_path = os.path.join(output_dir, 'consumer_duty_mi_summary.png')
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"[SUCCESS] Exported Consumer Duty MI Chart to {chart_path}")


if __name__ == '__main__':
    main()
