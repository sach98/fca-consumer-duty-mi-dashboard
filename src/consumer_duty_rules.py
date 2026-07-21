#!/usr/bin/env python3
"""
Consumer Duty MI: shared classification and aggregation rules.

This module is the single source of truth for the RAG thresholds and the
book-level aggregations. The batch report (src/generate_mi_report.py), the
Streamlit console (app.py) and the test suite all import from here, so the
three surfaces cannot drift apart.

THRESHOLD PROVENANCE
--------------------
The FCA does not publish numeric pass/fail thresholds for claims acceptance
or complaint volumes under Consumer Duty (FG22/5). The bands below are
INTERNAL review triggers chosen for this exercise, not regulatory limits.
They decide when a product line is escalated to a Fair Value review; they do
not determine compliance.
"""

# Internal review triggers. Not FCA-published limits. See module docstring.
ACCEPTANCE_GREEN_MIN = 85.0
ACCEPTANCE_AMBER_MIN = 75.0
COMPLAINTS_GREEN_MAX = 3.0
COMPLAINTS_AMBER_MAX = 5.0

# A product line below this earned-exposure floor is reported as
# INSUFFICIENT_EXPOSURE rather than being RAG-rated, so a small book cannot be
# escalated to a Fair Value review on the strength of a handful of claims.
MIN_CLAIMS_FOR_RATING = 100


def classify_acceptance(rate_pct):
    """RAG for claims acceptance rate. Higher is better."""
    if rate_pct >= ACCEPTANCE_GREEN_MIN:
        return 'GREEN'
    if rate_pct >= ACCEPTANCE_AMBER_MIN:
        return 'AMBER'
    return 'RED'


def classify_complaints(per_1k):
    """RAG for complaints per 1,000 policies. Lower is better."""
    if per_1k < COMPLAINTS_GREEN_MAX:
        return 'GREEN'
    if per_1k <= COMPLAINTS_AMBER_MAX:
        return 'AMBER'
    return 'RED'


def overall_rag(*rags):
    """Worst-of across the component RAGs. RED dominates AMBER dominates GREEN."""
    for level in ('RED', 'AMBER', 'GREEN'):
        if level in rags:
            return level
    raise ValueError(f"No recognised RAG value in {rags!r}")


def rate_product_line(row):
    """
    Full RAG assessment for one product line.

    Returns a dict of the three RAG columns. Product lines below the exposure
    floor are not rated at all.
    """
    if row['claims_submitted'] < MIN_CLAIMS_FOR_RATING:
        return {
            'claims_acceptance_rag': 'INSUFFICIENT_EXPOSURE',
            'complaints_rag': 'INSUFFICIENT_EXPOSURE',
            'regulatory_rag': 'INSUFFICIENT_EXPOSURE',
        }
    acceptance = classify_acceptance(row['claims_acceptance_rate_pct'])
    complaints = classify_complaints(row['complaints_per_1k'])
    return {
        'claims_acceptance_rag': acceptance,
        'complaints_rag': complaints,
        'regulatory_rag': overall_rag(acceptance, complaints),
    }


def apply_rag(df):
    """Return a copy of df with the three RAG columns appended."""
    rated = df.copy()
    assessments = rated.apply(rate_product_line, axis=1, result_type='expand')
    for column in assessments.columns:
        rated[column] = assessments[column]
    return rated


def check_vulnerable_sla(df):
    """
    BR-02: settlement turnaround for vulnerable policyholders must not exceed
    the standard turnaround on the same product line.

    Returns a frame with the per-line gap (standard minus vulnerable, so a
    positive number means vulnerable customers are served faster) and a
    boolean breach flag.
    """
    result = df[['product_line',
                 'avg_settlement_days_standard',
                 'avg_settlement_days_vulnerable']].copy()
    result['sla_gap_days'] = (
        result['avg_settlement_days_standard'] - result['avg_settlement_days_vulnerable']
    )
    result['br02_breach'] = result['sla_gap_days'] < 0
    return result


def book_level_metrics(df):
    """
    Exposure-weighted metrics for the book.

    An unweighted mean of per-product ratios silently treats a 15,000-policy
    book and a 45,000-policy book as equal contributors, which misstates the
    firm-level position. These aggregate on the underlying counts instead.
    """
    claims_submitted = df['claims_submitted'].sum()
    claims_accepted = df['claims_accepted'].sum()
    active_policies = df['active_policies'].sum()
    complaints = df['complaints_count'].sum()

    return {
        'active_policies': int(active_policies),
        'claims_submitted': int(claims_submitted),
        'claims_accepted': int(claims_accepted),
        'claims_acceptance_rate_pct': 100.0 * claims_accepted / claims_submitted,
        'complaints_per_1k': 1000.0 * complaints / active_policies,
        'fair_value_score': (
            (df['fair_value_score'] * df['active_policies']).sum() / active_policies
        ),
        'vulnerable_satisfaction_score': (
            (df['vulnerable_satisfaction_score'] * df['active_policies']).sum()
            / active_policies
        ),
    }
