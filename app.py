import os

import pandas as pd
import plotly.express as px
import streamlit as st

from src.consumer_duty_rules import (
    ACCEPTANCE_GREEN_MIN,
    COMPLAINTS_GREEN_MAX,
    apply_rag,
    book_level_metrics,
)

st.set_page_config(page_title="FCA Consumer Duty MI Dashboard", layout="wide")

st.title("FCA Consumer Duty & Fair Value Regulatory MI Console")
st.caption(
    "Synthetic illustrative data, not a real book. RAG bands are internal review "
    "triggers defined in src/consumer_duty_rules.py, not FCA-published limits."
)

base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, 'data', 'consumer_duty_dataset.csv')
df = pd.read_csv(data_path)

# Rate the whole book once, then filter. Rating after filtering would let the
# scatter and the table disagree about the same product line.
rated = apply_rag(df)

st.sidebar.header("Filter Product Line")
selected_product = st.sidebar.selectbox(
    "Select Product Line", ["All Products"] + list(rated['product_line'].unique())
)

if selected_product != "All Products":
    filtered_df = rated[rated['product_line'] == selected_product]
else:
    filtered_df = rated.copy()

st.subheader("1. Four Outcomes Executive Summary")
st.caption(
    "Exposure-weighted across the selection. An unweighted mean of per-product "
    "ratios would treat a 15,000-policy line and a 45,000-policy line as equals."
)
col1, col2, col3, col4 = st.columns(4)

book = book_level_metrics(filtered_df)

col1.metric(
    "Claims Acceptance Rate",
    f"{book['claims_acceptance_rate_pct']:.2f}%",
    delta=f"Trigger: >={ACCEPTANCE_GREEN_MIN:.0f}%",
)
col2.metric(
    "Complaints / 1k Policies",
    f"{book['complaints_per_1k']:.2f}",
    delta=f"Trigger: <{COMPLAINTS_GREEN_MAX:.1f}",
    delta_color="inverse",
)
col3.metric("Fair Value Score", f"{book['fair_value_score']:.2f} / 10")
col4.metric("Vulnerable Customer Score", f"{book['vulnerable_satisfaction_score']:.2f} / 10")

st.caption(
    f"Basis: {book['claims_accepted']:,} claims accepted of {book['claims_submitted']:,} "
    f"submitted, across {book['active_policies']:,} active policies."
)

st.subheader("2. Product Regulatory RAG Matrix")
st.dataframe(
    filtered_df[[
        'product_line', 'active_policies', 'claims_submitted',
        'claims_acceptance_rate_pct', 'claims_acceptance_rag',
        'complaints_per_1k', 'complaints_rag', 'fair_value_score', 'regulatory_rag',
    ]],
    use_container_width=True,
)

st.subheader("3. Claims Acceptance vs. Complaint Rates")
fig = px.scatter(
    filtered_df,
    x='claims_acceptance_rate_pct',
    y='complaints_per_1k',
    text='product_line',
    size='active_policies',
    color='regulatory_rag',
    color_discrete_map={
        'GREEN': '#2ca02c',
        'AMBER': '#ff7f0e',
        'RED': '#d62728',
        'INSUFFICIENT_EXPOSURE': '#7f7f7f',
    },
    title="Price & Value Outcome Matrix",
    labels={
        'claims_acceptance_rate_pct': 'Claims Acceptance Rate (%)',
        'complaints_per_1k': 'Complaints per 1k Policies',
    },
)
fig.add_vline(x=ACCEPTANCE_GREEN_MIN, line_dash="dash", line_color="grey")
fig.add_hline(y=COMPLAINTS_GREEN_MAX, line_dash="dash", line_color="grey")
st.plotly_chart(fig, use_container_width=True)
