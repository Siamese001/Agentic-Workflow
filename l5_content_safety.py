"""
L5 — Content Safety

Deterministic stub evaluators for PII and bias detection.
"""
from __future__ import annotations

import re
from typing import Dict, List


EMAIL_TOKEN = "@"
PHONE_REGEX = re.compile(r"\d{3}-\d{3}-\d{4}")
BIAS_KEYWORDS = ["gender", "race", "ethnicity"]


def detect_pii(text: str) -> Dict[str, object]:
    """Deterministic PII detection based on simple patterns."""

    instances: List[str] = []
    if EMAIL_TOKEN in text:
        instances.append("email-like")
    phone_matches = PHONE_REGEX.findall(text)
    if phone_matches:
        instances.extend(phone_matches)

    return {"pii_found": bool(instances), "instances": instances}


def detect_bias(text: str) -> Dict[str, object]:
    """Deterministic bias detection using keyword scanning."""

    categories = [keyword for keyword in BIAS_KEYWORDS if keyword in text.lower()]
    return {"bias_found": bool(categories), "categories": categories}
