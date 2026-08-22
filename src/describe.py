"""
Description generation (Phase 7) -- runs ONLY on canonical, post-fusion
Facts. Never invents fillers like "Industrial Grade". Deduplicates the
fact list before assembling any description so nothing repeats (e.g.
"Performance+, Metal, Performance+, Metal"). Never truncates mid-token --
INVOICE_DESC is built by adding whole tokens until the char budget is
used, not by slicing the finished string.
"""

from models import STATUS_CONFLICT


def _usable_facts(facts):
    """Facts safe to put in customer-facing copy: not CONFLICT, has a value."""
    seen = set()
    out = []
    for f in facts:
        if f.status == STATUS_CONFLICT:
            continue
        if not f.value:
            continue
        key = (f.label, str(f.value))
        if key in seen:
            continue
        seen.add(key)
        out.append(f)
    return out


def _tok(fact):
    return f"{fact.value} {fact.uom}".strip() if fact.uom else str(fact.value)


def build_invoice_desc(item_type, facts, limit=40):
    dim_labels = {"Diameter", "Thickness", "Arbor Size", "Width", "Length", "Blade Length"}
    dims = [f for f in _usable_facts(facts) if f.label in dim_labels]
    tokens = [item_type] + [_tok(f) for f in dims]
    out = []
    length = 0
    for t in tokens:
        add_len = len(t) + (1 if out else 0)
        if length + add_len > limit:
            break
        out.append(t)
        length += add_len
    return " ".join(out).upper()


def build_mobile_desc(manufacturer, brand, item_type, mpn, series=None, facts=None, classpath=None, lo=60, hi=80):
    base = [p for p in [manufacturer, brand, series, item_type, mpn] if p]
    if facts:
        for f in _usable_facts(facts):
            t = f"{f.label} {_tok(f)}" if f.label not in str(f.value) else _tok(f)
            if t not in base:
                base.append(t)
    if classpath:
        base.append(classpath)

    core = ", ".join(base)
    if len(core) > hi:
        candidate = core[:hi]
        last_comma = candidate.rfind(",")
        if last_comma >= lo - 15:
            return candidate[:last_comma].strip()
        return candidate.strip()

    return core


def build_short_desc(brand, mpn, item_type, facts, series=None, limit=None):
    key_facts = _usable_facts(facts)[:4]
    parts = [p for p in [brand, series, mpn, item_type] if p]
    s = " ".join(parts)
    if key_facts:
        s += " With " + ", ".join(_tok(f) for f in key_facts)
    return s[:limit] if limit else s


def build_long_desc(brand, item_type, facts, series=None, material=None):
    parts = [p for p in [brand, item_type] if p]
    s = " ".join(parts)
    detail = ", ".join(_tok(f) for f in _usable_facts(facts))
    tail = ", ".join(x for x in [series, detail, material] if x)
    if tail:
        s += f", {tail}"
    return s


def build_item_features(facts, series=None, notes=None):
    feats = []
    if series:
        feats.append(series)
    for f in _usable_facts(facts):
        feats.append(f"{f.label}: {_tok(f)}")
    if notes:
        feats.extend(notes)
    # dedupe while preserving order
    out, seen = [], set()
    for feat in feats:
        if feat not in seen:
            out.append(feat)
            seen.add(feat)
    return out[:20]
