---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-test-surface-consolidation-11acd9.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-test-surface-consolidation-11acd9.md'
source_sha256: 5d648d238e763aa05997c3e4520605420e13eef858cfeaec726f7ef13019a64a
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-test-surface-consolidation-11acd9
plan_type: governance
status: archived
superseded_by: apps-test-surface-consolidation-11acd9-v2
archived_date: 2026-05-09
archived_reason: Rebaselined against 2026-05-09 repo state. W3 unit scaffold partially done; new split surface (apps_rg/profiles/tests/) discovered; file counts updated. See v2 plan.
---

> ⚠️ **ARCHIVED** — Superseded by `.windsurf/plans/apps-test-surface-consolidation-11acd9-v2.md` (2026-05-09 rebaseline). All Author-Gate decisions (Q1–Q4), gap analysis, and SSOT file list carried forward unchanged into v2.

# Apps_* Test-Surface Consolidation

Establish a single canonical 3-surface test taxonomy (`tests/_apps_contract/`, `tests/unit/<app>/`, `tests/<app>/`) across all 10 `apps_*` packages, relocate 71 legacy app-internal test files, and update all SSOT folder-definition files to reflect the new surface.

---

## Context (SCQA)

- **Situation** — Test files for `apps_*` packages live in 4+ inconsistent locations: `tests/_apps_contract/test_<app>_*.py` (cross-app contract, all apps), `tests/unit/<app>/` (5 of 10 apps populated), `tests/<app>/` (4 of 10 apps populated), AND legacy `apps_<app>/tests/` dirs inside the app packages (71 files across 8 apps). Plus `tests/governance/test_apps_*` (76 files, architecture-compliance) and a handful in `tests/integration/` / `tests/e2e/` / `tests/runtime/`. ADG snapshot `05052026_0722` (140743 nodes / 863353 edges) confirms 16 distinct SSOT folder-definition files reference apps_* paths.
- **Complication** — Two roots for app tests (repo-rooted `tests/` + app-rooted `apps_<x>/tests/`) violate the user's "consistent testing surface" goal, fragment pytest collection, duplicate conftest fixtures, and confuse readers. The `.windsurf/rules/apps-folder-taxonomy.md` rule currently lists `tests/` as a legitimate app-internal subdir, perpetuating the split. Only `apps_rg` has all three repo-rooted surfaces populated.
- **Question** — How do we converge on a single canonical 3-surface test taxonomy (cross-app contract / unit / integration) for every `apps_*` package without breaking the governance suite, the AEH1 parity gate, or pytest collection?
- **Answer** — Drop the `apps_<x>/tests/` 4th surface from the rule, `git mv` all 71 legacy files into `tests/<app>/`, leave `tests/governance/test_apps_*` in place (cross-cutting), scaffold missing `tests/unit/<app>/` + `tests/<app>/` dirs with `__init__.py` + `conftest.py`, update the 16 SSOT folder-definition files to reflect the canonical taxonomy, and add a new advisory CI gate `check_apps_test_surface_parity.py` to prevent regression.

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
| `artifacts/_scratch/test_relocation_audit.py` + `relocate_out.txt` | Per-app legacy file lists (71 files, broken down by app) | ✅ |
| Author-Gate decisions Q3=A (governance stays), Q4=A (relocate apps_<x>/tests/) | User-resolved 2026-05-07 | ✅ |

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Plan + audit doc + ADR | Plan file (this), audit summary in `docs/reports/test_surface_audit/` | A | ~5K 🟢 |
| Wave 2 | SSOT updates | 16 SSOT files: rule, AGENTS.md, path_constants × 2, blueprint package × 4, blueprint shim, taxonomy guard, apps-folder-taxonomy gate, layer_paths, chroma_paths, ArtifactPaths, apps_e2e/paths.py | B | ~12K 🟢 |
| Wave 3 | Surface scaffolding | Missing `tests/<app>/` + `tests/unit/<app>/` dirs + `__init__.py` + `conftest.py` for 8 apps × 2 surfaces × 2 files = ~20–24 stubs | C | ~6K 🟢 |
| Wave 4 | Legacy relocation | 71 `git mv apps_<app>/tests/* tests/<app>/`; rewrite app-relative imports inside moved files; remove empty `apps_<app>/tests/` dirs | D | ~25K 🟡 |
| Wave 5 | Misplaced repo-test relocation | 6 `tests/integration/apps_*/` + `tests/integration/test_apps_*` → `tests/<app>/`; `tests/e2e/test_apps_research_live.py` + `tests/runtime/test_apps_rg_e2e_proof.py` stay (cross-cutting suites) | E | ~5K 🟢 |
| Wave 6 | Enforcement | New rule `.windsurf/rules/apps-test-surface-taxonomy.md` (always_on advisory) + helper `.windsurf/scripts/_apps_test_surface_check.py` + CI gate `ops_scripts/ci/check_apps_test_surface_parity.py` (advisory; bypass `APPS_TEST_SURFACE_BYPASS=1`) + `tests/unit/windsurf_scripts/test_apps_test_surface_check.py` | F | ~12K 🟢 |
| Wave 7 | Verification | `pytest --collect-only` sanity, AEH1 gate green, governance gate green, tests/_apps_contract/ full pass | G | ~6K 🟢 |

