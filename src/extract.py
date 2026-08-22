"""
Candidate attribute extraction (Phase 1 fix + Phase 5 candidate layer).

This module produces CANDIDATE Facts only (method=REGEX, status=UNVERIFIED).
It never writes directly to the final CSV -- evidence.py fuses these with
any live-retrieved evidence before anything is treated as canonical.

Fixes from the prototype:
  - dimension labels come from category_schema.label_dimension_chain(),
    which is keyed by the product's Fine category, not by how many numeric
    tokens happened to appear.
  - explicit units are preserved exactly (dim_parser.py).
  - "Material" is never asserted as a bare product-construction claim; it's
    tagged "Application Material" unless the category schema says otherwise,
    since "Metal" in a cut-off-disc description means "cuts metal", not
    "made of metal".
  - deduplicates candidate facts (no repeated Series/Material entries).
"""

import re
from dim_parser import parse_dimension_chain
from category_schema import label_dimension_chain
from models import Fact, METHOD_REGEX, STATUS_UNVERIFIED
from uom import classify_uom

SERIES_WORDS = ["Performance+", "Perform+", "Steel Demon", "Speed Demon",
                "Cubitron II", "General Purpose", "DKO", "Ceramic+"]

# category-aware: for abrasive/cutting accessories, a bare material word in
# the description describes what the product is used ON, not what it's
# made of -- hence "Application Material", not "Material".
APPLICATION_MATERIAL_CATEGORIES = {
    "Cut-Off Discs", "Cut & Grind Discs", "Grinding Wheels", "Saw Blades",
}
MATERIAL_WORDS = ["Metal", "Steel", "Aluminum", "Wood", "Masonry", "Concrete"]


def _strip_leading_part_num(desc: str) -> str:
    m = re.match(r"^([A-Za-z0-9][A-Za-z0-9\-]{3,})\s+(.*)", desc)
    if m and re.search(r"\d", m.group(1)):
        return m.group(2)
    return desc


