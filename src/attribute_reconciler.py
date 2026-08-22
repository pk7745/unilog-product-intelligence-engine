"""
Canonical Attribute Label Reconciler (Phase 2).

Reconciles raw, extracted, or retrieved web source attribute labels
(e.g., 'Blade Diameter', 'Dia.', 'OAL', 'Volts', 'For Use On') to canonical
attribute labels (e.g., 'Diameter', 'Length', 'Voltage Rating', 'Application Material')
defined by category schemas and controlled vocabularies.
"""

import re
from typing import Dict, Any

# Global explicit synonym dictionary mapping lowercased raw/source variants -> Canonical Attribute Label
SYNONYM_DICTIONARY = {
    # Diameter variants
    "diameter": "Diameter",
    "blade diameter": "Diameter",
    "blade dia.": "Diameter",
    "blade dia": "Diameter",
    "cutting diameter": "Diameter",
    "disc diameter": "Diameter",
    "wheel diameter": "Diameter",
    "dia": "Diameter",
    "dia.": "Diameter",
    "outer diameter": "Diameter",
    "od": "Diameter",

    # Thickness variants
    "thickness": "Thickness",
    "wheel thickness": "Thickness",
    "blade thickness": "Thickness",
    "thick": "Thickness",
    "thk": "Thickness",
    "thk.": "Thickness",
    "disc thickness": "Thickness",

    # Arbor / Hole Size variants
    "arbor size": "Arbor Size",
    "arbor": "Arbor Size",
    "arbor diameter": "Arbor Size",
    "hole size": "Arbor Size",
    "bore": "Arbor Size",
    "bore size": "Arbor Size",
    "center hole": "Arbor Size",

    # Length variants
    "length": "Length",
    "overall length": "Length",
    "oal": "Length",
    "blade length": "Length",
    "cut length": "Length",
    "len": "Length",

    # Width variants
    "width": "Width",
    "body width": "Width",
    "face width": "Width",
    "wd": "Width",
    "wd.": "Width",
    "belt width": "Width",

    # Height / Post Size variants
    "height": "Height",
    "overall height": "Height",
    "finished height": "Height",
    "post size": "Post Size",
    "post dimensions": "Post Size",

    # Grit variants
    "grit": "Grit",
    "grit size": "Grit",
    "grit rating": "Grit",
    "mesh": "Grit",
    "abrasive grit": "Grit",

    # Material / Abrasive Material variants
    "material": "Material",
    "abrasive material": "Abrasive Material",
    "abrasive grain": "Abrasive Material",
    "grain type": "Abrasive Material",
    "abrasive type": "Abrasive Material",

    # Application Material / Target Material variants
    "application material": "Application Material",
    "application": "Application Material",
    "for use on": "Application Material",
    "target material": "Application Material",
    "material application": "Application Material",
    "compatible material": "Application Material",

    # Electrical & Cordless Specs
    "voltage rating": "Voltage Rating",
    "voltage": "Voltage Rating",
    "volts": "Voltage Rating",
    "v": "Voltage Rating",
    "battery capacity": "Battery Capacity",
    "amp hours": "Battery Capacity",
    "ah": "Battery Capacity",
    "capacity": "Battery Capacity",
    "battery chemistry": "Battery Chemistry",
    "chemistry": "Battery Chemistry",
    "motor type": "Motor Type",
    "motor": "Motor Type",

    # Cutting & Fastener Specs
    "tooth count": "Tooth Count",
    "number of teeth": "Tooth Count",
    "teeth": "Tooth Count",
    "tpi": "Tooth Count",
    "teeth per inch": "Tooth Count",
    "gauge": "Gauge",
    "fastener gauge": "Gauge",
    "wire gauge": "Gauge",
    "collating angle": "Collation Angle",
    "collation angle": "Collation Angle",
    "degree": "Collation Angle",
    "angle": "Collation Angle",
    "crown width": "Crown Width",
    "crown": "Crown Width",

    # General Attributes
    "series": "Series",
    "collection": "Series",
    "product line": "Series",
    "color": "Color",
    "finish": "Color",
    "edge profile": "Edge Profile",
    "profile": "Edge Profile",
    "pack quantity": "Pack Quantity",
    "package quantity": "Pack Quantity",
    "qty": "Pack Quantity",
    "pack size": "Pack Quantity",
    "manufacturer (brand)": "Manufacturer (brand)",
    "brand": "Manufacturer (brand)",
    "manufacturer": "Manufacturer (brand)",
    "mfg": "Manufacturer (brand)",
    "classpath": "Classpath",
    "category": "Classpath",
}


def reconcile_attribute(source_label: str, category: str = "") -> Dict[str, Any]:
    """
    Reconciles a source attribute label to its canonical label.
    Returns dict:
      source_label: str
      canonical_label: str
      method: EXACT_MATCH | SYNONYM_DICTIONARY | NORMALIZED_MATCH | UNRESOLVED
      confidence: float (0.0 to 1.0)
      status: VERIFIED | AMBIGUOUS
    """
    if not source_label or not source_label.strip():
        return {
            "source_label": "",
            "canonical_label": "",
            "method": "UNRESOLVED",
            "confidence": 0.0,
            "status": "AMBIGUOUS"
        }

    raw = source_label.strip()
    norm = raw.lower().rstrip(".").strip()

    # 1. Exact match check
    if norm in SYNONYM_DICTIONARY:
        canonical = SYNONYM_DICTIONARY[norm]
        method = "EXACT_MATCH" if norm == canonical.lower() else "SYNONYM_DICTIONARY"
        return {
            "source_label": raw,
            "canonical_label": canonical,
            "method": method,
            "confidence": 1.0,
            "status": "VERIFIED"
        }

    # 2. Normalized string cleanup (strip punctuation & extra spaces)
    clean_norm = re.sub(r"[^\w\s]", "", norm)
    clean_norm = re.sub(r"\s+", " ", clean_norm).strip()

    if clean_norm in SYNONYM_DICTIONARY:
        return {
            "source_label": raw,
            "canonical_label": SYNONYM_DICTIONARY[clean_norm],
            "method": "NORMALIZED_MATCH",
            "confidence": 0.95,
            "status": "VERIFIED"
        }

    # 3. Partial substring matching for common terms
    if "dia" in clean_norm and "arbor" not in clean_norm:
        return {
            "source_label": raw,
            "canonical_label": "Diameter",
            "method": "SUBSTRING_MATCH",
            "confidence": 0.85,
            "status": "VERIFIED"
        }

    if "length" in clean_norm:
        return {
            "source_label": raw,
            "canonical_label": "Length",
            "method": "SUBSTRING_MATCH",
            "confidence": 0.85,
            "status": "VERIFIED"
        }

    # 4. Fallback: preserve original label if no confident canonical mapping
    return {
        "source_label": raw,
        "canonical_label": raw,
        "method": "UNRESOLVED",
        "confidence": 0.5,
        "status": "AMBIGUOUS"
    }
