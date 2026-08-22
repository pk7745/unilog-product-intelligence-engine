"""
Unit tests for Attribute Label Reconciler (src/attribute_reconciler.py).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from attribute_reconciler import reconcile_attribute


def test_reconciliation_exact_and_synonyms():
    # Exact canonical matches
    r1 = reconcile_attribute("Diameter")
    assert r1["canonical_label"] == "Diameter"
    assert r1["confidence"] == 1.0
    assert r1["status"] == "VERIFIED"

    # Synonym matches
    r2 = reconcile_attribute("Blade Diameter")
    assert r2["canonical_label"] == "Diameter"
    assert r2["method"] == "SYNONYM_DICTIONARY"

    r3 = reconcile_attribute("OAL")
    assert r3["canonical_label"] == "Length"

    r4 = reconcile_attribute("Volts")
    assert r4["canonical_label"] == "Voltage Rating"

    r5 = reconcile_attribute("For Use On")
    assert r5["canonical_label"] == "Application Material"

    r6 = reconcile_attribute("Arbor Size")
    assert r6["canonical_label"] == "Arbor Size"

    r7 = reconcile_attribute("Dia.")
    assert r7["canonical_label"] == "Diameter"

    print("[PASS] attribute reconciliation exact & synonym tests passed")


def run():
    test_reconciliation_exact_and_synonyms()
    print("All attribute reconciliation tests passed.")
    return 0


if __name__ == "__main__":
    exit(run())
