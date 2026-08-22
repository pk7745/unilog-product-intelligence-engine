"""
Category Schema Reference Data Loader (Phase 3).
Provides category schema lookups integrating LOV and category_schema.
"""

import os
from typing import Dict, Any, Optional

_CATEGORY_CACHE: Optional[Dict[str, Dict[str, Any]]] = None


def get_category_schema_map() -> Dict[str, Dict[str, Any]]:
    global _CATEGORY_CACHE
    if _CATEGORY_CACHE is not None:
        return _CATEGORY_CACHE

    from category_schema import SCHEMAS
    _CATEGORY_CACHE = SCHEMAS
    return _CATEGORY_CACHE


def get_schema_for_category(category_name: str) -> Dict[str, Any]:
    cat_map = get_category_schema_map()
    return cat_map.get(category_name, {
        "dimension_chain_roles": {},
        "expected_attributes": []
    })
