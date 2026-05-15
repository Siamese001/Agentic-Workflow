#!/usr/bin/env python3
"""
pre_user_prompt_author_gate_reminder.py — Author-Gate pipeline reminder gate.

Fires on every pre_user_prompt event. Two detection paths:

PATH A — Prompt signals (proactive):
    Scans the incoming prompt text for Author-Gate context keywords. When ≥2
    signals match, emits AUTHOR_GATE_PIPELINE_REMINDER so Cursor Agent sees the
    canonical pipeline before composing its response.

PATH B — Recent violation replay (reactive):
    Reads the last N rows of author_gate_ui_violations.jsonl. When a recent
    violation (within REPLAY_WINDOW_MINUTES) is present, emits a targeted
    AUTHOR_GATE_VIOLATION_REPLAY block citing the violation type and re-stating
    the correct pipeline step that was skipped.

Both paths are independent; either can fire in the same turn.

Exit codes:
    0 = always (this hook is informational; it NEVER blocks the prompt chain)

CONSTITUTIONAL
    - No shell=True, no PowerShell
    - subprocess.run with timeout=30 where applicable
    - Specific exceptions only; no bare except
    - UTF-8 stdio
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
VIOLATIONS_PATH = REPO_ROOT / "artifacts" / "cursor" / "author_gate_ui_violations.jsonl"
ASK_VIOLATIONS_PATH = REPO_ROOT / "artifacts" / "cursor" / "ask_user_question_packet_violations.jsonl"

REPLAY_WINDOW_MINUTES = int(os.environ.get("AG_REMINDER_REPLAY_WINDOW_MINUTES", "120"))
MAX_VIOLATIONS_SCAN = 50
BYPASS_ENV = "AG_REMINDER_BYPASS"

PIPELINE_REMINDER = """\
AUTHOR_GATE_PIPELINE_REMINDER: The canonical Author-Gate pipeline is:
  1. skill(refactor-decision-memory)     -- consult historical precedent
  2. skill(author-gate-packet-builder)   -- emit AUTHOR_GATE_PACKET: block
  3. skill(author-gate-ui-renderer)      -- render recommendation card + OPTIONS_JSON
  4. ask_user_question(options=OPTIONS_JSON)

FORBIDDEN: hand-crafting ask_user_question options without steps 1-3.
REQUIRED FORMAT for each surfaced option description:
  [RECOMMENDED ⭐ confidence=0.NN]  OR  [confidence=0.NN]
  followed by · trade-off: <≥20-char tradeoff text>

Skills to invoke (in order):
  skill("refactor-decision-memory")
  skill("author-gate-packet-builder")
  skill("author-gate-ui-renderer")
