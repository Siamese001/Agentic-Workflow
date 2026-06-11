---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-rg-canonical-dispatch-l7-gate-c8a4d1.md'
original_relative_path: '_archive\\2026-05\\apps-rg-canonical-dispatch-l7-gate-c8a4d1.md'
source_sha256: 96fbde98da69a613225d8072188eec371f8dfe111d679b4b2246bc8edbc0237b
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_rg canonical dispatch + L7 acceptance gate

**Status:** Completed  
**Slug:** `apps-rg-canonical-dispatch-l7-gate-c8a4d1`  
**Supersedes:** `apps-rg-entrypoint-convergence-e7f3c2` (archived under `.cursor/plans/_archive/`)

---

## Recommendation

**Do not build around the stub.** Make `dispatch_apps_rg_run` the **canonical product entrypoint** and wire it to the **real governed runtime**, with **L7 proof as the acceptance gate**.

Bluntly: **fix the entrypoint first, then certify.**

---

## Priority 1 — Single product chain + L7 gate

Wire:

```text
python -m apps_rg
  → apps_rg_parse
  → dispatch_apps_rg_run
  → governed apps_rg runtime
  → section execution
  → Exit / X3
  → L7 receipt / proof bundle
```

**Acceptance:** A successful product run **must** emit the L7 artifacts (e.g. `agentic_core_how_trace.json` and related spine/manifest bindings) produced by the governed path — **not** a parallel “side path only” L7 patch.

**Do not:**

- Certify CLI dry-run as runtime.
- Claim L7 if `dispatch_apps_rg_run` cannot emit it after real success.

---

## Priority 2 — `apps_rg.l2_recipe.registry`

Add **`apps_rg.l2_recipe.registry`** (export `get_apps_rg_recipe_metadata` per `agentic_core/runtime/l2_recipe_resolver.py`).

**Why:** Without the L2 recipe registry, the integrated R4 path stays **theoretical** and cannot be treated as product runtime. Recipe binding is required for real L2 execution under the spine.

---

## Do not do this

```text
Do not keep three “entrypoints” with ambiguous names.
Do not certify CLI dry-run as runtime.
Do not claim L7 if dispatch_apps_rg_run cannot emit it.
Do not patch L7 around the side path only.
```

---

## Final target (roles)

```text
apps_rg_parse
  = ingress adapter

dispatch_apps_rg_run
  = only public product runtime entrypoint

integrated_r4_deterministic_pipeline
  = internal implementation detail

apps_rg.l2_recipe.registry
  = required recipe binding for real L2 execution

L7
  = emitted only after actual governed runtime success
```

---

## Implementation notes (for execution waves; not done in this doc)

1. **Core vs app orchestration:** Decide whether `dispatch_apps_rg_run` delegates to an `apps_rg`-owned orchestrator (preferred for fat domain) or inlines spine calls in `agentic_core` (requires migration receipt / boundary audit per `agentic_core/AGENTS.md`).
2. **`GovernedRun` L7:** If any path uses `apps_shared/spine_emission/context.py`, replace broad `except Exception: pass` around L7 with fail-loud or explicit degraded mode — side-channel silent L7 drops audit value.
3. **Tests:** Reconcile contract tests and `apps_rg/__main__.py` so monkeypatches and public API match the single entrypoint.
4. **Dry-run / CI:** Preserve an explicit **non-runtime** mode (flags or separate test helper) so CI never conflates stub success with governed+L7 success.

---

## Success criteria

- Exactly **one** documented public runtime path for resume product behavior.
- `dispatch_apps_rg_run` executes governed flow end-to-end (not stub) for normal CLI.
- L7 bundle present **iff** governed run completed successfully (no fake L7).
- `apps_rg` registers in `resolve_l2_recipe` via `l2_recipe/registry.py`.

---

## References

- `agentic_core/runtime/entry/apps_rg_dispatch.py`
- `apps_rg/runtime/dispatch/apps_rg_dispatch.py`
- `apps_rg/__main__.py`
- `agentic_core/runtime/entrypoints/integrated_r4_deterministic_pipeline_run.py`
- `agentic_core/runtime/l2_recipe_resolver.py`
- `agentic_core/L7_auditability/` (HOW trace + coverage)
