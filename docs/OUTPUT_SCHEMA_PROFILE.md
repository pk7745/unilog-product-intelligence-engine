# Output Schema Profile: 252-Column Delivery Contract

**Document Version**: 1.0.0  
**Phase**: Phase 1 — Core Dataset & Ground-Truth Benchmark  
**Schema Contract**: `data/Unihack__Expected_Output_-_Delivery_Format.csv` (252 Immutable Columns)  

---

## 1. Executive Summary & Contract Constraints

The output format expected by the client consists of **exactly 252 columns** in fixed position and header nomenclature. 

### Non-Negotiable Contract Rules
1. **Zero Header Alterations**: Headers must not be added, removed, renamed, or reordered.
2. **Separation of QA Metadata**: QA review reasons, confidence scores, conflict counts, and validation logs belong in `output/qa_report.csv` and `output/field_provenance.jsonl`, **never** inside `output/final_delivery.csv`.
3. **Clean Blank Handling**: Empty/unpopulated attributes are rendered as empty strings `""`, avoiding string placeholders such as `"-- Unbranded --"` or `"N/A"`.

---

## 2. High-Level Column Functional Breakdown

| Functional Group | Column Range / Count | Primary Examples | Role in Commerce / Delivery |
| :--- | :--- | :--- | :--- |
| **Source Provenance URLs** | Cols 1–6 (6 cols) | `MFR URL`, `Ref URL 1` .. `Ref URL 5` | Traceability links to official manufacturer pages & secondary sources |
| **Product Identifiers** | Cols 7, 246–252 (8 cols) | `PART_NUMBER`, `GTIN`, `UPC`, `SKU` | Universal part identification keys |
| **Taxonomy & Hierarchy** | Cols 8–11 (4 cols) | `Dept`, `Class`, `Fine`, `Classpath` | 4-level category classification tree |
| **Manufacturer & Brand** | Cols 12–17 (6 cols) | `Manufacturer Name`, `Brand Name`, `Trade Name` | Entity-resolved manufacturer & brand strings |
| **Descriptions & Names** | Cols 18–25 (8 cols) | `INVOICE_DESC`, `MOBILE_DESC`, `SHORT_DESC`, `LONG_DESC1` | Multi-length channel-specific descriptions |
| **Item Features** | Cols 26–35 (10 cols) | `Feature 1` .. `Feature 10` | Bulleted key product selling features |
| **Category Attributes Grid**| Cols 36–235 (200 cols) | `Attribute 1 Name`, `Value`, `UOM` .. `Attribute 50` | Dynamic attribute triplet slots (Name, Value, UOM) |
| **Digital Assets & Media** | Cols 236–245 (10 cols) | `Primary Image URL`, `Spec Sheet PDF URL` | Product images & technical PDF document links |

---

## 3. Detailed Structural Summary of 252 Columns

### Provenance & Identifiers (Cols 1–7)
- **Col 1**: `MFR URL` (Official manufacturer product page link)
- **Cols 2–6**: `Ref URL 1` through `Ref URL 5` (Secondary reference links)
- **Col 7**: `PART_NUMBER` (Manufacturer Part Number / MPN)

### Taxonomy & Classification (Cols 8–11)
- **Col 8**: `Dept` (Department: e.g. `Tools & Equipment`, `Building Materials`, `Hardware`)
- **Col 9**: `Class` (Class: e.g. `Power Tools`, `Decking & Railing`, `Fasteners`)
- **Col 10**: `Fine` (Fine Category: e.g. `Cordless Power Tools`, `Deck Boards`, `Cut-Off Discs`)
- **Col 11**: `Classpath` (Canonical breadcrumb string: `Dept>Class>Fine`)

### Manufacturer & Brand Entity Identity (Cols 12–17)
- **Col 12**: `Manufacturer Name` (Canonical legal manufacturer, e.g. `Stanley Black & Decker, Inc.`)
- **Col 13**: `Manufacturer Code` (Canonical manufacturer ID)
- **Col 14**: `Brand Name` (Commercial brand, e.g. `DEWALT®`)
- **Col 15**: `Brand Code` (Canonical brand ID)
- **Col 16**: `Trade Name` (Trade/Series commercial name)
- **Col 17**: `Supplier Flag` (True if raw input manufacturer was a distributor like Parksite/Boise Cascade)

### Multichannel Product Descriptions (Cols 18–25)
- **Col 18**: `INVOICE_DESC` (Till receipt description, $\le 40$ chars, uppercase)
- **Col 19**: `MOBILE_DESC` (Mobile e-commerce app description, 60–80 chars)
- **Col 20**: `SHORT_DESC` (Product title for search result pages)
- **Col 21**: `LONG_DESC1` (Full product detail page description)
- **Cols 22–25**: Extended long descriptions & product marketing summary names.

### Item Features (Cols 26–35)
- **Cols 26–35**: `Feature 1` through `Feature 10` (Extracted selling bullet points)

### Attribute Triplets Grid (Cols 36–235)
- Structured as **50 Attribute Quad/Triplet Slots**:
  - `Attribute N Name` (e.g. `Voltage Rating`, `Length`, `Abrasive Material`)
  - `Attribute N Value` (e.g. `20`, `16`, `Zirconia`)
  - `Attribute N UOM` (e.g. `V`, `ft`, `in`, `mm`)
  - `Attribute N Normalized` (Clean LOV value)

### Digital Assets & Additional Identifiers (Cols 236–252)
- **Cols 236–245**: Product image URLs and technical datasheet/manual PDF links.
- **Cols 246–252**: GTIN, UPC, EAN, UNSPSC Code, and secondary part numbers.

---

## 4. Machine-Readable Profile Asset

The complete column-by-column breakdown is stored in:
[`output/schema_profile.csv`](file:///c:/Users/pky45/Downloads/unilog_pipeline_bundle/unilog/output/schema_profile.csv)
