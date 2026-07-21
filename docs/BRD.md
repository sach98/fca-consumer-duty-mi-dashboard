# Business Requirements Document (BRD)
## FCA Consumer Duty & Fair Value Management Information (MI) Framework

**Document Control**
- **Author:** Sachin Sharma (Lead Business Analyst, CII DipFPS R01-R06 Certified)
- **Status:** Approved / Baseline
- **Target Audience:** Chief Risk Officer, Regulatory Compliance Committee, Customer Outcomes Directors

---

## 1. Regulatory Context & Objectives
Under the Financial Conduct Authority (FCA) Consumer Duty regulations (FG22/5), UK financial services firms must set higher standards of consumer protection across **Four Outcomes**:
1. **Products & Services:** Ensuring products are fit for purpose and targeted correctly.
2. **Price & Value:** Demonstrating a reasonable relationship between price paid and benefits received.
3. **Consumer Understanding:** Equipping customers to make informed decisions.
4. **Consumer Support:** Providing responsive support without unreasonable barriers.

This project specifies the **Regulatory MI Dashboard Specification** to monitor product performance, claims acceptance ratios, settlement SLAs for vulnerable customers, and product RAG status.

---

## 2. Key Performance Indicators (KPIs) & Threshold Specs

### BR-01: Claims Acceptance Ratios (Price & Value Outcome)
- **Target Benchmark:** $\ge 85\%$ acceptance rate across all retail product lines.
- **RAG Criteria:**
  - `GREEN`: Acceptance Rate $\ge 85.0\%$
  - `AMBER`: Acceptance Rate $75.0\% - 84.9\%$ (Requires product committee review)
  - `RED`: Acceptance Rate $< 75.0\%$ (Breach of Fair Value; triggers immediate product freeze review)

### BR-02: Vulnerable Customer Support SLA (Consumer Support Outcome)
- **Requirement:** Settlement turnaround time for vulnerable policyholders must not exceed standard settlement times ($\text{SLA}_{vulnerable} \le \text{SLA}_{standard}$).

### BR-03: Complaints Threshold Monitoring (Consumer Understanding Outcome)
- **Target Benchmark:** $< 3.0$ complaints per 1,000 active policies.
