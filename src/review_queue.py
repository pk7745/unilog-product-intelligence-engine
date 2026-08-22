"""
Review Queue Manager:
1. Reads output/qa_report.csv to surface products requiring human review.
2. Applies human decisions from review/review_decisions.json to cache/evidence_cache.json.
3. Updates fact status:
   - RESOLVE -> status='VERIFIED', method='HUMAN', confidence=1.0, human_confirmed=True.
   - LEAVE_BLANK -> status='CONFLICT', method='HUMAN_DEFERRED', confidence=0.0, human_reviewed=True, human_action='LEAVE_BLANK'.
"""
import csv
import json
import os

QA_REPORT_PATH = "output/qa_report.csv"
DECISIONS_PATH = "review/review_decisions.json"
CACHE_PATH = "cache/evidence_cache.json"

def load_qa_review_queue():
    if not os.path.exists(QA_REPORT_PATH):
        print(f"[WARN] QA report not found at {QA_REPORT_PATH}")
        return []

    finalized_mpns = set()
    if os.path.exists(DECISIONS_PATH):
        try:
            with open(DECISIONS_PATH, encoding="utf-8") as f:
                decisions_data = json.load(f)
            for mpn, dec in decisions_data.items():
                act = dec.get("action")
                sub_acts = [item.get("action") for item in dec.get("decisions", [])]
                if act in ("RESOLVE", "LEAVE_BLANK") or any(sa in ("RESOLVE", "LEAVE_BLANK") for sa in sub_acts):
                    finalized_mpns.add(mpn)
        except Exception as e:
            print(f"[WARN] Could not parse decisions file: {e}")

    with open(QA_REPORT_PATH, encoding="utf-8") as f:
        qa_rows = list(csv.DictReader(f))

    review_needed = [
        r for r in qa_rows
        if r.get("Needs_Review") == "Yes" and r.get("Mfg_Part_Num") not in finalized_mpns
    ]
    # Rank by Num_Conflicts descending, then Overall_Confidence ascending
    review_needed.sort(key=lambda r: (-int(r.get("Num_Conflicts", 0)), float(r.get("Overall_Confidence", 0))))
    return review_needed

def apply_review_decisions():
    if not os.path.exists(DECISIONS_PATH):
        print(f"[WARN] Decisions file not found at {DECISIONS_PATH}. Nothing to apply.")
        return 0

    with open(DECISIONS_PATH, encoding="utf-8") as f:
        decisions_data = json.load(f)

    if not os.path.exists(CACHE_PATH):
        print(f"[WARN] Evidence cache not found at {CACHE_PATH}")
        return 0

    with open(CACHE_PATH, encoding="utf-8") as f:
        cache = json.load(f)

    applied_count = 0

    for mpn, dec_entry in decisions_data.items():
        if mpn not in cache:
            cache[mpn] = {
                "mpn": mpn,
                "sources": [],
                "note": "Created via review queue decision",
                "facts": [],
                "verification_status": "UNVERIFIED"
            }
        
        prod = cache[mpn]
        facts = prod.get("facts", [])
        top_action = dec_entry.get("action")
        decisions_list = dec_entry.get("decisions", [])

        if top_action:
            if top_action == "RESOLVE":
                for f in facts:
                    f["status"] = "VERIFIED"
                    f["method"] = "HUMAN"
                    f["confidence"] = 1.0
                    f["human_confirmed"] = True
                prod["verification_status"] = "VERIFIED"
                prod["human_review_status"] = "RESOLVE"
                applied_count += 1
            elif top_action == "LEAVE_BLANK":
                for f in facts:
                    f["status"] = "CONFLICT"
                    f["method"] = "HUMAN_DEFERRED"
                    f["confidence"] = 0.0
                    f["human_reviewed"] = True
                    f["human_action"] = "LEAVE_BLANK"
                prod["verification_status"] = "CONFLICT"
                prod["human_review_status"] = "LEAVE_BLANK"
                applied_count += 1

        for dec in decisions_list:
            label = dec.get("label")
            action = dec.get("action")
            reasoning = dec.get("reasoning", "")

            if action == "RESOLVE":
                resolved_val = dec.get("resolved_value")
                resolved_uom = dec.get("resolved_uom", "")

                found = False
                for f in facts:
                    if f.get("label") == label:
                        f["value"] = resolved_val
                        f["uom"] = resolved_uom
                        f["status"] = "VERIFIED"
                        f["method"] = "HUMAN"
                        f["confidence"] = 1.0
                        f["evidence_text"] = f"Human decision: {reasoning}"
                        f["human_confirmed"] = True
                        found = True
                        break
                
                if not found:
                    facts.append({
                        "label": label,
                        "value": resolved_val,
                        "uom": resolved_uom,
                        "status": "VERIFIED",
                        "method": "HUMAN",
                        "confidence": 1.0,
                        "evidence_text": f"Human decision: {reasoning}",
                        "human_confirmed": True
                    })
                applied_count += 1

            elif action == "LEAVE_BLANK":
                for f in facts:
                    if f.get("label") == label:
                        f["status"] = "CONFLICT"
                        f["method"] = "HUMAN_DEFERRED"
                        f["confidence"] = 0.0
                        f["evidence_text"] = f"Human decision LEAVE_BLANK: {reasoning}"
                        f["human_reviewed"] = True
                        f["human_action"] = "LEAVE_BLANK"
                applied_count += 1

        # Re-evaluate top-level verification status for prod
        remaining_conflicts = [f for f in facts if f.get("status") == "CONFLICT"]
        if top_action == "RESOLVE" or (not remaining_conflicts and prod.get("sources")):
            prod["verification_status"] = "VERIFIED"
        elif remaining_conflicts:
            prod["verification_status"] = "CONFLICT"

    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)

    print(f"[SUCCESS] Applied {applied_count} human review decisions across {len(decisions_data)} MPNs to evidence_cache.json.")
    return applied_count

def main():
    print("=== REVIEW QUEUE SUMMARY ===")
    queue = load_qa_review_queue()
    print(f"Total products requiring human review: {len(queue)}")
    for r in queue[:10]:
        print(f"  - MPN: {r['Mfg_Part_Num']} | Fine: {r['Fine']} | Conflicts: {r['Num_Conflicts']} | Confidence: {r['Overall_Confidence']}")
    
    print("\n=== APPLYING HUMAN REVIEW DECISIONS ===")
    applied = apply_review_decisions()
    print(f"Applied decisions count: {applied}")

if __name__ == "__main__":
    main()
