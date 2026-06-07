
# Agent Taxonomy & Product Spine Truth

> **ADR-088:** `docs/architecture/adr/ADR-088-product-spine-function-truth.md`  
> **Reference:** `docs/reference/agentic_core/product_spine_taxonomy_invariants.md`

## Spine law

The canonical product E2E spine is **function/stage based** (`run_integrated_single_action_spine` and linked pipeline functions). It is **not** a `*Agent` class execution graph.

## Taxonomy law

`AGENT_TAXONOMY_MAP` is an **inventory/control surface**, not the runtime execution graph.

**Forbidden claims without A1 artifact proof:**

- “Registered in taxonomy” → product-spine invoked
- Class name / `*Agent` suffix → spine participant
- Import or static mention in spine source → E2E proof
- Mock harness `_spine_proof_run/` → `ARTIFACT_PROVEN` (W0–W2)

## A1 / A2 (summary)

- **A1 (runtime):** Product-spine-invoked requires class/module/registry/OTEL/receipt identity in an E2E artifact.
- **A2 (inventory):** Taxonomy registration alone never implies E2E invocation.

W1 adds `agenthood_status`, `inventory_role`, `product_spine_invocation_status`, `runtime_proof_class` — orthogonal fields; defaults `NOT_ARTIFACT_PROVEN` + `NONE` on new rows.

## Harness shim

`agentic_core/L6_system_learning/snapshot/__init__.py` — report-generation import only; not architecture proof.
