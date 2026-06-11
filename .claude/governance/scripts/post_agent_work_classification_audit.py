"""Post-agent work-classification audit (Stop chain, Operating Model 2026-06-10).

Scans the agent response for plan-creation reflexes on sub-threshold work and
logs violations to artifacts/governance/work_classification_violations.jsonl.

A "reflex" is when the agent proposes or creates a plan artifact for work that
should have been classified as BUG_IMMEDIATE, BUG_DEFERRED, FINDING_APPS_RG,
PLAN_MICRO, or ENHANCEMENT_BACKLOG — all of which should never produce a new
plans/*.md file or a Notion Plans DB row.

Fail-open: exit 0 always. Never blocks the response.

Bypass: WORK_CLASSIFICATION_AUDIT_BYPASS=1
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
VIOLATIONS_FILE = REPO_ROOT / "artifacts" / "governance" / "work_classification_violations.jsonl"

# ─── Reflex patterns ──────────────────────────────────────────────────────────
# Phrases that suggest the agent is creating a new plan when it shouldn't.
_REFLEX_PATTERNS: list[tuple[re.Pattern, str]] = [
    (
        re.compile(
            r"(?i)(?:I['']ll|I will|let me|going to|will now)\s+"
            r"(?:create|write|mint|make)\s+(?:a\s+)?(?:new\s+)?plan(?:\s+file)?",
        ),
        "plan-creation intent phrase",
    ),
    (
        re.compile(r"(?i)(?:creating|writing|minting)\s+(?:a\s+)?(?:new\s+)?plan\s+(?:file|document|for)\b"),
        "plan-creation action phrase",
    ),
    (
        re.compile(r"plans/[a-z][a-z0-9_-]+-[0-9a-f]{6}\.md", re.IGNORECASE),
        "new plan slug reference",
    ),
    (
        re.compile(r"(?i)PLAN_CREATED:\s+plan="),
        "PLAN_CREATED marker without PLAN_MINT_OK",
    ),
]

# ─── Suppression patterns ─────────────────────────────────────────────────────
# If any of these appear, the reflex detection is suppressed (user authorized or
# the agent is correctly routing to the backlog / spawn_task / native plan mode).
_SUPPRESSION_PATTERNS: list[re.Pattern] = [
    re.compile(r"PLAN_MINT_OK=1"),
    re.compile(r"(?i)existing\s+plan"),
    re.compile(r"(?i)master\s+gap\s+inventory"),
    re.compile(r"(?i)\bspawn_task\b"),
    re.compile(r"(?i)backlog.*row|row.*backlog"),
    re.compile(r"(?i)EnterPlanMode|native\s+plan\s+mode"),
    re.compile(r"(?i)PLAN_MINT_OK"),
    re.compile(r"(?i)user\s+(?:authorized|auth(?:orized)?|approved)\s+a?\s*(?:new\s+)?plan"),
]


def _extract_response(data: dict) -> str:
    """Pull response text from various Stop-hook payload shapes."""
    text = (
        data.get("response")
        or data.get("content")
        or data.get("text")
        or ""
    )
    if isinstance(text, list):
        text = " ".join(
            (block.get("text") or "") for block in text if isinstance(block, dict)
        )
    return str(text)


def _append_violation(violation: dict) -> None:
    try:
        VIOLATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with VIOLATIONS_FILE.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(violation, ensure_ascii=False) + "\n")
    except OSError:
        pass


def main() -> int:
    try:
        if os.environ.get("WORK_CLASSIFICATION_AUDIT_BYPASS", "").strip().lower() in (
            "1", "true", "yes",
        ):
            return 0

        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
        response_text = _extract_response(data)

        if not response_text.strip():
            return 0

        # Check suppression first — any approved pattern ends the check.
        if any(p.search(response_text) for p in _SUPPRESSION_PATTERNS):
            return 0

        # Scan for reflex patterns.
        for pat, label in _REFLEX_PATTERNS:
            m = pat.search(response_text)
            if m:
                start = max(0, m.start() - 80)
                end = min(len(response_text), m.end() + 80)
                excerpt = response_text[start:end].strip()

                violation = {
                    "ts_utc": datetime.now(timezone.utc).isoformat(),
                    "kind": "plan_creation_reflex",
                    "label": label,
                    "pattern": pat.pattern,
                    "match": m.group(),
                    "excerpt": excerpt,
                    "remedy": (
                        "Classify work before creating plan artifacts. "
                        "BUG_IMMEDIATE → fix directly. "
                        "BUG_DEFERRED / ENHANCEMENT_BACKLOG → spawn_task. "
                        "FINDING_APPS_RG → Master Gap Inventory row. "
                        "PLAN_MICRO (single session, <2 waves) → native plan mode only, no disk file, no Notion. "
                        "Multi-wave plan only if user authorized (PLAN_MINT_OK=1). "
                        "Rule: .claude/rules/work-item-classification.md"
                    ),
                }
                _append_violation(violation)

                print(
                    f"[work-classification] plan-reflex: {label!r} — "
                    f"matched {m.group()!r}. "
                    "Classify work first; see .claude/rules/work-item-classification.md",
                    file=sys.stderr,
                )
                # One violation per response is sufficient.
                break

        return 0

    except Exception:  # guardian: allow-broad-exception -- hook fail-soft contract
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
