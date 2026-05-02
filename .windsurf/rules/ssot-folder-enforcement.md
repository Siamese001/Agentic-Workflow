---
trigger: always_on
description: SSOT folder routing — every NEW Python file must land in its canonical folder. scripts/, repo-root, tools/_oneoff/, tools/_oneshot/ are forbidden for new files. Hook scripts MUST live in .windsurf/scripts/. Constitutional §31.
---

# SSOT Folder Routing — New Files Land in Canonical Folders

> ⛔ **Every NEW Python file MUST be written into its canonical SSOT folder.** Pre-existing files are unaffected — the gate only catches new files.

## The Canonical Taxonomy

| File purpose | Filename pattern | Canonical SSOT folder |
|---|---|---|
| CI gate / pre-commit check | `check_*.py`, `*_gate.py`, `validate_*.py` | `ops_scripts/ci/` |
| Calibration / weekly report / ledger binder | `*_calibration.py`, `*_binder.py`, `*_poller.py`, `*_weekly_report.py` | `ops_scripts/calibration/` |
| Maintenance / cleanup | `purge_*.py`, `cleanup_*.py` | `ops_scripts/maintenance/` |
| Windsurf hook script | `pre_*_*.py`, `post_*_*.py` (matching `.windsurf/hooks.json`) | `.windsurf/scripts/` |
| Cascade-invoked utility | other | `tools/<domain>/` |
| Plan | `<slug>-<6hex>.md` | `.windsurf/plans/` (enforced by `plan-location.md`) |
| Report / evidence | `.md` | `docs/reports/` (enforced by `validate_report_location.py`) |

## Forbidden New-File Roots

| Root | Why forbidden | Allowlist |
|---|---|---|
| `scripts/<name>.py` | Legacy tier-verify entrypoint folder | `verify_tier\d+_(enforcement\|runtime_proof)_gate.py`, `verify_all_requirements_*.py`, `verify_tier_gate_hardening.py`, `c0_evidence_harness.py`, `scripts/proof/**` |
| Repo-root `<name>.py` | Top-level Python files clutter the workspace | `conftest.py` only |
| `tools/_oneoff/`, `tools/_oneshot/` | Tombstoned scratch folders | (none) |
| Hook-prefix file outside `.windsurf/scripts/` | Hooks discovered relative to that folder; misroute = silent disable | (none) |

## Forbidden Patterns

- ❌ `write_to_file` to `scripts/check_foo.py` — must be `ops_scripts/ci/check_foo.py`
- ❌ `write_to_file` to `scripts/post_cascade_bar.py` — must be `.windsurf/scripts/post_cascade_bar.py`
- ❌ `write_to_file` to `weekly_report.py` at repo root — must be `ops_scripts/calibration/weekly_report.py`
- ❌ `write_to_file` to `tools/_oneoff/cleanup.py` — must be `ops_scripts/maintenance/cleanup.py`

## Bypass

`SSOT_FOLDER_BYPASS=1` env var — emits a `WARNING:` line and lets the write proceed. Use only for allowlisted legacy archetypes or scripted batch runs with operator approval.

## Enforcement Layers

1. **This rule** (always-on — advisory)
2. **`.windsurf/scripts/_ssot_folder_check.py`** (helper — pure logic)
3. **`.windsurf/scripts/pre_write_gate.py`** (Windsurf hook — fail-closed at write time)
4. **`ops_scripts/ci/check_ssot_folder_routing.py`** (pre-commit `T7q` — fail-closed at commit time)
5. **Tests:** `tests/unit/windsurf_scripts/test_ssot_folder_check.py`

Constitutional rule §31. Sibling: `plan-location.md`. Same pattern: pure helper, two consumers (hook + CI), bypass env var, durable logging.
