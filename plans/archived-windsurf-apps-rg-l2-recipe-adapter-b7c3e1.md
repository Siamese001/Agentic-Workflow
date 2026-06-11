---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-rg-l2-recipe-adapter-b7c3e1.md'
original_relative_path: 'apps-rg-l2-recipe-adapter-b7c3e1.md'
source_sha256: a7cdf7a856c9801a3b86f5aca765068b08b5c5c4820ffa9fa78d4f78d5887906
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-04'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-l2-recipe-adapter-b7c3e1
plan_type: refactor
---

# Remove Hand-Built L2 Closure from apps_rg/__main__.py

Replace the hand-built `_build_l2_callable()` domain execution closure with a registry-resolved L2 recipe adapter. After this plan, `apps_rg/__main__.py` passes only `raw_request` to the R4 runner, and the runner resolves the L2 execution recipe from registry/static DAG config.

---

## Context (SCQA)

- **Situation** — `apps_rg/__main__.py` was refactored (plan `apps-rg-canonical-wireup-c8a4f2`) to delegate all execution to the R4 pipeline via `run_integrated_single_action_spine`. The file currently builds a hand-crafted `_build_l2_callable()` closure that directly calls `generate_resume.main()`, `narrative_pass`, and `docx_exporter`. The static DAG YAML at `apps_rg/config/apps_rg_static_dag.yaml` already defines `hop_4_generate_resume`, `hop_5_narrative_pass`, `hop_6_docx_export` as distinct L2 executor steps. The `StaticDagRegistry` in `agentic_core/L3_orchestration/registry/static_dag_registry.py` provides the pattern for DAG registration.

- **Complication** — The l2_callable closure violates the separation goal: `__main__.py` still contains 80 lines of domain execution logic (`_build_l2_callable` + `_run_post_pipeline`). This makes `__main__.py` impossible to test in isolation from the HOP pipeline, prevents the R4 runner from validating step-level receipts, and couples the entrypoint to legacy subprocess-based invocation patterns.

- **Question** — How do we remove all domain execution logic from `apps_rg/__main__.py` so it becomes a pure argument-parser + R4 delegation shim?

- **Answer** — Create an `apps_rg.l2_recipe` module that registers the apps_rg execution recipe with the `StaticDagRegistry`, expose a `resolve_l2_callable(dag_id, args)` function that the R4 runner (or `__main__.py`) can call, and strip `_build_l2_callable` + `_run_post_pipeline` from `__main__.py`.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `apps_rg/__main__.py` | Current l2_callable closure to remove | 🔲 |
| `apps_rg/config/apps_rg_static_dag.yaml` | Authoritative L2 step definitions | 🔲 |
| `agentic_core/L3_orchestration/registry/static_dag_registry.py` | Registry pattern to extend | 🔲 |
| `agentic_core/runtime/entrypoints/integrated_single_action_spine_run.py` | R4 API to adapt | 🔲 |
| `tests/_apps_contract/test_apps_rg_fail_closed.py` | Must preserve | 🔲 |

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | L2 recipe adapter created, registered | `apps_rg/l2_recipe/` | A | ~15K 🟢 |
| Wave 2 | R4 runner resolves callable from registry | `agentic_core/runtime/entrypoints/`, `apps_rg/__main__.py` | B | ~12K 🟢 |
| Wave 3 | Remove closure + post_pipeline from __main__ | `apps_rg/__main__.py` | C | ~5K 🟢 |
| Wave 4 | Tests proving new contract | `tests/_apps_contract/` | D | ~10K 🟢 |

**Total: ~42K tokens across 4 waves, all GREEN**

---

## Out Of Scope

