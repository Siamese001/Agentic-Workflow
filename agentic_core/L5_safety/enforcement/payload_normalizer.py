"""Payload normalizer — the E5 step the contract doc describes.

Closes gap G-06: raw ``Any`` payload was being passed through to L1 unchanged.
This module implements the E5 normalization described in
``docs/reference/01_Request_Intake/01_request_intake.md`` — bounded,
deterministic cleanup that is safe to apply to any untrusted payload *before*
the stamped request is published downstream.

Operations performed (all opt-in via :class:`NormalizerOptions`):

* Unicode NFC normalization on string fields.
* Trim + collapse internal runs of whitespace.
* Strip ASCII control characters (C0 / C1) other than newline/tab.
* Normalize line endings to LF.
* Cap individual string length at ``max_string_length``.
* Recursively apply to dicts/lists; cap recursion depth.

The normalizer does NOT attempt to *rewrite* semantic content (e.g. it does not
lowercase user text or strip punctuation). Its single job is to turn encoded
noise into a bounded, predictable canonical form.

Layer authority: L5 (policy plane) — pure function, no durable writes.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")
_WHITESPACE_RUN_RE = re.compile(r"[ \t]{2,}")
_CRLF_RE = re.compile(r"\r\n?")


@dataclass(frozen=True)
class NormalizerOptions:
    """Tunable knobs for :class:`PayloadNormalizer`.

    Defaults are conservative; individual source adapters may pass tighter
    limits (e.g. webhook payloads cap at 32 KB strings).
    """

    strip_control_chars: bool = True
    collapse_whitespace: bool = True
    normalize_line_endings: bool = True
    apply_nfc: bool = True
    max_string_length: int = 64_000
    max_depth: int = 16
    max_total_strings: int = 4096


class PayloadNormalizer:
    """Deterministic payload cleaner for E5.

    Usage::

        normalizer = PayloadNormalizer()
        cleaned = normalizer.normalize(raw_payload)
    """

    def __init__(self, options: NormalizerOptions | None = None) -> None:
        self._opts = options or NormalizerOptions()

    def normalize(self, payload: object) -> object:
        """Return a normalized copy of ``payload``.

        Primitives (int/float/bool/None) pass through unchanged. Strings are
        cleaned per options. Dicts and lists are walked recursively up to
        ``max_depth``; beyond that, the subtree is returned as a repr string to
        bound pathological nesting.
        """

        state = {"strings_seen": 0}
        return self._walk(payload, depth=0, state=state)

    def _walk(self, obj: object, depth: int, state: dict) -> object:
        if depth > self._opts.max_depth:
            return f"<truncated: depth>{self._opts.max_depth}>"

        if isinstance(obj, str):
            state["strings_seen"] += 1
            if state["strings_seen"] > self._opts.max_total_strings:
                return ""
            return self._clean_string(obj)

        if isinstance(obj, dict):
            return {str(k): self._walk(v, depth + 1, state) for k, v in obj.items()}

        if isinstance(obj, list):
            return [self._walk(v, depth + 1, state) for v in obj]

        if isinstance(obj, tuple):
            return tuple(self._walk(v, depth + 1, state) for v in obj)

        # Primitives — unchanged.
        return obj

    def _clean_string(self, s: str) -> str:
        out = s
        if self._opts.apply_nfc:
            out = unicodedata.normalize("NFC", out)
        if self._opts.normalize_line_endings:
            out = _CRLF_RE.sub("\n", out)
        if self._opts.strip_control_chars:
            out = _CONTROL_RE.sub("", out)
        if self._opts.collapse_whitespace:
            out = _WHITESPACE_RUN_RE.sub(" ", out)
            out = out.strip()
        if len(out) > self._opts.max_string_length:
            out = out[: self._opts.max_string_length]
        return out


def estimate_payload_size(payload: object) -> int:
    """Rough byte-size estimate of ``payload`` for oversize guards (E2)."""

    total = 0
    stack: list[object] = [payload]
    while stack:
        item = stack.pop()
        if isinstance(item, str):
            total += len(item.encode("utf-8"))
        elif isinstance(item, (int, float, bool)) or item is None:
            total += 8
        elif isinstance(item, dict):
            for k, v in item.items():
                stack.append(k)
                stack.append(v)
        elif isinstance(item, (list, tuple)):
            stack.extend(item)
        else:
            total += len(repr(item).encode("utf-8"))
    return total


def estimate_payload_depth(payload: object) -> int:
    """Maximum nesting depth in ``payload`` (0 for primitives / flat strings)."""

    def walk(obj: object, depth: int) -> int:
        if isinstance(obj, dict):
            return max((walk(v, depth + 1) for v in obj.values()), default=depth)
        if isinstance(obj, (list, tuple)):
            return max((walk(v, depth + 1) for v in obj), default=depth)
        return depth

    return walk(payload, 0)


__all__ = [
    "NormalizerOptions",
    "PayloadNormalizer",
    "estimate_payload_depth",
    "estimate_payload_size",
]
