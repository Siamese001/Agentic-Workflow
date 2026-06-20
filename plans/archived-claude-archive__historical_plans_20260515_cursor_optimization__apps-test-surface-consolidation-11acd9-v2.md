---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-test-surface-consolidation-11acd9-v2.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-test-surface-consolidation-11acd9-v2.md'
source_sha256: 8140429ebce7fb73c818227388ec0d27c68c9da78dc7e1a42b7f8c788645bafc
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-test-surface-consolidation-11acd9-v2
plan_type: governance
supersedes: apps-test-surface-consolidation-11acd9
rebaseline_date: 2026-05-09
---

# Apps_* Test-Surface Consolidation — v2 Rebaseline

Establish a single canonical 3-surface test taxonomy (`tests/_apps_contract/`, `tests/unit/<app>/`, `tests/<app>/`) across all 10 `apps_*` packages, relocate ~70 legacy app-internal test files, and update all SSOT folder-definition files to reflect the new surface.

**Supersedes**: `.windsurf/plans/apps-test-surface-consolidation-11acd9.md` (archived — pre-dates 2026-05-09 repo state; all baseline counts, gap analysis, and Author-Gate decisions from v1 remain valid and are incorporated here).

---

## Rebaseline Summary (2026-05-09 diff vs v1)

| Item | v1 (2026-05-07) | v2 (2026-05-09) | Delta |
|---|---|---|---|
| `tests/unit/<app>/` dirs populated | 5 of 10 | **10 of 10** | ✅ W3 unit scaffold DONE |
| `tests/<app>/` dirs populated | 0–1 of 10 | **4 of 10** (eval, research, rg, underwriting_ai) | partial progress |
| `tests/<app>/` dirs still missing | 6 | **6** (exec, lic, qna, repo_brief, rfp, shared) | unchanged |
| `apps_<x>/tests/` internal dirs | 8 apps, 71 files | **8 apps, ~70 test files** | ~unchanged (apps_exec/repo_brief never had any) |
| `tests/_apps_contract/` file count | 129 files | **129 files** | unchanged |
| `tests/governance/test_apps_*` | 76 | **77** | +1 |
| `tests/integration/` misplaced | 5 files | **5 + 1 new** (`test_apps_otel_runtime_coverage.py`) | +1 |
| New split surface discovered | — | `apps_rg/profiles/tests/test_profiles_declarative.py` | +1 to relocate |
| Wave 6 enforcement (rule+helper+gate) | 🔲 TODO | **🔲 TODO** | unchanged |
| Wave 7 verification | 🔲 TODO | **🔲 TODO** | unchanged |

**Effective work remaining**: Wave 3 (partial — unit scaffold done, `tests/<app>/` scaffold still needed for 6 apps), Wave 4 (70 files + 1 profiles test), Wave 5 (6 misplaced + 1 new), Wave 6 (new enforcement), Wave 7 (verification).

---

## Context (SCQA)

