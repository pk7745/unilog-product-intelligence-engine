"""
Taxonomy classification (Phase 1 stage 1: rule-based, high precision).

Per the upgrade spec: this stays the first-stage high-precision classifier
(no 161k hardcoded regex rules -- that's what the real cross-category LOV
is for, which wasn't provided). Confidence is now banded rather than a
bare True/False, and unmatched items are explicitly UNRESOLVED rather than
silently left blank with no signal of why.
"""

import re

RULES = [
    # (regex, Dept, Class, Fine, Classpath)
    (r"\bcut and grind\b", "Tools & Equipment", "Power Tool Accessories", "Cut & Grind Discs",
     "Tools & Equipment>Power Tool Accessories>Abrasives>Cut & Grind Discs"),
    (r"\bcut[- ]?off disc\b", "Tools & Equipment", "Power Tool Accessories", "Cut-Off Discs",
     "Tools & Equipment>Power Tool Accessories>Abrasives>Cut-Off Discs"),
    (r"\bsanding belt\b", "Tools & Equipment", "Power Tool Accessories", "Sanding Belts",
     "Tools & Equipment>Power Tool Accessories>Abrasives>Sanding Belts"),
    (r"\bsanding sponge\b", "Tools & Equipment", "Power Tool Accessories", "Sanding Sponges",
     "Tools & Equipment>Power Tool Accessories>Abrasives>Sanding Sponges"),
    (r"\b(stikit|disc/box|abrasive disc|sanding disc)\b", "Tools & Equipment", "Power Tool Accessories", "Sanding Discs",
     "Tools & Equipment>Power Tool Accessories>Abrasives>Sanding Discs"),
    (r"\bgrinding wheel\b", "Tools & Equipment", "Power Tool Accessories", "Grinding Wheels",
     "Tools & Equipment>Power Tool Accessories>Abrasives>Grinding Wheels"),
    (r"\bsaw blade\b", "Tools & Equipment", "Power Tool Accessories", "Saw Blades",
     "Tools & Equipment>Power Tool Accessories>Cutting Tools>Saw Blades"),
    (r"\b(router bit|drill bit|driver bit|bit set)\b", "Tools & Equipment", "Power Tool Accessories", "Bits",
     "Tools & Equipment>Power Tool Accessories>Cutting Tools>Bits"),
    (r"\b(file|rasp)\b", "Tools & Equipment", "Hand Tools", "Files & Rasps",
     "Tools & Equipment>Hand Tools>Files & Rasps"),
    # Decking & Railing Categories by Shape
    (r"\b(fascia|fascia board|rim board)\b", "Building Materials", "Decking & Railing", "Fascia Boards",
     "Building Materials>Decking & Railing>Fascia Boards"),
    (r"\b(railing kit|rail kit|railing|rail pack|horizontal rail|stair rail|classic horiz|alum baluster)\b", "Building Materials", "Decking & Railing", "Railing Kits",
     "Building Materials>Decking & Railing>Railing Kits"),
    # Building Materials Categories
    (r"\b(post sleeve|post cap|post skirt|solar cap|post collar|post base|decorative collar)\b", "Building Materials", "Decking & Railing", "Post Sleeves & Accessories",
     "Building Materials>Decking & Railing>Post Sleeves & Accessories"),
    (r"\b(deck board|decking board|decking|grooved board|square edge board|composite board|pvc board|lineage|transcend|select|enhance|armourguard|landmark|vintage collection|harvest collection|prime collection)\b", "Building Materials", "Decking & Railing", "Deck Boards",
     "Building Materials>Decking & Railing>Deck Boards"),
    (r"\b(gravity latch|gate latch|gate hinge|gate hardware)\b", "Building Materials", "Decking & Railing", "Gate Hardware",
     "Building Materials>Decking & Railing>Gate Hardware"),
    # Fasteners & Hardware Categories by Shape
    (r"\b(finish nail|brad nail|framing nail|roofing nail|coil nail|masonry nail)\b", "Hardware", "Fasteners", "Nails & Pins",
     "Hardware>Fasteners>Nails & Pins"),
    (r"\b(staple|staples|narrow crown staple|crown staple)\b", "Hardware", "Fasteners", "Staples",
     "Hardware>Fasteners>Staples"),
    # Power Tools & Outdoor Equipment Categories by Shape
    (r"\b(battery|batteries|battery pack|lithium-ion battery|m18 battery|20v battery|12v battery|charger|rapid charger|fast charger|power supply)\b", "Tools & Equipment", "Power Tools", "Batteries & Chargers",
     "Tools & Equipment>Power Tools>Batteries & Chargers"),
    (r"\b(plate only|insert|stand support|battery mounts)\b", "Tools & Equipment", "Power Tool Accessories", "Power Tool Accessories",
     "Tools & Equipment>Power Tool Accessories>Power Tool Accessories"),
    (r"\b(countersink|drill bit|torsion bit|driver set|bit set|bit assort)\b", "Tools & Equipment", "Power Tool Accessories", "Bits",
     "Tools & Equipment>Power Tool Accessories>Bits"),
    (r"\b(blade kit|sawzall blade)\b", "Tools & Equipment", "Power Tool Accessories", "Saw Blades",
     "Tools & Equipment>Power Tool Accessories>Saw Blades"),
    (r"\b(bandsaw|drill press|drilling system|table saw|oscillatingedge|spindle sander)\b", "Tools & Equipment", "Power Tools", "Benchtop & Stationary Power Tools",
     "Tools & Equipment>Power Tools>Benchtop & Stationary Power Tools"),
    (r"\b(nailer|stapler|autofeed|screwgun)\b", "Tools & Equipment", "Power Tools", "Power Fastening Tools",
     "Tools & Equipment>Power Tools>Power Fastening Tools"),
    (r"\b(drill|drill driver|impact|impact driver|impact wrench|angle impact|vacuum|blower|precision blower|trimmer|hedge trimmer|string trimmer|bare tool|tool[- ]only|bare|circ|circular saw|recip saw|reciprocating saw|jig saw|jigsaw|track saw|miter saw|grinder|angle grinder|die grinder|sander|orbit sander|polisher)\b", "Tools & Equipment", "Power Tools", "Cordless Power Tools",
     "Tools & Equipment>Power Tools>Cordless Power Tools"),
    (r"\b(rotary hammer|bench grinder|corded drill|corded sander)\b", "Tools & Equipment", "Power Tools", "Corded Power Tools",
     "Tools & Equipment>Power Tools>Corded Power Tools"),
]


def classify(part_desc: str):
    """Returns (dept, cls, fine, classpath, confidence_band, method, evidence)."""
    d = part_desc.lower()
    for pattern, dept, cls, fine, classpath in RULES:
        m = re.search(pattern, d)
        if m:
            return dept, cls, fine, classpath, "HIGH", "RULE", m.group(0)
    return "", "", "", "", "UNRESOLVED", "", ""
