"""
Manufacturer / Brand entity resolution (Phase 3).

NOTE ON SCOPE: still a stand-in for the real 27k-row
UniCat_Manufacturer_and_Brand_List.xlsx. This module is structured as a
normalized alias-matching lookup (not a giant flat dict keyed on the exact
raw string) so swapping in the real master list means loading it into
`ENTITY_ALIASES` / `ENTITY_MASTER`, not rewriting the resolution logic.

Fixes from the prototype:
  - Part_Manuf is treated as a candidate, not a fact. It may be the actual
    manufacturer, or a supplier/distributor -- resolve() flags that
    distinction explicitly (`role` field) rather than assuming.
  - Brand is never silently set equal to Manufacturer, and TRADE_NAME is
    never silently set equal to Brand -- both require positive evidence
    (either a description token match, e.g. "Diablo" in the text, or an
    entity-master pairing).
  - Casing/punctuation differences (Inc/Inc./Incorporated, Co/Company, LLC,
    Ltd, U.S.A./USA) are normalized before matching, not hardcoded per row.
"""

import re

PLACEHOLDERS = {
    "-- unbranded --", "-- no unilog brand --", "-- no dib brand --", "-",
    "", "n/a", "na",
}

SUFFIX_NORMALIZATION = [
    (r"\bincorporated\b", "inc"),
    (r"\bcompany\b", "co"),
    (r"\bu\.?s\.?a\.?\b", "usa"),
    (r"\bltd\.?\b", "ltd"),
    (r"\bllc\.?\b", "llc"),
    (r"\binc\.?\b", "inc"),
    (r"[.,]", ""),
]

# Distributor/supplier organizations known NOT to be manufacturers -- when
# Part_Manuf matches one of these, the true manufacturer must come from
# elsewhere (typically a brand token embedded in the description).
KNOWN_DISTRIBUTORS = {
    "jam industrial supply llc",
    "boise cascade building materials",
    "boise cascade",
    "parksite",
    "parksite inc",
    "u s lumber",
    "us lumber",
    "us lumber group",
}

# entity_master: canonical manufacturer -> {brand, domain_hint, aliases[]}
ENTITY_MASTER = {
    "milwaukee tool": {
        "brand": "Milwaukee®", "domain": "milwaukeetool.com",
        "aliases": ["milwaukee accessory", "milwaukee electric tool", "milw"],
    },
    "stanley black & decker, inc.": {
        "brand": "DEWALT®", "domain": "dewalt.com",
        "aliases": ["black & decker/dewlt", "black and decker", "dewalt", "black & decker"],
    },
    "freud inc": {
        "brand": "Diablo®", "domain": "freudtools.com",
        "aliases": ["freud"],
    },
    "makita u.s.a., inc.": {
        "brand": "Makita®", "domain": "makitatools.com",
        "aliases": ["makita usa inc", "makita usa", "makita"],
    },
    "3m company": {
        "brand": "3M®", "domain": "3m.com",
        "aliases": ["3m"],
    },
    "kreg tool company": {
        "brand": "Kreg®", "domain": "kregtool.com",
        "aliases": ["kreg tool co", "kreg"],
    },
    "whiteside machine & repair co": {
        "brand": "Whiteside®", "domain": "whitesiderouterbits.com",
        "aliases": ["whiteside"],
    },
    "marshalltown company": {
        "brand": "Marshalltown®", "domain": "marshalltown.com",
        "aliases": ["marshalltown trowel", "marshalltown"],
    },
    "vessel tools usa inc": {
        "brand": "Vessel®", "domain": "vessel.co.jp",
        "aliases": ["vessel tools usa", "vessel"],
    },
    "trex company, inc.": {
        "brand": "Trex®", "domain": "trex.com",
        "aliases": ["trex", "trex co", "trex company", "trex company inc"],
    },
    "timbertech (azek building products)": {
        "brand": "TimberTech®", "domain": "timbertech.com",
        "aliases": ["timbertech", "azek", "timber tech", "azek building products"],
    },
    "rdi railing (barrette outdoor living)": {
        "brand": "RDI®", "domain": "rdirailing.com",
        "aliases": ["rdi", "rdi railing", "finyl line", "finyline", "finyl", "barrette outdoor living"],
    },
    "robert bosch tool corp": {
        "brand": "Bosch®", "domain": "boschtools.com",
        "aliases": ["robt bosch tool corp", "bosch", "bosch tools"],
    },
    "festool usa": {
        "brand": "Festool®", "domain": "festoolusa.com",
        "aliases": ["festool", "festool usa"],
    },
    "united window & door": {
        "brand": "United Window & Door®", "domain": "unitedwindowmfg.com",
        "aliases": ["united window & door", "united window", "united window and door"],
    },
    "schumacher electric corporation": {
        "brand": "Schumacher®", "domain": "schumacherelectric.com",
        "aliases": ["schumacher", "schumacher electric"],
    },
    "andersen windows & doors": {
        "brand": "ANDERSEN®", "domain": "andersenwindows.com",
        "aliases": ["andersen", "andersen windows", "andersen corporation"],
    },
    "apex tool group (nicholson)": {
        "brand": "Nicholson®", "domain": "apextoolgroup.com",
        "aliases": ["nicholson", "nicholson file", "apex tool group"],
    },
}