- **Situation** — Test files for `apps_*` packages live in 4+ inconsistent locations: `tests/_apps_contract/test_<app>_*.py` (cross-app contract, all apps), `tests/unit/<app>/` (10/10 populated as of rebaseline), `tests/<app>/` (4/10 populated), AND legacy `apps_<app>/tests/` dirs inside the app packages (~70 files across 8 apps). Additionally `apps_rg/profiles/tests/` was discovered as a 5th split surface. `tests/governance/test_apps_*` (77 files, architecture-compliance) remain intentionally separate per Q3=A. `tests/integration/apps_*/` (6 files) are misplaced.
- **Complication** — Two (now three) roots for app tests violate the "consistent testing surface" goal, fragment pytest collection, duplicate conftest fixtures, and confuse readers. The `.windsurf/rules/apps-folder-taxonomy.md` rule still lists `tests/` as a legitimate app-internal subdir. Wave 6 enforcement hasn't landed. `tests/unit/<app>/` scaffolding is complete but `tests/<app>/` scaffolding is incomplete.
- **Question** — How do we converge on a single canonical 3-surface test taxonomy for every `apps_*` package without breaking the governance suite, the AEH1 parity gate, or pytest collection?
- **Answer** — Complete remaining `tests/<app>/` scaffolding (6 apps), `git mv` all ~70 + 2 legacy files, add Wave 6 enforcement gate, verify clean.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `.windsurf/rules/apps-folder-taxonomy.md` | Current rule lists `tests/` as legitimate app-internal subdir; must drop | 🔲 |
| `agentic_core/L0_routing/config/path_constants.py` | Primary path constants SSOT | 🔲 |
| `agentic_core/interfaces/path_constants.py` | Interface-layer copy | 🔲 |
| `agentic_core/L5_safety/config/structure_blueprint/{__init__,_constants,ssot,derived}.py` | Canonical blueprint SSOT package | 🔲 |
| `agentic_core/L5_safety/config/structure_blueprint_config.py` | Deprecated re-export shim | 🔲 |
| `agentic_core/L0_routing/enforcement/apps_taxonomy_guard.py` | Runtime taxonomy enforcement | 🔲 |
| `ops_scripts/ci/check_apps_folder_taxonomy.py` | apps_* taxonomy gate | 🔲 |
| `AGENTS.md` | Top-level taxonomy reference | 🔲 |
| ADG snapshot `artifacts/adg/adg_indexed_05052026_0722.sqlite` | Directly observed file inventory + scattered-tests classification | ✅ |
| Repo scan 2026-05-09 | Per-app current-state audit (this rebaseline) | ✅ |
| Author-Gate decisions Q1–Q4 from v1 | Carried forward unchanged | ✅ |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|-----------------|
| W1 | 1.1, 1.2 | Plan registration + audit summary | ~3K | Notion API live | ✅ DONE (v1 authored; v2 rebaseline) | Plan in Notion |
| W2 | 2.1–2.10 | SSOT updates (16 files) | ~12K | No circular imports | ✅ DONE | All 16 files updated/verified |
| W3 | 3.1, 3.2 | Surface scaffolding | ~4K | pytest --collect-only passes | ✅ DONE | unit: 10/10 ✅; `tests/<app>/`: 10/10 ✅ |
| W4 | 4.1–4.9 | Legacy relocation (~70 + 2 files) | ~25K | git mv history preserved | ✅ DONE | Zero `apps_<x>/tests/` remain |
| W5 | 5.1 | Misplaced repo-test relocation (6 files) | ~5K | — | ✅ DONE | `tests/integration/apps_*/` cleared |
| W6 | 6.1–6.4 | New enforcement rule + helper + CI gate + tests | ~12K | — | ✅ DONE | Gate green (TSP1 OK); 25/25 tests pass |
| W7 | 7.1 | Verification | ~4K | All previous waves done | ✅ DONE | TSP1 ✅ OK; ADR-082 tests/ clean; 25/25 tests pass |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS / PARTIAL · ✅ DONE · ❌ BLOCKED

