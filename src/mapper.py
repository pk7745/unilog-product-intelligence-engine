"""
Deterministic Canonical Model -> 252-column mapper (Phase 32).

This is the ONLY place that writes into the official delivery schema.
Nothing upstream (LLM, regex, evidence fusion) writes CSV columns directly.
QA/provenance data never goes into this row -- it's returned separately.
"""

import csv

SCHEMA_PATH_DEFAULT = None  # set by caller


def load_schema(path):
    with open(path, encoding="utf-8") as f:
        return next(csv.reader(f))


# Category-aware: which Fine categories have facts that legitimately map to
# the standard LENGTH/WIDTH/HEIGHT/WEIGHT columns (Section 33). A disc's
# Diameter is NEVER auto-mapped to WIDTH -- only categories where the
# schema's own attribute IS literally that standard dimension.
STANDARD_DIM_MAPPING = {
    "Sanding Belts": {"Width": "WIDTH", "Length": "LENGTH"},
}


def _clean_placeholder(val: str) -> str:
    v = str(val).strip()
    if v.lower() in ("-- unbranded --", "-- no unilog brand --", "-- no dib brand --", "null", "none"):
        return ""
    return v


def map_to_delivery_row(record, schema, best_official_url="", ref_urls=None):
    """record: ProductRecord (already fused/described). Returns dict with
    EXACTLY the columns in `schema`, no more, no less."""
    row = {c: "" for c in schema}
    ref_urls = ref_urls or []

    row["MFR URL"] = best_official_url
    for i, url in enumerate(ref_urls[:5], start=1):
        row[f"Ref URL {i}"] = url

    row["PART_NUMBER"] = record.mfg_part_num
    row["Mfg_Part_Num"] = record.mfg_part_num
    row["Part_Desc"] = record.part_desc
    row["E1_Brand"] = _clean_placeholder(record.raw_input.get("E1_Brand", ""))
    row["Unilog_Brand"] = _clean_placeholder(record.raw_input.get("Unilog_Brand", ""))
    row["DIB_Brand"] = _clean_placeholder(record.raw_input.get("DIB_Brand", ""))
    row["Part_Manuf"] = record.raw_input.get("Part_Manuf", "")
    row["MANUFACTURER_PART_NUMBER"] = record.mfg_part_num

    row["MANUFACTURER_NAME"] = record.identity.manufacturer_name
    row["BRAND_NAME"] = record.identity.brand_name
    row["TRADE_NAME"] = record.identity.trade_name

    row["Dept"] = record.taxonomy.dept
    row["Class"] = record.taxonomy.cls
    row["Fine"] = record.taxonomy.fine
    row["Classpath"] = record.taxonomy.classpath

    row["MOBILE_DESC"] = record.descriptions.get("MOBILE_DESC", "")
    row["INVOICE_DESC"] = record.descriptions.get("INVOICE_DESC", "")
    row["SHORT_DESC"] = record.descriptions.get("SHORT_DESC", "")
    row["LONG_DESC1"] = record.descriptions.get("LONG_DESC1", "")
    row["Product Name"] = record.descriptions.get("Product Name", "")

    for i, feat in enumerate(record.features[:20], start=1):
        row[f"ITEM_FEATURES_{i}"] = feat

    # attributes -> ATTRIBUTE_LABEL/VALUE/UOM 1..50 (never invent labels
    # for CONFLICT-status facts; those are surfaced in QA, not the CSV,
    # unless the guidelines require showing "See notes" -- left blank here
    # since blank + review beats a half-resolved conflict in the delivery file)
    slot = 1
    dim_map = STANDARD_DIM_MAPPING.get(record.taxonomy.fine, {})
    for fact in record.attributes:
        if fact.status == "CONFLICT":
            continue
        if slot > 50:
            break
        row[f"ATTRIBUTE_LABEL {slot}"] = fact.label
        row[f"ATTRIBUTE_VALUE {slot}"] = fact.value
        row[f"ATTRIBUTE_UOM {slot}"] = fact.uom
        slot += 1

        if fact.label in dim_map:
            std_col = dim_map[fact.label]
            row[std_col] = fact.value
            row[f"{std_col}_UOM"] = fact.uom

    return row
