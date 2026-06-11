---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\apps-rg-entrypoint-convergence-e7f3c2.md'
original_relative_path: '_archive\\apps-rg-entrypoint-convergence-e7f3c2.md'
source_sha256: c444b4046011773a358b85b8c6f8f1578be2962315c24a6f0935b4d1032b440d
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
> **ARCHIVED** — Superseded by **apps-rg-canonical-dispatch-l7-gate-c8a4d1** (active SSOT: `.cursor/plans/apps-rg-canonical-dispatch-l7-gate-c8a4d1.md` + matching Notion Plans row). Do not execute this document as current work.

# apps_rg single product entrypoint — dispatch vs R4 vs section seams (plan)

**Status:** Archived (superseded)  
**Slug:** `apps-rg-entrypoint-convergence-e7f3c2`  
**Scope:** apps_rg runtime entry surfaces, `agentic_core/runtime/entry/apps_rg_dispatch.py`, `integrated_r4_deterministic_pipeline_run`, section `*_dispatch` modules, L7 / recipe registry alignment  
**Non-goal (this plan):** Implement wiring in this document’s pass — execution is a follow-up.

---

## 1. Problem statement

There must be **one mental product entrypoint** for apps_rg. The repo currently exposes **three surfaces** because migration is incomplete:

| Surface | Role today | Should generate resume sections? |
|--------|------------|-----------------------------------|
| `apps_rg/runtime/dispatch/apps_rg_dispatch.py` | App-owned ingress: dict/envelope → `RequestEnvelope` / payload; forwards to core | **No** — parse + forward only |
| `agentic_core/runtime/entry/apps_rg_dispatch.py` | Core-visible shim: re-export `apps_rg_parse`, AG-2 `run_ag2_retrieval_and_prompt`, **`dispatch_apps_rg_run` stub** | **No** for full resume (except AG-2 C0/PA contract seam) |
| `integrated_r4_*` + `apps_rg.runtime.dispatch.*_dispatch` | **Actual runtime** for certification slices and R4 spine + section proofs | **Yes** — where real work runs today |

**Naming hazard:** `dispatch_apps_rg_run` reads like the canonical runtime but is a **stub-shaped future hook** (“no live LLM” seam). That mismatch is the main source of confusion.

**Architecture gap:** Governed spine should read as:

`ValidatedRequest → L1PlanContract → RouteContract → C0/PA/L3/L2 → Exit → X3`

Today apps_rg often looks like:

`parse/envelope → stub dispatch → separate integrated R4 and/or per-section dispatch CLIs`

That is a **transitional split**, not the declared end-state.

---

## 2. Target end-state (north star)

```text
apps_rg_parse          # U0 / app ingress adapter
        ↓
dispatch_apps_rg_run # THE single product hook — real governed spine (not stub)
        ↓
U0 → L1 → L0 → C0/PA (when required) → L3 or R4-shaped workflow → L2 (recipe) → Exit → X3
```

- **`integrated_r4_*`** becomes an **internal implementation** invoked from `dispatch_apps_rg_run` (or one thin orchestrator), not a competing “product” entrypoint for operators.
- **Section `*_dispatch` modules** either:
  - **A)** become **library functions** called from the L2 recipe / one spine run, or  
  - **B)** remain **dev/cert slice CLIs** only (`python -m ...`) with docs stating they are **not** the product path.

Honest labeling:

- `apps_rg_parse` = **ingress adapter**
- `dispatch_apps_rg_run` = **canonical product runtime** (rename stub if wiring slips)
- `integrated_r4_*` = **current spine implementation** until folded behind dispatch

---

## 3. Why the current layout exists (keep until replaced)

- **Stable import paths** for CI and contract tests (`apps_rg_parse`, AG-2 scan target in core entry module).
- **App-owned parse** keeps ingress shape out of core leakage.
- **Stub** avoids false “we ran the full LLM pipeline” claims while spine is unfinished.
- **Section dispatches** preserve **golden-path** iteration (exec summary, unify, IBM, competencies) without always paying full integrated-runtime cost.

---

## 4. Preconditions / repo facts to resolve in W1

1. **`apps_rg.l2_recipe.registry`** — `agentic_core/runtime/l2_recipe_resolver.py` expects `get_apps_rg_recipe_metadata`; registry module may be missing or incomplete. **Without this, `run_integrated_r4_deterministic_pipeline(..., app_name="apps_rg")` cannot be the production path.**
2. **`python -m apps_rg`** currently calls `dispatch_apps_rg_run` stub — no R4, no sections.
3. **`GovernedRun` L7 block** (`apps_shared/spine_emission/context.py`) uses broad `except Exception: pass` — if dispatch ever delegates there, fail-soft L7 undermines audit story.
4. **Contract tests** that patch `rg_main.run_integrated_r4_deterministic_pipeline` may assume `__main__` symbols that no longer match `__main__.py` — reconcile when wiring.

