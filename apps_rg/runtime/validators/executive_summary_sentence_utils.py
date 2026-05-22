"""Robust sentence splitting for executive_summary X2 gates."""

from __future__ import annotations

import re

# Order longest-first so nested tokens are not partially replaced.
_ABBREV_PROTECT: tuple[tuple[str, str], ...] = (
    ("U.S.A.", "\x1fUSA\x1f"),
    ("U.S.", "\x1fUS\x1f"),
    ("Basel III", "\x1fB3\x1f"),
    ("CCAR", "\x1fCCAR\x1f"),
    ("AWS", "\x1fAWS\x1f"),
    ("Dr.", "\x1fDR\x1f"),
    ("Inc.", "\x1fINC\x1f"),
    ("Ltd.", "\x1fLTD\x1f"),
    ("e.g.", "\x1fEG\x1f"),
    ("i.e.", "\x1fIE\x1f"),
    ("Mr.", "\x1fMR\x1f"),
    ("Ms.", "\x1fMS\x1f"),
    ("Prof.", "\x1fPR\x1f"),
    ("Sr.", "\x1fSR\x1f"),
    ("Jr.", "\x1fJR\x1f"),
    ("Ph.D.", "\x1fPHD\x1f"),
    ("No.", "\x1fNO\x1f"),
    ("vs.", "\x1fVS\x1f"),
)

_DECIMAL_RE = re.compile(r"\b\d+\.\d+\b")
_DECIMAL_PLACEHOLDER = "\x1fDEC\x1f"
_SENTENCE_BOUNDARY_RE = re.compile(r"(?<=[.!?])\s+")


def _protect_abbreviations(text: str) -> str:
    out = text
    for literal, token in _ABBREV_PROTECT:
        out = out.replace(literal, token)
    return out


def _unprotect_abbreviations(text: str) -> str:
    out = text
    for literal, token in _ABBREV_PROTECT:
        out = out.replace(token, literal)
    return out


def _restore_decimals(text: str, decimals: list[str]) -> str:
    out = text
    for i, val in enumerate(decimals):
        out = out.replace(f"{_DECIMAL_PLACEHOLDER}{i}\x1f", val)
    return out


def split_sentences(text: str) -> list[str]:
    """Split executive-summary prose on sentence boundaries with abbreviation guards."""
    raw = str(text or "").strip()
    if not raw:
        return []
    decimals: list[str] = []

    def _dec_sub(match: re.Match[str]) -> str:
        decimals.append(match.group(0))
        return f"{_DECIMAL_PLACEHOLDER}{len(decimals) - 1}\x1f"

    protected = _DECIMAL_RE.sub(_dec_sub, raw)
    protected = _protect_abbreviations(protected)
    parts = [p.strip() for p in _SENTENCE_BOUNDARY_RE.split(protected) if p.strip()]
    return [_unprotect_abbreviations(_restore_decimals(p, decimals)) for p in parts]