"""

AG_CONTEXT_SIGNALS: list[str] = [
    "author-gate",
    "author gate",
    "AUTHOR_GATE",
    "author_gate",
    "ask_user_question",
    "hitl",
    "HITL",
    "refactoring scope",
    "architecture choice",
    "anti-pattern",
    "dependency add",
    "deletion strategy",
    "test strategy",
    "error handling",
    "confidence score",
    "dominance",
    "refactor-decision-memory",
    "author-gate-packet-builder",
    "author-gate-ui-renderer",
    "AUTHOR_GATE_PACKET",
    "HITL_PACKET",
]

VIOLATION_REMEDIATION: dict[str, str] = {
    "missing_confidence_prefix": (
        "Invariant 1 violated: option description missing [confidence=0.NN] prefix. "
        "Invoke skill(author-gate-ui-renderer) to get OPTIONS_JSON with correct prefixes."
    ),
    "multiple_stars": (
        "Invariant 2 violated: multiple ⭐ stars in options. "
        "Only the dominant option (score ≥0.85, gap ≥0.12) gets a star. "
        "Re-run skill(author-gate-packet-builder) to let routing rules decide."
    ),
    "star_without_recommended_routing": (
        "Invariant 3 violated: ⭐ star present but routing verdict is not RECOMMENDED. "
        "Do not manually add ⭐ — let the emitter set it based on dominance rule."
    ),
    "description_missing_tradeoff": (
        "Invariant 4 violated: option description missing · trade-off: <text> segment. "
        "Invoke skill(author-gate-packet-builder) — it sets surface_description_floor "
        "with the tradeoff segment automatically from key_tradeoffs[0]."
    ),
    "handcrafted_author_gate_detected": (
        "Pipeline bypass detected: ask_user_question called without AUTHOR_GATE_PACKET block. "
        "REQUIRED: invoke skill(refactor-decision-memory) → skill(author-gate-packet-builder) "
        "→ skill(author-gate-ui-renderer) BEFORE ask_user_question."
    ),
    "ask_user_question_without_packet": (
        "Pipeline bypass detected: ask_user_question called without AUTHOR_GATE_PACKET block. "
        "REQUIRED: invoke skill(refactor-decision-memory) → skill(author-gate-packet-builder) "
        "→ skill(author-gate-ui-renderer) BEFORE ask_user_question."
    ),
    "ask_user_question_without_packet_high_density": (
        "HIGH-DENSITY bypass: ask_user_question called multiple times without any "
        "AUTHOR_GATE_PACKET block in the response. "
        "REQUIRED: invoke the full Author-Gate pipeline for EVERY decision point."
    ),
    "prose_options_menu": (
        "Markdown prose option menus are not Author-Gate. "
        "Use refactor-decision-memory -> author-gate-packet-builder -> "
        "author-gate-ui-renderer -> ask_user_question, or continue execution "
        "if no genuine decision exists."
    ),
}


def _count_prompt_signals(prompt_text: str) -> int:
    """Count how many AG context signal strings appear in the prompt."""
    count = 0
    lower = prompt_text.lower()
    for sig in AG_CONTEXT_SIGNALS:
        if sig.lower() in lower:
            count += 1
    return count


def _read_recent_violations(path: Path, window_minutes: int) -> list[dict[str, Any]]:
    """Read last MAX_VIOLATIONS_SCAN rows; return those within the replay window."""
    if not path.exists():
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    for line in lines[-MAX_VIOLATIONS_SCAN:]:
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts_raw = row.get("timestamp", "")
        try:
            ts = datetime.fromisoformat(ts_raw)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            continue
        if ts >= cutoff:
            rows.append(row)
    return rows


def main() -> int:
    if os.environ.get(BYPASS_ENV):
        return 0

    prompt_text = ""
    if not sys.stdin.isatty():
        try:
            prompt_text = sys.stdin.read(16_384)
        except OSError:
            pass

    fired = False

    prompt_signal_count = _count_prompt_signals(prompt_text)
    if prompt_signal_count >= 2:
        print(
            f"\nAG_REMINDER_PATH_A: prompt_signals={prompt_signal_count} "
            f"(threshold=2) → emitting pipeline reminder",
            file=sys.stderr,
        )
        print(PIPELINE_REMINDER, file=sys.stderr)
        fired = True

    recent_ui = _read_recent_violations(VIOLATIONS_PATH, REPLAY_WINDOW_MINUTES)
    recent_ask = _read_recent_violations(ASK_VIOLATIONS_PATH, REPLAY_WINDOW_MINUTES)
    recent_all = recent_ui + recent_ask

    bypass_violations = [
        v for v in recent_all
        if v.get("violation_type") in (
            "handcrafted_author_gate_detected",
            "ask_user_question_without_packet",
            "ask_user_question_without_packet_high_density",
        )
    ]
    ui_violations = [
        v for v in recent_ui
        if v.get("violation_type") not in (
            "handcrafted_author_gate_detected",
        )
        and v.get("violation_type") in VIOLATION_REMEDIATION
    ]

    if bypass_violations:
        print(
            f"\nAG_REMINDER_PATH_B: recent_bypass_violations={len(bypass_violations)} "
            f"(window={REPLAY_WINDOW_MINUTES}m) → replaying remediation",
            file=sys.stderr,
        )
        seen_types: set[str] = set()
        for v in bypass_violations[-3:]:
            vtype = v.get("violation_type", "unknown")
            if vtype in seen_types:
                continue
            seen_types.add(vtype)
            remediation = VIOLATION_REMEDIATION.get(vtype, f"violation_type={vtype}")
            ts = v.get("timestamp", "?")
            print(
                f"AUTHOR_GATE_VIOLATION_REPLAY: type={vtype} at={ts}\n"
                f"  → {remediation}",
                file=sys.stderr,
            )
        if not fired:
            print(PIPELINE_REMINDER, file=sys.stderr)
        fired = True

    if ui_violations:
        print(
            f"\nAG_REMINDER_PATH_B_UI: recent_ui_violations={len(ui_violations)} "
            f"(window={REPLAY_WINDOW_MINUTES}m)",
            file=sys.stderr,
        )
        seen_types = set()
        for v in ui_violations[-3:]:
            vtype = v.get("violation_type", "unknown")
            if vtype in seen_types:
                continue
            seen_types.add(vtype)
            remediation = VIOLATION_REMEDIATION.get(vtype, f"violation_type={vtype}")
            ts = v.get("timestamp", "?")
            print(
                f"AUTHOR_GATE_UI_REPLAY: type={vtype} at={ts}\n"
                f"  → {remediation}",
                file=sys.stderr,
            )
        fired = True

    if fired:
        print(
            "AG_REMINDER_SUMMARY: Canonical skills = "
            "refactor-decision-memory → author-gate-packet-builder → author-gate-ui-renderer → ask_user_question",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
