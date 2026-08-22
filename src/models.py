"""
Canonical internal product model.

Every factual field is represented as a Fact carrying its own provenance
(source, evidence text, extraction method, confidence, status) rather than
a bare string. Modules read/write Facts; only the final mapper (mapper.py)
flattens a ProductRecord into the 252-column delivery row.

Status values (never invent a value to avoid an empty/uncertain status):
    VERIFIED     - confirmed by an authoritative source
    UNVERIFIED   - extracted from the raw description only, not confirmed
    NOT_FOUND    - actively looked for, not found
    CONFLICT     - two or more disagreeing values, unresolved
    NOT_APPLICABLE
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
import time

STATUS_VERIFIED = "VERIFIED"
STATUS_UNVERIFIED = "UNVERIFIED"
STATUS_NOT_FOUND = "NOT_FOUND"
STATUS_CONFLICT = "CONFLICT"
STATUS_NOT_APPLICABLE = "NOT_APPLICABLE"

METHOD_REGEX = "REGEX"
METHOD_RULE = "RULE"
METHOD_MASTER_DATA = "MASTER_DATA"
METHOD_MANUFACTURER_PAGE = "MANUFACTURER_PAGE"
METHOD_MANUFACTURER_PDF = "MANUFACTURER_PDF"
METHOD_SECONDARY_SOURCE = "SECONDARY_SOURCE"
METHOD_HUMAN = "HUMAN"

CONF_HIGH = "HIGH"
CONF_MEDIUM = "MEDIUM"
CONF_LOW = "LOW"
CONF_UNVERIFIED = "UNVERIFIED"
CONF_CONFLICT = "CONFLICT"


@dataclass
class Source:
    url: str
    source_type: str            # official_manufacturer_page | official_pdf | secondary | unknown
    authority_score: float
    retrieved_at: float = field(default_factory=time.time)
    domain: str = ""


@dataclass
class Fact:
    label: str
    value: str = ""
    raw_value: str = ""
    uom: str = ""
    uom_kind: str = ""           # physical | selling | packaging
    source_type: str = ""        # description_parse | official_manufacturer_page | ...
    source_url: str = ""
    evidence_text: str = ""
    method: str = METHOD_REGEX
    confidence: float = 0.0
    confidence_band: str = CONF_UNVERIFIED
    status: str = STATUS_UNVERIFIED
    alternates: List[Dict[str, Any]] = field(default_factory=list)  # conflicting candidate values

    def to_dict(self):
        return asdict(self)


@dataclass
class Identity:
    manufacturer_name: str = ""
    manufacturer_confidence: str = CONF_UNVERIFIED
    manufacturer_method: str = ""
    brand_name: str = ""
    brand_confidence: str = CONF_UNVERIFIED
    trade_name: str = ""
    supplier_vs_manufacturer_flag: bool = False
    notes: List[str] = field(default_factory=list)


@dataclass
class Taxonomy:
    dept: str = ""
    cls: str = ""
    fine: str = ""
    classpath: str = ""
    confidence_band: str = CONF_UNVERIFIED
    method: str = ""
    evidence: str = ""


@dataclass
class ProductRecord:
    mfg_part_num: str
    part_desc: str
    raw_input: Dict[str, str] = field(default_factory=dict)

    identity: Identity = field(default_factory=Identity)
    taxonomy: Taxonomy = field(default_factory=Taxonomy)
    attributes: List[Fact] = field(default_factory=list)          # canonical, post-fusion
    candidate_attributes: List[Fact] = field(default_factory=list)  # pre-fusion, regex layer
    descriptions: Dict[str, str] = field(default_factory=dict)
    features: List[str] = field(default_factory=list)
    sources: List[Source] = field(default_factory=list)
    assets: Dict[str, str] = field(default_factory=dict)
    identifiers: Dict[str, Fact] = field(default_factory=dict)     # UPC/EAN/GTIN etc.
    compliance: Dict[str, str] = field(default_factory=dict)

    overall_confidence: float = 0.0
    overall_confidence_band: str = CONF_UNVERIFIED
    review_reasons: List[str] = field(default_factory=list)
    conflicts: List[Dict[str, Any]] = field(default_factory=list)

    def needs_review(self) -> bool:
        return len(self.review_reasons) > 0 or len(self.conflicts) > 0

    def to_dict(self):
        d = asdict(self)
        return d
