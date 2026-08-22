import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from uom import classify_uom

CASES = {
    "in": ("in", "physical", "APPROVED"),
    "inch": ("in", "physical", "APPROVED"),
    "inches": ("in", "physical", "APPROVED"),
    '"': ("in", "physical", "APPROVED"),
    "mm": ("mm", "physical", "APPROVED"),
    "millimeter": ("mm", "physical", "APPROVED"),
    "pc": ("pc", "selling", "APPROVED"),
    "pcs": ("pc", "selling", "APPROVED"),
    "pk": ("pk", "selling", "APPROVED"),
    "box": ("bx", "selling", "APPROVED"),
    "furlongs": ("furlongs", "unknown", "UNKNOWN"),  # never silently valid
}

def run():
    failures = 0
    for raw, expected in CASES.items():
        got = classify_uom(raw)
        ok = got == expected
        print(f"[{'PASS' if ok else 'FAIL'}] {raw!r} -> {got}")
        if not ok:
            failures += 1
    return failures

def test_uom():
    failures = run()
    assert failures == 0, f"{failures} UOM test failures"


if __name__ == "__main__":
    exit(1 if run() else 0)
