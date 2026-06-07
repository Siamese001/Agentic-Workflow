"""One-shot bootstrap: emit 10 per-ledger consulting-skill SKILL.md files
from LEDGER_REGISTRY. Safe to re-run (skips existing files unless --force).

Usage:
    python -m tools.ledgers._bootstrap_skills          # create missing skills
    python -m tools.ledgers._bootstrap_skills --force  # overwrite existing
"""

from __future__ import annotations

import argparse
from pathlib import Path

from tools.ledgers.schema_registry import LEDGER_REGISTRY, REPO_ROOT

SKILLS_DIR = REPO_ROOT / ".cursor" / "skills"

TRIGGER_HINTS = {
    "tool_routing": "Any retrieval-class tool dispatch (grep, ADG query, semantic search, read_file).",
    "refactor_outcome": "Wave planning, refactor-scope Author-Gate decisions, hotspot queue ordering.",
    "prompt_classifier": "Prompt-tier prediction (T0/T1/T2/T3) in pre_prompt_classifier or SR_INTAKE.",
    "mcp_invocation": "Before any mcp* tool call on a latency-sensitive path (e.g., inside a hook).",
    "hotspot_defect": "Hotspot-first refactoring gate, impact-formula review, wave queue prioritization.",
    "deferred_scope_calibration": "DEFERRED_SCOPE marker emission, P-band assignment, scorer tuning.",
    "guardian_exemption": "Any new '# guardian: allow-*' comment; before approving Author-Gate exemption.",
    "progress_eta": "ProgressReporter init for a named operation; subprocess timeout calibration.",
    "memory_recall": "Session-start recall weighting; before requesting mem_recall_session_start.",
    "test_selection": "'/adg-test-triage-gate' invocation; selecting tests for a change-set.",
}

FILTER_HINTS = {
    "tool_routing": "retrieval_tool_choice",
    "refactor_outcome": "wave_prediction",
    "prompt_classifier": "tier_prediction",
    "mcp_invocation": "mcp_call",
    "hotspot_defect": "hotspot_prediction",
    "deferred_scope_calibration": "deferred_scope_capture",
    "guardian_exemption": "exemption_created",
    "progress_eta": "eta_predicted",
    "memory_recall": "entity_recalled",
    "test_selection": "triage_selection",
}


def _render(spec) -> str:
    skill_slug = f"ledger-consulter-{spec.name.replace('_', '-')}"
    trigger = TRIGGER_HINTS.get(spec.name, "See base template.")
    default_kind = FILTER_HINTS.get(spec.name, "")
    return f"""---
name: {skill_slug}
description: Consult the {spec.name} ledger for precedent before acting. {spec.purpose} Inherits the contract from `ledger-consulter`. Use when {trigger}
trigger: model_decision
---

# Ledger Consulter — {spec.name}

## Purpose

{spec.purpose}

Every row in `artifacts/ledgers/{spec.name}.sqlite` captures a prediction paired
with a later-bound outcome. Before committing to a new decision of this class,
look up precedent and bias the current choice accordingly.

## When To Invoke

{trigger}

## Minimal Query

```python
from tools.ledgers import LedgerConsulter

verdict = LedgerConsulter("{spec.name}").lookup(
    query_text="<current intent summary>",
    filters={{"event_kind": "{default_kind}"}},
    limit=5,
)
```

## Verdict → Action

| `verdict.strength` | Required behavior |
|---|---|
| `strong`       | Bias current decision toward precedent; note alignment in packet/plan. |
| `suggestive`   | Surface precedent in Author-Gate packet or plan body; do not auto-bias. |
| `none`         | State explicitly: `Precedent: ledger had no match (novel case).` |

## Wave / Sunset

- **Wave**: {spec.wave}
- **Writer hook**: `{spec.writer_hook}`
- **Sunset criterion**: {spec.sunset_criterion}

## See Also

- Base skill: `.claude/skills/ledger-consulter/SKILL.md`
- Writer API: `tools/ledgers/writer.py`
- Schema: `.cursor/schemas/{spec.schema_file}`
- Plan: `.cursor/plans/_archive/windsurf_legacy_plans/intelligence-ledgers-ten-a7c3e2.md`
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="overwrite existing skill files")
    args = parser.parse_args()

    created = 0
    skipped = 0
    for spec in LEDGER_REGISTRY:
        slug = f"ledger-consulter-{spec.name.replace('_', '-')}"
        skill_dir = SKILLS_DIR / slug
        skill_file = skill_dir / "SKILL.md"
        skill_dir.mkdir(parents=True, exist_ok=True)
        if skill_file.exists() and not args.force:
            skipped += 1
            continue
        skill_file.write_text(_render(spec), encoding="utf-8")
        created += 1
        print(f"  + {skill_file.relative_to(REPO_ROOT)}")

    print(f"[bootstrap_skills] created={created} skipped={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
