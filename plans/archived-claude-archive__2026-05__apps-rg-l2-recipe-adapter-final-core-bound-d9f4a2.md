---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-rg-l2-recipe-adapter-final-core-bound-d9f4a2.md'
original_relative_path: '_archive\\2026-05\\apps-rg-l2-recipe-adapter-final-core-bound-d9f4a2.md'
source_sha256: 334311522c13d29cd10e25aa275335cba3f8ddf734e0aef4b6af891271fbafa6
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-l2-recipe-adapter-final-core-bound-d9f4a2
plan_type: refactor
---

# apps_rg L2 Recipe Adapter — Final Core-Bound Architecture

Supersedes the flawed Option B in `apps-rg-l2-recipe-adapter-b7c3e1` which left recipe resolution on the app side. This plan makes agentic_core the sole owner of recipe resolution and L2 execution.

---

## Context (SCQA)

- **Situation** — `apps_rg/__main__.py` currently builds a hand-crafted `_build_l2_callable()` closure and passes it to the R4 runner. The prior plan (`apps-rg-l2-recipe-adapter-b7c3e1`) proposed Option B: move the closure to `resolve_l2_callable()` in `apps_rg.l2_recipe.registry`, still called from `apps_rg/__main__.py`. The static DAG YAML and `StaticDagRegistry` infrastructure already exist in agentic_core.

- **Complication** — Option B violates sovereignty: apps_rg still resolves and injects executable work into agentic_core. The canonical dependency law requires agentic_core to own recipe resolution. apps_rg must only declare step implementations; it must never construct, resolve, or pass an executable callable.

- **Question** — How do we achieve true core-bound architecture where apps_rg is incapable of producing artifacts without agentic_core's governed L2 path?

- **Answer** — Extend the R4 runner to accept `app_name` instead of `l2_callable`, resolve the recipe inside agentic_core from the registered static DAG, and reduce `apps_rg/__main__.py` to a pure transport shim.

---

## Supersession Notice

This plan **explicitly supersedes** the following from `apps-rg-l2-recipe-adapter-b7c3e1`:
- ❌ Option B: `apps_rg/__main__.py` calls `resolve_l2_callable(raw_request)` — REJECTED
- ❌ Phase 2.1: "Expose resolve_l2_callable" — REJECTED
- ❌ Phase 2.2: "Rewrite __main__.py to use resolver" — REJECTED (resolver must not be called by apps_rg)

Correct architecture:
- ✅ `apps_rg/__main__.py` passes `app_name="apps_rg"` + `raw_request` only
- ✅ `agentic_core` R4 runner resolves recipe by `app_name` from registry
- ✅ `apps_rg/l2_recipe/` only registers and implements step classes
- ✅ Executable callable injection from app-side is forbidden in production

---

## Canonical Dependency Law

```
ALLOWED:
  apps_rg  →  calls agentic_core runner (with app_name + raw_request only)
  agentic_core  →  resolves apps_rg registered step implementations from registry
  agentic_core  →  invokes apps_rg L2 steps inside governed L2 execution

FORBIDDEN:
  apps_rg  →  resolves executable callable
  apps_rg  →  constructs L2 callable
  apps_rg  →  passes l2_callable to R4 runner
  apps_rg  →  runs HOP pipeline directly
  apps_rg  →  builds prompts directly for model call
  apps_rg  →  calls model directly
  apps_rg  →  writes artifacts outside L2/Exit path
  apps_rg  →  cache commits outside Exit/UWG
```

---

## Wave Structure

| Wave | Metric | Scope | Checkpoint | Tokens |
|------|--------|-------|------------|--------|
| W1 | L2 step adapters created | `apps_rg/l2_recipe/` | A | ~12K ✅ DONE |
| W2 | R4 runner accepts app_name, resolves recipe | `agentic_core/runtime/entrypoints/` | B | ~15K ✅ DONE |
| W3 | __main__.py is pure shim | `apps_rg/__main__.py` | C | ~5K ✅ DONE |
| W4 | Tests prove sovereignty | `tests/_apps_contract/` | D | ~15K ✅ DONE |

**Total: ~47K tokens across 4 waves, all GREEN**

---

## Out Of Scope

- Converting narrative_pass/docx_exporter subprocess calls to in-process (tracked separately)
- Full CompiledPromptArtifact pipeline (PA guard is fail-closed stub for now)
- R4 runner changes for other apps (apps_lic, apps_rfp, etc.)
- Notion writeback
- OTEL span instrumentation inside step adapters

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Create L2 step adapter classes | `apps_rg/l2_recipe/__init__.py`, `apps_rg/l2_recipe/steps.py` | No adapter pattern exists yet | ~8K | ✅ DONE |
| 1.2 | Create recipe registration module | `apps_rg/l2_recipe/registry.py` | Registry metadata only, not resolution | ~4K | ✅ DONE |
| 2.1 | Extend R4 runner API with app_name param | `agentic_core/runtime/entrypoints/integrated_r4_deterministic_pipeline_run.py` | Must preserve backward compat for tests | ~8K | ✅ DONE |
| 2.2 | Add recipe resolver inside R4 runner | `agentic_core/runtime/entrypoints/integrated_r4_deterministic_pipeline_run.py` | Must map app_name→DAG→callable | ~7K | ✅ DONE |
| 3.1 | Strip __main__.py to pure shim | `apps_rg/__main__.py` | Remove 140 lines of domain code | ~5K | ✅ DONE |
| 4.1 | Register apps_rg DAG in core registry | `agentic_core/runtime/l2_recipe_resolver.py` | Lazy-load via apps_rg.l2_recipe.registry | ~4K | ✅ DONE |
| 5.1 | PA guard on LLM-backed steps | `apps_rg/l2_recipe/steps.py` | Fail-closed stub | ~3K | ✅ DONE |
| 6.1 | Test: __main__ is thin shim | `tests/_apps_contract/test_apps_rg_main_is_thin_core_shim.py` | — | ~3K | ✅ DONE |
| 6.2 | Test: core resolves recipe | `tests/_apps_contract/test_apps_rg_core_resolves_l2_recipe.py` | — | ~3K | ✅ DONE |
| 6.3 | Test: cannot inject l2_callable | `tests/_apps_contract/test_apps_rg_cannot_inject_l2_callable.py` | — | ~3K | ✅ DONE |
| 6.4 | Test: missing recipe fails closed | `tests/_apps_contract/test_apps_rg_missing_recipe_fails_closed.py` | — | ~3K | ✅ DONE |
| 6.5 | Test: steps only via core recipe | `tests/_apps_contract/test_apps_rg_l2_steps_only_via_core_recipe.py` | — | ~3K | ✅ DONE |
| 6.6 | Test: LLM step requires PA | `tests/_apps_contract/test_apps_rg_llm_step_requires_pa_artifact.py` | — | ~3K | ✅ DONE |

