---
trigger: always_on
description: SSOT folder routing — every NEW Python file must land in its canonical folder. scripts/, repo-root, tools/_oneoff/, tools/_oneshot/ are forbidden for new files. Hook scripts MUST live in .windsurf/scripts/. Constitutional §31.
---

# SSOT Folder Routing — New Files Land in Canonical Folders

> ⛔ **Every NEW Python file MUST be written into its canonical SSOT folder.**
> Pre-existing files are unaffected — the gate only catches new files. The
> rule exists because Cascade has historically dropped files into
> `scripts/` (legacy tier-verify wrappers) and repo-root when they belonged
> in `ops_scripts/` or `.windsurf/scripts/`.

## The Canonical Taxonomy

| File purpose | Filename pattern | Canonical SSOT folder |
|---|---|---|
| CI gate / pre-commit check | `check_*.py`, `*_gate.py`, `validate_*.py` | `ops_scripts/ci/` |
| Calibration / weekly report / ledger binder | `*_calibration.py`, `*_binder.py`, `*_poller.py`, `*_weekly_report.py` | `ops_scripts/calibration/` |
| Maintenance / cleanup | `purge_*.py`, `cleanup_*.py` | `ops_scripts/maintenance/` |
| Windsurf hook script | `pre_*_*.py`, `post_*_*.py` (matching the hook chain in `.windsurf/hooks.json`) | `.windsurf/scripts/` |
| Cascade-invoked utility | other | `tools/<domain>/` |
| Plan | `<slug>-<6hex>.md` | `.windsurf/plans/` (enforced separately by `plan-location.md`) |
| Report / evidence | `.md` | `docs/reports/` (enforced separately by `validate_report_location.py`) |

## Forbidden New-File Roots

| Root | Why forbidden | Allowlist (kept for legacy entrypoints) |
|---|---|---|
| `scripts/<name>.py` | Legacy tier-verify entrypoint folder; not the canonical home for new utilities | `verify_tier\d+_(enforcement\|runtime_proof)_gate.py`, `verify_all_requirements_*.py`, `verify_tier_gate_hardening.py`, `c0_evidence_harness.py`, `scripts/proof/**` |
| Repo-root `<name>.py` | Top-level Python files clutter the workspace and bypass package boundaries | `conftest.py` only |
| `tools/_oneoff/`, `tools/_oneshot/` | Tombstoned scratch folders; new durable utilities must not land here | (none) |
| Hook-prefix file outside `.windsurf/scripts/` | Hooks defined in `.windsurf/hooks.json` are discovered relative to that folder; misrouted hook scripts go dark | (none) |

## How the Gate Decides

`.windsurf/scripts/_ssot_folder_check.py` is the SSOT logic. Two clients call it:

1. **`pre_write_gate.py`** (Windsurf `pre_write_code` hook) — blocks NEW
   file writes that violate routing, exit 2 with the canonical target
   suggestion in the error message.
2. **`ops_scripts/ci/check_ssot_folder_routing.py`** (pre-commit hook
   `T7q: SSOT Folder Routing`) — fails commits that introduce NEW files
   under any forbidden root. Pre-existing files are not flagged.

Both clients use the SAME helper, so behavior matches between the
in-session author-time gate and the commit-time gate. No drift.

## Bypass

`SSOT_FOLDER_BYPASS=1` environment variable — emits a `WARNING:` line
and lets the write proceed. Use only when:

- An allowlisted legacy archetype is being added (e.g., another
  `verify_tier7_enforcement_gate.py`) and the regex predates the new path,
- A scripted batch run is intentionally creating files outside the SSOT
  taxonomy with operator approval.

Each bypass is durable in stderr output for review.

## Forbidden Patterns

- ❌ `write_to_file` to `scripts/check_foo.py` — must be `ops_scripts/ci/check_foo.py`
- ❌ `write_to_file` to `scripts/post_cascade_bar.py` — must be `.windsurf/scripts/post_cascade_bar.py`
- ❌ `write_to_file` to `weekly_report.py` at repo root — must be `ops_scripts/calibration/weekly_report.py`
- ❌ `write_to_file` to `tools/_oneoff/cleanup.py` — must be `ops_scripts/maintenance/cleanup.py`
- ❌ Renaming an in-place existing file does NOT count as creating a new file at the destination — but creating a new file in the forbidden root, even if it shares a name with a moved file, is blocked

## Why This Exists

**Failure precedent (2026-04-30)**: Cascade authored
`scripts/<some-utility>.py` for what was effectively a CI gate.
The file should have been `ops_scripts/ci/<some-utility>.py`. The
distinction matters because:

- `ops_scripts/ci/` is the canonical home for CI gates — listed in
  `.pre-commit-config.yaml`, run by `run_contract_gates.py`, referenced by
  the constitutional rules (§4).
- `scripts/` is the legacy folder for tier-verify entrypoints
  (`verify_tier*_gate.py`, `c0_evidence_harness.py`); not the place for
  new check scripts.
- Without enforcement, this drift compounds — every session adds another
  misrouted file, the SSOT taxonomy degrades, and the legacy folder
  becomes indistinguishable from the canonical one.

The rule is fail-closed (block NEW files, exit 2) precisely because the
soft-warning approach has not held up in practice.

## Enforcement Layers

1. **This rule** (always-on — advisory) tells Cascade the invariant
2. **`.windsurf/scripts/_ssot_folder_check.py`** (helper — pure logic)
3. **`.windsurf/scripts/pre_write_gate.py`** (Windsurf hook — fail-closed at write time)
4. **`ops_scripts/ci/check_ssot_folder_routing.py`** (pre-commit `T7q` — fail-closed at commit time)
5. **Tests**: `tests/unit/windsurf_scripts/test_ssot_folder_check.py`

## Constitutional Tie-In

Constitutional rule §31 codifies this invariant. See `constitutional.md`.
Sibling rules: `plan-location.md` (plans only land in `.windsurf/plans/`),
`memory-notion-writeback.md` (writeback discipline). Same pattern: a
pure helper, two consumers (hook + CI), a bypass env var, durable logging.