- Changing the R4 pipeline's internal U0/L1/L0/Exit V6 logic
- Adding OTEL spans inside L2 step adapters (future plan)
- Converting subprocess-based narrative_pass/docx_export to in-process calls (already tracked in `apps_rg_static_dag.yaml` as "in-process W3 P8")
- Modifying `generate_resume.main()` internals
- Any changes to `apps_rg/prompt_assembly/pa_local.py`
- Notion writeback (deferred to plan end)

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Create L2 step adapter module | `apps_rg/l2_recipe/__init__.py`, `apps_rg/l2_recipe/steps.py` | PP-1: no adapter pattern exists | ~8K | 🔲 TODO |
| 1.2 | Register apps_rg DAG in StaticDagRegistry | `apps_rg/l2_recipe/registry.py`, `agentic_core/L3_orchestration/registry/static_dag_registry.py` | PP-2: registry only has demo DAG | ~7K | 🔲 TODO |
| 2.1 | Add `resolve_l2_callable` to R4 pipeline or __main__ | `agentic_core/runtime/entrypoints/integrated_single_action_spine_run.py` OR `apps_rg/__main__.py` | PP-3: API doesn't accept app_name yet | ~8K | 🔲 TODO |
| 2.2 | Rewrite __main__.py to use resolver | `apps_rg/__main__.py` | — | ~4K | 🔲 TODO |
| 3.1 | Remove `_build_l2_callable` + `_run_post_pipeline` | `apps_rg/__main__.py` | — | ~5K | 🔲 TODO |
| 4.1 | Test: __main__.py contains no domain closure | `tests/_apps_contract/test_apps_rg_no_domain_closure.py` | — | ~3K | 🔲 TODO |
| 4.2 | Test: R4 resolves apps_rg recipe from registry | `tests/_apps_contract/test_apps_rg_recipe_resolution.py` | — | ~4K | 🔲 TODO |
| 4.3 | Test: narrative + DOCX only as registered L2 steps | `tests/_apps_contract/test_apps_rg_l2_steps.py` | — | ~3K | 🔲 TODO |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

**GAP-1: R4 pipeline API does not accept `app_name` or registry lookup**
- Current signature: `run_integrated_single_action_spine(*, raw_request, l2_callable, artifact_dir, ...)`
- Impact: Either (a) add an optional `dag_id` param that auto-resolves the callable, or (b) move resolution to `__main__.py` which calls the resolver before passing to R4. Option (b) is simpler and preserves R4's generality.
- Decision: **Option (b)** — `__main__.py` calls `resolve_l2_callable(dag_id, raw_request)` and passes the result to R4. The resolver is in `apps_rg.l2_recipe.registry`.

**GAP-2: narrative_pass and docx_export currently use subprocess.run**
- The static DAG YAML labels them as "in-process (W3 P8)" — the plan to convert them exists.
- For this plan, the L2 step adapter wraps the existing subprocess invocations. The adapter is the registration surface; internal implementation can migrate later.
- Impact: minimal — the adapter pattern is correct regardless of whether steps are in-process or subprocess.

---

## Execution Plan

### Phase 1.1 — Create L2 Step Adapter Module

**Scope**: Create `apps_rg/l2_recipe/` with step adapters for each L2 execution node.

**Files**:
- `apps_rg/l2_recipe/__init__.py` — package init, exports
- `apps_rg/l2_recipe/steps.py` — `GenerateResumeStep`, `NarrativePassStep`, `DocxExportStep`
  Each step is a callable class with `__call__(self, context: dict) -> dict` interface.

**Acceptance**: Each step can be instantiated and called in isolation with a test context dict.

### Phase 1.2 — Register apps_rg DAG in StaticDagRegistry

**Scope**: Add `apps_rg.resume_generation_v1.static_dag` to the default registry catalog.

**Files**:
- `apps_rg/l2_recipe/registry.py` — builds `StaticDagProof` from YAML and exposes `resolve_l2_callable(dag_id, raw_request) -> Callable[[], Any]`
- Update `agentic_core/L3_orchestration/registry/static_dag_registry.py` — import apps_rg DAG builder and add to default catalog

**Acceptance**: `get_default_registry().get("apps_rg.resume_generation_v1.static_dag")` returns a valid proof.

### Phase 2.1 — Expose resolve_l2_callable

**Scope**: The resolver reads the DAG spec, chains the step adapters (hop_4 → hop_5 → hop_6), and returns a zero-argument callable.

**Files**:
- `apps_rg/l2_recipe/registry.py` — `resolve_l2_callable(raw_request: dict) -> Callable[[], dict]`

**Acceptance**: Calling `resolve_l2_callable(request)` returns a callable that, when invoked, executes hop_4 → hop_5 → hop_6 in sequence.

### Phase 2.2 — Rewrite __main__.py to use resolver

**Scope**: Replace `_build_l2_callable(args)` call with `resolve_l2_callable(raw_request)`.

**Target `__main__.py` shape**:
```python
from apps_rg.l2_recipe.registry import resolve_l2_callable

def main() -> None:
    if not _RUNNER_AVAILABLE:
        ...fail closed...

    args = parse_args()
    raw_request = _build_raw_request(args)
    l2_callable = resolve_l2_callable(raw_request)
    artifact_dir = Path(...)

    result = run_integrated_single_action_spine(
        raw_request=raw_request,
        l2_callable=l2_callable,
        artifact_dir=artifact_dir,
        policy_hash=raw_request["policy_hash"],
        blueprint_hash=raw_request["blueprint_hash"],
    )
    ...propagate exit code...
```

