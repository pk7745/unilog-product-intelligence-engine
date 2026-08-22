# Phase 2 — Ground Truth & Reference-Data Readiness Report

**Document Version**: 2.0.0  
**Phase**: Phase 2 — Readiness Audit & Quality Gates  
**Date**: 2026-08-21  

---

## 1. Physical Reference Data & Ground Truth Audit

A comprehensive audit of the workspace was completed:
- **Core Input Dataset**: `data/Unihack__Sample_Dataset_-_Input.csv` (1,000 raw supplier rows) — **PRESENT**
- **Delivery Schema Contract**: `data/Unihack__Expected_Output_-_Delivery_Format.csv` (252 immutable columns) — **PRESENT**
- **Test Subset**: `data/subset_tools.csv` (73 raw supplier rows) — **PRESENT**
- **Ground Truth Workbook**: `Unilog-Sample_200_Items-Input-vs-Output.xlsx` — **UNAVAILABLE**
- **Supplementary Reference Files**: The 8 Excel/Word reference files (`UNILOG_INTERNAL_CONTENT_GUIDELINES.docx`, `Unilog_Master_UOM_Standards_Abbreviations_and_Terms.xlsx`, `Decimal_Fraction.xlsx`, `UniCat_Manufacturer_and_Brand_List.xlsx`, `Unicat_Lov_v1_0_Updated_With_Remarks.xlsx`, `FAUCETS_LOV.xlsx`, `Fittings_LOV.xlsx`, `Reference_Documents_Summary.xlsx`) — **UNAVAILABLE**

### Benchmark Governance Policy
- Because the 200-item ground-truth workbook is not physically present in the workspace, the pipeline evaluation operates against `data/Unihack__Sample_Dataset_-_Input.csv` and the immutable 252-column schema contract.
- Generated delivery outputs (`output/final_delivery.csv`) are **never mislabeled as ground truth**.
- Reference data loaders in `src/reference_data/` operate using deterministic, high-precision fallback modules (`src/uom.py`, `src/brand_map.py`, `src/classify.py`, `src/category_schema.py`, `src/dim_parser.py`) until reference files are placed in `data/reference/`.

---

## 2. Unresolved Scope Analysis (634 / 1,000 Rows)

Detailed analysis of the 634 unresolved input rows is documented in [`docs/unresolved_analysis.md`](file:///c:/Users/pky45/Downloads/unilog_pipeline_bundle/unilog/docs/unresolved_analysis.md):
1. **Commercial & Residential Lighting (208 rows / ~33%)**: Phillips Lighting (111), Kichler (56), Satco (41).
2. **Major Home Appliances (100 rows / ~16%)**: Appliance Dealers Cooperative (84), Frigidaire, GE.
3. **Safety Gear, Apparel & Wiring (75 rows / ~12%)**: Southwire, Leviton, Tech Gear 5.7, Edge Eyewear.
4. **Specialty Tool Accessories & Apparel (100 rows / ~16%)**: Milwaukee pencils, heated gear, router bits.
5. **Raw / Unbranded / Miscellaneous (151 rows / ~23%)**: Cryptic short descriptions without taxonomy keywords.

**Policy**: Low-confidence products remain `UNRESOLVED` to prevent taxonomy and attribute contract corruption.

---

## 3. Automated Quality Gates Engine (`src/quality_gates.py`)

Eight automated quality gates prevent non-compliant delivery files:

1. **Exact 252-Column Schema Match**: PASS (252 / 252 exact sequence & header match)
2. **Unique MPN Preservation**: PASS (999 unique MPNs out of 1,000 rows matching raw input)
3. **Zero Placeholder Leakage**: PASS (0 leaked `-- Unbranded --` placeholders in final delivery)
4. **INVOICE_DESC Length Limit**: PASS (100% $\le 40$ chars)
5. **MOBILE_DESC Length Optimization**: PASS (100% $\le 80$ chars max limit)
6. **Evidence Provenance Governance**: PASS (0 regex candidates marked VERIFIED without provenance)
7. **Conflict Hold Enforcement**: PASS (Open conflict `VN56920` held in `CONFLICT` status)
8. **Row Count Integrity**: PASS (Exactly 1,000 rows generated)

---

## 4. Test Suite Execution Summary

All 8 unit and integration test suites passed with **0 regressions**:
1. `tests/test_dim_parser.py`: PASS
2. `tests/test_uom.py`: PASS
3. `tests/test_entity_resolution.py`: PASS
4. `tests/test_classify.py`: PASS
5. `tests/test_schema_contract.py`: PASS
6. `tests/test_attribute_reconciliation.py`: PASS
7. `tests/test_reference_loaders.py`: PASS
8. `tests/test_quality_gates.py`: PASS