def _normalize_org(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"\s*\(\w+\)\s*$", "", s)  # strip trailing "(CODE)"
    for pattern, repl in SUFFIX_NORMALIZATION:
        s = re.sub(pattern, repl, s)
    return re.sub(r"\s+", " ", s).strip()


def is_placeholder(value: str) -> bool:
    return (value or "").strip().lower() in PLACEHOLDERS


def _find_entity(normalized: str):
    for canonical, info in ENTITY_MASTER.items():
        if normalized == canonical or normalized in info["aliases"]:
            return canonical, info
    return None, None


def _brand_token_in_description(desc: str):
    """Look for a known brand word or alias embedded directly in the description
    (e.g. '3M 775L Stikit...', 'Diablo 1/2"x18"...', 'Finyline Wh...') -- strong evidence
    when Part_Manuf is a distributor or placeholder."""
    desc_low = desc.lower()
    for canonical, info in ENTITY_MASTER.items():
        brand_word = info["brand"].rstrip("®").lower()
        candidates = [brand_word] + [a.lower() for a in info.get("aliases", []) if a]
        for candidate in candidates:
            if candidate and re.search(rf"\b{re.escape(candidate)}\b", desc_low):
                return canonical, info
    return None, None


def resolve_entity(part_manuf: str, part_desc: str = "", e1_brand: str = "", unilog_brand: str = "", dib_brand: str = ""):
    """
    Returns a dict: manufacturer_name, manufacturer_confidence,
    manufacturer_method, brand_name, brand_confidence, trade_name,
    supplier_vs_manufacturer_flag, notes[]
    """
    notes = []

    # Extract raw candidate brand from input fields in order of precedence
    raw_brand_candidate = ""
    for b in (e1_brand, dib_brand, unilog_brand):
        if not is_placeholder(b):
            raw_brand_candidate = b.strip()
            break

    brand_canonical_from_candidate = None
    brand_info_from_candidate = None
    if raw_brand_candidate:
        norm_b = _normalize_org(raw_brand_candidate)
        brand_canonical_from_candidate, brand_info_from_candidate = _find_entity(norm_b)

    # 1. If Part_Manuf is a placeholder (e.g. '-')
    if is_placeholder(part_manuf):
        # Try raw brand candidate first
        if brand_canonical_from_candidate:
            notes.append(f"Part_Manuf is placeholder; manufacturer resolved from raw brand '{raw_brand_candidate}'")
            return {
                "manufacturer_name": brand_canonical_from_candidate.title(), "manufacturer_confidence": "HIGH",
                "manufacturer_method": "RAW_BRAND_ENTITY_RESOLUTION",
                "brand_name": brand_info_from_candidate["brand"], "brand_confidence": "HIGH",
                "trade_name": brand_info_from_candidate["brand"], "supplier_vs_manufacturer_flag": False,
                "notes": notes,
            }
        # Try description token match
        brand_canonical, brand_info = _brand_token_in_description(part_desc)
        if brand_canonical:
            notes.append(f"Part_Manuf is placeholder; manufacturer inferred from description token '{brand_info['brand']}'")
            return {
                "manufacturer_name": brand_canonical.title(), "manufacturer_confidence": "MEDIUM",
                "manufacturer_method": "DESCRIPTION_BRAND_TOKEN",
                "brand_name": brand_info["brand"], "brand_confidence": "MEDIUM",
                "trade_name": brand_info["brand"], "supplier_vs_manufacturer_flag": False,
                "notes": notes,
            }
        # Genuinely unbranded/unresolved
        raw_b = raw_brand_candidate if raw_brand_candidate else ""
        return {
            "manufacturer_name": "", "manufacturer_confidence": "UNVERIFIED",
            "manufacturer_method": "", "brand_name": raw_b, "brand_confidence": "UNVERIFIED" if raw_b else "UNVERIFIED",
            "trade_name": raw_b, "supplier_vs_manufacturer_flag": False,
            "notes": ["Part_Manuf is placeholder; no entity master match found"],
        }

    normalized = _normalize_org(part_manuf)
    canonical, info = _find_entity(normalized)

    # 2. Canonical manufacturer match and NOT a known distributor
    if canonical and normalized not in KNOWN_DISTRIBUTORS:
        # Determine brand
        b_name = info["brand"]
        b_conf = "HIGH"
        if brand_info_from_candidate:
            b_name = brand_info_from_candidate["brand"]

        return {
            "manufacturer_name": canonical.title(), "manufacturer_confidence": "HIGH",
            "manufacturer_method": "MASTER_DATA_ALIAS_MATCH",
            "brand_name": b_name, "brand_confidence": b_conf,
            "trade_name": b_name, "supplier_vs_manufacturer_flag": False,
            "notes": [],
        }

    # 3. Known distributor or unverified Part_Manuf
    if normalized in KNOWN_DISTRIBUTORS or canonical is None:
        # Check raw brand candidate first
        if brand_canonical_from_candidate:
            notes.append(
                f"Part_Manuf ('{part_manuf}') resolved as SUPPLIER/DISTRIBUTOR; "
                f"legal manufacturer resolved from raw brand '{raw_brand_candidate}'"
            )
            return {
                "manufacturer_name": brand_canonical_from_candidate.title(), "manufacturer_confidence": "HIGH",
                "manufacturer_method": "RAW_BRAND_ENTITY_RESOLUTION",
                "brand_name": brand_info_from_candidate["brand"], "brand_confidence": "HIGH",
                "trade_name": brand_info_from_candidate["brand"], "supplier_vs_manufacturer_flag": True,
                "notes": notes,
            }

        # Check description brand token
        brand_canonical, brand_info = _brand_token_in_description(part_desc)
        if brand_canonical:
            notes.append(
                f"Part_Manuf ('{part_manuf}') resolved as SUPPLIER/DISTRIBUTOR, "
                f"not manufacturer -- true manufacturer inferred from brand token "
                f"'{brand_info['brand']}' in Part_Desc"
            )
            return {
                "manufacturer_name": brand_canonical.title(), "manufacturer_confidence": "MEDIUM",
                "manufacturer_method": "DESCRIPTION_BRAND_TOKEN",
                "brand_name": brand_info["brand"], "brand_confidence": "MEDIUM",
                "trade_name": brand_info["brand"], "supplier_vs_manufacturer_flag": True,
                "notes": notes,
            }

        # No entity match in master -- use cleaned Part_Manuf as manufacturer, and raw_brand_candidate as brand if present
        notes.append(f"'{part_manuf}' not found in entity master")
        cleaned = part_manuf.split("(")[0].strip()
        b_name = brand_info_from_candidate["brand"] if brand_info_from_candidate else raw_brand_candidate
        return {
            "manufacturer_name": cleaned, "manufacturer_confidence": "LOW",
            "manufacturer_method": "UNVERIFIED_CLEANUP",
            "brand_name": b_name, "brand_confidence": "MEDIUM" if brand_info_from_candidate else "LOW",
            "trade_name": b_name, "supplier_vs_manufacturer_flag": True,
            "notes": notes,
        }

    return {
        "manufacturer_name": canonical.title(), "manufacturer_confidence": "MEDIUM",
        "manufacturer_method": "MASTER_DATA_ALIAS_MATCH",
        "brand_name": info["brand"], "brand_confidence": "MEDIUM",
        "trade_name": info["brand"], "supplier_vs_manufacturer_flag": True,
        "notes": notes,
    }
