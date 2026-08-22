"""
Decimal / Fraction Reference Data Loader (Phase 3).
Lazy-loads Decimal_Fraction.xlsx if present,
otherwise falls back to src/dim_parser.py FRACTION_TABLE.
"""

import os
from fractions import Fraction
from typing import Dict, Optional

_FRACTION_CACHE: Optional[Dict[float, str]] = None


def get_fraction_table() -> Dict[float, str]:
    global _FRACTION_CACHE
    if _FRACTION_CACHE is not None:
        return _FRACTION_CACHE

    _FRACTION_CACHE = {}
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ref_paths = [
        os.path.join(base_dir, "data", "reference", "Decimal_Fraction.xlsx"),
        os.path.join(base_dir, "data", "Decimal_Fraction.xlsx"),
    ]

    found_file = next((p for p in ref_paths if os.path.exists(p)), None)

    if found_file:
        try:
            import pandas as pd
            df = pd.read_excel(found_file)
            # Read block pairs
            for _, row in df.iterrows():
                for col in df.columns:
                    val = row[col]
                    if pd.notna(val):
                        val_str = str(val).strip()
                        if "/" in val_str:
                            try:
                                f = Fraction(val_str)
                                decimal_val = round(float(f), 6)
                                _FRACTION_CACHE[decimal_val] = val_str
                            except ValueError:
                                pass
            print(f"[INFO] Ingested {len(_FRACTION_CACHE)} decimal-fraction entries from {found_file}")
            return _FRACTION_CACHE
        except Exception as e:
            print(f"[WARN] Failed to load fraction reference file {found_file}: {e}")

    # Fallback to dim_parser FRACTION_TABLE
    from dim_parser import FRACTION_TABLE
    for dec, frac in FRACTION_TABLE.items():
        _FRACTION_CACHE[dec] = f"{frac.numerator}/{frac.denominator}"

    return _FRACTION_CACHE
