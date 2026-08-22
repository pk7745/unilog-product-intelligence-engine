"""
UOM registry and normalization.

NOTE ON SCOPE: still a stand-in for the real
Unilog_Master_UOM_Standards_Abbreviations_and_Terms.xlsx (~500 approved
abbreviations across 89 measurement types), which wasn't provided. This
module is structured so swapping in the real workbook only means replacing
APPROVED_PHYSICAL_UOM / APPROVED_SELLING_UOM below with a load from that
file -- nothing else in the pipeline changes.

Fix from the prototype: units are classified by KIND (physical vs
selling/packaging) and status (APPROVED/UNKNOWN/INVALID). An unrecognized
unit is never silently treated as valid -- it's tagged UNKNOWN so it
surfaces in QA rather than disappearing. Units are also never silently
converted (20mm never becomes 20in): classify_uom() only normalizes
CASING/SPELLING of a unit that was already explicitly present.
"""

APPROVED_PHYSICAL_UOM = {
    "IN": "in", "INCH": "in", "INCHES": "in", '"': "in",
    "MM": "mm", "MILLIMETER": "mm", "MILLIMETERS": "mm",
    "CM": "cm", "FT": "ft", "FEET": "ft", "FOOT": "ft", "'": "ft",
    "LB": "lb", "OZ": "oz", "KG": "kg",
    "V": "V", "A": "A", "DBA": "dBA", "HR": "hr", "KW-HR": "kW-hr",
}

APPROVED_SELLING_UOM = {
    "PK": "pk", "PACK": "pk", "PC": "pc", "PCS": "pc", "EA": "ea",
    "BOX": "bx", "BX": "bx", "SET": "set",
}

STATUS_APPROVED = "APPROVED"
STATUS_UNKNOWN = "UNKNOWN"
STATUS_INVALID = "INVALID"


def classify_uom(raw: str):
    """Return (normalized_form, kind, status). Never converts value/unit -
    only normalizes the spelling of whatever unit was explicitly given."""
    if not raw:
        return "", "", STATUS_UNKNOWN
    key = raw.strip().upper().rstrip(".")
    if key in APPROVED_PHYSICAL_UOM:
        return APPROVED_PHYSICAL_UOM[key], "physical", STATUS_APPROVED
    if key in APPROVED_SELLING_UOM:
        return APPROVED_SELLING_UOM[key], "selling", STATUS_APPROVED
    return raw.strip().lower(), "unknown", STATUS_UNKNOWN
