# Phase 3 Data Quality & Semantic Audit Report

**Document Version**: 1.0.0  
**Phase**: Phase 3 — Data Quality & Semantic Audit  
**Date**: 2026-08-21  

---

## 1. Executive Summary

An audit of `output/final_delivery.csv`, `output/qa_report.csv`, and `output/field_provenance.jsonl` was conducted to measure field population rates, evidence provenance quality, and schema contract adherence.

---

## 2. High-Level Population & Quality Metrics

| Field / Dimension | Total Input Rows | Populated Count | Population % | Quality Status / Governance |
| :--- | :--- | :--- | :--- | :--- |
| **`PART_NUMBER`** | 1,000 | 1,000 | 100.0% | **100% Unique & Preserved** |
| **`MANUFACTURER_NAME`** | 1,000 | 959 | 95.9% | Canonical entity resolved |
| **`BRAND_NAME`** | 1,000 | 390 | 39.0% | Placeholders cleared to empty string `""` |
| **`Fine` (Taxonomy)** | 1,000 | 366 | 36.6% | Honest non-forced classification |
| **`INVOICE_DESC`** | 1,000 | 1,000 | 100.0% | 100% compliant ($\le 40$ chars) |
| **`MOBILE_DESC`** | 1,000 | 1,000 | 100.0% | 100% compliant ($\le 80$ chars max limit) |
| **`SHORT_DESC`** | 1,000 | 1,000 | 100.0% | Channel search title format |
| **`LONG_DESC1`** | 1,000 | 1,000 | 100.0% | Detailed PDP marketing copy |
| **`MFR URL`** | 1,000 | 12 | 1.2% | Verified official manufacturer links |
| **Attribute Triplets Grid** | 1,000 | 1,231 slots | N/A | Dynamic Attribute 1..50 Name, Value, UOM |
| **Item Features Grid** | 1,000 | 1,260 slots | N/A | Feature 1..10 bullet points |

---

## 3. Provenance & Fact Status Distribution

Analysis of `output/field_provenance.jsonl` (1,233 field provenance records):

- **VERIFIED Facts (Tier 1 / Human / Agreeing)**: **105 facts**
- **UNVERIFIED Facts (Tier 3 / Regex Candidate)**: **1,126 facts**
- **CONFLICT Facts (Review Queue)**: **2 facts (`VN56920`)** held in open review state

---

## 4. Anti-Fabrication & Placeholder Clearance Compliance

1. **Zero Placeholder Leakage**: 100% of raw placeholder strings (`-- Unbranded --`, `-- No Unilog Brand --`, `-- No DIB Brand --`) are cleared to empty strings `""`.
2. **Zero Fabricated URLs**: Source MFR URLs are populated strictly when live manufacturer pages are retrieved. Missing URLs remain empty `""`.
3. **No Synthetic Fillers**: Descriptions do not contain speculative marketing phrases ("industrial grade", "premium performance").