**Total remaining: ~62K tokens (W2–W7).**

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Plan authored & registered in Notion | this file + Notion Plans row | — | ~2K | ✅ DONE |
| 1.2 | Audit summary published | `docs/reports/test_surface_audit/2026-W19.md` | — | ~2K | ✅ DONE |
| 2.1 | Rule update — `apps-folder-taxonomy.md` | drop `tests/` row; cross-link new rule | GAP-1 | ~1K | ✅ DONE |
| 2.2 | Path constants — primary | `agentic_core/L0_routing/config/path_constants.py` | GAP-2 | ~2K | ✅ DONE |
| 2.3 | Path constants — interface mirror | `agentic_core/interfaces/path_constants.py` re-export | — | ~1K | ✅ DONE |
| 2.4 | Blueprint `_constants.py` | add `APPS_TEST_SURFACE_DEFINITION` | GAP-3 | ~2K | ✅ DONE |
| 2.5 | Blueprint `ssot.py` `derived.py` | reflect new test surface | GAP-3 | ~2K | ✅ DONE |
| 2.6 | Blueprint shim re-export | `structure_blueprint_config.py` back-compat | — | ~1K | ✅ DONE |
| 2.7 | Runtime guard | `apps_taxonomy_guard.py` 3-surface canonical | GAP-2 | ~1K | ✅ DONE |
| 2.8 | Taxonomy gate | `check_apps_folder_taxonomy.py` flag `apps_<x>/tests/` | — | ~1K | ✅ DONE |
| 2.9 | Cert/ADG paths sweep | chroma_paths, artifact paths, layer_paths, apps_e2e/paths.py | — | ~1K | ✅ DONE |
| 2.10 | AGENTS.md | declare 3 canonical surfaces | — | ~1K | ✅ DONE |
| 3.1 | Scaffold `tests/unit/<app>/` | ~~5 apps~~ → **0 remaining** (all 10 exist) | — | — | ✅ DONE |
| 3.2 | Scaffold `tests/<app>/` for 6 missing apps | apps_exec, apps_lic, apps_qna, apps_repo_brief, apps_rfp, apps_shared | GAP-4 | ~3K | ✅ DONE |
| 4.1 | Relocate apps_qna/tests/ (22 files) | git mv → `tests/apps_qna/` | GAP-5 | ~5K | ✅ DONE |
| 4.2 | Relocate apps_eval/tests/ (9 test files) | git mv → `tests/apps_eval/` | GAP-5 | ~3K | ✅ DONE |
| 4.3 | Relocate apps_underwriting_ai/tests/ (10 files) | git mv → `tests/apps_underwriting_ai/` | GAP-5 | ~3K | ✅ DONE |
| 4.4 | Relocate apps_lic/tests/ (7 files) | git mv → `tests/apps_lic/` | GAP-5 | ~2K | ✅ DONE |
| 4.5 | Relocate apps_research/tests/ (7 files) | git mv → `tests/apps_research/` | GAP-5 | ~2K | ✅ DONE |
| 4.6 | Relocate apps_rfp/tests/ (6 files) | git mv → `tests/apps_rfp/` | GAP-5 | ~2K | ✅ DONE |
| 4.7 | Relocate apps_rg/tests/ (5 files) | git mv → `tests/apps_rg/` | GAP-5 | ~2K | ✅ DONE |
| 4.8 | Relocate apps_shared/tests/ (4 files) | git mv → `tests/apps_shared/` | GAP-5 | ~2K | ✅ DONE |
| 4.9 | Relocate apps_rg/profiles/tests/ (1 file) | `test_profiles_declarative.py` → `tests/apps_rg/` | GAP-5b | ~1K | ✅ DONE |
| 4.10 | Remove empty `apps_<x>/tests/` dirs | 8 dirs + apps_rg/profiles/tests/ | — | ~1K | ✅ DONE |
| 5.1 | Relocate misplaced `tests/integration/apps_*/` | 16 app-specific files → `tests/<app>/`; `test_apps_otel_runtime_coverage.py` kept (cross-cutting) | GAP-6 | ~3K | ✅ DONE |
| 6.1 | New rule | `.windsurf/rules/apps-test-surface-taxonomy.md` (always_on advisory) | GAP-7 | ~2K | ✅ DONE |
| 6.2 | Helper | `.windsurf/scripts/_apps_test_surface_check.py` | GAP-7 | ~3K | ✅ DONE |
| 6.3 | CI gate | `ops_scripts/ci/check_apps_test_surface_parity.py` (registered after AEH1) | GAP-7 | ~3K | ✅ DONE |
| 6.4 | Tests | `tests/unit/windsurf_scripts/test_apps_test_surface_check.py` (25 cases) | — | ~3K | ✅ DONE |
| 7.1 | Verification | TSP1 gate ✅; ADR-082 tests/ violations = 0; 25/25 tests pass | — | ~4K | ✅ DONE |

