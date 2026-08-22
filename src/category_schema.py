"""
Category schema registry.

Fixes the core Phase-1 bug: dimension labels must come from the product's
CATEGORY (Fine classification), not from how many numeric tokens happened
to appear in the description. Two categories can both have a 3-token
dimension chain and mean completely different things (Cut-Off Disc:
Diameter/Thickness/Arbor; a hypothetical box product: Length/Width/Height).

Each schema entry declares:
  - dimension_chain_roles: ordered semantic labels for an "A x B x C" chain,
    keyed by chain length. Only chain lengths explicitly declared here are
    labeled; anything else becomes "Unmapped Dimension N" + review flag
    rather than a guess.
  - expected_attributes: the full set of attributes a fully-enriched item
    in this category should have (used for coverage scoring, not just
    presence-of-cell scoring).
"""

SCHEMAS = {
    # NOTE: 2-token dimension chains are deliberately left UNMAPPED for these
    # three categories. A cut-off disc/grinding wheel is conventionally
    # Diameter x Thickness x Arbor -- when only 2 tokens appear, the omitted
    # one could be either Thickness or Arbor, and picking one from position
    # alone would be exactly the guess the spec forbids. These get flagged
    # for review instead of silently labeled.
    "Cut-Off Discs": {
        "dimension_chain_roles": {
            1: ["Diameter"],
            3: ["Diameter", "Thickness", "Arbor Size"],
        },
        "expected_attributes": [
            "Diameter", "Thickness", "Arbor Size", "Grit",
            "Application Material", "Series", "Pack Quantity",
        ],
    },
    "Cut & Grind Discs": {
        "dimension_chain_roles": {
            1: ["Diameter"],
            3: ["Diameter", "Thickness", "Arbor Size"],
        },
        "expected_attributes": [
            "Diameter", "Thickness", "Arbor Size",
            "Application Material", "Series", "Pack Quantity",
        ],
    },
    "Grinding Wheels": {
        "dimension_chain_roles": {
            1: ["Diameter"],
            3: ["Diameter", "Thickness", "Arbor Size"],
        },
        "expected_attributes": [
            "Diameter", "Thickness", "Arbor Size",
            "Application Material", "Pack Quantity",
        ],
    },
    "Sanding Belts": {
        "dimension_chain_roles": {
            1: ["Width"],
            2: ["Width", "Length"],
        },
        "expected_attributes": [
            "Width", "Length", "Grit", "Abrasive Material",
            "Backing", "Pack Quantity",
        ],
    },
    "Sanding Discs": {
        "dimension_chain_roles": {
            1: ["Diameter"],
            2: ["Diameter", "Thickness"],
        },
        "expected_attributes": [
            "Diameter", "Grit", "Abrasive Material", "Backing",
            "Pack Quantity", "Application",
        ],
    },
    "Sanding Sponges": {
        "dimension_chain_roles": {
            1: ["Length"],
            2: ["Length", "Width"],
        },
        "expected_attributes": ["Grit", "Shape", "Pack Quantity"],
    },
    "Saw Blades": {
        "dimension_chain_roles": {
            1: ["Diameter"],
            2: ["Diameter", "Kerf"],
        },
        "expected_attributes": [
            "Diameter", "Tooth Count", "Arbor Size", "Application", "Material",
        ],
    },
    "Bits": {
        "dimension_chain_roles": {
            1: ["Diameter"],
            2: ["Diameter", "Length"],
        },
        "expected_attributes": ["Diameter", "Length", "Pack Quantity", "Application"],
    },
    "Files & Rasps": {
        "dimension_chain_roles": {
            1: ["Length"],
            2: ["Width", "Length"],
        },
        "expected_attributes": ["Length", "Cut Type", "Application"],
    },
    # Decking & Railing categories declared strictly by product SHAPE
    "Deck Boards": {
        "dimension_chain_roles": {
            1: ["Length"],
            2: ["Thickness", "Width"],
            3: ["Thickness", "Width", "Length"],
        },
        "expected_attributes": [
            "Thickness", "Width", "Length", "Series", "Color", "Material", "Edge Profile",
        ],
    },
    "Fascia Boards": {
        "dimension_chain_roles": {
            1: ["Length"],
            2: ["Thickness", "Width"],
            3: ["Thickness", "Width", "Length"],
        },
        "expected_attributes": [
            "Thickness", "Width", "Length", "Series", "Color", "Material",
        ],
    },
    "Railing Kits": {
        "dimension_chain_roles": {
            1: ["Length"],
            2: ["Length", "Height"],
        },
        "expected_attributes": [
            "Length", "Height", "Series", "Color", "Material", "Baluster Type",
        ],
    },
    "Post Sleeves & Accessories": {
        "dimension_chain_roles": {
            1: ["Height"],
            2: ["Post Size", "Post Size"],
            3: ["Post Size", "Post Size", "Height"],
        },
        "expected_attributes": [
            "Post Size", "Height", "Series", "Color", "Material",
        ],
    },
    "Gate Hardware": {
        "dimension_chain_roles": {},
        "expected_attributes": [
            "Hardware Type", "Color", "Material", "Series",
        ],
    },
    "Nails & Pins": {
        "dimension_chain_roles": {
            1: ["Length"],
            2: ["Length", "Gauge"],
        },
        "expected_attributes": [
            "Length", "Gauge", "Fastener Type", "Pack Quantity", "Material",
        ],
    },
    "Staples": {
        "dimension_chain_roles": {
            1: ["Leg Length"],
            2: ["Crown Width", "Leg Length"],
        },
        "expected_attributes": [
            "Crown Width", "Leg Length", "Gauge", "Pack Quantity", "Material",
        ],
    },
    # Power Tools & Outdoor Equipment categories declared strictly by SHAPE
    "Cordless Power Tools": {
        "dimension_chain_roles": {
            1: ["Cutting Swath"],
            2: ["Width", "Length"],
        },
        "expected_attributes": [
            "Voltage Rating", "Motor Type", "Tool Form", "Air Volume", "Air Speed", "Series",
        ],
    },
    "Batteries & Chargers": {
        "dimension_chain_roles": {},
        "expected_attributes": [
            "Voltage Rating", "Battery Capacity", "Chemistry", "Series", "Pack Quantity",
        ],
    },
    "Corded Power Tools": {
        "dimension_chain_roles": {
            1: ["Chuck Size"],
        },
        "expected_attributes": [
            "Amperage Rating", "Motor Type", "Speed", "Series",
        ],
    },
    "Power Fastening Tools": {
        "dimension_chain_roles": {
            1: ["Fastener Length"],
            2: ["Fastener Length", "Gauge"],
        },
        "expected_attributes": [
            "Voltage Rating", "Fastener Type", "Gauge", "Collation Angle", "Fastener Length", "Series",
        ],
    },
    "Benchtop & Stationary Power Tools": {
        "dimension_chain_roles": {
            1: ["Blade Diameter"],
            2: ["Blade Diameter", "Capacity"],
        },
        "expected_attributes": [
            "Horsepower", "Voltage Rating", "Phase", "Speed", "Series",
        ],
    },
}

DEFAULT_SCHEMA = {
    "dimension_chain_roles": {},   # unknown category: never guess labels
    "expected_attributes": [],
}


def get_schema(fine: str):
    return SCHEMAS.get(fine, DEFAULT_SCHEMA)


def label_dimension_chain(fine: str, raw_tokens: list):
    """
    raw_tokens: list of (numeric_value, source_uom, raw_token) in the order
    they appeared. Returns list of (label, numeric_value, source_uom,
    raw_token, confident: bool).
    """
    schema = get_schema(fine)
    roles = schema["dimension_chain_roles"].get(len(raw_tokens))
    out = []
    if roles:
        for role, (val, uom, raw) in zip(roles, raw_tokens):
            out.append((role, val, uom, raw, True))
    else:
        for i, (val, uom, raw) in enumerate(raw_tokens, start=1):
            out.append((f"Unmapped Dimension {i}", val, uom, raw, False))
    return out
