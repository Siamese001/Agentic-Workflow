"""Thought-redaction primitive for the L1 → L0 boundary (ADR-043, W4/P4.4).

Enforces the v33 §2 invariant that ``published_rationale`` — the ONLY
rationale field that crosses the L1 → L0 boundary — contains no fragment
of the private scratchpad used inside the thinking desk.

This module is a pure function:

    redact_scratchpad(text) -> str              # strips known markers
    assert_no_leakage(text) -> None             # raises if canary present

``L1PlanContractV2.validate()`` already enforces the primary canary
(``<<<PRIVATE_SCRATCHPAD``) in W2; this module extends that coverage to a
taxonomy of known leakage markers and exposes the redactor as a reusable
primitive callers can run BEFORE building the contract.
"""

from __future__ import annotations

import re
from typing import Final


class ThoughtLeakageViolation(ValueError):
    """Raised when a redacted or to-be-published string still contains a canary."""


# Canonical canary markers — any occurrence fails closed.  Case-insensitive
# word-ish match; must match the W2 canary plus common leakage vocab.
_CANARY_PATTERNS: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(r"<<<\s*PRIVATE_SCRATCHPAD", re.IGNORECASE),
    re.compile(r"\bBEGIN\s+PRIVATE\s+SCRATCHPAD\b", re.IGNORECASE),
    re.compile(r"\bEND\s+PRIVATE\s+SCRATCHPAD\b", re.IGNORECASE),
    re.compile(r"\binternal[_\s]thought\b", re.IGNORECASE),
    re.compile(r"\bsecret[_\s]reasoning\b", re.IGNORECASE),
)


# Blocks that must be stripped before publishing.  Non-greedy so multiple
# sibling blocks each get removed independently.
_BLOCK_PATTERNS: Final[tuple[re.Pattern[str], ...]] = (
    # <<<PRIVATE_SCRATCHPAD ... >>>  (W2 canary form, bounded).
    re.compile(
        r"<<<\s*PRIVATE_SCRATCHPAD.*?>>>",
        re.IGNORECASE | re.DOTALL,
    ),
    # BEGIN PRIVATE SCRATCHPAD ... END PRIVATE SCRATCHPAD  (prose form).
    re.compile(
        r"BEGIN\s+PRIVATE\s+SCRATCHPAD.*?END\s+PRIVATE\s+SCRATCHPAD",
        re.IGNORECASE | re.DOTALL,
    ),
    # <scratchpad>...</scratchpad>  (XML-style form sometimes emitted by
    # few-shot exemplars or older model families).
    re.compile(r"<scratchpad>.*?</scratchpad>", re.IGNORECASE | re.DOTALL),
    # <thinking>...</thinking>
    re.compile(r"<thinking>.*?</thinking>", re.IGNORECASE | re.DOTALL),
)


def redact_scratchpad(text: str) -> str:
    """Strip known private-scratchpad blocks from ``text``.

    Idempotent: repeated application is a no-op after the first pass.
    Does NOT raise on residual canaries; use :func:`assert_no_leakage`
    afterward for a fail-closed check.

    Args:
        text: Arbitrary rationale text that MAY contain private-scratchpad
            markers.

    Returns:
        A new string with all matched blocks removed and consecutive
        whitespace runs collapsed.
    """
    if not isinstance(text, str):
        raise TypeError(f"redact_scratchpad requires str, got {type(text)!r}")

    cleaned = text
    for pat in _BLOCK_PATTERNS:
        cleaned = pat.sub("", cleaned)
    # Collapse the whitespace the block removals leave behind.
    cleaned = re.sub(r"\s{3,}", "\n\n", cleaned)
    return cleaned.strip()


def assert_no_leakage(text: str) -> None:
    """Raise :class:`ThoughtLeakageViolation` if any canary is present.

    Use on the final ``published_rationale`` right before packaging the
    L1PlanContractV2 so the contract's own ``validate()`` never gets a
    chance to see a leaked string.

    Args:
        text: The to-be-published rationale.

    Raises:
        ThoughtLeakageViolation: If any canary pattern matches.
    """
    if not isinstance(text, str):
        raise TypeError(f"assert_no_leakage requires str, got {type(text)!r}")
    for pat in _CANARY_PATTERNS:
        m = pat.search(text)
        if m:
            raise ThoughtLeakageViolation(
                f"published_rationale contains private-scratchpad canary "
                f"matching {pat.pattern!r} at offset {m.start()}."
            )


def publish_rationale(text: str) -> str:
    """Redact then assert — the canonical publish-side helper.

    Equivalent to::

        cleaned = redact_scratchpad(text)
        assert_no_leakage(cleaned)
        return cleaned

    Raises:
        ThoughtLeakageViolation: If a canary survives redaction (which
            should be impossible under the shipped patterns, but this is
            the fail-closed belt-and-suspenders layer).
    """
    cleaned = redact_scratchpad(text)
    assert_no_leakage(cleaned)
    return cleaned


__all__ = [
    "ThoughtLeakageViolation",
    "assert_no_leakage",
    "publish_rationale",
    "redact_scratchpad",
]
