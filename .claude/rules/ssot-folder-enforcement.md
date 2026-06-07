
<!-- Converted from `.claude/rules/ssot-folder-enforcement.md`. Original Cursor trigger: `always_on`. -->

# SSOT Folder Routing — New Files Land in Canonical Folders

> ⛔ **Every NEW Python file MUST be written into its canonical SSOT folder.** Pre-existing files are unaffected — the gate only catches new files.

## The Canonical Taxonomy

| File purpose | Filename pattern | Canonical SSOT folder |
|---|---|---|
| CI gate / pre-commit check | `check_*.py`, `*_gate.py`, `validate_*.py` | `ops_scripts/ci/` |
| Calibration / weekly report / ledger binder | `*_calibration.py`, `*_binder.py`, `*_poller.py`, `*_weekly_report.py` | `ops_scripts/calibration/` |
| Maintenance / cleanup | `purge_*.py`, `cleanup_*.py` | `ops_scripts/maintenance/` |
| Claude Code hook script | `pre_*_*.py`, `post_*_*.py` (matching `.claude/settings.json`) | `.claude/governance/scripts/` |
| Claude Code-invoked utility | other | `tools/<domain>/` |
| Plan | `<slug>-<6hex>.md` | `plans/` (canonical; legacy `.claude/plans/` still valid — enforced by `plan-location.md`) |
| Report / evidence | `.md` | `docs/reports/` (enforced by `validate_report_location.py`) |

## Forbidden New-File Roots

- `scripts/<name>.py` — except allowlist (`verify_tier\d+_*_gate.py`, `verify_all_requirements_*.py`, `verify_tier_gate_hardening.py`, `c0_evidence_harness.py`, `scripts/proof/**`)
- Repo-root `<name>.py` — except `conftest.py`
- `tools/_oneoff/`, `tools/_oneshot/` — tombstoned
- Hook-prefix files (`pre_*_*.py`, `post_*_*.py`) outside `.claude/governance/scripts/` — misroute = silent disable

## Forbidden Patterns

- ❌ `scripts/check_foo.py` → `ops_scripts/ci/check_foo.py`
- ❌ `scripts/post_cursor_agent_bar.py` → `.claude/governance/scripts/post_cursor_agent_bar.py`

## Bypass

`SSOT_FOLDER_BYPASS=1` env var — emits a `WARNING:` line and lets the write proceed. Use only for allowlisted legacy archetypes or scripted batch runs with operator approval.

## Enforcement

Helper `_ssot_folder_check.py` → hook `pre_write_gate.py` (fail-closed) → CI gate `check_ssot_folder_routing.py` (T7q) → tests `test_ssot_folder_check.py`. Constitutional §31. Sibling: `plan-location.md`.
