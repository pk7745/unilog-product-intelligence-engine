"""
Evidence fusion / conflict engine (Phase 6).

Merges the candidate (regex) attribute layer with any live-retrieved
evidence for the same product, producing the CANONICAL attribute set that
descriptions are built from. This is the module that enforces:
  - a VERIFIED live-evidence fact always outranks an UNVERIFIED regex
    candidate for the same label
  - two disagreeing VERIFIED facts for the same label become CONFLICT,
    never an arbitrary pick
  - facts that exist only as regex candidates stay UNVERIFIED in the
    final record (never silently promoted)
"""

import json
import os
from models import Fact, STATUS_VERIFIED, STATUS_UNVERIFIED, STATUS_CONFLICT

CACHE_PATH = os.path.join(os.path.dirname(__file__), "..", "cache", "evidence_cache.json")

_cache = None


def _load_cache():
    global _cache
    if _cache is None:
        try:
            with open(CACHE_PATH, encoding="utf-8") as f:
                _cache = json.load(f)
        except FileNotFoundError:
            _cache = {}
    return _cache


from attribute_reconciler import reconcile_attribute


def get_live_evidence(mpn: str):
    """Returns (facts: list[Fact], sources: list[dict], note: str) for an MPN,
    or ([], [], '') if no live evidence was gathered for it in this run."""
    cache = _load_cache()
    entry = cache.get(mpn)
    if not entry:
        return [], [], ""

    facts = []
    for f in entry.get("facts", []):
        raw_label = f["label"]
        rec = reconcile_attribute(raw_label)
        canonical_label = rec["canonical_label"] if rec["confidence"] >= 0.8 else raw_label
        facts.append(Fact(
            label=canonical_label,
            value=f["value"],
            uom=f.get("uom", ""),
            source_type=f.get("method", "SECONDARY_SOURCE"),
            evidence_text=f.get("evidence_text", ""),
            method=f.get("method", "SECONDARY_SOURCE"),
            confidence=f.get("confidence", 0.5),
            status=f.get("status", STATUS_VERIFIED),
            alternates=f.get("alternates", []),
        ))
    return facts, entry.get("sources", []), entry.get("note", "")


def fuse_attributes(candidate_facts, live_facts):
    """
    Merge candidate (regex, UNVERIFIED) facts with live (retrieved) facts.
    Rules:
      - same label + same value from both layers -> VERIFIED, confidence
        boosted (cross-source agreement)
      - live fact present, candidate absent -> add as VERIFIED (pure
        enrichment beyond what the description alone could give)
      - live fact status is CONFLICT -> always kept as CONFLICT regardless
        of what the candidate layer said
      - candidate-only fact (no live evidence for that label) -> stays
        UNVERIFIED, unchanged
    Returns (fused_facts: list[Fact], conflicts: list[dict])
    """
    by_label_live = {}
    for f in live_facts:
        by_label_live.setdefault(f.label, []).append(f)

    fused = []
    conflicts = []
    seen_labels = set()

    for cand in candidate_facts:
        live_matches = by_label_live.get(cand.label, [])
        if not live_matches:
            fused.append(cand)  # stays UNVERIFIED
            seen_labels.add(cand.label)
            continue

        seen_labels.add(cand.label)
        for live in live_matches:
            if live.status == STATUS_CONFLICT:
                conflicts.append({
                    "label": live.label,
                    "evidence_text": live.evidence_text,
                    "alternates": live.alternates,
                })
                fused.append(live)
                continue
            if str(cand.value).strip('"').strip() == str(live.value).strip('"').strip():
                live.confidence = min(1.0, live.confidence + 0.1)
                live.status = STATUS_VERIFIED
                fused.append(live)
            else:
                # disagreement between description-derived value and
                # retrieved evidence -- evidence wins but we keep the
                # candidate as an alternate for transparency
                live.alternates = (live.alternates or []) + [
                    {"value": cand.value, "source": "description_parse"}
                ]
                fused.append(live)

    # live facts for labels the candidate layer never found at all
    # (genuine enrichment: the description alone could never have given us this)
    for label, matches in by_label_live.items():
        if label in seen_labels:
            continue
        for live in matches:
            if live.status == STATUS_CONFLICT:
                conflicts.append({
                    "label": live.label,
                    "evidence_text": live.evidence_text,
                    "alternates": live.alternates,
                })
            fused.append(live)

    return fused, conflicts
