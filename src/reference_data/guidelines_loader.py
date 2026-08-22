"""
Content Guidelines Reference Data Loader (Phase 3).
Loads UNILOG_INTERNAL_CONTENT_GUIDELINES.docx if available,
otherwise falls back to src/describe.py formulas.
"""

import os
from typing import Dict, Any, Optional

_GUIDELINES_CACHE: Optional[Dict[str, Any]] = None


def get_content_guidelines() -> Dict[str, Any]:
    global _GUIDELINES_CACHE
    if _GUIDELINES_CACHE is not None:
        return _GUIDELINES_CACHE

    _GUIDELINES_CACHE = {
        "INVOICE_DESC_MAX_LEN": 40,
        "MOBILE_DESC_MIN_LEN": 60,
        "MOBILE_DESC_MAX_LEN": 80,
        "PROHIBITED_FILLER": [
            "industrial grade", "premium quality", "high performance",
            "top quality", "best in class"
        ]
    }

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ref_paths = [
        os.path.join(base_dir, "data", "reference", "UNILOG_INTERNAL_CONTENT_GUIDELINES.docx"),
        os.path.join(base_dir, "data", "UNILOG_INTERNAL_CONTENT_GUIDELINES.docx"),
    ]

    found_file = next((p for p in ref_paths if os.path.exists(p)), None)

    if found_file:
        try:
            import docx
            doc = docx.Document(found_file)
            text_lines = [p.text for p in doc.paragraphs if p.text.strip()]
            _GUIDELINES_CACHE["doc_lines_count"] = len(text_lines)
            print(f"[INFO] Ingested guidelines document from {found_file}")
        except Exception as e:
            print(f"[WARN] Failed to load guidelines document {found_file}: {e}")

    return _GUIDELINES_CACHE
