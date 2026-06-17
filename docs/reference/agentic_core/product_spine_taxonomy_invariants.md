# Product Spine & Agent Taxonomy Invariants

**ADR:** [ADR-088-product-spine-function-truth.md](../../architecture/adr/ADR-088-product-spine-function-truth.md)  
**Plan:** [agent-inventory-spine-taxonomy-b4e9f2](../../../.claude/plans/agent-inventory-spine-taxonomy-b4e9f2.md)  
**Assessment:** [agentic_core_agent_inventory_runtime_assessment.md](../../reports/agentic_core_agent_inventory_runtime_assessment.md) (STATUS: PARTIAL)

## Quick reference

| Question | Answer |
|----------|--------|
| What runs the product E2E spine? | Named **functions** and stages — see ADR-088 spine table |
| Does `AGENT_TAXONOMY_MAP` show runtime order? | **No** — inventory/control surface only |
| Does registering an agent imply spine invocation? | **No** (A2) |
| Does class name `*Agent` imply spine invocation? | **No** (A1) |
| Current artifact-proven spine-invoked `*Agent` count | **0** (2026-05-25 baseline) |

## A1 — Product-spine invoked

A runtime **claim** only. Requires an E2E artifact with class/module/registry/OTEL/receipt executor identity for that class.

## A2 — Taxonomy registration

An **inventory** claim only. Taxonomy rows document governance placement; they do not prove E2E invocation.

W1 will implement four orthogonal taxonomy fields (schema in plan W1.0):

| Field | Purpose |
|-------|---------|
| `agenthood_status` | TRUE_AGENT / NOT_AGENT / WRAPPER_ONLY / SHIM_OR_DEAD_LEGACY |
| `inventory_role` | Governance placement (not routing) |
| `product_spine_invocation_status` | ARTIFACT_PROVEN / NOT_ARTIFACT_PROVEN |
| `runtime_proof_class` | LIVE / REPLAY / TEST / MOCK_ONLY / NONE |

**Forbidden:** Using mock `_spine_proof_run/` artifacts to set `ARTIFACT_PROVEN` in W0–W2.

## Harness-only shim

`agentic_core/L6_system_learning/snapshot/__init__.py` — import convenience for assessment/spine report generation. **Not** architecture proof. Do not delete in W2; document only (W2.2).

## Code pointers

- Spine entry: `agentic_core/runtime/entrypoints/integrated_single_action_spine_run.py`
- Taxonomy (inventory): `agentic_core/L2_execution/types/agent_taxonomy_registry.py`
- Assessment generator: `docs/reports/agent_inventory/_generate_runtime_assessment.py`
