"""
Unit tests for Reference Data Loaders (src/reference_data/).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from reference_data.uom_loader import lookup_uom
from reference_data.manufacturer_loader import get_manufacturer_master
from reference_data.fraction_loader import get_fraction_table
from reference_data.lov_loader import get_lov_registry
from reference_data.guidelines_loader import get_content_guidelines


def test_reference_loaders_fallback_and_lookup():
    # UOM lookup
    uom, kind, status = lookup_uom("INCH")
    assert uom == "in"
    assert status == "APPROVED"

    # Manufacturer master
    mfg_map = get_manufacturer_master()
    assert len(mfg_map) > 0
    assert "milwaukee tool" in mfg_map or "stanley black & decker, inc." in mfg_map

    # Fraction table
    frac_map = get_fraction_table()
    assert len(frac_map) > 0

    # LOV registry
    lov_reg = get_lov_registry()
    assert len(lov_reg) > 0

    # Guidelines
    g = get_content_guidelines()
    assert g["INVOICE_DESC_MAX_LEN"] == 40

    print("[PASS] all reference loader unit tests passed")


def run():
    test_reference_loaders_fallback_and_lookup()
    return 0


if __name__ == "__main__":
    exit(run())
