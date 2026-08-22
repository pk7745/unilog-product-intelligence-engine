# Duplicate MPN Investigation & Analysis

**Document Version**: 1.0.0  
**Phase**: Phase 3 — Data Quality & Duplicate MPN Audit  
**Date**: 2026-08-21  

---

## 1. Executive Summary

An empirical audit of `data/Unihack__Sample_Dataset_-_Input.csv` (1,000 raw rows) revealed:
- **Total Input Dataset Rows**: **1,000**
- **Total Unique MPNs**: **999**
- **Duplicated MPN Count**: **1 MPN (`AVM6EV`)** appearing **2 times** (Rows 783 and 784).

---

## 2. Detailed Comparison of Duplicate Rows

| Attribute | Row 783 | Row 784 |
| :--- | :--- | :--- |
| **`Mfg_Part_Num`** | `AVM6EV` | `AVM6EV` |
| **`Part_Manuf`** | `Malco Prod (2370)` | `Malco Prod (2370)` |
| **`Part_Desc`** | `AVM6 EV Mini Snip Red` | `AVM7 EV Mini Snip Green` |
| **`E1_Brand`** | `-- Unbranded --` | `-- Unbranded --` |
| **`Unilog_Brand`** | `-- No Unilog Brand --` | `-- No DIB Brand --` |
| **`DIB_Brand`** | `-- No DIB Brand --` | `-- No DIB Brand --` |

---

## 3. Root Cause Classification

This duplicate represents **Category (c) Supplier Data Entry Typo Error**.

### Reasoning
- **Malco Tools Catalog Identification**:
  - `AVM6EV` corresponds to Malco's offset/left-cut mini aviation snip with **red handle grips**.
  - `AVM7EV` corresponds to Malco's right-cut mini aviation snip with **green handle grips**.
- **Supplier Record Error**: The raw supplier input catalog mistakenly assigned `AVM6EV` to Row 784 instead of `AVM7EV`.

---

## 4. Preservation & Governance Policy

- **Zero Automatic Deduplication**: All 1,000 input rows are preserved 1-to-1 in `output/final_delivery.csv` and `output/qa_report.csv`.
- **No Data Deletion**: Neither row is dropped or merged.
- **Traceability**: The quality gate engine tracks 999 unique MPNs across 1,000 rows as expected for this dataset.
