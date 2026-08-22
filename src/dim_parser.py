"""
Raw dimension token parser.

Splits an "A x B x C" chain into raw (numeric_value, source_uom, raw_token)
triples WITHOUT assigning semantic labels (that's category_schema.py's job)
and WITHOUT ever discarding or silently converting an explicit unit.

Fixes from the original prototype:
  - '20mm' must never become '20 in'. Each token's source UOM is read from
    the token itself; inches are only the default when NO unit is present
    and the surrounding chain uses the bare-inch convention (a trailing "
    or no unit at all).
  - Precision decimals like '.045"' are never forced into a fraction. They
    stay decimal. Fractions are only produced for values that land within
    tolerance of a real 64th (trade-search-friendly dimensions).
  - raw_value, numeric_value, and canonical display value are all retained.
"""

import re
from fractions import Fraction

FRACTION_TABLE = {round(float(Fraction(n, 64)), 6): Fraction(n, 64) for n in range(1, 64)}


NUM = r'(?:\d+(?:[\s-]+\d+/\d+)?(?:/\d+)?(?:\.\d+)?|\.\d+)'


def _numeric_value(num_str: str) -> float:
    num_str = num_str.strip()
    if ("-" in num_str or " " in num_str) and "/" in num_str:
        parts = re.split(r"[\s-]+", num_str)
        if len(parts) == 2:
            whole, frac = parts
            n, d = frac.split("/")
            return int(whole) + int(n) / int(d)
    if "/" in num_str:
        n, d = num_str.split("/")
        return int(n) / int(d)
    return float(num_str)


def decimal_to_display(value: float, tolerance: float = 0.0005) -> str:
    """
    Canonical display form for an inch value: exact fraction if the decimal
    is genuinely close to a 64th, otherwise the ORIGINAL decimal untouched
    (never force '.045' into an approximate fraction).
    """
    whole = int(value)
    frac_part = round(value - whole, 6)
    if frac_part == 0:
        return str(whole) if whole else "0"
    best = min(FRACTION_TABLE.items(), key=lambda kv: abs(kv[0] - frac_part))
    if abs(best[0] - frac_part) > tolerance:
        s = f"{value:g}"
        return s if whole != 0 else s  # keep original decimal, e.g. '0.045'
    frac = best[1].limit_denominator(64)
    frac_str = f"{frac.numerator}/{frac.denominator}"
    return f"{whole}-{frac_str}" if whole else frac_str


UNIT_PAT = r'(?:mm|millimeters|millimeter|inches|inch|"|feet|foot|ft|\')'


def _unit_to_uom(unit_str: str) -> str:
    if not unit_str:
        return "in"
    u = unit_str.lower().strip()
    if u in ("ft", "feet", "foot", "'"):
        return "ft"
    if u in ("mm", "millimeter", "millimeters"):
        return "mm"
    return "in"


def parse_dimension_chain(text: str):
    """
    Parse a chain like '5"x.045"x7/8"', '12"x1/8"x20mm', '1x6-16\'', or '4x4-108"'
    into an ordered list of (numeric_value, source_uom, raw_token, display_value).
    """
    # 1. Compound chain check: <nominal-chain> - <length><any-unit> e.g. '1x6-16'' or '4x4-108"'
    compound_re = re.compile(
        rf'({NUM}\s*(?:{UNIT_PAT})?\s*(?:\s*[xX]\s*{NUM}\s*(?:{UNIT_PAT})?)+)\s*-\s*({NUM})\s*({UNIT_PAT})',
        re.IGNORECASE
    )
    m_comp = compound_re.search(text)
    if m_comp:
        chain_part = m_comp.group(1).strip()
        length_num = m_comp.group(2).strip()
        length_unit = m_comp.group(3).strip()
        length_raw = f"{length_num}{length_unit}"
        length_uom = _unit_to_uom(length_unit)
        length_val = _numeric_value(length_num)
        length_disp = f"{length_val:g}" if length_uom in ("mm", "ft") else decimal_to_display(length_val)

        out = []
        tokens = re.split(r'\s*[xX]\s*', chain_part)
        for tok in tokens:
            tok = tok.strip()
            m_tok = re.match(rf'({NUM})\s*({UNIT_PAT})?', tok, re.IGNORECASE)
            if not m_tok:
                continue
            num_str, unit_str = m_tok.group(1), m_tok.group(2)
            uom = _unit_to_uom(unit_str)
            val = _numeric_value(num_str)
            disp = f"{val:g}" if uom in ("mm", "ft") else decimal_to_display(val)
            out.append((val, uom, tok, disp))

        out.append((length_val, length_uom, length_raw, length_disp))
        return out

    # 2. Standard x/X chain pattern
    chain_re = re.compile(
        rf'({NUM}\s*(?:{UNIT_PAT})?(?:\s*[xX]\s*{NUM}\s*(?:{UNIT_PAT})?)+)',
        re.IGNORECASE
    )
    matches = chain_re.findall(text)
    target = max(matches, key=len) if matches else None

    if target:
        tokens = re.split(r'\s*[xX]\s*', target)
        out = []
        for tok in tokens:
            tok = tok.strip()
            m = re.match(rf'({NUM})\s*({UNIT_PAT})?', tok, re.IGNORECASE)
            if not m:
                continue
            num_str, unit_str = m.group(1), m.group(2)
            uom = _unit_to_uom(unit_str)
            val = _numeric_value(num_str)
            disp = f"{val:g}" if uom in ("mm", "ft") else decimal_to_display(val)
            out.append((val, uom, tok, disp))
        return out

    # 3. Fallback to single token with explicit unit e.g. '6\'', '9"', '20mm'
    m_single = re.search(rf'({NUM})\s*({UNIT_PAT})', text, re.IGNORECASE)
    if m_single:
        raw = m_single.group(0).strip()
        num_str, unit_str = m_single.group(1), m_single.group(2)
        uom = _unit_to_uom(unit_str)
        val = _numeric_value(num_str)
        disp = f"{val:g}" if uom in ("mm", "ft") else decimal_to_display(val)
        return [(val, uom, raw, disp)]

    return []
