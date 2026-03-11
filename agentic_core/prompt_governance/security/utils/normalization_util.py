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

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

Logger = logging.getLogger(__name__)

# ── Hard Caps ────────────────────────────────────────────────────────────────
MAX_INPUT_CHARS: int = 100_000
MAX_DECODED_CHARS: int = 8_000
MAX_URL_DECODE_PASSES: int = 2

# ── Zero-width / control characters to strip ─────────────────────────────────
_ZERO_WIDTH_CHARS: frozenset[int] = frozenset(
    {
        0x200B,  # ZERO WIDTH SPACE
        0x200C,  # ZERO WIDTH NON-JOINER
        0x200D,  # ZERO WIDTH JOINER
        0x200E,  # LEFT-TO-RIGHT MARK
        0x200F,  # RIGHT-TO-LEFT MARK
        0x2060,  # WORD JOINER
        0x2061,  # FUNCTION APPLICATION
        0x2062,  # INVISIBLE TIMES
        0x2063,  # INVISIBLE SEPARATOR
        0x2064,  # INVISIBLE PLUS
        0xFEFF,  # BYTE ORDER MARK / ZERO WIDTH NO-BREAK SPACE
    }
)

# ── Leetspeak map (single-pass substitution) ─────────────────────────────────
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
    # Must look like base64: A-Za-z0-9+/= only, length divisible by 4 after padding
    b64_alphabet = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=")
    if not all(ch in b64_alphabet for ch in stripped):
        return None
    if len(stripped) < 8:
        return None
    try:
        raw = base64.b64decode(stripped, validate=True)
    except Exception:
        return None
    # Decoded bytes must be mostly printable UTF-8
    try:
        decoded = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    if len(decoded) > MAX_DECODED_CHARS:
        return None
    printable_ratio = sum(1 for c in decoded if c.isprintable() or c in ("\n", "\r", "\t")) / max(
        len(decoded), 1
    )
    if printable_ratio < 0.80:
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

    # Truncate oversized input
    truncated = len(text) > MAX_INPUT_CHARS
    raw = text[:MAX_INPUT_CHARS] if truncated else text

    transforms: list[str] = []
    if truncated:
        transforms.append("truncated")

    # (a) Unicode NFKC (case-preserving first — needed for base64 alphabet)
    raw = unicodedata.normalize("NFKC", raw)

    # (b) Strip zero-width / control chars (case-preserving)
    before_len = len(raw)
    raw = _strip_zero_width_and_control(raw)
    if len(raw) != before_len:
        transforms.append("strip_zerowidth")

    # (c) URL percent-decode (max 2 passes, case-preserving)
    before_url = raw
    raw = _url_percent_decode(raw)
    if raw != before_url:
        transforms.append("url_decode")

    # (d) Base64 high-confidence decode (on original-case text; append decoded)
    b64_decoded = _base64_high_confidence_decode(raw)

    # NOW casefold for the main working copy
    working = raw.casefold()
    transforms.append("nfkc_casefold")

    if b64_decoded is not None:
        working = working + " " + b64_decoded.casefold()
        transforms.append("base64_decode")

    # (e) Leetspeak normalization
    before_leet = working
    working = _leetspeak_normalize(working)
    if working != before_leet:
        transforms.append("leetspeak")

    metadata = {"transforms": transforms}
    return (working, metadata)
