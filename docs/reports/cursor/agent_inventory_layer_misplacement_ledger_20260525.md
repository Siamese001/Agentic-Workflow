# Agent Inventory — Layer Misplacement Ledger

**Plan:** [agent-inventory-spine-taxonomy-b4e9f2](../../../.cursor/plans/agent-inventory-spine-taxonomy-b4e9f2.md)  
**Assessment:** [agentic_core_agent_inventory_runtime_assessment.md](../agentic_core_agent_inventory_runtime_assessment.md)  
**Date:** 2026-05-25  
**W2 scope:** Document only — physical package moves deferred to [agent-inventory-deferred-followup-c2a8f1](../../.cursor/plans/agent-inventory-deferred-followup-c2a8f1.md) (DS-3).

## Purpose

Static inventory of `*Agent` classes whose **package path** does not match their governance/safety role. These are **not** product-spine participants (ADR-088 A1/A2).

## Misplacement register

| Class | Current path | Declared layer (folder) | Expected role | Product spine? | Action |
|-------|--------------|-------------------------|---------------|----------------|--------|
| `SemanticGatekeeperAgent` | `agentic_core/L3_orchestration/reasoning/` | L3 | Safety / gatekeeper (not DAG owner) | No | Document; move to L5 or safety package in future wave |
| `BootstrapAgent` | `agentic_core/L5_safety/reasoning/` | L5 | L0 routing/bootstrap | No | Document; inherits L0 routing base in L5 folder |
| `PreCommitSovereignAgent` | `agentic_core/L5_safety/reasoning/` | L5 | L0 routing / pre-commit | No | Document; same as Bootstrap pattern |
| `GospelSyncAgent` | `agentic_core/L5_safety/reasoning/` | L5 | L0 sync / routing adjacency | No | Document; move deferred |

## Shim register (distinct from misplacement)

| Artifact | Path | W2 treatment | Architecture evidence? |
|----------|------|--------------|------------------------|
| `RootCustomsAgent` | `agentic_core/L0_routing/reasoning/RootCustomsAgent.py` | **W2.0:** legacy orphan body → [archive](../../../archives/agents/2026-05-25/agentic_core__L0_routing__reasoning__RootCustomsAgent_legacy_orphan_body.py); thin delegating shim retained | No — use `root_customs_util` |
| L6 snapshot re-export | `agentic_core/L6_system_learning/snapshot/__init__.py` | **W2.2:** **Preserve** — report-generation / harness import only | **No** (ADR-088 NON_CLAIMS) |

## L6 snapshot harness (W2.2 — not dead legacy)

The `snapshot/__init__.py` module exists so `spine_proof_bundle` and the runtime assessment generator can import `RuntimeADGSnapshot` without restructuring L6_observability imports.

- **Do not delete** in the same bucket as `RootCustomsAgent`.
- **Do not cite** as proof of product-spine `*Agent` invocation.
- **Do not** set `product_spine_invocation_status=ARTIFACT_PROVEN` from mock `_spine_proof_run/` artifacts.

See [runtime/LAYER.md](../../../agentic_core/runtime/LAYER.md) and [ADR-088](../../../docs/architecture/adr/ADR-088-product-spine-function-truth.md).

## Spine chain verification

Canonical product spine modules (`run_integrated_single_action_spine`, intake, route gates, L1 bridge, L2 resolver, Exit pipeline) **must not** import `RootCustomsAgent`. W2 receipt records grep proof.
