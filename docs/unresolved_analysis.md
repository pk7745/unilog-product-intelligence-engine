# Unresolved Scope & Product Taxonomy Analysis

**Document Version**: 1.0.0  
**Phase**: Phase 2C — Classification & Unresolved Scope Analysis  
**Date**: 2026-08-21  

---

## 1. Executive Summary

Of the 1,000 raw supplier input rows, **366 rows (36.6%)** are classified into 21 Fine categories, while **634 rows (63.4%)** remain cleanly routed to `UNRESOLVED`.

This report provides an empirical audit of the 634 unresolved rows, explaining why they are unclassified and establishing governance rules against speculative rule creation.

---

## 2. Unresolved Breakdown by Product Family & Manufacturer

### Group 1: Commercial & Residential Lighting (208+ rows / ~33% of unresolved)
- **Top Manufacturers**: Phillips Lighting (111), Kichler Lighting (56), Satco Prod Inc (41).
- **Keywords**: `light`, `pendant`, `chandelier`, `ceiling`, `cand`, `fixture`, `bulb`.
- **Root Cause**: Lighting fixtures belong to Electrical & Lighting taxonomy branches for which no category schemas or LOV definitions exist in the available datasets.

### Group 2: Consumer & Commercial Appliances (100+ rows / ~16% of unresolved)
- **Top Manufacturers**: Appliance Dealers Cooperative (APPDE - 84 rows), Frigidaire, Electrolux, GE.
- **Keywords**: `display`, `only`, `dryer`, `range`, `refrigerator`, `dishwasher`.
- **Root Cause**: Major appliances (ovens, ranges, dryers) are outside the 21 active industrial power tool / decking & railing / abrasive categories.

### Group 3: Electrical Wiring, Safety & Hand Tools (75+ rows / ~12% of unresolved)
- **Top Manufacturers**: Southwire (19), Leviton Mfg (17), Tech Gear 5.7 (11), Edge Eyewear (10), US Tape (10).
- **Keywords**: `glove`, `heated`, `jacket`, `eyewear`, `tape`, `wire`, `switch`.
- **Root Cause**: Apparel, PPE, measuring tapes, and electrical switches are outside tool & hardware scope.

### Group 4: Specialty Tool Accessories & Apparel (100+ rows / ~16% of unresolved)
- **Top Manufacturers**: Milwaukee Accessory (42), Freud Inc (29), Dewalt (25), Festool USA (14).
- **Keywords**: `pencil`, `lead`, `heated`, `router bit`, `guide rail`, `adapter`.
- **Root Cause**: Specialty items (mechanical pencils, heated gear, router bits) do not match the 21 defined Fine category rules.

### Group 5: Raw / Unbranded / Miscellaneous (151 rows / ~23% of unresolved)
- **Top Manufacturers**: Unbranded (`-`), regional distributors, specialty fasteners.
- **Root Cause**: Cryptic short descriptions without explicit product type keywords.

---

## 3. Governance Policy: Quality over Speculative Coverage

Per challenge guidelines:
1. **No Forced Guesses**: Low-confidence products must remain `UNRESOLVED` rather than misclassified into inappropriate schemas.
2. **Preserve Integrity**: Do not create generic fallback categories (e.g. `General Hardware` or `Miscellaneous Tools`) that corrupt attribute schema contracts.
3. **Honest Confidence**: A product is only classified when an exact or high-confidence rule match confirms its Fine category taxonomy.
