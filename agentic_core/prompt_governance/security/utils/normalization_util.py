"""
normalization_util.py - Deterministic normalize+decode pipeline for injection detection.

Transforms obfuscated text into a canonical form so that injection signatures
can be matched even when attackers use Unicode tricks, URL encoding, Base64,
or leetspeak substitution.

All transforms are bounded and linear-time. No new dependencies.
"""

from __future__ import annotations

import base64
import logging
import unicodedata
import urllib.parse

Logger = logging.getLogger(__name__)
MAX_INPUT_CHARS: int = 100000
MAX_DECODED_CHARS: int = 8000
MAX_URL_DECODE_PASSES: int = 2
_ZERO_WIDTH_CHARS: frozenset[int] = frozenset(
    {8203, 8204, 8205, 8206, 8207, 8288, 8289, 8290, 8291, 8292, 65279},
)
_LEET_MAP: dict[str, str] = {
    "0": "o",
    "1": "i",
    "3": "e",
    "4": "a",
    "5": "s",
    "7": "t",
    "@": "a",
    "$": "s",
    "!": "i",
    "(": "c",
    "|": "l",
}


def _strip_zero_width_and_control(text: str) -> str:
    """Remove zero-width Unicode characters and C0/C1 control chars (except common whitespace)."""
    out: list[str] = []
    for ch in text:
        cp = ord(ch)
        if cp in _ZERO_WIDTH_CHARS:
            continue
        cat = unicodedata.category(ch)
        if cat.startswith("C") and ch not in ("\n", "\r", "\t"):
            continue
        out.append(ch)
    return "".join(out)


def _url_percent_decode(text: str, max_passes: int = MAX_URL_DECODE_PASSES) -> str:
    """Iterative URL percent-decode up to *max_passes* rounds, capped by MAX_DECODED_CHARS."""
    result = text
    for _ in range(max_passes):
        decoded = urllib.parse.unquote(result)
        if decoded == result:
            break
        result = decoded
    return result[:MAX_DECODED_CHARS] if len(result) > MAX_DECODED_CHARS else result


def _base64_high_confidence_decode(text: str) -> str | None:
    """Attempt Base64 decode only when high-confidence heuristics pass.

    Returns decoded UTF-8 string or None (never raises).
    """
    stripped = text.strip()
    if not stripped or len(stripped) > MAX_DECODED_CHARS:
        return None
    b64_alphabet = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=")
    if not all(ch in b64_alphabet for ch in stripped):
        return None
    if len(stripped) < 8:
        return None
    try:
        raw = base64.b64decode(stripped, validate=True)
    except (
        ValueError,
        TypeError,
        RuntimeError,
    ):  # guardian: allow-return-none-swallow -- base64 decode failure: caller treats None as non-base64 input
        return None
    try:
        decoded = raw.decode("utf-8")
    except (
        UnicodeDecodeError
    ):  # guardian: allow-return-none-swallow -- UTF-8 decode failure: caller treats None as non-text payload
        return None
    if len(decoded) > MAX_DECODED_CHARS:
        return None
    printable_ratio = sum(1 for c in decoded if c.isprintable() or c in ("\n", "\r", "\t")) / max(
        len(decoded),
        1,
    )
    if printable_ratio < 0.8:
        return None
    return decoded


def _leetspeak_normalize(text: str) -> str:
    """Single-pass leetspeak substitution. Does not expand length."""
    return "".join(_LEET_MAP.get(ch, ch) for ch in text)


def normalize_and_decode(text: str) -> tuple[str, dict]:
    """Deterministic normalize+decode pipeline.

    Returns:
        (normalized_text, metadata) where metadata records which transforms fired.
    """
    if not text:
        return ("", {"transforms": []})
    truncated = len(text) > MAX_INPUT_CHARS
    raw = text[:MAX_INPUT_CHARS] if truncated else text
    transforms: list[str] = []
    if truncated:
        transforms.append("truncated")
    raw = unicodedata.normalize("NFKC", raw)
    before_len = len(raw)
    raw = _strip_zero_width_and_control(raw)
    if len(raw) != before_len:
        transforms.append("strip_zerowidth")
    before_url = raw
    raw = _url_percent_decode(raw)
    if raw != before_url:
        transforms.append("url_decode")
    b64_decoded = _base64_high_confidence_decode(raw)
    working = raw.casefold()
    transforms.append("nfkc_casefold")
    if b64_decoded is not None:
        working = working + " " + b64_decoded.casefold()
        transforms.append("base64_decode")
    before_leet = working
    working = _leetspeak_normalize(working)
    if working != before_leet:
        transforms.append("leetspeak")
    metadata = {"transforms": transforms}
    return (working, metadata)
