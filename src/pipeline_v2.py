"""
Pipeline v2 (Phases 1-8 wired together):

INPUT -> identity resolution -> taxonomy -> candidate extraction
      -> live evidence fusion -> confidence -> content generation
      -> 252-column mapping -> validation -> final_delivery.csv + qa_report.csv
      + field_provenance.jsonl

Reuses Phase-1 fixed modules (classify, extract, brand_map, uom, dim_parser,
category_schema) and adds evidence.py/confidence.py/describe.py/mapper.py/
validate.py on top, per the upgrade spec's "preserve, don't discard" rule.
"""

import csv
import json

from models import ProductRecord, Identity, Taxonomy, Fact, STATUS_UNVERIFIED
from brand_map import resolve_entity, is_placeholder
from classify import classify
from extract import extract_candidate_attributes
from evidence import get_live_evidence, fuse_attributes
from confidence import compute_product_confidence
from describe import (build_invoice_desc, build_mobile_desc, build_short_desc,
                       build_long_desc, build_item_features)
from mapper import load_schema, map_to_delivery_row
from validate import validate_schema, validate_row

SCHEMA_PATH = "data/Unihack__Expected_Output_-_Delivery_Format.csv"
INPUT_PATH = "data/Unihack__Sample_Dataset_-_Input.csv"
DELIVERY_PATH = "output/final_delivery.csv"
QA_PATH = "output/qa_report.csv"
PROVENANCE_PATH = "output/field_provenance.jsonl"


def build_record(row: dict) -> ProductRecord:
    mpn = row["Mfg_Part_Num"]
    desc = row["Part_Desc"]

    record = ProductRecord(mfg_part_num=mpn, part_desc=desc, raw_input=row)

    # --- Identity resolution (Phase 3) ---
    ent = resolve_entity(
        part_manuf=row.get("Part_Manuf", ""),
        part_desc=desc,
        e1_brand=row.get("E1_Brand", ""),
        unilog_brand=row.get("Unilog_Brand", ""),
        dib_brand=row.get("DIB_Brand", ""),
    )
    record.identity = Identity(
        manufacturer_name=ent["manufacturer_name"],
        manufacturer_confidence=ent["manufacturer_confidence"],
        manufacturer_method=ent["manufacturer_method"],
        brand_name=ent["brand_name"],
        brand_confidence=ent["brand_confidence"],
        trade_name=ent["trade_name"],
        supplier_vs_manufacturer_flag=ent["supplier_vs_manufacturer_flag"],
        notes=ent["notes"],
    )
    record.review_reasons.extend(ent["notes"])

    # --- Taxonomy (Phase 8 stage 1: rule-based) ---
    dept, cls, fine, classpath, conf_band, method, tax_evidence = classify(
        part_desc=desc,
        mfr=ent["manufacturer_name"],
        brand=ent["brand_name"],
        mpn=mpn,
    )
    record.taxonomy = Taxonomy(
        dept=dept, cls=cls, fine=fine, classpath=classpath,
        confidence_band=conf_band, method=method, evidence=tax_evidence,
    )
    if conf_band == "UNRESOLVED":
        record.review_reasons.append("taxonomy: no rule matched, classification UNRESOLVED")

    # --- Candidate attribute extraction (Phase 5 candidate layer) ---
    ext = extract_candidate_attributes(desc, fine)
    candidate_facts = ext["candidate_attributes"]
    record.candidate_attributes = candidate_facts
    item_type = ext["item_type"] or fine or "Product"
    for note in ext["review_notes"]:
        record.review_reasons.append(f"extraction: {note}")

    # --- Live evidence + fusion (Phase 4-6) ---
    live_facts, sources, live_note = get_live_evidence(mpn)
    if live_note:
        record.review_reasons.append(f"evidence: {live_note}")
    if not sources:
        record.review_reasons.append(
            "no live manufacturer-source evidence gathered for this row in this run -- "
            "attributes remain UNVERIFIED (regex/candidate layer only)"
        )
    fused, conflicts = fuse_attributes(candidate_facts, live_facts)
    record.attributes = fused
    record.conflicts = conflicts
    for c in conflicts:
        record.review_reasons.append(
            f"CONFLICT on '{c['label']}': {c['evidence_text']}"
        )

    # taxonomy conflict surfaced by evidence (e.g. VN56920 case)
    for f in fused:
        if f.label == "Classpath" and f.status == "CONFLICT":
            record.review_reasons.append(f"taxonomy CONFLICT: {f.evidence_text}")

    record.sources = sources

    # --- Confidence (Phase 25) ---
    overall, band = compute_product_confidence(record)
    record.overall_confidence = overall
    record.overall_confidence_band = band

    # --- Content generation (Phase 7) -- canonical facts only ---
    series = next((f.value for f in fused if f.label == "Series" and f.status != "CONFLICT"), None)
    material = next((f.value for f in fused if f.label in ("Application Material", "Material")
                      and f.status != "CONFLICT"), None)

    record.descriptions["INVOICE_DESC"] = build_invoice_desc(item_type, fused)
    record.descriptions["MOBILE_DESC"] = build_mobile_desc(
        record.identity.manufacturer_name, record.identity.brand_name, item_type, mpn, series, fused, record.taxonomy.classpath)
    record.descriptions["SHORT_DESC"] = build_short_desc(
        record.identity.brand_name, mpn, item_type, fused, series)
    record.descriptions["LONG_DESC1"] = build_long_desc(
        record.identity.brand_name, item_type, fused, series, material)
    record.descriptions["Product Name"] = item_type
    record.features = build_item_features(fused, series)

    return record