---

## Gap Register

**GAP-1: R4 runner must support app_name without breaking existing callers**
- Solution: Add `app_name: str = ""` param. When non-empty AND `l2_callable` is None, resolve from registry. When `l2_callable` is provided with `_test_mode=True`, allow (test compat). When `l2_callable` is provided without test mode flag for a production app_name, fail closed.

**GAP-2: Step adapter → callable bridge**
- The registry maps `app_name` → recipe metadata → ordered list of step classes → composite callable.
- The composite callable chains GenerateResumeStep → NarrativePassStep → DocxExportStep.
- This bridge lives in `agentic_core/runtime/l2_recipe_resolver.py` (core-owned, not app-owned).

---

## Execution Plan

### W1 P1.1 — L2 Step Adapters

Create `apps_rg/l2_recipe/steps.py`:
- `GenerateResumeStep.__call__(context: dict) -> dict` — wraps `generate_resume.main()`
- `NarrativePassStep.__call__(context: dict) -> dict` — wraps narrative_pass subprocess
- `DocxExportStep.__call__(context: dict) -> dict` — wraps docx_exporter subprocess
- Each step is a registered implementation only. No routing, no Exit, no L4 write.

### W1 P1.2 — Recipe Registration

Create `apps_rg/l2_recipe/registry.py`:
- `APPS_RG_DAG_ID = "apps_rg.resume_generation_v1.static_dag"`
- `APPS_RG_L2_STEPS` — ordered tuple of step classes
- `get_apps_rg_recipe_metadata() -> dict` — returns step list + DAG ID + route binding
- This module is IMPORTED BY agentic_core (not by apps_rg/__main__.py)

### W2 P2.1 — R4 Runner API Extension

Add to `run_integrated_r4_deterministic_pipeline`:
```python
def run_integrated_r4_deterministic_pipeline(
    *,
    raw_request: dict[str, Any],
    app_name: str = "",
    l2_callable: Callable[[], Any] | None = None,  # deprecated for production
    artifact_dir: Path,
    policy_hash: str = "",
    blueprint_hash: str = "",
    _test_mode: bool = False,
) -> R4IntegratedRunResult:
```

### W2 P2.2 — Core-Owned Recipe Resolver

Create `agentic_core/runtime/l2_recipe_resolver.py`:
- `resolve_l2_recipe(app_name: str, raw_request: dict) -> Callable[[], Any]`
- Imports `apps_rg.l2_recipe.registry` to get step classes
- Chains steps into a composite zero-arg callable
- Fails closed if app_name has no registered recipe

### W3 P3.1 — Pure Shim __main__.py

Final shape:
```python
result = run_integrated_r4_deterministic_pipeline(
    app_name="apps_rg",
    raw_request=raw_request,
    artifact_dir=artifact_dir,
    policy_hash=raw_request["policy_hash"],
    blueprint_hash=raw_request["blueprint_hash"],
)
```

---

## Rules

- `apps_rg/__main__.py` must not import anything from `apps_rg.l2_recipe`
- `apps_rg/__main__.py` must not contain `l2_callable` as a variable or parameter
- `l2_callable` param on R4 runner is deprecated; only allowed with `_test_mode=True`
- Production path: `app_name` → core resolves → core executes
- All existing 35 tests must pass (with minor mock adjustments for new API)

---

## Success Criteria

- [x] `apps_rg/__main__.py` zero hits for forbidden keywords
- [x] R4 runner resolves recipe by `app_name="apps_rg"` without caller-supplied callable
- [x] Missing recipe → fail closed (exit 1, no artifacts)
- [x] Injecting l2_callable without _test_mode → fail closed
- [x] L2 steps registered in `apps_rg/l2_recipe/steps.py`
- [x] LLM-backed steps fail closed without PA artifact
- [x] 137 existing tests pass (0 regressions)
- [x] 39 new targeted tests pass (6 new files)
- [x] `apps_rg` cannot produce résumé artifacts when recipe resolution is disabled

---

## Rollback Strategy

1. Restore `_build_l2_callable` + `_run_post_pipeline` from prior commit
2. Revert R4 runner `app_name` param addition
3. Delete `apps_rg/l2_recipe/` directory
4. Delete `agentic_core/runtime/l2_recipe_resolver.py`
