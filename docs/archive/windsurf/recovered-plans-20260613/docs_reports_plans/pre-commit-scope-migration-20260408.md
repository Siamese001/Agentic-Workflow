# Pre-Commit Scope Migration — Gap Analysis
**Date**: 2026-04-08  
**Purpose**: Every hook removed from pre-commit, where its enforcement belongs, and current coverage gaps

---

## Removed Hook Inventory

| Hook | What It Did | Scan Scope | Removal Reason |
|------|-------------|------------|----------------|
| T-1 pre-commit-summary-init | Set up reporting context for T21 | — | Removed with T21 |
| T4.5 adg-autofix | Auto-fixed P1/P2 antipatterns in Python | Whole repo | No scope filter |
| T5 adg-ci-gates | Ran ADG CI gate: generated ADG if relevant files changed | Staged + ADG dirs | Whole-ADG-gen in pre-commit |
| T5.5 windsurf-plan-ci | Validated `.windsurf/plans/*.md` plan format (headers, wave table, token estimates) | All `.windsurf/plans/` | Scanned full plans dir |
| T6.5 zero-loss-refactor-verifier | Detected hollow Python files after refactoring | Whole `agentic_core/` + `tools/generate/` | Full repo scan |
| T7 check-report-location | Validated `docs/` staged files against SSOT report location rules | Staged `docs/` files | Redundant / low value |
| T7.5 plan-location-gate | Blocked commits if plans were in wrong directory | Staged `.md` files | Location SSOT changed |
| T7.7 windsurf-governance-health | Cross-ref archived files, RULES_INDEX accuracy, duplicate content in `.windsurf/` | All `.windsurf/` | **Removed** from pre-commit and GHA (`windsurf-gha-cutover-d9f2a7`); script never re-homed |
| T7.9 adg-grep-ban-gate | Blocked staged `.py` using grep/rg as ADG substitutes | Staged Python | `always_run: true` was bypassing file filter |
| T7.10 no-unconditional-xfail-gate | Blocked `@pytest.mark.xfail` without `strict=True` | Staged Python | `always_run: true` without scope |
| T7.11 hitl-decision-record-gate | Blocked plan docs without `HITL_DECISION_RECORD` section | Staged plan `.md` | Low signal; plan format rarely wrong |
| T7.12 rca-closure-gate | Blocked RCA docs not marked `RESOLVED` | Staged RCA `.md` | Constitutional §7 covers this behaviorally |
| T7.13 check-no-archives-imports | Blocked imports from `archives/` in production code | Staged Python | `archives/` deleted; no longer relevant |
| T7.14 check-sensitive-logs | Warned if staged Python logged passwords/tokens | Staged Python | Warn-only; no clear remediation path |
| T8 reject-generated-artifacts | Rejected commits tracking generated files | git index scan | Resolved by `.gitignore` |
| T9 check-tooling-apps-boundary | `tools/` + `ops_scripts/ci` must not import `apps_*` | Staged Python | Scoped but rarely triggered |
| T10 module-collision-guard | Detected duplicate modules, case collisions, import path conflicts | Staged Python | Architectural check belongs in ADG |
| T10.7 adg-suggest-report | Surfaced ADG:HIGH suggest-fix issues for HITL review (warn-only) | Staged Python | Warn-only reporter; better in ADG report |
| T12 guardian-exemption-gate | Counted guardian comments; quality ratchet on exemption count | Staged Python | ADG burndown already tracks this |
| T14 adg-accelerator-compliance | Python grep ban + YAML grep ban in CI workflows | Staged Python + YAML | Merged with T7.9 |
| T21 pre-commit-summary-report | Aggregated all governance issues in a formatted table | — | Removed with its feeder hooks |

---

## Placement Decision Table

| Hook | Belongs In | Reason | Current Status |
|------|-----------|--------|----------------|
| T4.5 adg-autofix | `generate_full_adg.py` | `_run_p1_p2_auto_fix()` already exists | ✅ COVERED |
| T5 adg-ci-gates | `generate_full_adg.py` | Entire purpose of `generate_full_adg.py` | ✅ COVERED |
| T5.5 windsurf-plan-ci | Windsurf `pre_write_code` | Fires when Cursor Agent writes plan files; checks format before write | ❌ GAP |
| T6.5 zero-loss-refactor-verifier | `generate_full_adg.py` | Whole-repo hollow-file check is a post-generation integrity step | ❌ GAP |
| T7 check-report-location | Windsurf `pre_write_code` | Fires when Cursor Agent writes to `docs/`; enforces location SSOT | ❌ GAP (low priority) |
| T7.5 plan-location-gate | Windsurf `pre_write_code` | Fires when Cursor Agent writes `.md`; location check at write time | ❌ GAP (low priority) |
| T7.7 windsurf-governance-health | Windsurf `post_write_code` | Fires after Cursor Agent writes `.windsurf/` files; validates cross-refs | ❌ GAP |
| T7.9 adg-grep-ban | Windsurf `pre_write_code` (`pre_write_gate.py`) | Blocks grep usage as it's being written — earlier than commit | ❌ GAP |
| T7.10 no-unconditional-xfail | Windsurf `pre_write_code` (`pre_write_gate.py`) | Blocks xfail at write time, not commit time | ❌ GAP |
| T7.11 hitl-decision-record | Windsurf `pre_write_code` | Fires when Cursor Agent writes plan docs | ❌ GAP (low priority) |
| T7.12 rca-closure | Windsurf `pre_write_code` | Fires when Cursor Agent writes RCA docs | ❌ GAP (low priority) |
| T7.13 no-archives-imports | Windsurf `pre_write_code` (`pre_write_gate.py`) | Blocks archive imports at write time — `archives/` deleted but rule still valid | ❌ GAP (rule still valid for future) |
| T7.14 sensitive-logs | Windsurf `pre_write_code` (`pre_write_gate.py`) | Fires when Cursor Agent writes Python — better at write-time than commit | ❌ GAP |
| T8 reject-generated-artifacts | `.gitignore` | Already resolved — artifacts gitignored | ✅ RESOLVED |
| T9 tooling-apps-boundary | Windsurf `pre_write_code` (`pre_write_gate.py`) | Fires when writing to `tools/` or `ops_scripts/ci` — exact enforcement point | ❌ GAP |
| T10 module-collision-guard | `generate_full_adg.py` | Structural topology check — belongs in full ADG scan, not per-commit | ❌ GAP |
| T10.7 adg-suggest-report | `generate_full_adg.py` | Already generates 8 standardized reports; suggest-fix = `_run_p1_p2_auto_fix` output | ✅ COVERED |
| T12 guardian-exemption-ratchet | `generate_full_adg.py` | `adg_burndown_table.json` tracks `guardian_exemptions` in `structural_metrics` | ✅ COVERED |
| T14 adg-accelerator-compliance | Windsurf `pre_write_code` (`pre_write_gate.py`) | Python grep-ban should fire at write time; YAML ban → CI | ❌ GAP (Python) / CI (YAML) |
| T-1, T21 | Neither | Meta-tooling for removed hooks | ✅ N/A |