---

## Out Of Scope

- Adding new test cases or improving coverage in any moved file (pure relocation — content unchanged except for import-path rewrites).
- Touching `tests/governance/test_apps_*` (77 files) — Q3=A user decision: leave in place as cross-cutting concern.
- Touching `tests/e2e/test_apps_research_live.py` or `tests/runtime/test_apps_rg_e2e_proof.py` — e2e/runtime cross-cutting harnesses.
- Touching `tests/_archived_obsolete/**` — already archived.
- Fixing or refactoring any test logic discovered during relocation — file `NEXT_STEP:` markers, do not edit.
- Promoting the new `apps-test-surface-taxonomy.md` rule from advisory to fail-closed — deferred.
- Updating downstream pytest markers on relocated files — deferred unless collection breaks.
- `tests/integration/test_apps_otel_runtime_coverage.py` — evaluate at W5.1 execution time; likely cross-cutting, likely stays.
- `apps_exec` — has only a stub `config/` dir; no app-internal tests exist.
- `apps_repo_brief` — no app-internal tests exist.

---

## Gap Register

**GAP-1: Rule lists `tests/` as legitimate apps_<x>/ subdir**
- `.windsurf/rules/apps-folder-taxonomy.md` still includes `tests/` as "App-local unit tests" inside an `apps_*` package.
- Fix: drop the row; explicitly forbid `apps_<x>/tests/`; cross-link to new `apps-test-surface-taxonomy.md`.

**GAP-2: Path-constant SSOT files have no apps_* test-surface constants**
- No `APPS_TEST_SURFACES`, `apps_test_unit_dir(app)`, `apps_test_integration_dir(app)`, or `apps_contract_glob(app)` in either path-constants file.

**GAP-3: Blueprint package's apps-subfolder-map functions don't enforce 3-surface contract**
- `ssot.py` may include `tests/` as a valid app-internal subdir.

**GAP-4: 6 apps still lack `tests/<app>/` dirs** *(unit scaffold complete as of 2026-05-09)*
- Missing `tests/<app>/` for apps_exec, apps_lic, apps_qna, apps_repo_brief, apps_rfp, apps_shared.

**GAP-5: ~70 legacy files in `apps_<app>/tests/`**
- Confirmed per 2026-05-09 scan: apps_qna 22, apps_underwriting_ai 10, apps_eval 9, apps_lic 7, apps_research 7, apps_rfp 6, apps_rg 5, apps_shared 4. Total: 70.

**GAP-5b: New split surface — `apps_rg/profiles/tests/`**
- `apps_rg/profiles/tests/test_profiles_declarative.py` discovered 2026-05-09. Not in v1 plan.
- Fix: `git mv` to `tests/apps_rg/`.

**GAP-6: 5–6 misplaced repo-rooted tests**
- `tests/integration/apps_eval/test_apps_eval_integration.py`, `apps_research/test_apps_research_integration.py`, `apps_rfp/test_apps_rfp_integration.py`, `apps_shared/test_apps_shared_integration.py`, `test_apps_qna_c0_retrieval.py`.
- `test_apps_otel_runtime_coverage.py` — evaluate at execution time (likely cross-cutting; may stay).

**GAP-7: No CI enforcement against re-introducing the split**
- No `apps-test-surface-taxonomy.md` rule, no helper, no CI gate yet.

---

## Author-Gate Decisions Carried Forward

| Decision | User selection | Rationale |
|---|---|---|
| Q1 — Scaffolding depth | C — Full audit + relocate scattered tests | User chose high-cost option for real coverage gain. |
| Q2 — SSOT update scope | Full — find ALL folder-definition files (16 found via ADG) | Comprehensive consistency. |
| Q3 — `tests/governance/test_apps_*` | A — Leave in `tests/governance/` ⭐ | Cross-cutting concern. |
| Q4 — Legacy `apps_<app>/tests/` | A — Relocate all to `tests/<app>/` | Single canonical home. |

