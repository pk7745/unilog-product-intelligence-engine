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
    # --- TOOLS & EQUIPMENT > POWER TOOL ACCESSORIES > ABRASIVES ---
    (r"\bcut and grind\b", "Tools & Equipment", "Power Tool Accessories", "Cut & Grind Discs",
     "Tools & Equipment>Power Tool Accessories>Abrasives>Cut & Grind Discs"),
    (r"\b(cut[- ]?off disc|cut[- ]?off wheel|metal cut disc|perform\+dual metal cut n grind)\b", "Tools & Equipment", "Power Tool Accessories", "Cut-Off Discs",
     "Tools & Equipment>Power Tool Accessories>Abrasives>Cut-Off Discs"),
    (r"\bsanding belt\b", "Tools & Equipment", "Power Tool Accessories", "Sanding Belts",
     "Tools & Equipment>Power Tool Accessories>Abrasives>Sanding Belts"),
    (r"\bsanding sponge\b", "Tools & Equipment", "Power Tool Accessories", "Sanding Sponges",
     "Tools & Equipment>Power Tool Accessories>Abrasives>Sanding Sponges"),
    (r"\b(stikit|hookit|abranet|hiolit|abrasive disc|sanding disc|disc/box|micro mesh|sanding paper|sand paper|sanding sheet|abrasive roll|abrasive sheet|polishing pad|buffing wheel|abrasive set|gr pro)\b", "Tools & Equipment", "Power Tool Accessories", "Sanding Discs",
     "Tools & Equipment>Power Tool Accessories>Abrasives>Sanding Discs"),
    (r"\bgrinding wheel\b", "Tools & Equipment", "Power Tool Accessories", "Grinding Wheels",
     "Tools & Equipment>Power Tool Accessories>Abrasives>Grinding Wheels"),

    # --- TOOLS & EQUIPMENT > CUTTING & DRILLING ---
    (r"\b(saw blade|sawzall blade|recip blade|reciprocating blade|jig blade|jigsaw blade|circ blade|circular saw blade|diamond blade|carbide blade|planer blade|jointer blade|tile blade|replacement blade|planer knives)\b", "Tools & Equipment", "Power Tool Accessories", "Saw Blades",
     "Tools & Equipment>Power Tool Accessories>Cutting Tools>Saw Blades"),
    (r"\b(router bit|drill bit|driver bit|bit set|torx|phillips|hex bit|drive bit|insert bit|step drill|countersink|bit assort|nutsetter|socket adapter|torsion bit|dado pro set|hole dozer)\b", "Tools & Equipment", "Power Tool Accessories", "Bits",
     "Tools & Equipment>Power Tool Accessories>Cutting Tools>Bits"),

    # --- TOOLS & EQUIPMENT > HAND TOOLS ---
    (r"\b(file bstd|mill file|half round|flat file|taper file|rasp|files & rasps|file)\b", "Tools & Equipment", "Hand Tools", "Files & Rasps",
     "Tools & Equipment>Hand Tools>Files & Rasps"),
    (r"\b(wrench|pliers|hammer|socket|ratchet|utility knife|clamp|tape measure|hand tool|level|kneeling pad|bottle opener|inflator gauge|tire pressure|chalk & reel|organizer|tool chest)\b", "Tools & Equipment", "Hand Tools", "Hand Tools",
     "Tools & Equipment>Hand Tools>Hand Tools"),

    # --- TOOLS & EQUIPMENT > SAFETY & WORKWEAR ---
    (r"\b(heated jacket|heated vest|heated hoodie|heated coat|work jacket|parka|hoodie|workwear)\b", "Tools & Equipment", "Safety & Workwear", "Heated Gear & Apparel",
     "Tools & Equipment>Safety & Workwear>Heated Gear & Apparel"),
    (r"\b(glove|gloves|work gloves|leather gloves|cut resistant glove)\b", "Tools & Equipment", "Safety & Workwear", "Safety Gloves",
     "Tools & Equipment>Safety & Workwear>Safety Gloves"),
    (r"\b(safety glasses|eyewear|goggles|face shield|hard hat|earplugs|ear muff|respirator|knee pads|glasses)\b", "Tools & Equipment", "Safety & Workwear", "Safety Glasses & Eyewear",
     "Tools & Equipment>Safety & Workwear>Safety Glasses & Eyewear"),

    # --- TOOLS & EQUIPMENT > POWER TOOLS & ACCESSORIES ---
    (r"\b(battery|batteries|battery pack|lithium-ion battery|m18 battery|20v battery|12v battery|charger|rapid charger|fast charger|power supply|jumpstart|starter kit|flexvolt)\b", "Tools & Equipment", "Power Tools", "Batteries & Chargers",
     "Tools & Equipment>Power Tools>Batteries & Chargers"),
    (r"\b(plate only|insert|stand support|battery mounts|xtender fence|t-glide fence|fence|table assembly|framing magazine|paper bag)\b", "Tools & Equipment", "Power Tool Accessories", "Power Tool Accessories",
     "Tools & Equipment>Power Tool Accessories>Power Tool Accessories"),
    (r"\b(bandsaw|drill press|drilling system|table saw|oscillatingedge|spindle sander|planing machine|shaper|stock feeder|jointer|benchtop planer|portable planer|miter sled)\b", "Tools & Equipment", "Power Tools", "Benchtop & Stationary Power Tools",
     "Tools & Equipment>Power Tools>Benchtop & Stationary Power Tools"),
    (r"\b(nailer|stapler|autofeed|screwgun)\b", "Tools & Equipment", "Power Tools", "Power Fastening Tools",
     "Tools & Equipment>Power Tools>Power Fastening Tools"),
    (r"\b(drill|drill driver|impact|impact driver|impact wrench|angle impact|vacuum|blower|precision blower|trimmer|hedge trimmer|string trimmer|bare tool|tool[- ]only|bare|circ|circular saw|recip saw|reciprocating saw|jig saw|jigsaw|track saw|miter saw|grinder|angle grinder|die grinder|sander|orbit sander|polisher|hydraulic driver|surge kit|plunge router|rotary tool|dust extractor|jobsite speaker|speaker|2pc kit|rachet|open head rachet|grease gun)\b", "Tools & Equipment", "Power Tools", "Cordless Power Tools",
     "Tools & Equipment>Power Tools>Cordless Power Tools"),
    (r"\b(rotary hammer|bench grinder|corded drill|corded sander)\b", "Tools & Equipment", "Power Tools", "Corded Power Tools",
     "Tools & Equipment>Power Tools>Corded Power Tools"),

    # --- BUILDING MATERIALS > DECKING & RAILING ---
    (r"\b(fascia|fascia board|rim board)\b", "Building Materials", "Decking & Railing", "Fascia Boards",
     "Building Materials>Decking & Railing>Fascia Boards"),
    (r"\b(railing kit|rail kit|railing|rail pack|horizontal rail|stair rail|classic horiz|alum baluster|baluster|top rail|bottom rail|wh gate|gate sq bal|gate rd|ada rail|ada wall mount|ada int end cap|handrail)\b", "Building Materials", "Decking & Railing", "Railing Kits",
     "Building Materials>Decking & Railing>Railing Kits"),
    (r"\b(post sleeve|post cap|post skirt|solar cap|post collar|post base|decorative collar|post trim|blank post|support post|post wrap)\b", "Building Materials", "Decking & Railing", "Post Sleeves & Accessories",
     "Building Materials>Decking & Railing>Post Sleeves & Accessories"),
    (r"\b(deck board|decking board|decking|grooved board|square edge board|composite board|pvc board|lineage|transcend|select|enhance|armourguard|landmark|vintage collection|harvest collection|prime collection)\b", "Building Materials", "Decking & Railing", "Deck Boards",
     "Building Materials>Decking & Railing>Deck Boards"),
    (r"\b(gravity latch|gate latch|gate hinge|gate hardware)\b", "Building Materials", "Decking & Railing", "Gate Hardware",
     "Building Materials>Decking & Railing>Gate Hardware"),

    # --- BUILDING MATERIALS > WINDOWS, DOORS & BUILDING SUPPLIES ---
    (r"\b(patio dr|gliding patio|slider|skylt|skylight|access door|window|door|bsmt ecoliteplus|hopper)\b", "Building Materials", "Windows & Doors", "Windows & Doors",
     "Building Materials>Windows & Doors>Windows & Doors"),
    (r"\b(drywall|easi-lite|firelite|mortar|type n|rainscreen|sub floor|osb|doug fir|lumber|premier rib|metal panel|siding|sheathing|hardie sdg|hardiepanel|hardieplank|smart lap|smart pan|soffit|shingle|eaveguard|ice guard|roofing|trudef|weathr lk|fine fissured|ceiling tile)\b", "Building Materials", "Building Materials", "Structural & Wall Materials",
     "Building Materials>Building Materials>Structural & Wall Materials"),

    # --- LIGHTING & CEILING FANS ---
    (r"\b(chandelier|chandeliers)\b", "Lighting & Ceiling Fans", "Ceiling Lights", "Chandeliers",
     "Lighting & Ceiling Fans>Ceiling Lights>Chandeliers"),
    (r"\b(pendant|pendants|mini pendant)\b", "Lighting & Ceiling Fans", "Ceiling Lights", "Pendant Lights",
     "Lighting & Ceiling Fans>Ceiling Lights>Pendant Lights"),
    (r"\b(sconce|wall sconce|vanity light|wall light|lantern|outdoor lantern|post light)\b", "Lighting & Ceiling Fans", "Wall Lights", "Wall Sconces & Lanterns",
     "Lighting & Ceiling Fans>Wall Lights>Wall Sconces & Lanterns"),
    (r"\b(ceiling fan|fan w/light|outdoor fan|gilmour fan|sent hunter fan|anisten fan|cassius fan|jetty hunter fan|xidane hunter fan)\b", "Lighting & Ceiling Fans", "Ceiling Fans", "Ceiling Fans",
     "Lighting & Ceiling Fans>Ceiling Fans>Ceiling Fans"),
    (r"\b(flush mount|semi flush|flushmount|canister light|recessed light|track light|cove light|highbay light|motion lt|flat panel|down lt|downlight|down light|shop light|wrap lt|wrap light)\b", "Lighting & Ceiling Fans", "Ceiling Lights", "Flush Mount & Recessed Lights",
     "Lighting & Ceiling Fans>Ceiling Lights>Flush Mount & Recessed Lights"),
    (r"\b(led bulb|incandescent|halogen|par30|par38|br30|mr16|candelabra|a19|light bulb|bulb|incan|led t9|edison st19|40w inc|8w led|12w led)\b", "Lighting & Ceiling Fans", "Light Bulbs", "Light Bulbs",
     "Lighting & Ceiling Fans>Light Bulbs>Light Bulbs"),
    (r"\b(kichler|lighting fixture|light fixture|downrod|landscape light|led lt|strip light|ceiling lt|ceiling light|flash light|flashlight|flashlt|headlight|work light|clip light|twin head|light - rechargeable|rechargeable)\b", "Lighting & Ceiling Fans", "Light Fixtures", "Lighting Fixtures",
     "Lighting & Ceiling Fans>Light Fixtures>Lighting Fixtures"),

    # --- MAJOR APPLIANCES ---
    (r"\b(dishwasher|dish washer)\b", "Appliances", "Major Appliances", "Dishwashers",
     "Appliances>Major Appliances>Dishwashers"),
    (r"\b(dryer|clothes dryer|elect dryer|gas dryer|sq elect dryer|sq gas dryer)\b", "Appliances", "Major Appliances", "Clothes Dryers",
     "Appliances>Major Appliances>Clothes Dryers"),
    (r"\b(washer|washing machine|speed queen washer)\b", "Appliances", "Major Appliances", "Washing Machines",
     "Appliances>Major Appliances>Washing Machines"),
    (r"\b(laundry center|washer dryer combo)\b", "Appliances", "Major Appliances", "Laundry Centers",
     "Appliances>Major Appliances>Laundry Centers"),
    (r"\b(refrigerator|fridge|freezer|ice maker|beverage center)\b", "Appliances", "Major Appliances", "Refrigerators",
     "Appliances>Major Appliances>Refrigerators"),
    (r"\b(range|cooktop|wall oven|stove|microwave|range hood|vent hood|coffee maker|espresso|espresso machine|toaster|toast oven)\b", "Appliances", "Major Appliances", "Cooking Appliances",
     "Appliances>Major Appliances>Cooking Appliances"),
    (r"\b(heater kit|appliance part|dryer cord|water filter)\b", "Appliances", "Appliance Parts", "Appliance Parts & Accessories",
     "Appliances>Appliance Parts>Appliance Parts & Accessories"),

    # --- HARDWARE > FASTENERS & HARDWARE ---
    (r"\b(finish nail|brad nail|framing nail|roofing nail|coil nail|masonry nail|pin)\b", "Hardware", "Fasteners", "Nails & Pins",
     "Hardware>Fasteners>Nails & Pins"),
    (r"\b(staple|staples|narrow crown staple|crown staple)\b", "Hardware", "Fasteners", "Staples",
     "Hardware>Fasteners>Staples"),
    (r"\b(screw|wood screw|deck screw|drywall screw|machine screw|self tapping|bolt|hex bolt|lag bolt|anchor|toggle bolt|nut|hex nut|washer|flat washer)\b", "Hardware", "Fasteners", "Screws & Fasteners",
     "Hardware>Fasteners>Screws & Fasteners"),
    (r"\b(threshold|alum threshold|hinge|door trim|latch)\b", "Hardware", "Door Hardware", "Door Hardware & Thresholds",
     "Hardware>Door Hardware>Door Hardware & Thresholds"),

    # --- ELECTRICAL & PLUMBING ---
    (r"\b(elect tape|electrical tape|vinyl tape|sealing tape|emseal tape|tape)\b", "Electrical", "Electrical Accessories", "Tapes & Adhesives",
     "Electrical>Electrical Accessories>Tapes & Adhesives"),
    (r"\b(outlet|receptacle|switch|wall plate|junction box|switch box|outlet box|wire nut|cable tie|box cover|oct box|square box|2g box|1g box|decor plate|dimmer|lutron|hanger|box w/hanger|box w/bracket|timer|indoor timer|outdoor timer|load center|load cntr|entrance cable|so cord|cat5e wire|stranded wire|wire|cable|cord|triplex|cord grip|wall tap|gfci|outler|cord conn|welder outet|outet|cover wh|1g cover|wallplate)\b", "Electrical", "Wiring & Boxes", "Electrical Wiring & Boxes",
     "Electrical>Wiring & Boxes>Electrical Wiring & Boxes"),
    (r"\b(faucet|shower head|sink|toilet|pipe|fitting|valve)\b", "Plumbing", "Plumbing Fixtures", "Plumbing Fixtures & Fittings",
     "Plumbing>Plumbing Fixtures>Plumbing Fixtures & Fittings"),
]


def classify(part_desc: str, mfr: str = "", brand: str = "", mpn: str = ""):
    """Returns (dept, cls, fine, classpath, confidence_band, method, evidence)."""
    text = f"{part_desc} {mfr} {brand} {mpn}".lower()
    for pattern, dept, cls, fine, classpath in RULES:
        m = re.search(pattern, text)
        if m:
            return dept, cls, fine, classpath, "HIGH", "RULE", m.group(0)

    return "", "", "", "", "UNRESOLVED", "", ""
