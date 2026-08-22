"""
Authoritative source discovery (Phase 4).

Built as a GENERIC, reusable module per the upgrade spec -- the same
interface should work whether you run it on 10 products or 1,000. The
actual network calls in THIS execution environment are made by the
orchestrating agent (web_search / web_fetch tools), not by this sandbox's
Python runtime (which has no general internet egress). This module
therefore separates:

  1. build_queries()      - pure function, no network
  2. classify_source()    - pure function: URL -> source_type + authority
  3. SourceDiscovery       - orchestration class that accepts injectable
                             search_fn/fetch_fn callables, so in a real
                             deployment you plug in live API calls, and in
                             this demo run you plug in a small cache reader
                             populated from real web_search/web_fetch calls
                             made once per selected product.

Marketplaces/distributors (Section 17: "do not use marketplaces as
authoritative evidence") are explicitly deprioritized/rejected as PRIMARY
evidence, only ever usable as secondary/supporting.
"""

import re
from urllib.parse import urlparse

AUTHORITY_SCORES = {
    "official_manufacturer_page": 1.00,
    "official_pdf": 0.98,
    "official_manual": 0.97,
    "official_catalog": 0.95,
    "trusted_distributor": 0.75,
    "secondary": 0.45,
    "unknown": 0.20,
}

MARKETPLACE_DOMAINS = {
    "amazon.com", "ebay.com", "walmart.com", "homedepot.com", "lowes.com",
    "grainger.com", "zoro.com", "acmetools.com", "toolnut.com",
}


def build_queries(mpn: str, manufacturer: str = "", brand: str = "", official_domain: str = ""):
    """Ordered candidate queries, most targeted first."""
    queries = []
    if official_domain:
        queries.append(f'site:{official_domain} "{mpn}"')
    if manufacturer:
        queries.append(f'"{manufacturer}" "{mpn}" specifications')
    if brand:
        queries.append(f'"{brand}" "{mpn}"')
    queries.append(f'"{mpn}" datasheet')
    queries.append(f'"{mpn}" specifications')
    return queries


def classify_source(url: str, official_domain: str = ""):
    """Return (source_type, authority_score)."""
    domain = urlparse(url).netloc.lower().replace("www.", "")

    if any(m in domain for m in MARKETPLACE_DOMAINS):
        return "secondary", AUTHORITY_SCORES["secondary"]

    if official_domain and official_domain.lower() in domain:
        if url.lower().endswith(".pdf"):
            return "official_pdf", AUTHORITY_SCORES["official_pdf"]
        return "official_manufacturer_page", AUTHORITY_SCORES["official_manufacturer_page"]

    if url.lower().endswith(".pdf"):
        return "unknown_pdf", AUTHORITY_SCORES["secondary"]

    return "unknown", AUTHORITY_SCORES["unknown"]


def extract_spec_mentions(text: str, mpn: str):
    """
    Very lightweight evidence extraction: find numeric spec-like mentions
    near common attribute keywords, and confirm the MPN actually appears in
    the text (so we don't attribute another product's specs to this one).
    Returns list of dicts: {label, value, uom, evidence_text}.
    """
    if mpn.lower() not in text.lower():
        return [], False

    found = []
    patterns = {
        "Diameter": r"(?:diameter|dia\.?)[:\s]+([\d.\-/]+)\s*(in|inch|inches|mm|\")",
        "Thickness": r"(?:thickness)[:\s]+([\d.\-/]+)\s*(in|inch|inches|mm|\")",
        "Arbor Size": r"(?:arbor)[:\s]+([\d.\-/]+)\s*(in|inch|inches|mm|\")",
        "Weight": r"(?:weight)[:\s]+([\d.]+)\s*(lb|lbs|oz|kg)",
        "Grit": r"(?:grit)[:\s]+(\d{2,4})",
        "RPM": r"(?:max\.?\s*rpm|rpm)[:\s]+([\d,]+)",
    }
    for label, pat in patterns.items():
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            groups = m.groups()
            value = groups[0]
            uom = groups[1] if len(groups) > 1 else ""
            found.append({
                "label": label, "value": value, "uom": uom,
                "evidence_text": text[max(0, m.start() - 40):m.end() + 40].strip(),
            })
    return found, True


class SourceDiscovery:
    def __init__(self, search_fn=None, fetch_fn=None):
        self.search_fn = search_fn
        self.fetch_fn = fetch_fn

    def discover(self, mpn, manufacturer="", brand="", official_domain=""):
        """Returns list of ranked (url, source_type, authority_score)."""
        if not self.search_fn:
            return []
        queries = build_queries(mpn, manufacturer, brand, official_domain)
        candidates = []
        for q in queries:
            for url in self.search_fn(q):
                source_type, score = classify_source(url, official_domain)
                candidates.append((url, source_type, score))
        candidates.sort(key=lambda c: -c[2])
        return candidates

    def fetch_evidence(self, url, mpn):
        if not self.fetch_fn:
            return [], False
        text = self.fetch_fn(url)
        return extract_spec_mentions(text, mpn)