---

## 5. Phased work (implementation deferred to follow-up PRs)

### Wave 1 — Truth in naming + docs (low blast radius)

- [ ] Add module-level **ARCHITECTURE / DEPRECATED / CANONICAL** notes on:
  - `agentic_core/runtime/entry/apps_rg_dispatch.py` (explicit: `dispatch_apps_rg_run` is stub until wired; product runtime is TBD single call).
  - `apps_rg/runtime/dispatch/apps_rg_dispatch.py` (parse is real; dispatch tail calls stub).
- [ ] Either **rename** stub to `dispatch_apps_rg_dry_run_stub` **or** add `DEPRECATED_ALIAS` doc and a single line in `AGENTS.md` / `apps_rg/AGENTS.md` pointing to the future canonical call.
- [ ] Update `apps_rg/__main__.py` docstring to state: CLI today = stub seam; real generation = R4 entrypoint or section modules until W2.

### Wave 2 — Registry + single spine hook

- [ ] Implement or restore **`apps_rg/l2_recipe/registry.py`** (or relocate metadata) so `resolve_l2_recipe("apps_rg")` always resolves.
- [ ] Define **one internal function** e.g. `run_apps_rg_governed_resume_pipeline(...)` that:
  - builds `raw_request` from CLI/envelope,
  - calls `run_integrated_r4_deterministic_pipeline(..., app_name="apps_rg", artifact_dir=...)`,
  - returns the same dict shape `__main__` / tests expect (`exit_status`, `outcome_authorized`, paths).
- [ ] **Replace** `dispatch_apps_rg_run` body to delegate to that function (or call through a tiny apps_rg orchestrator in `apps_rg` that imports the R4 runner — avoid fat logic inside core if policy prefers app-owned orchestration; if orchestration stays in core, document receipt per `agentic_core` edit rules).

### Wave 3 — Section dispatches vs recipe

- [ ] Map each `*_dispatch` to either **callable from L2 step** or **slice-only CLI**; eliminate duplicate provider wiring where possible.
- [ ] Ensure **L7 / HOW trace** emission path matches the chosen single entry (R4 integrated already emits L7; stub dispatch does not).

### Wave 4 — Tests & CI

- [ ] Point contract tests at **one** public API (`dispatch_apps_rg_run` after real, or `run_integrated_r4_deterministic_pipeline` documented as harness-only per existing file docstring).
- [ ] Fix or remove **stale monkeypatches** on `apps_rg.__main__` if symbols moved.
- [ ] Optional gate: assert no new `python -m apps_rg.runtime.dispatch.*` references from product code (slices allowed from `tests/` only).

---

## 6. Success criteria

- One **documented** product path from CLI and envelope: **same** spine, **same** Exit semantics.
- `dispatch_apps_rg_run` **either** runs the governed pipeline **or** is renamed so nobody mistakes it for production.
- `integrated_r4_deterministic_pipeline_run` remains the **verifier-trusted** producer for Fort Knox / L7 but is not marketed as the second CLI.
- No regression: AG-2 contract (`run_ag2_retrieval_and_prompt`) and `apps_rg_parse` tests still pass.

---

## 7. Risks

- **Core vs app boundary:** pushing orchestration into `agentic_core` may trigger governance receipts; keeping orchestration in `apps_rg` may duplicate envelope handling — decide explicitly in W2.
- **Long-running LLM:** single entry must preserve explicit flags for dry-run / no-provider CI.
- **Notion / disk drift:** keep this markdown SSOT; Notion row holds status + summary only.

---

## 8. References (code)

- `apps_rg/runtime/dispatch/apps_rg_dispatch.py` — `apps_rg_parse`, `apps_rg_dispatch`
- `agentic_core/runtime/entry/apps_rg_dispatch.py` — `dispatch_apps_rg_run`, `run_ag2_retrieval_and_prompt`
- `agentic_core/runtime/entrypoints/integrated_r4_deterministic_pipeline_run.py` — R4 spine + L2 recipe resolution
- `agentic_core/runtime/l2_recipe_resolver.py` — recipe registration
- `apps_rg/runtime/dispatch/*_dispatch.py` — section runtime slices
