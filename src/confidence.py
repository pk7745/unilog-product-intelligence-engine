"""
Field-level and product-level confidence (Phase 25).

Replaces the prototype's `sum(bool)/count` formula. Confidence is now a
function of: source authority, extraction method, and whether the value
was cross-confirmed by an independent source. Overall product confidence
is a coverage-weighted aggregate, not an average that can hit 1.0 while
whole categories of information (identifiers, images, docs) are still
completely unverified.
"""

from models import CONF_HIGH, CONF_MEDIUM, CONF_LOW, CONF_UNVERIFIED, CONF_CONFLICT

METHOD_BASE_CONFIDENCE = {
    "MANUFACTURER_PAGE": 0.95,
    "MANUFACTURER_PDF": 0.95,
    "SECONDARY_SOURCE": 0.55,
    "MASTER_DATA_ALIAS_MATCH": 0.9,
    "DESCRIPTION_BRAND_TOKEN": 0.5,
    "REGEX": 0.3,
    "RULE": 0.6,
    "UNVERIFIED_CLEANUP": 0.2,
    "HUMAN": 1.0,
}


def band_for_score(score: float) -> str:
    if score >= 0.85:
        return CONF_HIGH
    if score >= 0.5:
        return CONF_MEDIUM
    if score > 0:
        return CONF_LOW
    return CONF_UNVERIFIED


def field_confidence(fact) -> float:
    if fact.status == "CONFLICT":
        return 0.0
    base = METHOD_BASE_CONFIDENCE.get(fact.method, 0.3)
    return max(fact.confidence, base) if fact.confidence else base


# Coverage groups used for the QA report (Section 25/37) -- what fraction
# of each group is populated AND evidence-backed, tracked separately.
COVERAGE_GROUPS = {
    "identity": ["MANUFACTURER_NAME", "BRAND_NAME"],
    "taxonomy": ["Classpath"],
    "core_attributes": [],  # filled per-category from category_schema.expected_attributes
    "identifiers": ["UPC", "EAN", "GTIN"],
    "assets": ["Product Image", "Specification Sheet", "SDS"],
}


def compute_product_confidence(record):
    """
    Aggregate confidence across identity, taxonomy, and attributes.
    Weighted, not averaged blindly: identity and taxonomy each count once;
    attributes count as a block (mean of populated-attribute confidences).
    Unpopulated groups pull the overall score down rather than being
    excluded from the denominator -- an all-blank identifiers group is a
    real gap, not something to ignore when scoring.
    """
    scores = []

    id_score = 0.0
    if record.identity.manufacturer_name:
        id_score += 0.5 * {"HIGH": 1.0, "MEDIUM": 0.6, "LOW": 0.3, "UNVERIFIED": 0.0}.get(
            record.identity.manufacturer_confidence, 0.0)
    if record.identity.brand_name:
        id_score += 0.5 * {"HIGH": 1.0, "MEDIUM": 0.6, "LOW": 0.3, "UNVERIFIED": 0.0}.get(
            record.identity.brand_confidence, 0.0)
    scores.append(id_score)

    tax_score = {"HIGH": 1.0, "MEDIUM": 0.6, "LOW": 0.3, "UNRESOLVED": 0.0}.get(
        record.taxonomy.confidence_band, 0.0)
    scores.append(tax_score)

    if record.attributes:
        attr_scores = [field_confidence(f) for f in record.attributes]
        scores.append(sum(attr_scores) / len(attr_scores))
    else:
        scores.append(0.0)

    # identifiers/assets: real gaps in this build (enrichment not run at
    # scale), scored honestly as 0 rather than excluded
    scores.append(0.0)  # identifiers
    scores.append(0.0)  # assets

    overall = sum(scores) / len(scores)
    return round(overall, 3), band_for_score(overall)
