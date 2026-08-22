import sys, os, csv
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from validate import validate_schema

def run():
    with open(os.path.join(os.path.dirname(__file__), "..", "data", "Unihack__Expected_Output_-_Delivery_Format.csv"), encoding="utf-8") as f:
        expected = next(csv.reader(f))
    with open(os.path.join(os.path.dirname(__file__), "..", "output", "final_delivery.csv"), encoding="utf-8") as f:
        actual = next(csv.reader(f))

    ok, errors = validate_schema(expected, actual)
    print(f"[{'PASS' if ok else 'FAIL'}] 252-column exact schema contract")
    print(f"  expected columns: {len(expected)}")
    print(f"  actual columns:   {len(actual)}")
    for e in errors:
        print("  -", e)
    return 0 if ok else 1

def test_schema_contract():
    res = run()
    assert res == 0, "Schema contract validation failed"


if __name__ == "__main__":
    exit(run())
