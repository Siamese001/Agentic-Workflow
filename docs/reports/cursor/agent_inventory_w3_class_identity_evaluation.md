# W3 — Class identity on spine (Decision 1 evaluation)

**Plan:** [agent-inventory-spine-taxonomy-b4e9f2.md](../../../.cursor/plans/agent-inventory-spine-taxonomy-b4e9f2.md)  
**ADR:** [ADR-088-product-spine-function-truth.md](../../architecture/adr/ADR-088-product-spine-function-truth.md)  
**Live proof:** [w3_live_spine_proof_report.json](../../../artifacts/reports/agent_inventory/_w3_live_spine_proof_run/w3_live_spine_proof_report.json)

## Recommendation: defer (no schema change)

Do **not** add `invoked_class`, `executor_class`, or `agent_class` fields to `agentic_core_how_trace.json` or spine proof bundles in this plan.

## Evidence from live run (2026-05-25)

| Check | Result |
|-------|--------|
| `runtime_proof_class` | `LIVE_RUNTIME_PROOF` |
| `mock_mode_detected` | `false` |
| `class_identity_fields_present` in HOW trace | `false` |
| `*Agent` strings in spine artifacts | **0** |
| HOW stages | Function/stage IDs only (`U0_INTAKE` … `L6_RUNTIME_EXHAUST`) |
| `producer_component` | `agentic_core.runtime.entrypoints.integrated_single_action_spine_run` |

Live run reached real L2 (`_test_mode=False`, `resolve_l2_recipe` for `apps_rg`). L2 returned `FAILED_MODULAR_R4` (lane prerequisite policy — headline run dir / prior lane chain). That is an **execution outcome**, not proof that the spine is class-agent based.

## Rationale

1. **ADR-088** — Product spine truth is **function/stage based**. Taxonomy `*Agent` rows describe inventory and governance routing, not runtime ownership.
2. **A1** — No artifact in the live run names an invoked `*Agent` class. Adding class fields would invite mis-reading registration as invocation (A2 violation).
3. **Cost** — Class identity on spine requires binding every L2 step to a stable class name, replay contracts, and CI that forbids stale class strings when implementations move to functions/modules.

## If revisited later

Scope expansion (separate plan) would need:

- Explicit product approval for spine JSON schema bump
- Per-stage optional `executor_module` (not `*Agent` class) aligned with `producer_component` discipline
- Replay + live gates that fail when class fields appear without matching artifact proof

Until then, use `inventory_role` + `product_spine_invocation_status` on taxonomy rows only; keep `ARTIFACT_PROVEN` empty for all `agentic_core` `*Agent` classes.
