#!/usr/bin/env python3
"""
pre_user_prompt_deferred_plan_gate.py — Surface blocked deferred-scope plans.

Hook: pre_user_prompt (show_output=true, so Cursor Agent sees the output).

Scans .windsurf/plans/*.md for files that carry a DO_NOT_IMPLEMENT_GUARD:
marker, meaning the plan was explicitly written as a deferred-scope holding
plan that requires a separate Author-Gate decision before any wave execution.

When such plans exist, emits one line per plan:

    DEFERRED_PLAN_BLOCKED: plan=<slug> reason=<short>

Cursor Agent MUST treat this signal as an execution block — it must NOT call
wave_execution_state.py start or begin implementing waves for a blocked plan
without first surfacing an Author-Gate decision to the user.

Fail policy: OPEN. Never blocks the turn itself. The output is a soft signal
that Cursor Agent reads at the top of its context. The hard enforcement is the
Author-Gate pipeline (constitutional §6, §35).

Bypass: DEFERRED_PLAN_GATE_BYPASS=1.

Root cause this addresses (RCA 2026-05-10): plan
notion-test-hardening-deferred-scope-a7b4c9 contained explicit "do not
implement without Author-Gate" prose. Cursor Agent ignored it, executed waves
W1/W2/W7 without calling wave_execution_state.py start, leaving Notion at
Not Started. Machine-readable guard markers + this hook make the block
visible at every turn instead of relying on prose Cursor Agent can skip.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLANS_DIR = REPO_ROOT / ".windsurf" / "plans"

# Machine-readable guard marker that plan authors must add to deferred-scope plans.
_GUARD_RE = re.compile(
    r"^\s*DO_NOT_IMPLEMENT_GUARD\s*:\s*(?P<body>.+?)\s*$",
    re.MULTILINE,
)

# Fallback: detect prose patterns that imply a guard even without the marker.
# Used to warn about plans that need the marker added.
_PROSE_GUARD_RE = re.compile(
    r"(?:should not|must not|do not|without)\s+be\s+implemented\s+without"
    r"|nothing\s+here\s+should\s+be\s+implemented\s+without"
    r"|do\s+not\s+implement\s+without",
    re.IGNORECASE,
)


def _extract_guard_reason(text: str) -> str | None:
    """Return the first DO_NOT_IMPLEMENT_GUARD: reason, or None."""
    m = _GUARD_RE.search(text)
    if m:
        body = m.group("body").strip()
        # Extract reason= field if present
        reason_m = re.search(r"reason=(.+?)(?:\s+\w+=|$)", body)
        if reason_m:
            return reason_m.group(1).strip()[:120]
        return body[:120]
    return None


def _has_prose_guard(text: str) -> bool:
    """True when plan contains "do not implement without" prose (no marker)."""
    return bool(_PROSE_GUARD_RE.search(text))


def _slug_from_path(p: Path) -> str:
    return p.stem


def _scan_plans() -> list[tuple[str, str, bool]]:
    """
    Return list of (slug, reason, has_marker) for plans with a guard.

    has_marker=True  → has DO_NOT_IMPLEMENT_GUARD: marker (canonical)
    has_marker=False → only has prose guard (needs marker added)
    """
    if not PLANS_DIR.exists():
        return []
    results: list[tuple[str, str, bool]] = []
    try:
        paths = sorted(PLANS_DIR.glob("*.md"))
    except OSError:
        return []
    for p in paths:
        if p.name.startswith("_"):
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        reason = _extract_guard_reason(text)
        if reason is not None:
            results.append((_slug_from_path(p), reason, True))
        elif _has_prose_guard(text):
            results.append((
                _slug_from_path(p),
                "prose guard present — add DO_NOT_IMPLEMENT_GUARD: marker",
                False,
            ))
    return results


def main() -> int:
    if os.environ.get("DEFERRED_PLAN_GATE_BYPASS") == "1":
        return 0

    guarded = _scan_plans()
    if not guarded:
        return 0

    for slug, reason, has_marker in guarded:
        tag = "DEFERRED_PLAN_BLOCKED" if has_marker else "DEFERRED_PLAN_PROSE_GUARD"
        print(f"{tag}: plan={slug} reason={reason}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
