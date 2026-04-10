# Hook Scripts — Agent Guidance

## Directory Purpose

`ops_scripts/hooks/` contains Python scripts invoked by Windsurf hooks (`.windsurf/hooks.json`)
and CI gates. These are **not** Windsurf rules — they are executed scripts.

## Scripts in This Directory

| Script | Hook Event | Role |
|--------|-----------|------|
| `adg_unified_gate.py` | pre_write_code (via gate) | ADG layer-boundary and import-hygiene enforcement |
| `adg_autofix_hook.py` | CI | Automated ADG anti-pattern fix suggestions |
| `adg_suggest_hook.py` | CI | ADG refactor suggestions |
| `validate_report_location.py` | CI | Enforce plan/report SSOT paths |
| `windsurf_plan_ci.py` | CI | Plan location CI gate |
| `reject_tracked_generated_artifacts.py` | pre-commit | Block generated artifacts from git |

## Windsurf Hook Scripts

The primary Windsurf hook scripts live in `.windsurf/scripts/`, not here. See:
- `.windsurf/hooks.json` — hook wiring
- `.windsurf/scripts/` — all hook implementations

## Refactor Decision Capture

The `post_cascade_response` hook runs `.windsurf/scripts/post_cascade_hitl_capture.py`,
which detects surfaced HITL decision packets and writes to the decision ledger at:
`.windsurf/state/refactor_decisions/refactor_decision_ledger.sqlite`

This is advisory — the hook always exits 0 and never blocks.

## Constitutional Constraints

- All scripts must use `subprocess.run(argv, shell=False, timeout=30)`
- All scripts must exit 0 on error (advisory, never blocking)
- No PowerShell
- Specific exception types only — no bare `except Exception` without guardian comment