`AG_QUEUE_SEED: plan=apps-test-surface-consolidation-11acd9-v2 id=W6_rule_promotion depends_on=W6_landing title=promote_apps-test-surface-taxonomy_advisory_to_fail_closed_after_30day_clean`

---

## Execution Plan

### Phase 1.2 — Audit summary
**Scope**: `docs/reports/test_surface_audit/2026-W19.md` + rebaseline delta doc.
**Acceptance**: report exists with per-app counts table.

### Phase 2.1–2.10 — SSOT folder-definition file updates

| # | File | Edit |
|---|---|---|
| 1 | `.windsurf/rules/apps-folder-taxonomy.md` | drop `tests/` row; cross-link new rule |
| 2 | `agentic_core/L0_routing/config/path_constants.py` | add `APPS_TEST_SURFACES`, helper functions |
| 3 | `agentic_core/interfaces/path_constants.py` | re-export new names |
| 4 | `agentic_core/L5_safety/config/structure_blueprint/_constants.py` | add `APPS_TEST_SURFACE_DEFINITION` dict |
| 5 | `agentic_core/L5_safety/config/structure_blueprint/ssot.py` | remove `tests/` from apps-internal subfolder map |
| 6 | `agentic_core/L5_safety/config/structure_blueprint/derived.py` | reflect new surface |
| 7 | `agentic_core/L5_safety/config/structure_blueprint/__init__.py` | export new names in `__all__` |
| 8 | `agentic_core/L5_safety/config/structure_blueprint_config.py` | re-export new names (deprecated shim) |
| 9 | `agentic_core/L0_routing/enforcement/apps_taxonomy_guard.py` | recognize 3-surface canonical; flag `apps_<x>/tests/` |
| 10 | `ops_scripts/ci/check_apps_folder_taxonomy.py` | flag `apps_<x>/tests/` as violation |
| 11–15 | chroma_paths, artifact paths, layer_paths, apps_e2e/paths.py | confirm no apps_<x>/tests/ refs (likely no-op) |
| 16 | `AGENTS.md` | declare 3 canonical surfaces |

### Phase 3.2 — Scaffold missing `tests/<app>/`
**Apps**: apps_exec, apps_lic, apps_qna, apps_repo_brief, apps_rfp, apps_shared.
Each: `__init__.py` + `conftest.py`.
**Acceptance**: `pytest --collect-only tests/<app>/` succeeds for all 6.

### Phase 4.1–4.10 — Legacy relocation

Per-app `git mv` to `tests/<app>/`; rewrite app-relative imports; delete empty source dirs.

| Phase | App | Internal count | Destination |
|---|---|---|---|
| 4.1 | apps_qna | 22 | `tests/apps_qna/` |
| 4.2 | apps_eval | 9 | `tests/apps_eval/` |
| 4.3 | apps_underwriting_ai | 10 | `tests/apps_underwriting_ai/` |
| 4.4 | apps_lic | 7 | `tests/apps_lic/` |
| 4.5 | apps_research | 7 | `tests/apps_research/` |
| 4.6 | apps_rfp | 6 | `tests/apps_rfp/` |
| 4.7 | apps_rg | 5 | `tests/apps_rg/` |
| 4.8 | apps_shared | 4 | `tests/apps_shared/` |
| 4.9 | apps_rg/profiles/tests/ | 1 | `tests/apps_rg/` |
| 4.10 | Remove empty dirs | 8 + 1 | — |

Total: **71 files** via `git mv`.

### Phase 5.1 — Misplaced repo-test relocation

