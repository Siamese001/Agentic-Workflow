# Runtime Layer — Product Spine Entry

> **ADR-088:** [Product spine function truth](../../docs/architecture/adr/ADR-088-product-spine-function-truth.md)  
> **Invariants:** [product_spine_taxonomy_invariants.md](../../docs/reference/agentic_core/product_spine_taxonomy_invariants.md)

## Canonical product spine (function/stage based)

The **current** canonical E2E product path is a **governed functional pipeline**, not a class-per-agent graph.

| Function | Location |
|----------|----------|
| `run_integrated_single_action_spine` | `entrypoints/integrated_single_action_spine_run.py` |
| `run_request_intake` | `../L0_routing/intake/pipeline.py` |
| `validated_request_to_plan_contract` | `../L1_cognition/bridges/u0_to_l1_plan.py` |
| `check_route_gates` | `../L0_routing/reasoning/route_gates.py` |
| `resolve_l2_recipe` | `l2_recipe_resolver.py` |
| `ExitEvalPipeline.run` | `../L3_orchestration/exit_eval/v6/pipeline.py` |

HOW / spine proof artifacts emitted from this entrypoint document **stage/function execution** (e.g. `U0_INTAKE`, `L1_PLAN`, `producer_component` on the entrypoint module). They do **not**, by themselves, prove that any `*Agent` class was selected or invoked.

## Taxonomy vs runtime graph

`AGENT_TAXONOMY_MAP` (`L2_execution/types/agent_taxonomy_registry.py`) is an **inventory/control surface** for `*Agent` classes — **not** the product runtime execution graph.

- Taxonomy registration ≠ E2E invocation (A2).
- No `*Agent` may be described as product-spine-invoked without artifact proof (A1).

## `*Agent` classes in other layers

Adjacent governance, healing, validation, and legacy `*Agent` classes may exist off the product spine unless a future runtime receipt proves selection/invocation. See [runtime assessment](../../docs/reports/agentic_core_agent_inventory_runtime_assessment.md).

## Report-generation import shim (not architecture proof)

`agentic_core/L6_system_learning/snapshot/__init__.py` re-exports `RuntimeADGSnapshot` so spine proof / assessment tooling can import during **harness and report generation**. It is **not** evidence of class-agent spine architecture.
