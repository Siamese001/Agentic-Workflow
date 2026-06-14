"""Post-agent work-classification audit (Stop chain, Operating Model 2026-06-10).

Scans the agent response and logs violations to
artifacts/governance/work_classification_violations.jsonl. Two complementary checks:

  1. OVER-planning (``plan_creation_reflex``) — proposing/creating a plan artifact for
     sub-threshold work (BUG_IMMEDIATE / BUG_DEFERRED / FINDING_APPS_RG / PLAN_MICRO /
     ENHANCEMENT_BACKLOG), which should never produce a new plans/*.md file.

  2. UNDER-persisting (``missing_plan_persistence``, plan-persistence-discipline 2026-06-14) —
     genuinely multi-wave EXECUTION that left no minted plans/<slug>-<6hex>.md SSOT plan.
     Per work-item-classification, ≥2 waves (or a large/cross-layer change) must mint a disk
     plan at the start; native plan mode persists nothing durable (RCA: ADR-104).

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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _post_agent_payload import extract_response_text  # noqa: E402

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


# ─── Unpersisted multi-wave detection (RCA fix #3, plan-persistence-discipline) ──
# The INVERSE of the reflex check: flag genuinely multi-wave EXECUTION that left no
# minted plans/<slug>-<6hex>.md SSOT record — the gap from ADR-104 (a 7-wave T3 change
# ran entirely in native plan mode and persisted nothing to the repo SSOT). Advisory.
_WAVE_MARKER_RE = re.compile(r"(?:\bW|\bWave\s+)([1-9][0-9]?)\b", re.IGNORECASE)
_EXECUTION_EVIDENCE_RE = re.compile(
    r"(?i)FILES_CHANGED|STATUS:\s*(?:PASS|PARTIAL|FAIL)|\bcommitt?ed\b|\bpushed\b|✅"
)
_MINTED_PLAN_RE = re.compile(r"plans/[a-z0-9][a-z0-9_-]*-[0-9a-f]{6}\.md", re.IGNORECASE)


def _detect_unpersisted_multiwave(text: str) -> int | None:
    """Count distinct waves when the response shows multi-wave EXECUTION but
    references no minted SSOT plan; else None (no gap).

    Suppressed when: a `plans/<slug>-<6hex>.md` is referenced (plan was persisted),
    `PLAN_MINT_OK` appears (user authorized / minting in progress), or there is no
    execution evidence (pure planning/discussion, not a completed multi-wave run).
    """
    if _MINTED_PLAN_RE.search(text):
        return None
    if "PLAN_MINT_OK" in text:
        return None
    if not _EXECUTION_EVIDENCE_RE.search(text):
        return None
    distinct = {int(m.group(1)) for m in _WAVE_MARKER_RE.finditer(text)}
    return len(distinct) if len(distinct) >= 2 else None


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

        response_text = extract_response_text(sys.stdin.read())

        if not response_text.strip():
            return 0

        # Check 1 (UNDER-persisting): genuinely multi-wave execution with no minted
        # SSOT plan. Independent of the reflex suppression below — native plan mode is
        # NOT a valid suppression here (it IS the gap). Advisory; never returns early.
        wave_count = _detect_unpersisted_multiwave(response_text)
        if wave_count is not None:
            _append_violation({
                "ts_utc": datetime.now(timezone.utc).isoformat(),
                "kind": "missing_plan_persistence",
                "distinct_waves": wave_count,
                "remedy": (
                    f"Response shows ~{wave_count}-wave execution but references no minted "
                    "plans/<slug>-<6hex>.md SSOT plan. Per work-item-classification, ≥2 waves "
                    "(or a large/cross-layer change) must mint a disk plan at the start — native "
                    "plan mode persists nothing durable. Rule: .claude/rules/work-item-classification.md"
                ),
            })
            print(
                f"[work-classification] missing_plan_persistence: ~{wave_count}-wave execution "
                "with no minted plans/<slug>-<6hex>.md — mint a disk SSOT plan for complex work. "
                "See .claude/rules/work-item-classification.md",
                file=sys.stderr,
            )

        # Check 2 (OVER-planning): plan-creation reflex on sub-threshold work.
        # Suppression first — any approved pattern ends THIS check.
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
