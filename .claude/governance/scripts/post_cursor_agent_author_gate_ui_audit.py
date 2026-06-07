#!/usr/bin/env python3
"""
post_cursor_agent_author_gate_ui_audit.py — Windsurf post_cursor_agent_response UI conformance audit.

Scans the cursor agent response for ask_user_question invocations and the most recent
AUTHOR_GATE_PACKET: block in the turn. Validates four invariants from
author-gate-enforcement.md Pipeline step 7:

    1. Every surfaced option description begins with
       `[confidence=0.NN]` or `[RECOMMENDED ⭐ confidence=0.NN]`.
    2. At most one option carries the ⭐ prefix.
    3. Star presence matches packet recommendation:
         - packet.recommended_option_id set  -> exactly 1 star required (leading option)
         - no recommendation (low confidence) -> zero stars required
    4. Every surfaced option description carries a tradeoff segment, namely
       ` · trade-off: <≥20 non-whitespace chars>` somewhere after the prefix.
       Plan author-gate-four-req-enforcement-c4d2a8 W1.P3 — closes the
       pros/cons enforcement gap. The emitter (`emit_packet.py`) sets a
       deterministic floor; this invariant catches any consumer that drops
       or rebuilds the description without preserving the tradeoff.

    5. (W2.P1 — plan author-gate-pre-response-guard-d3e8a1)
       When the response contains an `ask_user_question` invocation AND Author-Gate context
       words (e.g. "Author-Gate", "AG:", "decision point") BUT no `AUTHOR_GATE_PACKET:`
       block is present, emit invariant `handcrafted_author_gate_detected` (severity=WARN).
       This catches hand-crafted Author-Gate invocations that bypass the canonical emitter
       pipeline. Advisory only — logged to violations log, never blocks.

Violations append JSONL to artifacts/cursor/author_gate_ui_violations.jsonl.

Fail policy: OPEN — always exits 0 (advisory, same shape as sibling post_cursor_agent hooks).

Bypass: env `AUTHOR_GATE_UI_BYPASS=1` logs a row with reason="bypass" and returns.

The hook reads the response payload from stdin in the Windsurf post_cursor_agent_response
contract; payload shape is a JSON object with a "response" or "text" key containing
Cursor Agent's composed response. If stdin is empty or not JSON, exits 0 silently.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
VIOLATIONS_LOG = REPO_ROOT / "artifacts" / "cursor" / "author_gate_ui_violations.jsonl"

# Patterns
_CONFIDENCE_PREFIX_RE = re.compile(r"^\[(RECOMMENDED \u2b50 )?confidence=0\.\d{2}\]")
_STAR_PREFIX_RE = re.compile(r"^\[RECOMMENDED \u2b50 confidence=0\.\d{2}\]")
# Plan author-gate-four-req-enforcement-c4d2a8 W1.P3 — invariant 4 regex.
# Matches ` · trade-off: <≥20 non-whitespace chars>` anywhere after the prefix.
# The 20-char floor avoids accepting "trade-off: tbd" or other placeholders.
_TRADEOFF_SEGMENT_RE = re.compile(
    r"\s\u00b7\s*trade-off:\s*(\S(?:.*?\S){19,})",
    re.DOTALL,
)
_TRADEOFF_MIN_CHARS = 20
_PACKET_START_RE = re.compile(r"AUTHOR_GATE_PACKET:\s*(?=\{)")
# ask_user_question invocations: locate the start of the options array; the end
# is resolved by bracket-balanced scan because descriptions may contain `]`.
_AUQ_OPTIONS_START_RE = re.compile(
    r"ask_user_question.*?\"options\"\s*:\s*(?=\[)",
    re.DOTALL,
)
# Invariant 5 — handcrafted Author-Gate detection (plan author-gate-pre-response-guard-d3e8a1)
# Detects ask_user_question present in text (tool call or prose reference).
_AUQ_PRESENT_RE = re.compile(r"\bask_user_question\b")
# Guard words that signal Author-Gate intent (high-precision; ordered by specificity).
AG_CONTEXT_WORDS: tuple[str, ...] = (
    "Author-Gate",
    "Author Gate",
    "AUTHOR_GATE",
    "AG:",
    "decision point",
    "HITL_PACKET",
)


def detect_handcrafted_author_gate(response_text: str) -> list[dict[str, Any]]:
    """Invariant 5 — detect ask_user_question in AG context without AUTHOR_GATE_PACKET.

    Returns a list with one violation dict if all three conditions hold:
      (a) ask_user_question appears in the response text,
      (b) at least one AG context word appears,
      (c) no AUTHOR_GATE_PACKET: block is present.
    Returns [] otherwise (including when packet IS present — canonical path is fine).
    Fail-soft: any unexpected error returns [].
    """
    try:
        if not _AUQ_PRESENT_RE.search(response_text):
            return []
        if _PACKET_START_RE.search(response_text):
            return []
        matched_words = [w for w in AG_CONTEXT_WORDS if w in response_text]
        if not matched_words:
            return []
        return [
            {
                "invariant": "handcrafted_author_gate_detected",
                "severity": "WARN",
                "matched_context_words": matched_words,
                "detail": (
                    "ask_user_question called with Author-Gate context words "
                    "but no AUTHOR_GATE_PACKET: block emitted. "
                    "Use the canonical emitter pipeline: refactor-decision-memory → "
                    "author-gate-packet-builder → author-gate-ui-renderer."
                ),
            }
        ]
    except Exception:
        return []


def _append_violation(row: dict[str, Any]) -> None:
    try:
        VIOLATIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with VIOLATIONS_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    except OSError:
        # Fail open — never break the hook chain.
        pass


def _extract_latest_packet(response_text: str) -> dict[str, Any] | None:
    """Find the last AUTHOR_GATE_PACKET: block and return its parsed JSON, or None."""
    matches = list(_PACKET_START_RE.finditer(response_text))
    if not matches:
        return None
    obj_start = matches[-1].end()
    raw = _balanced_slice(response_text, obj_start, "{", "}")
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _balanced_slice(text: str, start: int, open_ch: str, close_ch: str) -> str | None:
    """Return the substring [start:end+1] covering a balanced open/close span.

    Skips over strings (handles backslash escapes). Returns None on unbalanced input.
    """
    if start >= len(text) or text[start] != open_ch:
        return None
    depth = 0
    i = start
    in_str = False
    escape = False
    while i < len(text):
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
            elif ch == open_ch:
                depth += 1
            elif ch == close_ch:
                depth -= 1
                if depth == 0:
                    return text[start : i + 1]
        i += 1
    return None


def _extract_auq_option_descriptions(response_text: str) -> list[list[str]]:
    """Return [[desc, desc, ...], ...] — one inner list per ask_user_question call."""
    invocations: list[list[str]] = []
    for match in _AUQ_OPTIONS_START_RE.finditer(response_text):
        array_start = match.end()
        raw = _balanced_slice(response_text, array_start, "[", "]")
        if raw is None:
            continue
        try:
            opts = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(opts, list):
            continue
        descs: list[str] = []
        for opt in opts:
            if isinstance(opt, dict):
                desc = opt.get("description") or opt.get("label") or ""
                if isinstance(desc, str):
                    descs.append(desc.lstrip())
        if descs:
            invocations.append(descs)
    return invocations


def _audit_invocation(
    descriptions: list[str],
    packet: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Return list of violation dicts for a single ask_user_question call."""
    violations: list[dict[str, Any]] = []

    # Invariant 1: every description begins with [confidence=0.NN] or [RECOMMENDED ⭐ confidence=0.NN]
    missing_prefix = [i for i, d in enumerate(descriptions) if not _CONFIDENCE_PREFIX_RE.match(d)]
    if missing_prefix:
        violations.append(
            {
                "invariant": "confidence_prefix_missing",
                "option_indices": missing_prefix,
                "count": len(missing_prefix),
            }
        )

    # Invariant 2: at most one star
    star_indices = [i for i, d in enumerate(descriptions) if _STAR_PREFIX_RE.match(d)]
    if len(star_indices) > 1:
        violations.append(
            {
                "invariant": "multiple_stars",
                "star_indices": star_indices,
                "count": len(star_indices),
            }
        )

    # Invariant 4: every description carries a tradeoff segment.
    # Plan author-gate-four-req-enforcement-c4d2a8 W1.P3.
    missing_tradeoff: list[int] = []
    for i, d in enumerate(descriptions):
        match = _TRADEOFF_SEGMENT_RE.search(d)
        if match is None:
            missing_tradeoff.append(i)
            continue
        body = match.group(1).strip()
        if len(body) < _TRADEOFF_MIN_CHARS:
            missing_tradeoff.append(i)
    if missing_tradeoff:
        violations.append(
            {
                "invariant": "description_missing_tradeoff",
                "option_indices": missing_tradeoff,
                "count": len(missing_tradeoff),
                "min_chars": _TRADEOFF_MIN_CHARS,
            }
        )

    # Invariant 3: star presence matches recommended_option_id (Cursor leading-option UI).
    if packet is not None:
        rule = ((packet.get("routing") or {}).get("rule_applied") or "").strip()
        recommended_id = packet.get("recommended_option_id")
        if recommended_id:
            if len(star_indices) != 1:
                violations.append(
                    {
                        "invariant": "recommended_requires_exactly_one_star",
                        "rule_applied": rule,
                        "recommended_option_id": recommended_id,
                        "star_count": len(star_indices),
                    }
                )
        elif rule == "dominance_fires":
            # Legacy packets without recommended_option_id.
            if len(star_indices) != 1:
                violations.append(
                    {
                        "invariant": "dominance_requires_exactly_one_star",
                        "rule_applied": rule,
                        "star_count": len(star_indices),
                    }
                )
        elif len(star_indices) != 0:
            violations.append(
                {
                    "invariant": "no_recommendation_forbids_star",
                    "rule_applied": rule,
                    "star_count": len(star_indices),
                }
            )

    return violations


