"""Utilities for reversible masking of personally identifiable information."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Tuple


_PII_PATTERN = re.compile(r"(?P<email>[\w.+-]+@[\w.-]+)" "|" r"(?P<phone>\+?\d[\d -]{7,}\d)")


@dataclass(frozen=True)
class SanitizedInputs:
    prompt: str
    company_id: str | None
    contact_id: str | None


SanitizeResult = Tuple[SanitizedInputs, Dict[str, str]]


def _placeholder(counter: int) -> str:
    return f"<PII_{counter}>"


def sanitize_pii(inputs) -> SanitizeResult:
    """Mask simple PII patterns while returning a reversible map."""

    prompt = getattr(inputs, "prompt", "")
    company_id = getattr(inputs, "company_id", None)
    contact_id = getattr(inputs, "contact_id", None)

    replacements: Dict[str, str] = {}
    counter = 1

    def _mask(match: re.Match[str]) -> str:
        nonlocal counter
        value = match.group(0)
        token = _placeholder(counter)
        counter += 1
        replacements[token] = value
        return token

    sanitized_prompt = _PII_PATTERN.sub(_mask, prompt)
    return SanitizedInputs(sanitized_prompt, company_id, contact_id), replacements
