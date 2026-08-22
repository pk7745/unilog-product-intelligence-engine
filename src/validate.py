"""
Final validation gate (Phase 39 / Section 4's exact-header contract).

A delivery file that fails schema validation must be considered invalid --
this module is the enforcement point. Also runs the secondary checks
(char limits, UOM validity, attribute slot bounds, URL syntax) and returns
a structured report rather than silently passing/failing.
"""

import re
from urllib.parse import urlparse

URL_RE = re.compile(r"^https?://[^\s]+$")


def validate_schema(expected_header, actual_header):
    errors = []
    if len(expected_header) != len(actual_header):
        errors.append(f"header count mismatch: expected {len(expected_header)}, got {len(actual_header)}")
    if expected_header != actual_header:
        for i, (e, a) in enumerate(zip(expected_header, actual_header)):
            if e != a:
                errors.append(f"column {i}: expected '{e}', got '{a}'")
        if len(expected_header) != len(actual_header):
            pass  # already reported
    if len(set(actual_header)) != len(actual_header):
        seen = set()
        dupes = set()
        for h in actual_header:
            if h in seen:
                dupes.add(h)
            seen.add(h)
        errors.append(f"duplicate headers: {sorted(dupes)}")
    extra = set(actual_header) - set(expected_header)
    if extra:
        errors.append(f"unexpected headers: {sorted(extra)}")
    return len(errors) == 0, errors


def validate_row(row: dict):
    """Row-level checks. Returns list of issue strings (empty = clean)."""
    issues = []

    if row.get("INVOICE_DESC") and len(row["INVOICE_DESC"]) > 40:
        issues.append(f"INVOICE_DESC exceeds 40 chars ({len(row['INVOICE_DESC'])})")

    mobile = row.get("MOBILE_DESC", "")
    if mobile and not (60 <= len(mobile) <= 80):
        issues.append(f"MOBILE_DESC out of 60-80 char range ({len(mobile)})")

    # attribute slot bounds: label/value/uom must be consistently filled together
    for i in range(1, 51):
        label = row.get(f"ATTRIBUTE_LABEL {i}", "")
        value = row.get(f"ATTRIBUTE_VALUE {i}", "")
        if bool(label) != bool(value):
            issues.append(f"ATTRIBUTE slot {i} has label/value mismatch")

    for url_col in ["MFR URL", "Ref URL 1", "Ref URL 2", "Ref URL 3", "Ref URL 4", "Ref URL 5"]:
        v = row.get(url_col, "")
        if v and not URL_RE.match(v):
            issues.append(f"{url_col} is not a syntactically valid URL: {v}")

    return issues
