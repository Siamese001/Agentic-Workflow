---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\runtime-adg-tier3-broader-adoption-8f2d1c.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\runtime-adg-tier3-broader-adoption-8f2d1c.md'
source_sha256: 9a1a954c888a163a3ca3476f763e2d25013bfbd71655da300f96d3a329b962d3
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: Runtime ADG Tier 3 — Broader `seal_step` Adoption

**Slug**: `runtime-adg-tier3-broader-adoption-8f2d1c`
**Status**: Backlog (P5)
**Tier**: T2
**Parent**: `runtime-adg-tier2h-tier3-c4d8e2`
**Created**: 2026-04-23

## Context

Tier 2 harden + Tier 3 shipped in commit `a8d6620f1a` proved the `seal_step()`
pattern end-to-end:
  * `AutoPersistenceTracingAdapter.trace_orchestrator` installs the adapter
    as a `contextvars.ContextVar`-scoped ambient reference.
  * Any nested code resolves the adapter via `get_current_adapter()` and
    wraps its step-boundary work in `seal_step()` with zero plumbing.
  * First caller wired: `HOPPipelineExecutor._process` (9 HOP stages).

The remaining work is **mechanical copy-paste** of the 3-line recipe into
every remaining step-boundary caller. The spine is load-bearing; this is
adoption, not architecture.

## The Recipe

```python
from system_learning.runtime_adg.runtime_span_emitter import (
    get_current_adapter,
    seal_step,
)

with seal_step(get_current_adapter(), step_id="<stable-id>", trace_id="") as bag:
    result = <existing-step-body>
    bag["output"] = result
return result
```

Rules:
1. `step_id` MUST be stable across runs of the same logical step.
2. `trace_id=""` is correct — the back-patch + contextvar pipeline unifies it.
3. `seal_step` is fail-open: when no adapter is active (unit tests, CLI runs)
   the handler runs untouched and no span is emitted.

## Adoption Targets (by priority of blast-radius)

| Priority | Module | Step boundary | Est. stages/call |
|---|---|---|---|
| 1 | `apps_exec/engines/base_exec_engine.py` | base class `_run_step` | every exec step across 8 engines |
| 2 | `apps_rg/engines/achievement_prioritizer_engine.py` | main pipeline step | 1 per call |
| 3 | `apps_rg/engines/ats_compatibility_engine.py` | compatibility check step | 1 per call |
| 4 | `apps_rg/engines/*` (remaining 43) | per-engine step | 1 per call |
| 5 | `apps_research/engines/research_assembly_engine.py` | assembly step | 1 per call |
| 6 | `apps_rfp/engines/proposal_assembly_engine.py` | assembly step | 1 per call |
| 7 | `apps_lic/engines/control_plane.py` | control step | 1 per call |

## Success Criteria

1. Every base engine class adopts the recipe in its `_run_step` / `_process` method (1 change covers N subclasses).
2. Individual engines without a base adopter each wire directly.
3. Coverage audit on a real production snapshot shows ≥ 5 distinct `L2.step.seal`
   spans per run (indicating multiple callers exercised).
4. No regression on `tests/integration/system_learning/runtime_adg/test_tier2_tier3_e2e.py`.

## Out of Scope

* Re-architecting step boundaries where none exist today.
* Adding new spans beyond the Tier 1 five categories.
* Refactoring unrelated lint warnings in touched files.

## Deferred-Scope Marker Reference

```
DEFERRED_SCOPE: plan=NEW:runtime-adg-tier3-broader-adoption wave=RT3
phase=RT3.P2 layer=L2 fan_in=10 surface=Execution coverage_gap_pct=0.0
est_tokens=5000 reason=Wire seal_step into apps_exec/apps_rg engines
using the proven 3-line recipe
```

Scorer band: **P5** (impact score 0 because `coverage_gap_pct=0.0`; a
realistic restating would use gap % = percent of step-boundary callers
NOT yet adopting `seal_step`, which is currently ~98%, giving P1).
