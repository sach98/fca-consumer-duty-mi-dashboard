import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="FCA Consumer Duty MI Dashboard", layout="wide")

st.title("🏛️ FCA Consumer Duty & Fair Value Regulatory MI Console")
st.markdown("**Author:** Sachin Sharma | Senior Business Analyst (CII DipFPS Certified)")

base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, 'data', 'consumer_duty_dataset.csv')
df = pd.read_csv(data_path)

st.sidebar.header("📊 Filter Product Line")
selected_product = st.sidebar.selectbox("Select Product Line", ["All Products"] + list(df['product_line'].unique()))

if selected_product != "All Products":
    filtered_df = df[df['product_line'] == selected_product]
else:
    filtered_df = df.copy()

st.subheader("1. Four Outcomes Executive Summary")
col1, col2, col3, col4 = st.columns(4)

avg_acceptance = filtered_df['claims_acceptance_rate_pct'].mean()
avg_complaints = filtered_df['complaints_per_1k'].mean()
avg_fair_value = filtered_df['fair_value_score'].mean()
avg_vuln_sat = filtered_df['vulnerable_satisfaction_score'].mean()

col1.metric("Claims Acceptance Rate", f"{avg_acceptance:.1f}%", delta="Target: >=85%")
col2.metric("Complaints / 1k Policies", f"{avg_complaints:.2f}", delta="Target: <3.0", delta_color="inverse")
col3.metric("Fair Value Score", f"{avg_fair_value:.1f} / 10")
col4.metric("Vulnerable Customer Score", f"{avg_vuln_sat:.1f} / 10")

# Product RAG Matrix
st.subheader("2. Product Regulatory RAG Matrix")

def get_rag(row):
    if row['claims_acceptance_rate_pct'] >= 85 and row['complaints_per_1k'] < 3.0:
        return '🟢 GREEN'
    elif row['claims_acceptance_rate_pct'] < 80 or row['complaints_per_1k'] > 5.0:
        return '🔴 RED'
    else:
        return '🟡 AMBER'

filtered_df['regulatory_rag'] = filtered_df.apply(get_rag, axis=1)

st.dataframe(filtered_df[['product_line', 'active_policies', 'claims_acceptance_rate_pct', 'complaints_per_1k', 'fair_value_score', 'regulatory_rag']])

# Interactive Chart
st.subheader("3. Claims Acceptance vs. Complaint Rates")
fig = px.scatter(df, x='claims_acceptance_rate_pct', y='complaints_per_1k', text='product_line', size='active_policies', color='regulatory_rag',
                 title="Price & Value Outcome Matrix", labels={'claims_acceptance_rate_pct': 'Claims Acceptance Rate (%)', 'complaints_per_1k': 'Complaints per 1k Policies'})
st.plotly_chart(fig, use_container_width=True)
