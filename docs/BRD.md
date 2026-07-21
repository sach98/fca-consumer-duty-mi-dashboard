# Business Requirements Document (BRD)
## FCA Consumer Duty & Fair Value Management Information (MI) Framework

**Document Control**
- **Author:** Sachin Sharma (Business Analyst, CII DipFPS R01-R06 Certified)
- **Version:** 1.1
- **Date:** 2026-07-22
- **Status:** Draft. This is a portfolio exercise on synthetic data. It has not been
  reviewed or approved by any firm, and no approver is named because none exists.
- **Intended audience (illustrative):** Chief Risk Officer, Regulatory Compliance
  Committee, Customer Outcomes Directors

**Threshold provenance.** The FCA does not publish numeric pass/fail thresholds for
claims acceptance or complaint volumes under Consumer Duty. Every band below is an
**internal review trigger** chosen for this exercise. Breaching one escalates a product
line to an internal Fair Value review. It does not constitute a regulatory breach, and
no regulatory consequence should be inferred from it.

**Traceability.** Each requirement below names the function that implements it and the
test that covers it. All thresholds are defined once, in
`src/consumer_duty_rules.py`.

| Req | Implemented by | Covered by |
|---|---|---|
| BR-01 | `classify_acceptance()` | `TestAcceptanceBoundaries` |
| BR-02 | `check_vulnerable_sla()` | `TestBookLevelMetrics`, report output |
| BR-03 | `classify_complaints()` | `TestComplaintsBoundaries` |
| BR-04 | `book_level_metrics()` | `TestBookLevelMetrics` |
| BR-05 | `rate_product_line()` | `TestExposureFloor` |

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
- **Internal review trigger:** 85% acceptance rate across retail product lines.
- **RAG bands:**
  - `GREEN`: acceptance rate >= 85.0%
  - `AMBER`: acceptance rate 75.0% to 84.99% (product committee review)
  - `RED`: acceptance rate < 75.0% (escalate to Fair Value review)

### BR-02: Vulnerable Customer Support SLA (Consumer Support Outcome)
- **Requirement:** settlement turnaround for vulnerable policyholders must not exceed
  the standard turnaround on the same product line.
- **Measure:** `sla_gap_days = avg_settlement_days_standard - avg_settlement_days_vulnerable`.
  A negative gap is a breach.
- **Output:** `outputs/vulnerable_sla_check.csv`, one row per product line.

### BR-03: Complaints Threshold Monitoring (Consumer Understanding Outcome)
- **Internal review trigger:** 3.0 complaints per 1,000 active policies.
- **RAG bands:**
  - `GREEN`: < 3.0 per 1,000
  - `AMBER`: 3.0 to 5.0 per 1,000
  - `RED`: > 5.0 per 1,000

### BR-04: Book-Level Aggregation
- **Requirement:** firm-level measures must be weighted by exposure, not averaged
  across product lines. Acceptance aggregates on claim counts; complaint rates and
  score averages aggregate on active policies.
- **Rationale:** an unweighted mean treats a 15,000-policy line and a 45,000-policy
  line as equal contributors and misstates the firm position. On the current dataset
  it understates book acceptance by 2.05 percentage points.

### BR-05: Minimum Exposure for Rating
- **Requirement:** a product line with fewer than 100 submitted claims is reported as
  `INSUFFICIENT_EXPOSURE` and is not RAG-rated.
- **Rationale:** prevents a thin book from being escalated to a Fair Value review on
  the strength of a handful of claims.

### Overall product RAG
- Worst-of across BR-01 and BR-03. A line that is AMBER on acceptance and RED on
  complaints reports RED overall.
