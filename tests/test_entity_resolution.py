import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from brand_map import resolve_entity

def check(name, part_manuf, part_desc, expect_manu, expect_conf, expect_supplier_flag):
    r = resolve_entity(part_manuf, part_desc)
    ok = (r["manufacturer_name"] == expect_manu and
          r["manufacturer_confidence"] == expect_conf and
          r["supplier_vs_manufacturer_flag"] == expect_supplier_flag)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {r['manufacturer_name']} / {r['manufacturer_confidence']} / supplier_flag={r['supplier_vs_manufacturer_flag']}")
    return ok

def run():
    results = []
    results.append(check(
        "Milwaukee Accessory -> clean HIGH-confidence manufacturer match",
        "Milwaukee Accessory (4031)", "49-94-0013 Milw 5\"x.045\"x7/8\" Metal Cut Off Disc",
        "Milwaukee Tool", "HIGH", False))
    results.append(check(
        "Freud Inc -> manufacturer resolved, brand (Diablo) != manufacturer",
        "Freud Inc (2435)", "DBD090094101F Diablo 9\" - Metal Cut-Off Disc",
        "Freud Inc", "HIGH", False))
    results.append(check(
        "Boise Cascade -> supplier flag TRUE, Trex resolved from desc brand token",
        "Boise Cascade Building Materials", "543140016 Trex Lineage 1x6-16' Deck Board",
        "Trex Company, Inc.", "MEDIUM", True))
    results.append(check(
        "Parksite -> supplier flag TRUE, TimberTech resolved from desc brand token",
        "Parksite Inc", "ADB15516CS TimberTech Advanced PVC 1x6-16' Deck Board",
        "Timbertech (Azek Building Products)", "MEDIUM", True))
    results.append(check(
        "RDI Finyl Line -> direct manufacturer match",
        "Barrette Outdoor Living", "73019603 RDI Finyl Line Railing Kit",
        "Rdi Railing (Barrette Outdoor Living)", "HIGH", False))
    results.append(check(
        "Black & Decker/dewlt -> alias/suffix normalization match",
        "Black & Decker/dewlt (2585)", "DCM200B Dewalt 1/2in x 18in - Band File",
        "Stanley Black & Decker, Inc.", "HIGH", False))
    results.append(check(
        "Unknown manufacturer not in master list -> LOW confidence, not invented",
        "Some Random Vendor Inc (9999)", "unknown widget",
        "Some Random Vendor Inc", "LOW", True))

    failures = results.count(False)
    print(f"\n{len(results)-failures}/{len(results)} passed")
    return failures

def test_entity_resolution():
    failures = run()
    assert failures == 0, f"{failures} entity resolution test failures"


if __name__ == "__main__":
    exit(1 if run() else 0)
