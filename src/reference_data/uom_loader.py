"""
UOM Reference Data Loader (Phase 3).
Lazy-loads Unilog_Master_UOM_Standards_Abbreviations_and_Terms.xlsx if available,
otherwise falls back to src/uom.py.
"""

import os
from typing import Dict, Tuple, Optional

# Lazy-loaded cache
_UOM_CACHE: Optional[Dict[str, Tuple[str, str, str]]] = None


def get_uom_map() -> Dict[str, Tuple[str, str, str]]:
    global _UOM_CACHE
    if _UOM_CACHE is not None:
        return _UOM_CACHE

    _UOM_CACHE = {}
    
    # Check for external reference file in data/reference/ or data/
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ref_paths = [
        os.path.join(base_dir, "data", "reference", "Unilog_Master_UOM_Standards_Abbreviations_and_Terms.xlsx"),
        os.path.join(base_dir, "data", "Unilog_Master_UOM_Standards_Abbreviations_and_Terms.xlsx"),
    ]

    found_file = next((p for p in ref_paths if os.path.exists(p)), None)

    if found_file:
        try:
            import pandas as pd
            df = pd.read_excel(found_file, sheet_name=0)
            # Normalize data rows
            for _, row in df.iterrows():
                abbrev = str(row.get("Approved Abbreviation", "")).strip()
                unit_kind = str(row.get("Unit Kind", "physical")).strip().lower()
                status = str(row.get("Status", "APPROVED")).strip()
                if abbrev:
                    key = abbrev.upper()
                    _UOM_CACHE[key] = (abbrev, unit_kind, status)
            print(f"[INFO] Ingested {len(_UOM_CACHE)} UOM entries from {found_file}")
            return _UOM_CACHE
        except Exception as e:
            print(f"[WARN] Failed to parse UOM reference file {found_file}: {e}")

    # Fallback to internal uom.py maps
    from uom import APPROVED_PHYSICAL_UOM, APPROVED_SELLING_UOM, STATUS_APPROVED
    for raw_key, norm in APPROVED_PHYSICAL_UOM.items():
        _UOM_CACHE[raw_key.upper()] = (norm, "physical", STATUS_APPROVED)
    for raw_key, norm in APPROVED_SELLING_UOM.items():
        _UOM_CACHE[raw_key.upper()] = (norm, "selling", STATUS_APPROVED)

    return _UOM_CACHE


def lookup_uom(raw_unit: str) -> Tuple[str, str, str]:
    """Returns (normalized_form, kind, status)."""
    if not raw_unit or not raw_unit.strip():
        return "", "unknown", "UNKNOWN"
    
    uom_map = get_uom_map()
    key = raw_unit.strip().upper().rstrip(".")
    if key in uom_map:
        return uom_map[key]
    
    return raw_unit.strip().lower(), "unknown", "UNKNOWN"
