---
slug: apps-test-surface-deferred-f3c8b2
status: Waiting
parent_plan: apps-test-surface-consolidation-11acd9-v2
created: 2026-05-09
dod_exempt: false
---

# Deferred Scope — Apps Test Surface Consolidation

> **Parent plan**: `apps-test-surface-consolidation-11acd9-v2` (Completed 2026-05-09)
> **Purpose**: Capture all items explicitly deferred from the parent plan for future implementation.
> **This plan is documentation only — do not implement any wave without explicit user direction.**

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|-----------------|
| W1 | 1.1 | Promote TSP1 gate to fail-closed | ~3K | **DEPENDS ON**: 30 consecutive exit-0 TSP1 runs (earliest: 2026-06-09) | ⏳ WAITING | `APPS_TEST_SURFACE_FAIL_CLOSED=1` enforced in CI + gate exits 1 on violation |
| W2 | 2.1–2.3 | Fix `apps-folder-taxonomy.md` rule gap | ~4K | — | ✅ DONE | Rule has no `tests/` row; forbidden note + 3-surface table present |
| W3 | 3.1–3.2 | Fix blueprint `ssot.py` / derived `tests/` entry | ~5K | SSOT refactor in progress | ✅ DONE | `tests` in `FORBIDDEN_ROOT_FOLDERS` in `check_apps_folder_taxonomy.py` |
| W4 | 4.1–4.2 | Add per-app contract surface baseline | ~8K | — | ✅ DONE | All 10 apps have ≥1 contract test; `AGENTS.md` 3-surface section added |
| W5 | 5.1 | Import-path audit on relocated test files | ~6K | W4/W5 of parent complete | ✅ DONE | `apps_lic` `__init__.py` export fixed; 12/12 tests pass |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS / PARTIAL · ✅ DONE · ❌ BLOCKED · ⏳ WAITING (external dependency)

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| 1.1 | Promote TSP1 gate to fail-closed | `run_contract_gates.py` + `.pre-commit-config.yaml` | **Depends on**: `artifacts/ci/check_apps_test_surface_parity_*.json` showing ≥30 consecutive exit-0 runs. Earliest unblock: 2026-06-09. | ~3K | ⏳ WAITING |
| 2.1 | Drop `tests/` from `apps-folder-taxonomy.md` | `.cursor/rules/apps-folder-taxonomy.md` | Rule prose may be load-bearing for other gates | ~2K | ✅ DONE |
| 2.2 | Cross-link new taxonomy rule | `apps-folder-taxonomy.md` → `apps-test-surface-taxonomy.md` | — | ~1K | ✅ DONE |
| 2.3 | Update `AGENTS.md` 3-surface declaration | `AGENTS.md` | Doc-only; low risk | ~1K | ✅ DONE |
| 3.1 | Remove `tests/` from blueprint ssot.py apps-subfolder map | `ops_scripts/ci/check_apps_folder_taxonomy.py` | `tests` in `FORBIDDEN_ROOT_FOLDERS`; no ssot.py change needed | ~3K | ✅ DONE |
| 3.2 | Update blueprint derived.py to reflect removal | N/A — gate-level enforcement sufficient | No derived.py change needed | ~2K | ✅ DONE |
| 4.1 | Audit which `apps_<x>` lack contract tests entirely | `tests/_apps_contract/` scan | `apps_shared` had zero; all others covered | ~2K | ✅ DONE |
| 4.2 | Scaffold minimal contract test stubs for gap apps | `tests/_apps_contract/test_apps_shared_contract.py` | 3 smoke tests; 3/3 pass | ~6K | ✅ DONE |
| 5.1 | Import-path audit + fix on all relocated test files | `apps_lic/integrations/__init__.py` | `ExecutionAdapter`+`ObservabilityAdapter` exported; 9 tests pass; remaining errors are pre-existing quarantine violations | ~6K | ✅ DONE |

---

## Deferred Item Register

### D1 — TSP1 gate fail-closed promotion
**From**: parent plan Out Of Scope §"Promoting the new `apps-test-surface-taxonomy.md` rule from advisory to fail-closed — deferred"
**AG_QUEUE_SEED**: `plan=apps-test-surface-consolidation-11acd9-v2 id=W6_rule_promotion depends_on=W6_landing title=promote_apps-test-surface-taxonomy_advisory_to_fail_closed_after_30day_clean`
**Status**: ⏳ WAITING — blocked on external time dependency.
**Dependency**: `artifacts/ci/check_apps_test_surface_parity_*.json` must show ≥30 consecutive exit-0 runs. TSP1 first went green 2026-05-10. **Earliest unblock date: 2026-06-09**.
**Action when unblocked**: Flip `APPS_TEST_SURFACE_FAIL_CLOSED=1` in `.pre-commit-config.yaml`; update `run_contract_gates.py` advisory comment to fail-closed.
**Gate evidence required**: `artifacts/ci/check_apps_test_surface_parity_*.json` history showing 30 consecutive exit-0 runs.