**Total: ~71K tokens across 7 waves, mostly GREEN with one YELLOW (Wave 4 relocation risk).**

---

## Out Of Scope

- Adding new test cases or improving coverage in any moved file (pure relocation only — content unchanged except for import-path rewrites required by the move).
- Touching `tests/governance/test_apps_*` (76 files) — Q3=A user decision: leave in place as cross-cutting concern.
- Touching `tests/e2e/test_apps_research_live.py` or `tests/runtime/test_apps_rg_e2e_proof.py` — these are e2e/runtime cross-cutting harnesses, not per-app tests.
- Touching `tests/_archived_obsolete/**` — already archived.
- Modifying `tests/unit/tools_analysis/test_audit_apps_shared_stubs.py` — legitimately lives where it does (it's a tools-analysis test that happens to audit apps_shared stubs).
- Fixing or refactoring any test logic discovered during relocation — file `NEXT_STEP:` markers, do not edit.
- Promoting the new `apps-test-surface-taxonomy.md` rule from advisory to fail-closed — deferred.
- Updating downstream pytest markers (`@pytest.mark.integration`, etc.) on relocated files — deferred unless collection breaks.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Plan authored & registered in Notion | this file + Notion Plans row | — | ~3K | 🔲 TODO |
| 1.2 | Audit summary published | `docs/reports/test_surface_audit/2026-W19.md` (uses `relocate_out.txt`) | — | ~2K | 🔲 TODO |
| 2.1 | Rule update — `apps-folder-taxonomy.md` | drop `tests/` from app-internal subdir table | GAP-1 | ~1K | 🔲 TODO |
| 2.2 | Path constants — primary | `agentic_core/L0_routing/config/path_constants.py` add `APPS_TEST_SURFACES`, `apps_test_unit_dir(app)`, `apps_test_integration_dir(app)`, `apps_contract_glob(app)` | GAP-2 | ~2K | 🔲 TODO |
| 2.3 | Path constants — interface mirror | `agentic_core/interfaces/path_constants.py` re-export | — | ~1K | 🔲 TODO |
| 2.4 | Blueprint package — `_constants.py` | add `APPS_TEST_SURFACE_DEFINITION` dict; remove `tests/` from any apps_* SubfolderDefinition | GAP-3 | ~2K | 🔲 TODO |
| 2.5 | Blueprint package — `ssot.py` `derived.py` | reflect new test surface in derived registries | GAP-3 | ~2K | 🔲 TODO |
| 2.6 | Blueprint shim re-export | `structure_blueprint_config.py` re-export new names for back-compat | — | ~1K | 🔲 TODO |
| 2.7 | Runtime guard | `agentic_core/L0_routing/enforcement/apps_taxonomy_guard.py` recognize 3-surface canonical | GAP-2 | ~1K | 🔲 TODO |
| 2.8 | Taxonomy gate | `ops_scripts/ci/check_apps_folder_taxonomy.py` flag any new `apps_<x>/tests/` as violation | — | ~1K | 🔲 TODO |
| 2.9 | Cert/ADG paths sweep | `agentic_core/L4_state/config/chroma_paths.py`, `agentic_core/adg/artifact/{paths,ArtifactPaths}.py`, `agentic_core/runtime/prove_requirements/layer_paths.py`, `tools/certification/apps_e2e/paths.py` — confirm no apps_<x>/tests/ refs; if any, update | — | ~1K | 🔲 TODO |
| 2.10 | AGENTS.md | refresh test-surface section to declare 3 canonical surfaces | — | ~1K | 🔲 TODO |
| 3.1 | Scaffold missing `tests/unit/<app>/` for 5 apps | apps_eval, apps_exec, apps_lic-confirm, apps_qna-confirm, apps_repo_brief, apps_rfp; create `__init__.py` + `conftest.py` | GAP-4 | ~3K | 🔲 TODO |
| 3.2 | Scaffold missing `tests/<app>/` for 6 apps | apps_exec, apps_lic, apps_qna, apps_repo_brief, apps_rfp, apps_shared; create `__init__.py` + `conftest.py` | GAP-4 | ~3K | 🔲 TODO |
| 4.1 | Relocate apps_qna/tests/ (22 files) | `git mv apps_qna/tests/* tests/apps_qna/`; rewrite imports | GAP-5 | ~5K | 🔲 TODO |
| 4.2 | Relocate apps_eval/tests/ + services/ test (10) | git mv → `tests/apps_eval/`; resolve `services/test_discovery_service.py` location | GAP-5 | ~3K | 🔲 TODO |
| 4.3 | Relocate apps_underwriting_ai/tests/ (10) | `git mv … tests/apps_underwriting_ai/` | GAP-5 | ~3K | 🔲 TODO |
| 4.4 | Relocate apps_lic/tests/ (7) | `git mv … tests/apps_lic/` | GAP-5 | ~2K | 🔲 TODO |
| 4.5 | Relocate apps_research/tests/ (7) | `git mv … tests/apps_research/` | GAP-5 | ~2K | 🔲 TODO |
| 4.6 | Relocate apps_rfp/tests/ (6) | `git mv … tests/apps_rfp/` | GAP-5 | ~2K | 🔲 TODO |
| 4.7 | Relocate apps_rg/tests/ (5) | `git mv … tests/apps_rg/` | GAP-5 | ~2K | 🔲 TODO |
| 4.8 | Relocate apps_shared/tests/ (4) | `git mv … tests/apps_shared/` | GAP-5 | ~2K | 🔲 TODO |
| 4.9 | Remove empty `apps_<x>/tests/` dirs | 8 dirs deleted | — | ~1K | 🔲 TODO |
| 5.1 | Relocate `tests/integration/apps_*/` + filename-named misplaced tests | 6 files: `tests/integration/apps_eval/test_apps_eval_integration.py`, `tests/integration/apps_research/test_apps_research_integration.py`, `tests/integration/apps_rfp/test_apps_rfp_integration.py`, `tests/integration/apps_shared/test_apps_shared_integration.py`, `tests/integration/test_apps_qna_c0_retrieval.py`, `tests/_archived_obsolete/integration/apps_exec/...` (skip — archived) | GAP-6 | ~3K | 🔲 TODO |
| 6.1 | New rule | `.windsurf/rules/apps-test-surface-taxonomy.md` (always_on advisory) | GAP-7 | ~2K | 🔲 TODO |
| 6.2 | Helper | `.windsurf/scripts/_apps_test_surface_check.py` — pure `decide(app, fp) -> Violation \| None` | GAP-7 | ~3K | 🔲 TODO |
| 6.3 | CI gate | `ops_scripts/ci/check_apps_test_surface_parity.py` — registered in `run_contract_gates.py` after AEH1; advisory; bypass `APPS_TEST_SURFACE_BYPASS=1` | GAP-7 | ~3K | 🔲 TODO |
| 6.4 | Tests | `tests/unit/windsurf_scripts/test_apps_test_surface_check.py` — ≥30 cases | — | ~3K | 🔲 TODO |
| 7.1 | Verification | `pytest --collect-only`; `python ops_scripts/ci/check_app_domain_harness_parity.py`; `python ops_scripts/ci/check_apps_folder_taxonomy.py`; `python ops_scripts/ci/check_apps_test_surface_parity.py`; full `pytest tests/_apps_contract/` | — | ~4K | 🔲 TODO |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

**GAP-1: Rule lists `tests/` as legitimate apps_<x>/ subdir**
- `.windsurf/rules/apps-folder-taxonomy.md` row 34 lists `tests/` as "App-local unit tests" inside an `apps_*` package, perpetuating the split-root problem.
- Fix: drop the row; explicitly forbid `apps_<x>/tests/`; cross-link to new `apps-test-surface-taxonomy.md`.

**GAP-2: Path-constant SSOT files have no apps_* test-surface constants**
- Cascade and downstream tools have to re-derive `tests/<app>/`, `tests/unit/<app>/`, `tests/_apps_contract/test_<app>_*.py` glob ad hoc.
- Fix: define `APPS_TEST_SURFACES = ("contract", "unit", "integration")`, `apps_test_unit_dir(app)`, `apps_test_integration_dir(app)`, `apps_contract_glob(app)` in `agentic_core/L0_routing/config/path_constants.py` + re-export from interface mirror + structure_blueprint package.

**GAP-3: Blueprint package's apps-subfolder-map functions don't enforce 3-surface contract**
- `get_apps_eval_subfolder_map()` etc. in `structure_blueprint/ssot.py` may include `tests/` as a valid app-internal subdir.
- Fix: remove `tests/` from any apps-internal subfolder map; expose `get_apps_test_surface_definition()` returning the 3 canonical surfaces.

**GAP-4: 5 apps lack `tests/unit/<app>/` and 6 apps lack `tests/<app>/`**
- After today's audit: missing `tests/unit/<app>/` for apps_eval, apps_exec, apps_lic-confirm, apps_qna-confirm, apps_repo_brief, apps_rfp; missing `tests/<app>/` for apps_exec, apps_lic, apps_qna, apps_repo_brief, apps_rfp, apps_shared.
- Fix: scaffold `__init__.py` + `conftest.py` for each missing surface (~20-24 stubs).

**GAP-5: 71 legacy files in `apps_<app>/tests/` (Q4=A user decision)**
- Per `artifacts/_scratch/relocate_out.txt`: apps_qna 22, apps_eval 10, apps_underwriting_ai 10, apps_lic 7, apps_research 7, apps_rfp 6, apps_rg 5, apps_shared 4.
- Fix: `git mv` to `tests/<app>/`; rewrite app-relative imports inside the moved files (e.g. `from ..engines import X` → `from apps_<app>.engines import X`); delete empty source dirs.

**GAP-6: 6 misplaced repo-rooted tests**
- `tests/integration/apps_*/` (4 files: apps_eval, apps_research, apps_rfp, apps_shared) and `tests/integration/test_apps_qna_c0_retrieval.py` and `tests/integration/test_apps_eval_integration.py`.
- Fix: `git mv` to `tests/<app>/`. Note: `tests/_archived_obsolete/`, `tests/e2e/`, `tests/runtime/` excluded.
- Note: `tests/governance/test_apps_*` (76 files) explicitly LEFT IN PLACE per Q3=A.

**GAP-7: No CI enforcement against re-introducing the split**
- After consolidation, nothing prevents a future commit from re-creating `apps_<x>/tests/` or scattering tests elsewhere.
- Fix: add advisory CI gate following the established 5-component pattern (rule + helper + hook/gate + bypass + tests) — same shape as `ssot-folder-enforcement.md`, `notion-plans-status-enforcement-7a1e2d.md`.

---

## Author-Gate Decisions Captured

| Decision | User selection | Rationale |
|---|---|---|
| Q1 — Scaffolding depth for missing `tests/unit/<app>/` dirs | C — Full audit + relocate scattered tests | User explicitly chose high-cost option for real coverage gain. |
| Q2 — SSOT update scope | Full SSOT update — find ALL folder-definition files (16 found via ADG) | User intent: comprehensive consistency. |
| Q3 — `tests/governance/test_apps_*` (76 files) | A — Leave in `tests/governance/` ⭐ | Cross-cutting concern; moving fragments suite discovery; zero-risk to gate. |
| Q4 — Legacy `apps_<app>/tests/` (71 files) | A — Relocate all 71 to `tests/<app>/` | Single canonical home; matches "consistent surface" goal. |

`AG_QUEUE_SEED: plan=apps-test-surface-consolidation-11acd9 id=W6_rule_promotion depends_on=W6_landing title=promote_apps-test-surface-taxonomy_advisory_to_fail_closed_after_30day_clean`

---

## Execution Plan

### Phase 1.1 — Plan & Notion registration

**Scope**: this plan file + Plans DB row (Status=Not Started).

**Acceptance**: `.windsurf/plans/apps-test-surface-consolidation-11acd9.md` exists; Notion Plans row created with `Slug`, `Status="Not Started"`, `Plan File Path`, `Summary`, `AI Summary `.

### Phase 1.2 — Audit summary

**Scope**: `docs/reports/test_surface_audit/2026-W19.md` summarizing the 16 SSOT files + per-app counts table + 71-file legacy inventory.

**Acceptance**: report exists; cross-linked from this plan.

### Phase 2.1–2.10 — SSOT folder-definition file updates

**Files** (16):

| # | File | Edit |
|---|---|---|
| 1 | `.windsurf/rules/apps-folder-taxonomy.md` | drop `tests/` row from app-internal subdir table; cross-link new rule |
| 2 | `agentic_core/L0_routing/config/path_constants.py` | add `APPS_TEST_SURFACES`, helper functions |
| 3 | `agentic_core/interfaces/path_constants.py` | re-export new names |
| 4 | `agentic_core/L5_safety/config/structure_blueprint/_constants.py` | add `APPS_TEST_SURFACE_DEFINITION` dict |
| 5 | `agentic_core/L5_safety/config/structure_blueprint/ssot.py` | remove `tests/` from any apps-internal subfolder map; add `get_apps_test_surface_definition()` |
| 6 | `agentic_core/L5_safety/config/structure_blueprint/derived.py` | reflect new surface in derived registries |
| 7 | `agentic_core/L5_safety/config/structure_blueprint/__init__.py` | export new names in `__all__` |
| 8 | `agentic_core/L5_safety/config/structure_blueprint_config.py` | re-export new names (deprecated shim) |
| 9 | `agentic_core/L0_routing/enforcement/apps_taxonomy_guard.py` | recognize 3-surface canonical; flag `apps_<x>/tests/` as violation |
| 10 | `ops_scripts/ci/check_apps_folder_taxonomy.py` | flag `apps_<x>/tests/` as violation |
| 11 | `agentic_core/L4_state/config/chroma_paths.py` | confirm no apps_<x>/tests/ refs (likely no-op) |
| 12 | `agentic_core/adg/artifact/paths.py` | confirm; likely no-op |
| 13 | `agentic_core/adg/artifact/ArtifactPaths.py` | confirm; likely no-op |
| 14 | `agentic_core/runtime/prove_requirements/layer_paths.py` | confirm; likely no-op |
| 15 | `tools/certification/apps_e2e/paths.py` | confirm; likely no-op |
| 16 | `AGENTS.md` | declare 3 canonical surfaces |

**Acceptance**: every file edited or explicitly noted as no-op; existing tests pass; no new pyright errors.

### Phase 3.1, 3.2 — Surface scaffolding

**Scope**: create `__init__.py` + `conftest.py` for each missing `tests/<app>/` and `tests/unit/<app>/`.

**Commands**:

```bash
# Per app, per missing surface:
mkdir -p tests/<surface>/<app>
echo "" > tests/<surface>/<app>/__init__.py
# minimal conftest.py
```

**Acceptance**: `pytest --collect-only tests/<app>/` and `pytest --collect-only tests/unit/<app>/` succeed (zero collected tests is fine for newly-scaffolded dirs).

### Phase 4.1–4.9 — Relocate 71 legacy files

**Scope**: `git mv apps_<app>/tests/* tests/<app>/` per app; rewrite app-relative imports.

**Per-app recipe**:

```bash
git mv apps_qna/tests/test_acceptance.py tests/apps_qna/test_acceptance.py
# (repeat for each file)
# rewrite ../engines, ../config style imports to apps_qna.engines, apps_qna.config
python tools/test_relocation/rewrite_imports.py --root tests/apps_qna --app apps_qna   # tool to be authored as part of W4
```

**Acceptance**: `pytest --collect-only tests/<app>/` succeeds for all 8 apps; each moved file imports cleanly; no `apps_<x>/tests/` directory remains.

### Phase 5.1 — Misplaced repo-test relocation

**Scope**: `git mv` 6 files from `tests/integration/apps_*/` and `tests/integration/test_apps_*` to `tests/<app>/`.

**Acceptance**: `pytest --collect-only` whole-tree succeeds.

### Phase 6.1–6.4 — New CI enforcement

**Files**:

- `.windsurf/rules/apps-test-surface-taxonomy.md` (always_on advisory)
- `.windsurf/scripts/_apps_test_surface_check.py` — `decide(app, fp) -> Violation | None`
- `ops_scripts/ci/check_apps_test_surface_parity.py` — registered in `run_contract_gates.py`
- `tests/unit/windsurf_scripts/test_apps_test_surface_check.py` — ≥30 cases

**Bypass**: `APPS_TEST_SURFACE_BYPASS=1`.

**Acceptance**: gate runs green; tests pass; violation row produced when any apps_<x>/tests/ re-appears.

### Phase 7.1 — Verification

**Commands**:

```bash
pytest --collect-only 2>&1 | tail -50
python ops_scripts/ci/check_app_domain_harness_parity.py
python ops_scripts/ci/check_apps_folder_taxonomy.py
python ops_scripts/ci/check_apps_test_surface_parity.py
python -m pytest tests/_apps_contract/ -q
python -m pytest tests/governance/ -k apps_ -q
```

**Acceptance**: all green; AEH1 ERROR=0 WARN=0 INFO=0; governance suite count unchanged from baseline.

---

## Rules

- No new test logic added — pure relocation + import rewrites.
- `tests/governance/test_apps_*` (76 files) NOT TOUCHED (Q3=A).
- `tests/_archived_obsolete/**`, `tests/e2e/`, `tests/runtime/` NOT TOUCHED.
- Every edit obeys constitutional §31 SSOT folder routing for any new file.
- Every relocation is `git mv` (preserves history); never copy-and-delete.
- Pre-commit gate runs before each wave commits.

---

## Success Criteria

- [ ] All 10 `apps_*` packages have a populated or scaffolded `tests/<app>/` (8 with content, 2 with stub: apps_repo_brief, apps_shared if no real integration tests).
- [ ] All 10 `apps_*` packages have a populated or scaffolded `tests/unit/<app>/`.
- [ ] All 10 `apps_*` packages have ≥1 file in `tests/_apps_contract/test_<app>_*.py` (apps_shared exempt — library, no contract row).
- [ ] Zero `apps_<x>/tests/` directories remain.
- [ ] 71 + 6 = 77 files relocated via `git mv` (history preserved).
- [ ] All 16 SSOT folder-definition files updated or explicitly verified no-op.
- [ ] `pytest --collect-only` whole-tree succeeds.
- [ ] `tests/_apps_contract/` test count unchanged (255 baseline) or higher.
- [ ] `tests/governance/test_apps_*` count unchanged (76 baseline).
- [ ] AEH1 gate: ERROR=0 WARN=0 INFO=0.
- [ ] New CI gate `check_apps_test_surface_parity.py` registered and green.
- [ ] New rule `apps-test-surface-taxonomy.md` always_on; `apps-folder-taxonomy.md` no longer lists `tests/` as app-internal subdir.
- [ ] Plan registered in Notion Plans DB (Status: Completed at end).

---

## Implementation Commands

```bash
# Wave 1
# (this plan + Notion registration)

# Wave 2 (per file)
# manual edits via Cascade edit tool

# Wave 3 (per app)
mkdir -p tests/apps_<app> tests/unit/apps_<app>
type nul > tests/apps_<app>/__init__.py
type nul > tests/unit/apps_<app>/__init__.py
# author conftest.py manually

# Wave 4 (per app, per file)
git mv apps_<app>/tests/<file>.py tests/apps_<app>/<file>.py
# rewrite imports inside file

# Wave 5
git mv tests/integration/apps_<app>/test_*.py tests/apps_<app>/

# Wave 6
# author rule + helper + gate + tests via edit tool
python -m pytest tests/unit/windsurf_scripts/test_apps_test_surface_check.py -q

# Wave 7
pytest --collect-only > artifacts/_scratch/collect_post.txt 2>&1
python ops_scripts/ci/check_app_domain_harness_parity.py
python ops_scripts/ci/check_apps_test_surface_parity.py
python -m pytest tests/_apps_contract/ -q
```

---

## Rollback Strategy

If a wave breaks pytest collection or a CI gate:

1. **Wave 4/5 (relocations)**: `git restore --source HEAD~<n> -- <path>` per file; the `git mv` history makes the inverse trivial. Never delete the source files until pytest passes.
2. **Wave 2 (SSOT edits)**: `git restore <file>`; SSOT files are read by many consumers — restore one at a time, run the affected gate, iterate.
3. **Wave 6 (new gate)**: set `APPS_TEST_SURFACE_BYPASS=1` in CI to suppress; revert the gate registration line in `run_contract_gates.py`; keep the helper + tests for next attempt.
4. **Whole-plan abort**: `git revert <merge-commit>`; the plan is structured so each wave is its own commit, making partial rollback feasible.

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| `apps_<x>/tests/` dirs remaining | 0 | `find apps_* -type d -name tests` |
| Files relocated via `git mv` | 71 + 6 = 77 | `git log --diff-filter=R --name-status --since="<plan-start>"` |
| `tests/_apps_contract/` count | ≥255 | `pytest --collect-only tests/_apps_contract/ 2>&1 \| grep "test session"` |
| `tests/governance/test_apps_*` count | =76 | `find tests/governance -name "test_apps_*.py" \| wc -l` |
| AEH1 gate exit code | 0 | `python ops_scripts/ci/check_app_domain_harness_parity.py; echo $?` |
| New gate exit code | 0 | `python ops_scripts/ci/check_apps_test_surface_parity.py; echo $?` |
| pytest --collect-only whole-tree | succeeds | exit 0 |
| SSOT files updated or no-op-verified | 16 / 16 | per-file checklist in Phase 2 |

## Cascade Alignment Checks

- Always-on rules stay lean — detailed enforcement procedures live in the helper + skill.
- ADG SQLite is the audit primary source (already executed; results in `artifacts/_scratch/`).
- Structural matches via filename heuristic + canonical-home check before semantic expansion.
- Pre-execution evidence already gathered: 16 SSOT files identified, 71 + 6 + 76 file inventory complete.
- Deterministic enforcement is the new CI gate, not template prose.
