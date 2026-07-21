# FCA Consumer Duty & Fair Value MI Dashboard

A regulatory Management Information (MI) analytics framework and business analysis specification aligned with the UK Financial Conduct Authority (FCA) Consumer Duty regulations (FG22/5).

---

## 📸 Empirical Proof of Execution & Visual Deliverables

### 1. FCA Four Outcomes Regulatory MI Dashboard
![Consumer Duty MI Summary](outputs/consumer_duty_mi_summary.png)

### 2. Automated Unit Test Verification (100% Pass)
```bash
python3 -m unittest discover -s tests
..
----------------------------------------------------------------------
Ran 2 tests in 0.002s

OK
```

---

## 📊 Summary Results & Executive MI

| Product Line | Active Policies | Claims Acceptance (%) | Acceptance RAG | Complaints per 1k | Complaints RAG | Fair Value Score (out of 10) |
|---|---|---|---|---|---|---|
| **Pet Insurance** | 22,000 | **93.0%** | 🟢 GREEN | **2.00** | 🟢 GREEN | **8.9** |
| **Motor Insurance** | 45,000 | **90.0%** | 🟢 GREEN | **3.11** | 🟡 AMBER | **8.4** |
| **Home Insurance** | 38,000 | **88.0%** | 🟢 GREEN | **2.50** | 🟢 GREEN | **8.1** |
| **Travel Insurance** | 15,000 | **79.0%** | 🔴 RED | **5.47** | 🔴 RED | **7.2** |

*Travel Insurance is flagged in RED due to low claims acceptance (79%) and elevated complaint rates (5.47/1k), triggering a mandatory Product Governance & Fair Value Review under FCA rules.*

---

## 🚀 How to Run & Reproduce

```bash
git clone https://github.com/sach98/fca-consumer-duty-mi-dashboard.git
cd fca-consumer-duty-mi-dashboard
python3 src/generate_mi_report.py
python3 -m unittest discover -s tests
streamlit run app.py
```
*Generates `outputs/consumer_duty_mi_summary.csv` and `outputs/consumer_duty_mi_summary.png`.*

---

## 📜 Regulatory & DAX Artifacts
- **[docs/BRD.md](docs/BRD.md)** — FCA Consumer Duty Four Outcomes Business Requirements Document.
- **[docs/DAX_MEASURES.md](docs/DAX_MEASURES.md)** — Power BI DAX Measure Library for Consumer Duty.
