# Data Quality Anomaly Analysis Report

**Generated:** 2026-11-20T15:54:18.050236+00:00  
**Total Records Analyzed:** 10  
**Total Columns:** 4  
**Anomalies Detected:** 3  

---

## 1. Executive Summary

⚠️ **Dataset Status: ACTION REQUIRED.** Found 3 anomalies requiring review.

## 2. Column Summary Table

| Column | Null Count | Null % | Type | Details |
| :--- | :--- | :--- | :--- | :--- |
| `id` | 0 | 0.0% | Numeric | Mean: 5.5, StdDev: 2.8723 |
| `transaction_amount` | 0 | 0.0% | Numeric | Mean: 1590.2, StdDev: 4469.9337 |
| `account_status` | 1 | 10.0% | Categorical/Text | N/A |
| `city` | 1 | 10.0% | Categorical/Text | N/A |

## 3. Detected Anomalies Ledger

| Anomaly Type | Column | Severity | Description |
| :--- | :--- | :--- | :--- |
| `STATISTICAL_OUTLIER` | `transaction_amount` | **MEDIUM** | Row 10: Value 15000.0 (Z=3.0) |
| `MISSING_DATA` | `account_status` | **MEDIUM** | 1 missing entries |
| `MISSING_DATA` | `city` | **MEDIUM** | 1 missing entries |