def extract_candidate_attributes(part_desc: str, fine: str):
    desc = _strip_leading_part_num(part_desc)
    facts = []
    review_notes = []
    seen_labels_values = set()

    def add_fact(label, value, uom_raw, raw_value, confident=True):
        key = (label, str(value))
        if key in seen_labels_values:
            return
        seen_labels_values.add(key)
        norm_uom, uom_kind, uom_status = classify_uom(uom_raw)
        facts.append(Fact(
            label=label,
            value=str(value),
            raw_value=raw_value,
            uom=norm_uom,
            uom_kind=uom_kind,
            source_type="description_parse",
            method=METHOD_REGEX,
            confidence=0.55 if confident else 0.25,
            confidence_band="MEDIUM" if confident else "LOW",
            status=STATUS_UNVERIFIED,
        ))

    # 1. Dimension chain -> raw (value, uom, raw_token, display) tuples
    raw_dims = parse_dimension_chain(desc)
    if raw_dims:
        # convert to (numeric_value, source_uom, raw_token) for the schema labeler
        chain_input = [(v, u, r) for (v, u, r, disp) in raw_dims]
        disp_by_raw = {r: disp for (v, u, r, disp) in raw_dims}
        labeled = label_dimension_chain(fine, chain_input)
        for label, val, uom, raw, confident in labeled:
            disp = disp_by_raw.get(raw, str(val))
            add_fact(label, disp, uom, raw, confident=confident)
            if not confident:
                review_notes.append(f"dimension chain length has no schema mapping for '{fine}'")
    else:
        review_notes.append("no dimension pattern matched")

    # 2. Grit e.g. P150, P80, or "220 Grit"
    grit_match = re.search(r"\bP(\d{2,4})\b", desc) or re.search(r"(\d{2,4})\s*Grit\b", desc, re.IGNORECASE)
    if grit_match:
        add_fact("Grit", grit_match.group(1), "", grit_match.group(0))

    # 3. Pack quantity e.g. 6pc, 10pc, 50 Disc/Box, 25pc Bit Set
    pack_match = re.search(r"(\d+)\s*(pc|pcs)\b", desc, re.IGNORECASE)
    if pack_match:
        add_fact("Pack Quantity", pack_match.group(1), "pc", pack_match.group(0))
    box_match = re.search(r"(\d+)\s*Disc/Box", desc, re.IGNORECASE)
    if box_match:
        add_fact("Pack Quantity", box_match.group(1), "pc", box_match.group(0))

    # 4. Tooth count e.g. "60 Tooth", "24T", "60T"
    tooth_match = re.search(r"(\d+)\s*(?:Tooth|TPI|T)\b", desc, re.IGNORECASE)
    if tooth_match and fine == "Saw Blades":
        add_fact("Tooth Count", tooth_match.group(1), "", tooth_match.group(0))

    # 5. Material -- category-aware semantic label
    for mat in MATERIAL_WORDS:
        if re.search(rf"\b{mat}\b", desc, re.IGNORECASE):
            label = "Application Material" if fine in APPLICATION_MATERIAL_CATEGORIES else "Material"
            add_fact(label, mat, "", mat)
            break

    # 6. Series / product line qualifier
    for series in SERIES_WORDS:
        if series.lower() in desc.lower():
            add_fact("Series", series, "", series)
            break

    # 8. Power Tools specific attribute extraction
    v_match = re.search(r"\b(\d+)\s*V\b", desc, re.IGNORECASE) or re.search(r"\bM(\d{2})\b", desc)
    if v_match:
        add_fact("Voltage Rating", v_match.group(1), "V", v_match.group(0))

    ah_match = re.search(r"\b(\d+(?:\.\d+)?)\s*AH\b", desc, re.IGNORECASE)
    if ah_match:
        add_fact("Battery Capacity", ah_match.group(1), "Ah", ah_match.group(0))

    motor_match = re.search(r"\b(brushless)\b", desc, re.IGNORECASE)
    if motor_match:
        add_fact("Motor Type", motor_match.group(1).title(), "", motor_match.group(0))

    form_match = re.search(r"\b(bare tool|bare|tool[- ]only|kit)\b", desc, re.IGNORECASE)
    if form_match:
        raw_f = form_match.group(1).lower()
        val_f = "Kit" if "kit" in raw_f else "Tool Only"
        add_fact("Tool Form", val_f, "", form_match.group(0))

    cfm_match = re.search(r"\b(\d+)\s*CFM\b", desc, re.IGNORECASE)
    if cfm_match:
        add_fact("Air Volume", cfm_match.group(1), "CFM", cfm_match.group(0))

    mph_match = re.search(r"\b(\d+)\s*MPH\b", desc, re.IGNORECASE)
    if mph_match:
        add_fact("Air Speed", mph_match.group(1), "MPH", mph_match.group(0))

    # 9. Fasteners specific attribute extraction
    ga_match = re.search(r"\b(\d+)\s*(?:GA|Gauge)\b", desc, re.IGNORECASE)
    if ga_match:
        add_fact("Gauge", ga_match.group(1), "GA", ga_match.group(0))

    fastener_type_match = re.search(r"\b(Finish Nail|Brad Nail|Framing Nail|Roofing Nail|Staple|Gravity Latch)\b", desc, re.IGNORECASE)
    if fastener_type_match:
        add_fact("Fastener Type", fastener_type_match.group(1).title(), "", fastener_type_match.group(0))

    # 7. Item type (kept for description templating, not itself an ATTRIBUTE slot)
    type_match = re.search(
        r"(Cut[- ]?and[- ]?Grind Disc|Cut[- ]?Off Disc|Sanding Belt|Sanding Disc|"
        r"Sanding Sponge|Grinding Wheel|Saw Blade|Router Bit|Drill Bit|File|Rasp)",
        desc, re.IGNORECASE)
    item_type = type_match.group(1).title() if type_match else ""
    if not item_type:
        review_notes.append("item type not confidently identified")

    return {
        "candidate_attributes": facts,
        "item_type": item_type,
        "review_notes": review_notes,
    }
