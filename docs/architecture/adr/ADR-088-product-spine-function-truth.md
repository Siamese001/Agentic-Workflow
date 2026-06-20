# ADR-088: Product Spine Function Truth & Taxonomy Inventory Separation

**Status:** Accepted
**Date:** 2026-05-25
**Plan:** [agent-inventory-spine-taxonomy-b4e9f2](../../../.codex/plans/agent-inventory-spine-taxonomy-b4e9f2.md) W0
**Evidence:** [Runtime assessment (PARTIAL)](../../reports/agentic_core_agent_inventory_runtime_assessment.md)

## Context

AST inventory found **118** `*Agent` class candidates in `agentic_core`; **31** are registered in `AGENT_TAXONOMY_MAP`. A mock-L2 spine harness run emitted HOW/spine JSON with stage IDs (`U0_INTAKE` … `L6_RUNTIME_EXHAUST`) and `producer_component=agentic_core.runtime.entrypoints.integrated_single_action_spine_run` — **no per-class `*Agent` identity fields**.

**Baseline (2026-05-25):** **0/118** candidates are artifact-proven as product-spine-invoked.

Teams routinely conflate:

- taxonomy registration → runtime invocation
- class name / inheritance → spine participant
- static import or grep hit in spine modules → E2E proof

Decision 1 (spine truth) and Decision 2 (inventory cleanup) are **not equivalent**.

## Decision

### Mandatory statements

1. The **current canonical product spine is function/stage based** — not a class-agent execution graph.
2. The **taxonomy registry (`AGENT_TAXONOMY_MAP`) is an inventory/control surface**, not the runtime execution graph.
3. Runtime graph claims require a **runtime receipt** that proves selection/invocation (A1 fields below) — not taxonomy presence, import fan-in, or static call path in spine source.
4. **Registration** and **`product_spine_invocation_status`** are **orthogonal** (A2 below). W1 inventory-only registration must not imply product-spine participation.

### Canonical product spine functions

| Stage / function | Module |
|------------------|--------|
| `run_integrated_single_action_spine` | `agentic_core/runtime/entrypoints/integrated_single_action_spine_run.py` |
| `run_request_intake` | `agentic_core/L0_routing/intake/pipeline.py` |
| `validated_request_to_plan_contract` | `agentic_core/L1_cognition/bridges/u0_to_l1_plan.py` |
| `check_route_gates` | `agentic_core/L0_routing/reasoning/route_gates.py` |
| `resolve_l2_recipe` | `agentic_core/runtime/l2_recipe_resolver.py` |
| `ExitEvalPipeline.run` | `agentic_core/L3_orchestration/exit_eval/v6/pipeline.py` |

L2 product execution resolves to **`apps_*` step callables** via `resolve_l2_recipe` — out of scope for `*Agent` class inventory in `agentic_core`.

### Acceptance invariant A1 — Product-spine invoked (runtime claim)

No `agentic_core` class may be described as **product-spine invoked** unless an E2E artifact contains at least one of:

- class name
- module path
- registry selected agent id
- execution profile id bound to that class
- OTEL span naming that class/module
- receipt producer/consumer/executor naming that class/module

### Acceptance invariant A2 — Taxonomy registration (inventory claim)

**No taxonomy registration may be interpreted as E2E invocation.**

- Adding or updating an `AGENT_TAXONOMY_MAP` row is inventory/control metadata only.
- Forbidden inference: taxonomy key present → product-spine participant; import → invoked; static mention in spine source → invoked.
- Any future `product_spine_invocation_status=ARTIFACT_PROVEN` (W1+ schema) **must** cite `spine_proof_ref` pointing to a runtime artifact satisfying A1 — not merely taxonomy key, import graph, or grep.

### W1 taxonomy axes (forward reference)

W1 will add four orthogonal fields per entry: `agenthood_status`, `inventory_role`, `product_spine_invocation_status`, `runtime_proof_class`. See [product_spine_taxonomy_invariants.md](../../reference/agentic_core/product_spine_taxonomy_invariants.md).

**W1 registration defaults:** `product_spine_invocation_status=NOT_ARTIFACT_PROVEN`, `runtime_proof_class=NONE` for all new rows unless an artifact already satisfies A1 (baseline: none).

## NON_CLAIMS

- This ADR does **not** prove `*Agent` classes are unused everywhere.
- This ADR proves they are **not artifact-proven** as invoked by the canonical E2E spine run inspected (PARTIAL assessment).
- Mock L2 harness proof (`artifacts/reports/agent_inventory/_spine_proof_run/`) is valid only for spine **path shape** (stage/function flow), not live product model/tool execution.
- [`agentic_core/L6_system_learning/snapshot/__init__.py`](../../../agentic_core/L6_system_learning/snapshot/__init__.py) exists for **report-generation / harness import only** — not architecture evidence.

## Consequences

- Documentation, plans, and CI must not describe any `*Agent` as product-spine-invoked without A1 proof.
- W1 bulk taxonomy registration is inventory-only; it does **not** add classes to the product runtime graph.
- W3 (live spine proof) remains DEFERRED; mock harness artifacts **must not** backfill `ARTIFACT_PROVEN` or upgrade `runtime_proof_class` in W0–W2.
- `AGENT_TAXONOMY_MAP` must not be drawn as the product runtime graph in architecture diagrams without explicit “inventory only” labeling.

## Related

- [Runtime assessment MD](../../reports/agentic_core_agent_inventory_runtime_assessment.md)
- [Runtime assessment JSON](../../reports/agentic_core_agent_inventory_runtime_assessment.json)
- [Product spine taxonomy invariants (reference)](../../reference/agentic_core/product_spine_taxonomy_invariants.md)
- [Runtime LAYER.md](../../../agentic_core/runtime/LAYER.md)
- W0 receipt: [agent_inventory_spine_taxonomy_w0_receipt.md](../../reports/cursor/agent_inventory_spine_taxonomy_w0_receipt.md)