**Acceptance**: `main()` is <50 lines. No domain imports inside `main()`.

### Phase 3.1 — Remove dead code

**Scope**: Delete `_build_l2_callable()` and `_run_post_pipeline()` from `__main__.py`.

**Acceptance**: `grep -n "generate_resume\|narrative_pass\|docx_exporter\|_run_post_pipeline\|_build_l2_callable" apps_rg/__main__.py` returns zero hits.

### Phase 4.1 — Test: no domain closure in __main__

**Scope**: Source-inspection test proving `apps_rg/__main__.py` contains no domain execution code.

**Assertions**:
- `_build_l2_callable` not in source
- `_run_post_pipeline` not in source
- `generate_resume` not in source
- `narrative_pass` not in source
- `docx_exporter` not in source
- `asyncio.run` not in source
- `subprocess.run` not in source

### Phase 4.2 — Test: R4 resolves from registry

**Scope**: Test that `resolve_l2_callable(raw_request)` returns a valid zero-arg callable whose execution surface is registered in the static DAG.

**Assertions**:
- `resolve_l2_callable(request)` returns a callable
- The callable takes zero arguments
- `get_default_registry().get("apps_rg.resume_generation_v1.static_dag")` succeeds
- The proof's node list includes hop_4, hop_5, hop_6

### Phase 4.3 — Test: narrative + DOCX only as registered steps

**Scope**: Test that `NarrativePassStep` and `DocxExportStep` are the ONLY way to invoke narrative/DOCX logic.

**Assertions**:
- `apps_rg/l2_recipe/steps.py` contains `NarrativePassStep` and `DocxExportStep`
- No other file in `apps_rg/` (except `l2_recipe/steps.py`) contains a call to `narrative_pass` or `docx_exporter` as subprocess/import (excluding test files)
- `apps_rg/__main__.py` has zero references to narrative_pass or docx_exporter

---

## Rules

- Existing fail-closed tests (`test_apps_rg_fail_closed.py`) MUST continue to pass without modification.
- `apps_rg/__main__.py` must remain <80 lines total after this refactor.
- No changes to the R4 pipeline's function signature (l2_callable remains a `Callable[[], Any]` param).
- L2 step adapters must preserve the current behavior: generate_resume runs first, then narrative_pass (conditional on target_company), then DOCX export.
- The static DAG YAML is read-only in this plan (it already has the correct step definitions).

---

## Success Criteria

- [ ] `apps_rg/__main__.py` contains zero domain execution code (no generate_resume, narrative_pass, docx_exporter, subprocess, asyncio.run)
- [ ] `_build_l2_callable` and `_run_post_pipeline` are deleted from `__main__.py`
- [ ] `apps_rg/l2_recipe/steps.py` defines `GenerateResumeStep`, `NarrativePassStep`, `DocxExportStep`
- [ ] `apps_rg/l2_recipe/registry.py` defines `resolve_l2_callable(raw_request) -> Callable`
- [ ] `apps_rg.resume_generation_v1.static_dag` is registered in `get_default_registry()`
- [ ] 35 existing tests continue to pass (test_apps_rg_fail_closed + test_apps_rg_artifact_completeness + test_apps_rg_acceptance_checks)
- [ ] 3+ new tests prove the no-closure, registry-resolution, and step-only constraints

---

## Rollback Strategy

If things go wrong:
1. Restore `_build_l2_callable` and `_run_post_pipeline` from git (the previous commit has the full functions)
2. Revert `__main__.py` to call `_build_l2_callable(args)` directly
3. Remove `apps_rg/l2_recipe/` directory
4. Revert any changes to `static_dag_registry.py`

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| `__main__.py` line count | <80 lines | `wc -l apps_rg/__main__.py` |
| Domain keywords in `__main__.py` | 0 | grep for generate_resume, narrative_pass, docx_exporter, subprocess, asyncio |
| Existing test suite | 35/35 pass | `pytest tests/_apps_contract/test_apps_rg_*.py` |
| New test suite | 3+ pass | `pytest tests/_apps_contract/test_apps_rg_no_domain_closure.py test_apps_rg_recipe_resolution.py test_apps_rg_l2_steps.py` |
| Registry resolution | succeeds | `resolve_l2_callable(request)` returns callable |

## Cursor Agent Alignment Checks

- Keep always-on rules lean; place detailed procedures in skills or workflows.
- Retrieve local or scoped evidence before synthesis.
- Prefer exact or structural matches before broad semantic expansion.
- For high-risk outputs, extract evidence or quotes before summarizing.
- Reserve deterministic enforcement for hooks or scripts, not template prose.
