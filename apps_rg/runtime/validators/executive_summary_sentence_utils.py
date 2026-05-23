"""Robust sentence splitting for executive_summary X2 gates."""

from __future__ import annotations

import re

# Private-use sentinels — must not match ``\s`` or be stripped by ``str.strip()``.
def _tok(label: str) -> str:
    return f"\ue000{label}\ue001"


# Order longest-first so nested tokens are not partially replaced.
_ABBREV_PROTECT: tuple[tuple[str, str], ...] = (
    ("U.S.A.", _tok("USA")),
    ("U.S.", _tok("US")),
    ("Basel III", _tok("B3")),
    ("CCAR", _tok("CCAR")),
    ("AWS", _tok("AWS")),
    ("Dr.", _tok("DR")),
    ("Inc.", _tok("INC")),
    ("Ltd.", _tok("LTD")),
    ("e.g.", _tok("EG")),
    ("i.e.", _tok("IE")),
    ("Mr.", _tok("MR")),
    ("Ms.", _tok("MS")),
    ("Prof.", _tok("PR")),
    ("Sr.", _tok("SR")),
    ("Jr.", _tok("JR")),
    ("Ph.D.", _tok("PHD")),
    ("No.", _tok("NO")),
    ("vs.", _tok("VS")),
)

_DECIMAL_RE = re.compile(r"\b\d+\.\d+\b")
_DECIMAL_PLACEHOLDER = _tok("DEC")
# ASCII whitespace only — abbrev guard bytes must not be consumed as boundaries.
_SENTENCE_BOUNDARY_RE = re.compile(r"(?<=[.!?])[ \t\n\r\f\v]+")


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
        out = out.replace(f"{_DECIMAL_PLACEHOLDER}{i}\ue001", val)
    return out


def split_sentences(text: str) -> list[str]:
    """Split executive-summary prose on sentence boundaries with abbreviation guards."""
    raw = str(text or "").strip()
    if not raw:
        return []
    decimals: list[str] = []

    def _dec_sub(match: re.Match[str]) -> str:
        decimals.append(match.group(0))
        return f"{_DECIMAL_PLACEHOLDER}{len(decimals) - 1}\ue001"

    protected = _DECIMAL_RE.sub(_dec_sub, raw)
    protected = _protect_abbreviations(protected)
    parts = [p.strip() for p in _SENTENCE_BOUNDARY_RE.split(protected) if p.strip()]
    return [_unprotect_abbreviations(_restore_decimals(p, decimals)) for p in parts]


def join_executive_summary_sentences(sentences: list[str]) -> str:
    """Join split sentences for display without re-splitting abbrev guards."""
    return " ".join(str(s).strip() for s in sentences if str(s).strip()).strip()
