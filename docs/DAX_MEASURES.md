# Power BI DAX Measure Library
## FCA Consumer Duty & Fair Value Management Information (MI)

This document provides production-ready Data Analysis Expressions (DAX) measures for Power BI developers implementing FCA Consumer Duty dashboards.

---

## 1. Price & Value Outcome Measures

### `Claims Acceptance Rate %`
```dax
Claims Acceptance Rate % = 
VAR AcceptedClaims = CALCULATE(COUNTROWS(FactClaims), FactClaims[Status] = "Accepted")
VAR TotalSubmitted = COUNTROWS(FactClaims)
RETURN
    DIVIDE(AcceptedClaims, TotalSubmitted, 0)
```

### `Product Fair Value Score`
```dax
Product Fair Value Score = 
AVERAGE(DimProduct[FairValueScore])
```

### `Claims Acceptance RAG Status`
```dax
Claims Acceptance RAG Status = 
VAR AcceptanceRate = [Claims Acceptance Rate %]
RETURN
    SWITCH(
        TRUE(),
        AcceptanceRate >= 0.85, "GREEN",
        AcceptanceRate >= 0.75, "AMBER",
        "RED"
    )
```

---

## 2. Consumer Support & Vulnerability SLA Measures

### `Average Settlement Days (Vulnerable)`
```dax
Avg Settlement Days (Vulnerable) = 
CALCULATE(
    AVERAGE(FactClaims[SettlementDays]),
    DimCustomer[IsVulnerable] = 1
)
```

### `Vulnerability Settlement SLA Variance`
```dax
Vulnerability SLA Variance Days = 
VAR VulnDays = [Avg Settlement Days (Vulnerable)]
VAR StdDays = CALCULATE(AVERAGE(FactClaims[SettlementDays]), DimCustomer[IsVulnerable] = 0)
RETURN
    VulnDays - StdDays
```

---

## 3. Consumer Understanding & Complaints Measures

### `Complaints per 1,000 Policies`
```dax
Complaints per 1k Policies = 
VAR TotalComplaints = COUNTROWS(FactComplaints)
VAR TotalActivePolicies = COUNTROWS(FactPolicies)
RETURN
    DIVIDE(TotalComplaints, TotalActivePolicies, 0) * 1000
```