def audit_response(response_text: str) -> list[dict[str, Any]]:
    """Pure function — returns a list of violation records (empty if clean)."""
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    all_violations: list[dict[str, Any]] = []

    invocations = _extract_auq_option_descriptions(response_text)

    if not invocations:
        # No structured ask_user_question options found — check for handcrafted pattern.
        for v in detect_handcrafted_author_gate(response_text):
            v["ts"] = ts
            all_violations.append(v)
        return all_violations

    packet = _extract_latest_packet(response_text)

    for inv_idx, descs in enumerate(invocations):
        for v in _audit_invocation(descs, packet):
            v.update(
                {
                    "ts": ts,
                    "ask_user_question_index": inv_idx,
                    "option_count": len(descs),
                    "packet_routing": (packet.get("routing") if packet else None),
                    "packet_decision_id": (packet.get("decision_id") if packet else None),
                }
            )
            all_violations.append(v)

    # Invariant 5: also check for handcrafted pattern when options are present but no packet.
    if packet is None:
        for v in detect_handcrafted_author_gate(response_text):
            v["ts"] = ts
            all_violations.append(v)

    return all_violations


def _read_stdin_text() -> str:
    raw = sys.stdin.read()
    if not raw.strip():
        return ""
    # Windsurf post_cursor_agent_response delivers a JSON payload; grab text fields
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        # Treat raw as plain text response
        return raw
    if isinstance(payload, dict):
        for key in ("response", "text", "assistant_text", "content"):
            val = payload.get(key)
            if isinstance(val, str):
                return val
        # Fall back: stringify the whole payload so regexes still find markers
        return json.dumps(payload, ensure_ascii=False)
    if isinstance(payload, str):
        return payload
    return raw


def main() -> int:
    if os.environ.get("AUTHOR_GATE_UI_BYPASS") == "1":
        _append_violation(
            {
                "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "reason": "bypass",
            }
        )
        return 0

    text = _read_stdin_text()
    if not text:
        return 0

    violations = audit_response(text)
    for row in violations:
        _append_violation(row)

    # Advisory: always exit 0 regardless of findings.
    return 0


if __name__ == "__main__":
    sys.exit(main())