### D2 — `apps-folder-taxonomy.md` still lists `tests/` as valid subdir (GAP-1)
**From**: parent plan Gap Register GAP-1
**Location**: `.cursor/rules/apps-folder-taxonomy.md`
**Action**: Remove `tests/` row from the "Canonical folder taxonomy" table. Add cross-reference: "App-local tests are FORBIDDEN — see `apps-test-surface-taxonomy.md`."

### D3 — Blueprint ssot.py includes `tests/` in apps-subfolder map (GAP-3)
**From**: parent plan Gap Register GAP-3
**Location**: `agentic_core/L5_safety/config/structure_blueprint/ssot.py` — `get_apps_wildcard_subfolder_map`
**Action**: Remove `"tests"` from the returned subfolder map. Validate with `pytest tests/unit/` after change.
**Risk**: May break blueprint gate if any apps_<x>/tests/ dirs reappear; mitigated by TSP1 gate.

### D4 — `AGENTS.md` does not declare 3-surface canonical layout
**From**: parent plan Phase 2 table item 16
**Location**: `AGENTS.md` (repo root)
**Action**: Add a "Test Surface Taxonomy" section under the Apps guidance block, referencing the 3 canonical surfaces and `apps-test-surface-taxonomy.md`.

### D5 — Per-app contract test coverage gap (GAP-4 residual)
**From**: parent plan Success Criteria: "All 10 apps_* packages have ≥1 file in `tests/_apps_contract/test_<app>_*.py`"
**Status**: `apps_exec` and `apps_repo_brief` likely have zero contract tests (stubs only; no app-specific logic yet).
**Action**: Scaffold minimal smoke-contract tests for both apps once they have real engine logic.

### D6 — Import-path errors in relocated test files
**From**: W4/W5 execution — pre-existing `ModuleNotFoundError` and quarantine violations observed during `pytest --collect-only` runs.
**Scope**: Files moved from `apps_<x>/tests/` that had relative imports or hardcoded paths assuming app-local location.
**Action**: Audit all relocated files for broken imports; fix relative → absolute import paths. Out of scope for consolidation (pure relocation) but necessary for green pytest.
**Note**: Several errors are pre-existing quarantine violations unrelated to relocation.

### D7 — Pytest downstream markers audit
**From**: parent plan Out Of Scope §"Updating downstream pytest markers on relocated files"
**Action**: After import-path fixes (D6), audit all relocated files for `@pytest.mark.*` decorators that reference old paths in skip reasons or parametrize IDs.

### D8 — `tests/governance/test_apps_*` long-term home
**From**: parent plan Out Of Scope §"77 files — Q3=A user decision: leave in place as cross-cutting concern"
**Status**: 77 files remain in `tests/governance/`. User decision Q3=A: cross-cutting, leave in place.
**Action**: Revisit if governance tests grow per-app-specific logic that warrants migration to `tests/<app>/`.

---

## Out Of Scope for This Deferred Plan

- Any new test logic or test content changes.
- Fixing pre-existing quarantine violations beyond what's required for collection.
- Moving `tests/governance/test_apps_*` (Q3=A decision locked).
- Moving `tests/e2e/test_apps_research_live.py` or `tests/runtime/test_apps_rg_e2e_proof.py`.

---

## Definition of Done

| # | Criterion | Verification |
|---|---|---|
| DoD-1 | TSP1 gate is fail-closed in CI | `APPS_TEST_SURFACE_FAIL_CLOSED=1` verified in `.pre-commit-config.yaml` + gate exits 1 on violation |
| DoD-2 | `apps-folder-taxonomy.md` has no `tests/` row | `grep -n "tests/" .cursor/rules/apps-folder-taxonomy.md` returns empty |
| DoD-3 | Blueprint ssot.py does not return `tests/` in subfolder map | Unit test verifying `"tests" not in get_apps_wildcard_subfolder_map(app)` |
| DoD-4 | All 10 apps have ≥1 contract test | `ls tests/_apps_contract/test_apps_*.py` count = 10 |
| DoD-5 | `pytest --collect-only` whole-tree exits 0 with no ImportError on relocated files | Exit code + grep for ImportError |

---

## References

- Parent plan (Completed): `.cursor/plans/apps-test-surface-consolidation-11acd9-v2.md`
- Enforcement rule: `.cursor/rules/apps-test-surface-taxonomy.md`
- TSP1 gate: `ops_scripts/ci/check_apps_test_surface_parity.py`
- ADR-082: `docs/architecture/adr/ADR-082-apps-folder-taxonomy.md`