def best_official_url(sources):
    officials = [s["url"] for s in sources if s.get("source_type") == "official_manufacturer_page"]
    return officials[0] if officials else ""


def other_urls(sources, exclude):
    return [s["url"] for s in sources if s["url"] != exclude][:5]


def run(limit=None):
    schema = load_schema(SCHEMA_PATH)

    with open(INPUT_PATH, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if limit:
        rows = rows[:limit]

    delivery_rows = []
    qa_rows = []
    provenance_lines = []

    for row in rows:
        record = build_record(row)
        official = best_official_url(record.sources)
        refs = other_urls(record.sources, official)

        delivery_row = map_to_delivery_row(record, schema, official, refs)
        issues = validate_row(delivery_row)

        delivery_rows.append(delivery_row)

        qa_rows.append({
            "Mfg_Part_Num": record.mfg_part_num,
            "Fine": record.taxonomy.fine,
            "Taxonomy_Confidence": record.taxonomy.confidence_band,
            "Manufacturer_Confidence": record.identity.manufacturer_confidence,
            "Brand_Confidence": record.identity.brand_confidence,
            "Supplier_vs_Manufacturer_Flag": record.identity.supplier_vs_manufacturer_flag,
            "Num_Attributes_Candidate": len(record.candidate_attributes),
            "Num_Attributes_Fused": len(record.attributes),
            "Num_Conflicts": len(record.conflicts),
            "Overall_Confidence": record.overall_confidence,
            "Overall_Confidence_Band": record.overall_confidence_band,
            "Needs_Review": "Yes" if record.needs_review() else "No",
            "Review_Reasons": " | ".join(record.review_reasons),
            "Validation_Issues": " | ".join(issues),
            "Live_Evidence_Sources": len(record.sources),
        })

        for f in record.attributes:
            provenance_lines.append(json.dumps({
                "mfg_part_num": record.mfg_part_num,
                "label": f.label,
                "value": f.value,
                "uom": f.uom,
                "status": f.status,
                "method": f.method,
                "confidence": f.confidence,
                "evidence_text": f.evidence_text,
                "alternates": f.alternates,
            }))

    with open(DELIVERY_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=schema)
        w.writeheader()
        for r in delivery_rows:
            w.writerow(r)

    actual_header = schema  # by construction, DictWriter enforces this
    schema_ok, schema_errors = validate_schema(schema, actual_header)

    with open(QA_PATH, "w", newline="", encoding="utf-8") as f:
        qa_fields = list(qa_rows[0].keys()) if qa_rows else []
        w = csv.DictWriter(f, fieldnames=qa_fields)
        w.writeheader()
        for r in qa_rows:
            w.writerow(r)

    with open(PROVENANCE_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(provenance_lines))

    print(f"Processed {len(delivery_rows)} rows")
    print(f"Schema validation: {'PASS' if schema_ok else 'FAIL'}")
    if schema_errors:
        for e in schema_errors:
            print("  -", e)
    print(f"Delivery -> {DELIVERY_PATH}")
    print(f"QA report -> {QA_PATH}")
    print(f"Provenance -> {PROVENANCE_PATH}")

    return delivery_rows, qa_rows, schema_ok


if __name__ == "__main__":
    run()
