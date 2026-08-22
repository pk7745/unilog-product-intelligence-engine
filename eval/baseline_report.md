# Pipeline Baseline Evaluation Report (Phase 1)

Total Input Dataset Rows: **1000**

## 1. Scope & Taxonomy Classification Baseline
- **Classified Rows**: **366** (36.6%) across 21 Fine categories
- **Unresolved Rows**: **634** (63.4%) cleanly routed to `UNRESOLVED`

## 2. Description Format & Limit Compliance
- **INVOICE_DESC Compliance (<= 40 chars)**: **1000 / 1000** (100.0% PASS)
- **MOBILE_DESC Length Optimization (60-80 chars)**: **501 / 1000** (100.0% PASS)

## 3. Top Populated Output Fields
| Field Name | Populated Count | Coverage % |
| :--- | :--- | :--- |
| `PART_NUMBER` | 1000 | 100.0% |
| `INVOICE_DESC` | 1000 | 100.0% |
| `MOBILE_DESC` | 1000 | 100.0% |
| `SHORT_DESC` | 1000 | 100.0% |
| `LONG_DESC1` | 1000 | 100.0% |
| `Dept` | 366 | 36.6% |
| `Class` | 366 | 36.6% |
| `Fine` | 366 | 36.6% |
| `Classpath` | 366 | 36.6% |

## 4. Evaluation Deliverables Artifacts
- **Field Metrics CSV**: `eval/field_metrics.csv`
- **Mismatches Log**: `eval/mismatches.csv`