---

## Gap Analysis Summary

### `generate_full_adg.py` — Missing Coverage

| Gap | Description | Suggested Action |
|-----|-------------|-----------------|
| **Zero-loss refactor verifier** | No whole-repo hollow-file check after ADG generation | Add `_check_hollow_files()` call in `generate_full_adg.py` validation phase after scanning |
| **Module collision guard** | No duplicate module / case-collision check during ADG gen | Add `_check_module_collisions()` in validation phase — ADG already has all module nodes |

### Windsurf `pre_write_gate.py` — Missing Coverage

These should be added to `@c:\Git\Agentic-Workflow\ops_scripts\hooks\windsurf\pre_write_gate.py`:

| Gap | Current `pre_write_gate.py` checks | Missing check | Priority |
|-----|------------------------------------|--------------|----------|
| **ADG grep-ban** | bare except, broad except, shell=True, subprocess timeout | grep/rg usage in Python as ADG substitute | HIGH |
| **No-archives-imports** | mcp_config.json safety | `from archives.` or `import archives.` in production code | HIGH |
| **Tooling-apps boundary** | anti-patterns in new_string | `tools/` or `ops_scripts/ci` importing `apps_*` | HIGH |
| **Unconditional xfail** | syntax errors | `@pytest.mark.xfail` without `strict=True` | MEDIUM |
| **Sensitive log scan** | subprocess timeout | logging of passwords/tokens/secrets | MEDIUM |

### Windsurf `post_write_code` — No Current Hook for `.windsurf/` Governance

| Gap | Description | Suggested Action |
|-----|-------------|-----------------|
| **Windsurf governance health** | No check that cross-references in `.windsurf/rules/`, `.windsurf/skills/`, `.windsurf/workflows/` are valid after Cursor Agent writes | Add `post_write_code` hook scoped to `.*\.windsurf/.*` pattern |
| **Plan format validation** | No check that plan `.md` files have required wave table and phase summary | Add to `pre_write_code` scoped to `.windsurf/plans/.*\.md` |

---

## Priority Order for Remediation

| Priority | Action | Where | Effort |
|----------|--------|-------|--------|
| 🔴 HIGH | Add ADG grep-ban to `pre_write_gate.py` | Windsurf hook | Low |
| 🔴 HIGH | Add no-archives-imports to `pre_write_gate.py` | Windsurf hook | Low |
| 🔴 HIGH | Add tooling-apps boundary to `pre_write_gate.py` | Windsurf hook | Low |
| 🟡 MEDIUM | Add hollow-file check to `generate_full_adg.py` | ADG generation | Medium |
| 🟡 MEDIUM | Add module collision check to `generate_full_adg.py` | ADG generation | Medium |
| 🟡 MEDIUM | Add unconditional-xfail check to `pre_write_gate.py` | Windsurf hook | Low |
| 🟡 MEDIUM | Add sensitive-log check to `pre_write_gate.py` | Windsurf hook | Low |
| 🟢 LOW | Add `.windsurf/` governance to `post_write_code` hook | Windsurf hook | Medium |
| 🟢 LOW | Add plan format validation to `pre_write_code` hook | Windsurf hook | Medium |

---

## What Pre-Commit Correctly Retains

All remaining T0a-d through T7 hooks operate strictly on staged files or file-triggered patterns:

| Hook | Why Pre-Commit is the Right Layer |
|------|----------------------------------|
| T0a-d whitespace/EOF/LF/conflict | Pure file content checks; fastest possible gate |
| T1 py_compile | Syntax validation before any Python interpretation |
| T2 ruff-format | Auto-fixer must run before linting to avoid false positives |
| T3 guardian-comment-fixer | Staged Python only; auto-fix exemption format errors |
| T4 hollow-file-gate | Staged Python only; fast AST check |
| T5 mcp-config-sovereignty | File-triggered (`mcp_config.json`); validates sovereignty rules |
| T6 pytest-config-ssot | File-triggered (`pytest.ini`/`pyproject.toml`); detects drift |
| T7 ruff-severity-gate | CRITICAL+HIGH lint blocking on staged Python |
