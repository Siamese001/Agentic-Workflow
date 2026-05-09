#!/usr/bin/env python3
"""
_author_gate_pipeline_check.py — Author-Gate pipeline-completion helper.

Plan: author-gate-ui-renderer-hardening-a7f3c2 W1.P1.1.

Pure logic. No I/O at import. Safe to import from the post-cascade audit hook
(`.windsurf/scripts/post_cascade_author_gate_pipeline_audit.py`) and from the
CI freshness gate (`ops_scripts/ci/check_author_gate_pipeline_freshness.py`).

Single responsibility: given a Cascade response text, detect whether an
``AUTHOR_GATE_PACKET:`` (or legacy ``HITL_PACKET:``) block was emitted
WITHOUT a corresponding ``ask_user_question`` invocation in the same response.

Contract:
    decide(response_text: str) -> Violation | None
        Returns a Violation when the response contains a packet marker but
        no ask_user_question tool invocation. Returns None when:
          - no packet marker is present (nothing to enforce),
          - packet marker AND ask_user_question are both present (compliant),
          - the packet marker appears only inside a quoted/fenced block
            (not a real emission).

    Violation has fields:
        invariant       — "packet_without_ask_user_question"
        severity        — "critical"
        packet_count    — number of real packet markers found
        has_ask         — False (always, by construction)
        detail          — human-readable explanation
        packet_ids      — list of decision_id values extracted (best-effort)

Bypass: callers are responsible for honoring AG_PIPELINE_AUDIT_BYPASS=1
themselves (the helper does not read the environment — it stays pure).

Constitutional tie-in: §6 (Author-Gate), §30 (capture health).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Violation:
    invariant: str
    severity: str
    packet_count: int
    has_ask: bool
    detail: str
    packet_ids: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Detection patterns
# ---------------------------------------------------------------------------

# Real packet emission: AUTHOR_GATE_PACKET: followed by a JSON object.
# Must appear at the start of a line (after optional whitespace) to
# distinguish from quoted/inline mentions.
_PACKET_LINE_RE = re.compile(
    r"^[ \t]*(?:AUTHOR_GATE_PACKET|HITL_PACKET):\s*(?=\{)",
    re.MULTILINE,
)

# Quoted/fenced mentions that should NOT count as real emissions.
# We strip these regions before scanning for real packets.
# Pattern 1: fenced code blocks (``` ... ```)
_FENCED_BLOCK_RE = re.compile(r"```.*?```", re.DOTALL)
# Pattern 2: inline code (`...`)
_INLINE_CODE_RE = re.compile(r"`[^`]+`")
# Pattern 3: blockquote lines starting with >
_BLOCKQUOTE_LINE_RE = re.compile(r"^>.*$", re.MULTILINE)

# ask_user_question invocation — the XML tool-call form Cascade uses.
_ASK_INVOKE_RE = re.compile(r'<invoke\s+name="ask_user_question">')

# Fallback: also accept the function-call JSON form used in some contexts.
_ASK_FUNCTION_RE = re.compile(r'"name"\s*:\s*"ask_user_question"')


def _strip_quoted_regions(text: str) -> str:
    """Remove fenced blocks, inline code, and blockquote lines."""
    text = _FENCED_BLOCK_RE.sub("", text)
    text = _INLINE_CODE_RE.sub("", text)
    text = _BLOCKQUOTE_LINE_RE.sub("", text)
    return text


def _has_ask_user_question(text: str) -> bool:
    """Detect ask_user_question invocation in raw (unstripped) response."""
    return bool(_ASK_INVOKE_RE.search(text) or _ASK_FUNCTION_RE.search(text))


def _count_real_packets(stripped_text: str) -> int:
    """Count packet markers in text with quoted regions already removed."""
    return len(_PACKET_LINE_RE.findall(stripped_text))


def _extract_packet_ids(text: str) -> list[str]:
    """Best-effort extraction of decision_id from packet JSON blocks."""
    ids: list[str] = []
    for match in _PACKET_LINE_RE.finditer(text):
        start = match.end()
        raw = _balanced_slice(text, start)
        if raw is None:
            continue
        try:
            parsed = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            continue
        if isinstance(parsed, dict):
            did = parsed.get("decision_id")
            if isinstance(did, str) and did:
                ids.append(did)
    return ids


def _balanced_slice(text: str, start: int) -> str | None:
    """Return the balanced { ... } substring starting at ``start``."""
    if start >= len(text) or text[start] != "{":
        return None
    depth = 0
    in_str = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if escape:
            escape = False
        elif in_str:
            if ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start : i + 1]
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def decide(response_text: str) -> Violation | None:
    """Decide whether response violates the pipeline-completion invariant.

    Returns a Violation when an AUTHOR_GATE_PACKET: (or HITL_PACKET:) marker
    was emitted in the response without an accompanying ask_user_question
    tool invocation. Returns None when compliant or when no packet is present.
    """
    if not response_text:
        return None

    # Strip quoted regions so we don't flag documentation/examples.
    stripped = _strip_quoted_regions(response_text)
    packet_count = _count_real_packets(stripped)

    if packet_count == 0:
        return None

    # Check for ask_user_question in the FULL (unstripped) text — the tool
    # invocation may legitimately appear anywhere.
    if _has_ask_user_question(response_text):
        return None

    # Violation: packet emitted but no ask_user_question.
    packet_ids = _extract_packet_ids(stripped)

    return Violation(
        invariant="packet_without_ask_user_question",
        severity="critical",
        packet_count=packet_count,
        has_ask=False,
        detail=(
            f"Response contains {packet_count} AUTHOR_GATE_PACKET/HITL_PACKET "
            f"marker(s) but no ask_user_question tool invocation. The pipeline "
            f"requires packet → render-card → ask_user_question in the same "
            f"response. See plan author-gate-ui-renderer-hardening-a7f3c2."
        ),
        packet_ids=packet_ids,
    )


# Convenience alias matching the sibling _ssot_folder_check.py contract.
def check(response_text: str) -> tuple[Violation | None]:
    """Return (violation,) or (None,) — tuple form for callers expecting it."""
    return (decide(response_text),)
