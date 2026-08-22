"""
LOV (List of Values) Controlled Vocabulary Loader (Phase 3).
Lazy-loads Unicat_Lov_v1_0_Updated_With_Remarks.xlsx, FAUCETS_LOV.xlsx, and Fittings_LOV.xlsx if present,
otherwise falls back to src/category_schema.py definitions.
"""

import os
from typing import Dict, List, Any, Optional

_LOV_CACHE: Optional[Dict[str, Dict[str, Any]]] = None


def get_lov_registry() -> Dict[str, Dict[str, Any]]:
    global _LOV_CACHE
    if _LOV_CACHE is not None:
        return _LOV_CACHE

    _LOV_CACHE = {}
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ref_paths = [
        os.path.join(base_dir, "data", "reference", "Unicat_Lov_v1_0_Updated_With_Remarks.xlsx"),
        os.path.join(base_dir, "data", "Unicat_Lov_v1_0_Updated_With_Remarks.xlsx"),
    ]

    found_file = next((p for p in ref_paths if os.path.exists(p)), None)

    if found_file:
        try:
            import pandas as pd
            df = pd.read_excel(found_file)
            for _, row in df.iterrows():
                cp = str(row.get("Classpath", "")).strip()
                attr_label = str(row.get("Attribute Label", "")).strip()
                norm_label = str(row.get("Normalized Label", attr_label)).strip()
                vals = str(row.get("Attribute Values", "")).strip()
                norm_vals = [v.strip() for v in str(row.get("Normalized Values", vals)).split(",") if v.strip()]

                if cp and norm_label:
                    if cp not in _LOV_CACHE:
                        _LOV_CACHE[cp] = {"attributes": {}}
                    _LOV_CACHE[cp]["attributes"][norm_label] = norm_vals

            print(f"[INFO] Ingested {len(_LOV_CACHE)} LOV category classpaths from {found_file}")
            return _LOV_CACHE
        except Exception as e:
            print(f"[WARN] Failed to load LOV reference file {found_file}: {e}")

    # Fallback to category_schema SCHEMAS
    from category_schema import SCHEMAS
    for fine, schema in SCHEMAS.items():
        _LOV_CACHE[fine] = {
            "attributes": {attr: [] for attr in schema.get("expected_attributes", [])}
        }

    return _LOV_CACHE
