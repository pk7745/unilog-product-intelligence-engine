"""
Manufacturer & Brand Reference Data Loader (Phase 3).
Lazy-loads UniCat_Manufacturer_and_Brand_List.xlsx if present,
otherwise falls back to src/brand_map.py ENTITY_MASTER.
"""

import os
from typing import Dict, Any, Optional

_ENTITY_MASTER_CACHE: Optional[Dict[str, Dict[str, Any]]] = None


def get_manufacturer_master() -> Dict[str, Dict[str, Any]]:
    global _ENTITY_MASTER_CACHE
    if _ENTITY_MASTER_CACHE is not None:
        return _ENTITY_MASTER_CACHE

    _ENTITY_MASTER_CACHE = {}
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ref_paths = [
        os.path.join(base_dir, "data", "reference", "UniCat_Manufacturer_and_Brand_List.xlsx"),
        os.path.join(base_dir, "data", "UniCat_Manufacturer_and_Brand_List.xlsx"),
    ]

    found_file = next((p for p in ref_paths if os.path.exists(p)), None)

    if found_file:
        try:
            import pandas as pd
            df = pd.read_excel(found_file)
            for _, row in df.iterrows():
                mfg_name = str(row.get("MANUFACTURER_NAME", "")).strip()
                brand_name = str(row.get("BRAND_NAME", "")).strip()
                mfg_code = str(row.get("MANUFACTURER_CODE", "")).strip()
                brand_code = str(row.get("BRAND_CODE", "")).strip()
                if mfg_name:
                    key = mfg_name.lower()
                    _ENTITY_MASTER_CACHE[key] = {
                        "canonical_mfg": mfg_name,
                        "mfg_code": mfg_code,
                        "brand": brand_name or mfg_name,
                        "brand_code": brand_code,
                        "aliases": [mfg_name.lower()]
                    }
            print(f"[INFO] Ingested {len(_ENTITY_MASTER_CACHE)} manufacturer records from {found_file}")
            return _ENTITY_MASTER_CACHE
        except Exception as e:
            print(f"[WARN] Failed to load manufacturer master file {found_file}: {e}")

    # Fallback to internal brand_map ENTITY_MASTER
    from brand_map import ENTITY_MASTER
    for canonical, info in ENTITY_MASTER.items():
        _ENTITY_MASTER_CACHE[canonical] = {
            "canonical_mfg": canonical.title(),
            "mfg_code": "",
            "brand": info["brand"],
            "brand_code": "",
            "domain": info.get("domain", ""),
            "aliases": info.get("aliases", []),
        }

    return _ENTITY_MASTER_CACHE
