#!/usr/bin/env python3
"""
post_cascade_next_step_miss_detector.py — Retroactive NEXT_STEP miss audit.

Hooks post_cascade_response. Scans the response for prose that suggests
follow-up work (deferred implementation, scaffolded stubs, "future work"
sections, TODO-style residue) WITHOUT a matching ``NEXT_STEP:`` marker.

This is the sibling of ``post_cascade_author_gate_miss_detector.py``:
    - author-gate miss detector     → DECISION_CAPTURED: markers
    - next-step miss detector       → NEXT_STEP: markers   (THIS FILE)
    - deferred-scope miss detector  → DEFERRED_SCOPE: markers (captured inline)

Root cause it exists to close (2026-04-24 RCA): Cascade can list follow-ups
in a prose bullet list ("## Follow-ups (not implemented)") and skip the
rule's `NEXT_STEP:` marker, leaving no plan scaffold and no Notion row.
The always-on rule fades after ~15 tool calls; a deterministic post-response
detector is the backstop.

Signals (each adds weight toward a miss):
    - "follow-up" / "follow up" / "followup" mentions
    - "not implemented", "out of scope", "deferred"
    - "future work", "later", "next step(s)"
    - "scaffolded but", "stubbed", "to be implemented"
    - Headings like ``## Follow-ups``, ``## Future Work``, ``## TODO``,
      ``## Not Implemented``, ``## Deferred``
    - Bullet lists under those headings with multiple items

Anti-signals (presence zeros out the score):
    - One or more ``NEXT_STEP:`` markers
    - One or more ``DEFERRED_SCOPE:`` markers (related discipline)
    - Explicit negation ("no follow-ups", "nothing deferred")

Output: artifacts/windsurf/next_step_misses.jsonl  (append-only)

Fail policy: OPEN. Audit only — never blocks. Windsurf hook reads exit 0.

CONSTITUTIONAL
    - Specific exceptions (json.JSONDecodeError, OSError)
    - UTF-8 I/O
    - Bounded: response capped at 1 MB before analysis
    - No subprocess, no shell
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
MISS_LOG = REPO_ROOT / "artifacts" / "windsurf" / "next_step_misses.jsonl"
MAX_RESPONSE_BYTES = 1_048_576  # 1 MB fail-safe cap

# Threshold: miss_score >= this counts as a suspected miss. Set low because
# NEXT_STEP markers are cheap and the rule is explicit.
MISS_SCORE_THRESHOLD = 2


# Positive signals ----------------------------------------------------- #

_FOLLOWUP_KEYWORDS = (
    "follow-up",
    "follow up",
    "followup",
    "not implemented",
    "out of scope",
    "future work",
    "to be implemented",
    "scaffolded but",
    "stubbed",
    "remains to",
    "remaining work",
    "next step",
    "next steps",
    "for a future",
    "deferred to",
    "could be done later",
    "could do later",
    "separate plan",
)

# Section headings that typically enumerate follow-ups
_FOLLOWUP_HEADINGS = re.compile(
    r"(?m)^\s{0,3}#{1,6}\s*(?:"
    r"follow[- ]?ups?"
    r"|future\s+work"
    r"|todo[s]?"
    r"|not\s+implemented"
    r"|deferred(?:\s+scope)?"
    r"|next\s+steps?"
    r"|open\s+(?:items|questions)"
    r"|residual(?:\s+work)?"
    r")\b",
    re.IGNORECASE,
)

# Bullet pattern — enumerates items in a list under a heading
_BULLET_ITEM = re.compile(r"(?m)^\s{0,3}[-*+]\s+\S")


# Anti-signals --------------------------------------------------------- #

_NEXT_STEP_MARKER = re.compile(r"(?m)^\s*NEXT_STEP:\s*plan=")
_DEFERRED_SCOPE_MARKER = re.compile(r"(?m)^\s*DEFERRED_SCOPE:\s*plan=")
_EXPLICIT_NEGATION = re.compile(
    r"\b(?:no\s+follow[- ]?ups?"
    r"|nothing\s+deferred"
    r"|no\s+(?:residual|remaining|pending)\s+work"
    r"|no\s+next\s+steps?)\b",
    re.IGNORECASE,
)


# --------------------------------------------------------------------- #


def _keyword_hits(text: str) -> list[str]:
    lower = text.lower()
    return [kw for kw in _FOLLOWUP_KEYWORDS if kw in lower]


def _bullets_under_followup_heading(text: str) -> int:
    """Count bullet items that appear in the 30 lines after any followup heading."""
    count = 0
    for match in _FOLLOWUP_HEADINGS.finditer(text):
        # Extract ~30 lines after the heading; cap the slice to bound work
        start = match.end()
        slice_end = start + 3000
        section = text[start:slice_end]
        # Stop at next heading (same or higher level)
        next_heading = re.search(r"(?m)^\s{0,3}#{1,6}\s+\S", section)
        if next_heading:
            section = section[: next_heading.start()]
        count += len(_BULLET_ITEM.findall(section))
    return count


def _compute_miss_score(text: str) -> tuple[int, dict[str, Any]]:
    """Return (score, report). Higher score = more likely a miss."""
    score = 0
    signals: list[str] = []

    # Anti-signal short-circuit: any NEXT_STEP marker = not a miss
    ns_hits = _NEXT_STEP_MARKER.findall(text)
    if ns_hits:
        return 0, {
            "positive_signals": [],
            "anti_signal": "next_step_marker_present",
            "next_step_marker_count": len(ns_hits),
        }

    # Related-marker anti-signal: DEFERRED_SCOPE counts too (same discipline)
    ds_hits = _DEFERRED_SCOPE_MARKER.findall(text)
    if ds_hits:
        return 0, {
            "positive_signals": [],
            "anti_signal": "deferred_scope_marker_present",
            "deferred_scope_marker_count": len(ds_hits),
        }

    # Explicit negation = author affirmed "nothing deferred"
    if _EXPLICIT_NEGATION.search(text):
        return 0, {
            "positive_signals": [],
            "anti_signal": "explicit_negation",
        }

    # Positive signal 1: followup-class heading present
    heading_matches = _FOLLOWUP_HEADINGS.findall(text)
    if heading_matches:
        score += 2
        signals.append(f"followup_heading:{len(heading_matches)}")

    # Positive signal 2: bullets enumerated under a followup heading
    bullets = _bullets_under_followup_heading(text)
    if bullets >= 3:
        score += 2
        signals.append(f"bullets_under_heading:{bullets}")
    elif bullets >= 1:
        score += 1
        signals.append(f"bullets_under_heading:{bullets}")

    # Positive signal 3: follow-up keyword density
    kws = _keyword_hits(text)
    if len(kws) >= 3:
        score += 2
        signals.append(f"keywords:{len(kws)}")
    elif len(kws) >= 1:
        score += 1
        signals.append(f"keywords:{len(kws)}")

    return score, {
        "positive_signals": signals,
        "keywords_hit": kws,
        "followup_heading_count": len(heading_matches),
        "bullets_under_heading": bullets,
    }


def _append_miss_record(record: dict) -> None:
    try:
        MISS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with MISS_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:  # guardian: allow-silent-swallow -- miss audit log: non-fatal, fail-open
        pass


def main() -> int:
    try:
        raw = sys.stdin.read(MAX_RESPONSE_BYTES + 1)
    except OSError:
        return 0
    if not raw.strip():
        return 0
    if len(raw) > MAX_RESPONSE_BYTES:
        raw = raw[:MAX_RESPONSE_BYTES]

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        payload = {"response_text": raw}

    if not isinstance(payload, dict):
        return 0

    text = (
        payload.get("response_text")
        or payload.get("text")
        or payload.get("content")
        or (payload.get("tool_info") or {}).get("response_text")
        or ""
    )
    if not text or not isinstance(text, str):
        return 0

    score, report = _compute_miss_score(text)
    if score < MISS_SCORE_THRESHOLD:
        return 0

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "cascade_id": payload.get("cascade_id") or payload.get("session_id"),
        "miss_score": score,
        "threshold": MISS_SCORE_THRESHOLD,
        "signals": report.get("positive_signals", []),
        "keywords_hit": report.get("keywords_hit", []),
        "followup_heading_count": report.get("followup_heading_count", 0),
        "bullets_under_heading": report.get("bullets_under_heading", 0),
        "response_excerpt": text[:500],
    }
    _append_miss_record(record)

    print(
        f"[next_step_miss_detector] ADVISORY miss_score={score} signals={report.get('positive_signals', [])}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
