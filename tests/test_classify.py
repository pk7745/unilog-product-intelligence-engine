import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from classify import classify

def run():
    cases = [
        ("49-94-0013 Milw 5\"x.045\"x7/8\" Metal Cut Off Disc", "Cut-Off Discs", "HIGH"),
        ("49-94-0501 Milw 4\"x1/4\"x5/8\" Metal Grinding Wheel", "Grinding Wheels", "HIGH"),
        ("48-22-3301 Milw Mechanical Pencil w/ Lead Pack", "", "UNRESOLVED"),  # unrelated product, must not force-classify
        ("XLC10ZW Makita 18V Cordless Vacuum (Bare)", "Cordless Power Tools", "HIGH"),
    ]
    failures = 0
    for desc, expect_fine, expect_conf in cases:
        dept, cls, fine, classpath, conf, method, evidence = classify(desc)
        ok = (fine == expect_fine and conf == expect_conf)
        print(f"[{'PASS' if ok else 'FAIL'}] {desc[:50]!r} -> fine={fine!r} conf={conf}")
        if not ok:
            failures += 1
    return failures

def test_classify():
    failures = run()
    assert failures == 0, f"{failures} classification test failures"


if __name__ == "__main__":
    exit(1 if run() else 0)