```bash
git mv tests/integration/apps_eval/test_apps_eval_integration.py tests/apps_eval/
git mv tests/integration/apps_research/test_apps_research_integration.py tests/apps_research/
git mv tests/integration/apps_rfp/test_apps_rfp_integration.py tests/apps_rfp/
git mv tests/integration/apps_shared/test_apps_shared_integration.py tests/apps_shared/
git mv tests/integration/test_apps_qna_c0_retrieval.py tests/apps_qna/
# test_apps_otel_runtime_coverage.py — evaluate; likely stays (cross-cutting OTEL)
```

### Phase 6.1–6.4 — New CI enforcement

- `.windsurf/rules/apps-test-surface-taxonomy.md` (always_on advisory)
- `.windsurf/scripts/_apps_test_surface_check.py` — `decide(app, fp) -> Violation | None`
- `ops_scripts/ci/check_apps_test_surface_parity.py` — registered in `run_contract_gates.py` after AEH1; bypass `APPS_TEST_SURFACE_BYPASS=1`
- `tests/unit/windsurf_scripts/test_apps_test_surface_check.py` — ≥30 cases

### Phase 7.1 — Verification

```bash
pytest --collect-only 2>&1 | tail -50
python ops_scripts/ci/check_app_domain_harness_parity.py
python ops_scripts/ci/check_apps_folder_taxonomy.py
python ops_scripts/ci/check_apps_test_surface_parity.py
python -m pytest tests/_apps_contract/ -q
python -m pytest tests/governance/ -k apps_ -q
```

---

## Success Criteria

- [ ] All 10 `apps_*` packages have a populated or scaffolded `tests/<app>/`.
- [ ] All 10 `apps_*` packages have a populated `tests/unit/<app>/` (**already met**).
- [ ] All 10 `apps_*` packages have ≥1 file in `tests/_apps_contract/test_<app>_*.py`.
- [ ] Zero `apps_<x>/tests/` directories remain (including `apps_rg/profiles/tests/`).
- [ ] 71 + 5 = 76 files relocated via `git mv` (history preserved).
- [ ] All 16 SSOT folder-definition files updated or explicitly verified no-op.
- [ ] `pytest --collect-only` whole-tree succeeds.
- [ ] `tests/_apps_contract/` test count ≥129 files baseline.
- [ ] `tests/governance/test_apps_*` count = 77 (do not decrease).
- [ ] AEH1 gate: ERROR=0 WARN=0.
- [ ] New CI gate `check_apps_test_surface_parity.py` registered and green.
- [ ] New rule `apps-test-surface-taxonomy.md` always_on advisory.
- [ ] `apps-folder-taxonomy.md` no longer lists `tests/` as app-internal subdir.
- [ ] Plan registered in Notion Plans DB.

---

## Rollback Strategy

1. **W4/W5 (relocations)**: `git restore --source HEAD~<n> -- <path>` per file; `git mv` history makes inverse trivial. Never delete source until pytest passes.
2. **W2 (SSOT edits)**: `git restore <file>`; restore one at a time, run affected gate, iterate.
3. **W6 (new gate)**: set `APPS_TEST_SURFACE_BYPASS=1`; revert gate registration line in `run_contract_gates.py`.
4. **Whole-plan abort**: `git revert <merge-commit>` — each wave is its own commit.

---

## Definition of Done

| # | Criterion | Verification |
|---|---|---|
| DoD-1 | Functional: zero `apps_<x>/tests/` dirs remain | `Get-ChildItem -Recurse -Filter "tests" apps_* -Directory` returns empty |
| DoD-2 | Smoke: `pytest --collect-only` exits 0 whole-tree | exit code check |
| DoD-3 | Tests: `tests/_apps_contract/` count ≥129 files; `tests/governance/` count = 77 | file count checks |
| DoD-4 | CI gates: AEH1 ERROR=0; new surface gate green | gate exit codes |
| DoD-5 | Doc/memory: Notion Plans row Status=Completed; plan file on disk | Notion API + disk check |
