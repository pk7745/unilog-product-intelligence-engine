# Pipeline Evaluation Report & Quality Benchmark

Total Dataset Input Rows: **1000**

## 1. Classification & Scope Coverage
- **Classified Rows**: **366** (36.6%) across 21 populated Fine categories
- **Unresolved Rows**: **634** (63.4%) correctly routed to UNRESOLVED (honest non-forced classification)

## 2. Reconciled 21-Category Breakdown
| Department | Category (Fine) | Assigned Rows |
| :--- | :--- | :--- |
| Decking & Railing | Deck Boards | 138 |
| Power Tools | Cordless Power Tools | 59 |
| Abrasives | Cut-Off Discs | 35 |
| Decking & Railing | Fascia Boards | 26 |
| Decking & Railing | Railing Kits | 20 |
| Power Tools | Batteries & Chargers | 14 |
| Power Tool Accessories | Saw Blades | 14 |
| Power Tools | Power Fastening Tools | 12 |
| Power Tool Accessories | Bits | 9 |
| Power Tools | Benchtop & Stationary Power Tools | 7 |
| Abrasives | Grinding Wheels | 7 |
| Abrasives | Sanding Discs | 6 |
| Decking & Railing | Post Sleeves & Accessories | 5 |
| Abrasives | Cut & Grind Discs | 3 |
| Power Tool Accessories | Power Tool Accessories | 3 |
| Abrasives | Files & Rasps | 2 |
| Fasteners & Hardware | Staples | 2 |
| Decking & Railing | Gate Hardware | 1 |
| Fasteners & Hardware | Nails & Pins | 1 |
| Abrasives | Sanding Belts | 1 |
| Abrasives | Sanding Sponges | 1 |
| **Total Classified** | **21 Categories** | **366** |

## 3. Evidence Coverage & Quality Tiering
- **Tier 1 (Directly-Fetched Verified)**: **24** rows (6.6% of classified)
- **Tier 2 (Family-Inherited)**: **0** rows (0.0% of classified)
- **Tier 3 (Candidate-Only / UNVERIFIED)**: **342** rows (93.4% of classified)

## 4. Unresolved Conflicts (Review Queue)
- **Open Conflicts**: **1** products held in `CONFLICT` status
  - **`VN56920`**: INSUFFICIENT/CONFLICTING EVIDENCE CASE, deliberately selected. Two problems surface here, both real: (1) BRAND CONFLICT -- the official marshalltown.com page sells VN56920, but Amazon lists the same MPN under brand 'VAUGHAN' (a separate documented Vaughan & Bushnell Mfg. Co. trademark family, 'Bear Saw'). Marshalltown may distribute/license it, but nothing found confirms Marshalltown as the legal manufacturer of record. (2) CLASSIFICATION MISMATCH -- the raw description '10 1/2" Saw Blade' was rule-classified as a power-tool 'Saw Blade' (Cutting Tools taxonomy), but the retrieved evidence shows this is actually a hand pull-saw REPLACEMENT BLADE (Bear Saw / interchangeable hand-tool blade), a completely different product family with no power-tool dimension schema (Diameter/Tooth Count/Arbor) applicable at all. Both are routed to review rather than resolved silently.

## 5. Schema Contract & Deliverables Verification
- **Schema Contract**: **PASS** (252 / 252 columns exact header & order match)
- **Final Delivery**: `output/final_delivery.csv` (1000 rows, clean of QA columns)
- **QA Report**: `output/qa_report.csv` (1000 rows, per-row confidence & review flags)
- **Provenance Log**: `output/field_provenance.jsonl` (line-by-line field evidence traces)
