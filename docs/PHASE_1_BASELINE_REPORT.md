# Phase 1 Baseline & Evaluation Report

**Document Version**: 1.0.0  
**Phase**: Phase 1 — Core Dataset + Ground-Truth Benchmark  
**Date**: 2026-08-21  

---

## 1. Dataset Inventory & Verification

The primary working datasets present in `unilog/data/` were audited and profiled:

| Dataset Name | Filename | Record Count | Structure / Purpose |
| :--- | :--- | :--- | :--- |
| **Raw Supplier Input** | `data/Unihack__Sample_Dataset_-_Input.csv` | **1,000 rows** | 6 fields: `Mfg_Part_Num`, `Part_Desc`, `E1_Brand`, `Unilog_Brand`, `DIB_Brand`, `Part_Manuf` |
| **Delivery Schema Contract** | `data/Unihack__Expected_Output_-_Delivery_Format.csv` | **252 columns** | Immutable output contract grid specifying exact column names & ordering |
| **Testing Subset** | `data/subset_tools.csv` | **73 rows** | Rapid testing subset |

---

## 2. 252-Column Schema Profile Analysis

The output format specifies **252 immutable columns** partitioned into 8 functional areas:

- **Source Provenance URLs** (Cols 1–6): `MFR URL`, `Ref URL 1` .. `Ref URL 5`
- **Primary Product Identifiers** (Cols 7, 246–252): `PART_NUMBER`, `GTIN`, `UPC`, `SKU`
- **Taxonomy & Hierarchy** (Cols 8–11): `Dept`, `Class`, `Fine`, `Classpath`
- **Manufacturer & Brand Entity Identity** (Cols 12–17): `Manufacturer Name`, `Brand Name`, `Trade Name`, `Supplier Flag`
- **Multichannel Product Descriptions** (Cols 18–25): `INVOICE_DESC` ($\le 40$ chars), `MOBILE_DESC` (60–80 chars), `SHORT_DESC`, `LONG_DESC1`
- **Item Features** (Cols 26–35): `Feature 1` .. `Feature 10`
- **Category Attributes Grid** (Cols 36–235): 50 Attribute Triplets (`Attribute N Name`, `Value`, `UOM`)
- **Digital Assets & Documentation** (Cols 236–245): Image URLs & Spec Sheet PDF URLs

---

## 3. Current Pipeline Baseline Metrics

- **Total Input Rows Processed**: **1,000 / 1,000 (100.0%)**
- **Taxonomy Classification Coverage**: **366 / 1,000 rows (36.6%)** across 21 Fine categories
- **Honest Unresolved Scope**: **634 / 1,000 rows (63.4%)** cleanly routed to `UNRESOLVED`
- **Evidence Quality Tiering**:
  - **Tier 1 (Directly-Fetched / Human-Verified)**: **24 / 366 rows (6.6%)**
  - **Tier 2 (Family-Inherited)**: **0 / 366 rows (0.0%)**
  - **Tier 3 (Candidate-Only / UNVERIFIED)**: **342 / 366 rows (93.4%)**
- **Open Conflict Count**: **1 product (`VN56920`)** held open with `HUMAN_DEFERRED` method
- **Schema Contract Compliance**: **100% PASS** (252 / 252 columns exact header match)
- **Description Limits Compliance**:
  - `INVOICE_DESC` ($\le 40$ chars): **1,000 / 1,000 (100.0% PASS)**
  - `MOBILE_DESC` (60–80 chars): **1,000 / 1,000 (100.0% PASS)**

---

## 4. Error & Weakness Analysis

Analysis of the generated `eval/mismatches.csv` and `eval/field_metrics.csv` reveals the following primary error categories:

1. **Unresolved Scope (63.4%)**: 634 raw input rows represent products outside the 21 currently populated Fine categories (e.g. electrical cables, plumbing fittings, specialized hand tools).
2. **Candidate-Only Evidence Gap (93.4% Tier 3)**: 342 classified rows currently rely strictly on regex candidate extraction from `Part_Desc` without live fetched evidence.
3. **Missing GTIN / UPC / Image URLs**: Raw input supplier CSV contains no GTIN or image links.

---

## 5. Dimension Parser Bug Fix & Test Verification

### Issue Addressed
Space-separated mixed fractions like `"10 1/2""` were previously parsed as two separate numeric tokens (`10 in` and `1/2 in`).

### Resolution in `src/dim_parser.py`
Updated `NUM` regex and `_numeric_value()` function to parse space-separated mixed fractions into unified decimal and display forms (`10.5 in` $\rightarrow$ `10-1/2`).

### Regression Test Output (`tests/test_dim_parser.py`)
```text
[PASS] '5"x.045"x7/8"' -> [(5.0, 'in', '5'), (0.045, 'in', '0.045'), (0.875, 'in', '7/8')]
[PASS] '6-1/2"x1/8"x5/8"' -> [(6.5, 'in', '6-1/2'), (0.125, 'in', '1/8'), (0.625, 'in', '5/8')]
[PASS] '10 1/2"' -> [(10.5, 'in', '10-1/2')]
[PASS] '10-1/2"' -> [(10.5, 'in', '10-1/2')]
[PASS] '1/2"x18"' -> [(0.5, 'in', '1/2'), (18.0, 'in', '18')]
[PASS] '12"x1/8"x20mm' -> [(12.0, 'in', '12'), (0.125, 'in', '1/8'), (20.0, 'mm', '20')]
[PASS] '7/8"' -> [(0.875, 'in', '7/8')]
[PASS] '.045"' -> [(0.045, 'in', '0.045')]
[PASS] '3/32"' -> [(0.09375, 'in', '3/32')]
[PASS] "1x6-16'" -> [(1.0, 'in', '1'), (6.0, 'in', '6'), (16.0, 'ft', '16')]
[PASS] '4x4-108"' -> [(4.0, 'in', '4'), (4.0, 'in', '4'), (108.0, 'in', '108')]
[PASS] "6'" -> [(6.0, 'ft', '6')]

-- non-negotiable checks --
[PASS] 20mm never converted to inches
[PASS] 0.045 stays decimal (not forced to 3/64)

All dimension parser tests passed.
```

---

## 6. Recommended Next Three Engineering Priorities

1. **Priority 1 — Canonical Attribute Label Reconciliation**: Build an attribute reconciler (`src/attribute_reconciler.py`) to map synonym evidence labels (`Blade Diameter`, `Dia.`) to canonical schema names (`Diameter`) before evidence fusion.
2. **Priority 2 — Reference Data Loader Architecture**: Structure `src/reference_data/` modules to ingest master UOM, manufacturer, and LOV tables when present with lazy-loading and indexing.
3. **Priority 3 — Safe Evidence Discovery & RAG Snippet Caching**: Expand evidence discovery for Tier 3 products using official domain searches and cached snippet storage.
