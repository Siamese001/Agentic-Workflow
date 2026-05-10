---
slug: apps-test-surface-deferred-f3c8b2
status: Not Started
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
| W1 | 1.1 | Promote TSP1 gate to fail-closed | ~3K | 30+ clean days since TSP1 green | 🔲 TODO | `APPS_TEST_SURFACE_FAIL_CLOSED=1` enforced in CI |
| W2 | 2.1–2.3 | Fix `apps-folder-taxonomy.md` rule gap | ~4K | — | 🔲 TODO | Rule no longer lists `tests/` as app-internal subdir |
| W3 | 3.1–3.2 | Fix blueprint `ssot.py` / derived `tests/` entry | ~5K | SSOT refactor in progress | 🔲 TODO | Blueprint does not validate `apps_<x>/tests/` as canonical |
| W4 | 4.1–4.2 | Add per-app contract surface baseline | ~8K | — | 🔲 TODO | Every `apps_<x>` has ≥1 `tests/_apps_contract/test_<app>_*.py` |
| W5 | 5.1 | Import-path audit on relocated test files | ~6K | W4/W5 of parent complete | 🔲 TODO | All moved files pass `pytest --collect-only` without ImportError |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS / PARTIAL · ✅ DONE · ❌ BLOCKED

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| 1.1 | Promote TSP1 gate to fail-closed | `run_contract_gates.py` + CI config | Requires 30-day clean-run baseline evidence | ~3K | 🔲 TODO |
| 2.1 | Drop `tests/` from `apps-folder-taxonomy.md` | `.windsurf/rules/apps-folder-taxonomy.md` | Rule prose may be load-bearing for other gates | ~2K | 🔲 TODO |
| 2.2 | Cross-link new taxonomy rule | `apps-folder-taxonomy.md` → `apps-test-surface-taxonomy.md` | — | ~1K | 🔲 TODO |
| 2.3 | Update `AGENTS.md` 3-surface declaration | `AGENTS.md` | Doc-only; low risk | ~1K | 🔲 TODO |
| 3.1 | Remove `tests/` from blueprint ssot.py apps-subfolder map | `agentic_core/L5_safety/config/structure_blueprint/ssot.py` | May break blueprint gate if apps still had tests/ dirs | ~3K | 🔲 TODO |
| 3.2 | Update blueprint derived.py to reflect removal | `agentic_core/L5_safety/config/structure_blueprint/derived.py` | Downstream of 3.1 | ~2K | 🔲 TODO |
| 4.1 | Audit which `apps_<x>` lack contract tests entirely | `tests/_apps_contract/` scan | apps_exec, apps_repo_brief likely have zero | ~2K | 🔲 TODO |
| 4.2 | Scaffold minimal contract test stubs for gap apps | `tests/_apps_contract/test_<app>_contract.py` × N | Need to define what "contract" means per app | ~6K | 🔲 TODO |
| 5.1 | Import-path audit + fix on all relocated test files | All files moved in W4+W5 of parent | Pre-existing quarantine violations complicate this | ~6K | 🔲 TODO |

---

## Deferred Item Register

### D1 — TSP1 gate fail-closed promotion
**From**: parent plan Out Of Scope §"Promoting the new `apps-test-surface-taxonomy.md` rule from advisory to fail-closed — deferred"
**AG_QUEUE_SEED**: `plan=apps-test-surface-consolidation-11acd9-v2 id=W6_rule_promotion depends_on=W6_landing title=promote_apps-test-surface-taxonomy_advisory_to_fail_closed_after_30day_clean`
**Action**: After 30+ consecutive clean TSP1 runs in CI, flip `APPS_TEST_SURFACE_FAIL_CLOSED=1` in `.pre-commit-config.yaml` and register as fail-closed in `run_contract_gates.py`.
**Gate evidence required**: `artifacts/ci/check_apps_test_surface_parity_*.json` history showing 30 consecutive exit-0 runs.

### D2 — `apps-folder-taxonomy.md` still lists `tests/` as valid subdir (GAP-1)
**From**: parent plan Gap Register GAP-1
**Location**: `.windsurf/rules/apps-folder-taxonomy.md`
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
| DoD-2 | `apps-folder-taxonomy.md` has no `tests/` row | `grep -n "tests/" .windsurf/rules/apps-folder-taxonomy.md` returns empty |
| DoD-3 | Blueprint ssot.py does not return `tests/` in subfolder map | Unit test verifying `"tests" not in get_apps_wildcard_subfolder_map(app)` |
| DoD-4 | All 10 apps have ≥1 contract test | `ls tests/_apps_contract/test_apps_*.py` count = 10 |
| DoD-5 | `pytest --collect-only` whole-tree exits 0 with no ImportError on relocated files | Exit code + grep for ImportError |

---

## References

- Parent plan (Completed): `.windsurf/plans/apps-test-surface-consolidation-11acd9-v2.md`
- Enforcement rule: `.windsurf/rules/apps-test-surface-taxonomy.md`
- TSP1 gate: `ops_scripts/ci/check_apps_test_surface_parity.py`
- ADR-082: `docs/architecture/adr/ADR-082-apps-folder-taxonomy.md`
