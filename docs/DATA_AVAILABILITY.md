# Data Availability & Reference File Audit

**Document Version**: 1.0.0  
**Phase**: Phase 2 — Ground-Truth & Reference-Data Readiness Audit  
**Date**: 2026-08-21  

---

## 1. Executive Summary

A comprehensive, recursive physical audit of the local filesystem (`unilog/`, `bundle/`, `Downloads/`, `Desktop/`, `AppData/`) was conducted. 

The environment contains **3 core dataset files** and **0 of the 9 supplementary Excel/Word reference files**.

---

## 2. Comprehensive Inventory Table

| Reference File | Status | Exact Path | Role & Usage |
| :--- | :--- | :--- | :--- |
| **`Unihack__Sample_Dataset_-_Input.csv`** | **PRESENT** | `data/Unihack__Sample_Dataset_-_Input.csv` | **Core Input Dataset** (1,000 raw supplier rows) |
| **`Unihack__Expected_Output_-_Delivery_Format.csv`** | **PRESENT** | `data/Unihack__Expected_Output_-_Delivery_Format.csv` | **Immutable Delivery Schema Contract** (252 Columns) |
| **`subset_tools.csv`** | **PRESENT** | `data/subset_tools.csv` | **Testing Subset** (73 raw supplier rows) |
| **`Unilog-Sample_200_Items-Input-vs-Output.xlsx`** | **UNAVAILABLE** | N/A | 200-item ground-truth benchmark workbook |
| **`UNILOG_INTERNAL_CONTENT_GUIDELINES.docx`** | **UNAVAILABLE** | N/A | Master content formatting guidelines |
| **`Unilog_Master_UOM_Standards_Abbreviations_and_Terms.xlsx`** | **UNAVAILABLE** | N/A | ~500 approved UOM master mapping |
| **`Decimal_Fraction.xlsx`** | **UNAVAILABLE** | N/A | 63 exact inch decimal-fraction lookup table |
| **`UniCat_Manufacturer_and_Brand_List.xlsx`** | **UNAVAILABLE** | N/A | 27,000+ approved manufacturer & brand list |
| **`Unicat_Lov_v1_0_Updated_With_Remarks.xlsx`** | **UNAVAILABLE** | N/A | ~161,000 row List of Values vocabulary |
| **`FAUCETS_LOV.xlsx`** | **UNAVAILABLE** | N/A | Faucets category depth spec |
| **`Fittings_LOV.xlsx`** | **UNAVAILABLE** | N/A | Pipe/tube fittings category depth spec |
| **`Reference_Documents_Summary.xlsx`** | **UNAVAILABLE** | N/A | Reference documents index |

---

## 3. Ground Truth Availability Statement

**The 200-item Input-vs-Delivery ground-truth workbook (`Unilog-Sample_200_Items-Input-vs-Output.xlsx`) does NOT exist in the accessible workspace.**

### Governance Impact
- The pipeline evaluation operates against `data/Unihack__Sample_Dataset_-_Input.csv` (1,000 rows) and the immutable 252-column schema contract `data/Unihack__Expected_Output_-_Delivery_Format.csv`.
- Generated delivery outputs (`output/final_delivery.csv`) are **never mislabeled as ground truth**.
- Reference data loaders in `src/reference_data/` operate using deterministic, high-precision fallback modules (`src/uom.py`, `src/brand_map.py`, `src/classify.py`, `src/category_schema.py`, `src/dim_parser.py`) until reference files are placed in `data/reference/`.
- No synthetic or fabricated reference files have been created.
