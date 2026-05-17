"""Shared checks: single-sentence role narratives must not repeat the candidate name.

The résumé header already states the name; repeating it reads redundant and unprofessional.
"""

from __future__ import annotations

import re

def narrative_leaks_candidate_name_tokens(narrative: str, candidate_name: str) -> tuple[bool, str | None]:
    """Return (leaks, first_token_or_none) when any name token (length ≥ 2) appears as a whole word."""
    n = (narrative or "").strip()
    cn = (candidate_name or "").strip()
    if not n or not cn:
        return False, None
    n_low = n.lower()
    raw_parts = re.split(r"[\s,]+", cn)
    tokens: list[str] = []
    for p in raw_parts:
        tok = p.strip(".,;:'\"`-()[]")
        if len(tok) >= 2:
            tokens.append(tok)
    if not tokens:
        return False, None
    for tok in tokens:
        try:
            pat = rf"\b{re.escape(tok.lower())}\b"
        except re.error:
            continue
        if re.search(pat, n_low):
            return True, tok
    return False, None


__all__ = ["narrative_leaks_candidate_name_tokens"]
