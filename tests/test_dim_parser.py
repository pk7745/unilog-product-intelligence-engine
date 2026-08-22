import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from dim_parser import parse_dimension_chain

CASES = [
    ('5"x.045"x7/8"',       [(5.0,'in','5'), (0.045,'in','0.045'), (0.875,'in','7/8')]),
    ('6-1/2"x1/8"x5/8"',    [(6.5,'in','6-1/2'), (0.125,'in','1/8'), (0.625,'in','5/8')]),
    ('10 1/2"',             [(10.5,'in','10-1/2')]),
    ('10-1/2"',            [(10.5,'in','10-1/2')]),
    ('1/2"x18"',            [(0.5,'in','1/2'), (18.0,'in','18')]),
    ('12"x1/8"x20mm',       [(12.0,'in','12'), (0.125,'in','1/8'), (20.0,'mm','20')]),
    ('7/8"',                [(0.875,'in','7/8')]),
    ('.045"',               [(0.045,'in','0.045')]),
    ('3/32"',               [(0.09375,'in','3/32')]),
    ("1x6-16'",             [(1.0,'in','1'), (6.0,'in','6'), (16.0,'ft','16')]),
    ('4x4-108"',            [(4.0,'in','4'), (4.0,'in','4'), (108.0,'in','108')]),
    ("6'",                  [(6.0,'ft','6')]),
]

def run():
    failures = 0
    for text, expected in CASES:
        got = parse_dimension_chain(text)
        got_simplified = [(v, u, d) for (v, u, raw, d) in got]
        ok = got_simplified == expected
        status = "PASS" if ok else "FAIL"
        if not ok:
            failures += 1
        print(f"[{status}] {text!r} -> {got_simplified}" + ("" if ok else f"  (expected {expected})"))

    # critical non-negotiables
    print("\n-- non-negotiable checks --")
    mm_check = parse_dimension_chain('12"x1/8"x20mm')
    mm_val = [t for t in mm_check if t[1] == 'mm']
    assert mm_val and mm_val[0][0] == 20.0, "20mm must stay 20mm, never convert to inches"
    print("[PASS] 20mm never converted to inches")

    precision = parse_dimension_chain('.045"')
    assert precision[0][3] == '0.045', "0.045 must stay decimal, not be forced to nearest fraction"
    print("[PASS] 0.045 stays decimal (not forced to 3/64)")

    if failures:
        print(f"\n{failures} FAILURES")
    else:
        print("\nAll dimension parser tests passed.")
    return failures

def test_dim_parser():
    failures = run()
    assert failures == 0, f"{failures} dimension parser test failures"


if __name__ == "__main__":
    exit(1 if run() else 0)
