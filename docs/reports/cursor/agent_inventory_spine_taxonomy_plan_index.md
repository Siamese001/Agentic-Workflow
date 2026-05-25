# Agent inventory — plan index (review)

**Created:** 2026-05-25  
**Status:** **Completed** (2026-05-25) — follow-up [agent-inventory-deferred-followup-c2a8f1](agent_inventory_deferred_followup_plan_index.md)

## Plan (SSOT)

| Field | Value |
|-------|-------|
| Slug | `agent-inventory-spine-taxonomy-b4e9f2` |
| Disk | [.cursor/plans/agent-inventory-spine-taxonomy-b4e9f2.md](../../.cursor/plans/agent-inventory-spine-taxonomy-b4e9f2.md) |
| Notion | [agent-inventory-spine-taxonomy-b4e9f2](https://www.notion.so/agent-inventory-spine-taxonomy-b4e9f2-36b27693f55c81d3b7a7d9b54d461f83) |
| Notion page ID | `36b27693-f55c-81d3-b7a7-d9b54d461f83` |
| Plans DB status | Completed |
| Closeout receipt | [agent_inventory_spine_taxonomy_closeout_receipt.md](agent_inventory_spine_taxonomy_closeout_receipt.md) |
| Follow-up plan | [agent-inventory-deferred-followup-c2a8f1](../../.cursor/plans/agent-inventory-deferred-followup-c2a8f1.md) |
| Deferred register | [agent_inventory_deferred_scope_register_20260525.md](agent_inventory_deferred_scope_register_20260525.md) |
| W0 receipt | [agent_inventory_spine_taxonomy_w0_receipt.md](agent_inventory_spine_taxonomy_w0_receipt.md) |
| W1 receipt | [agent_inventory_spine_taxonomy_w1_receipt.md](agent_inventory_spine_taxonomy_w1_receipt.md) |
| W2 receipt | [agent_inventory_spine_taxonomy_w2_receipt.md](agent_inventory_spine_taxonomy_w2_receipt.md) |
| W3 receipt | [agent_inventory_spine_taxonomy_w3_receipt.md](agent_inventory_spine_taxonomy_w3_receipt.md) |
| W3 class-identity eval | [agent_inventory_w3_class_identity_evaluation.md](agent_inventory_w3_class_identity_evaluation.md) |
| W3 live proof | [\_w3_live_spine_proof_run/](../../artifacts/reports/agent_inventory/_w3_live_spine_proof_run/) |
| Misplacement ledger | [agent_inventory_layer_misplacement_ledger_20260525.md](agent_inventory_layer_misplacement_ledger_20260525.md) |
| ADR-088 | [ADR-088-product-spine-function-truth.md](../../architecture/adr/ADR-088-product-spine-function-truth.md) |

## Evidence inputs

| Report | Path |
|--------|------|
| Runtime assessment (MD) | [agentic_core_agent_inventory_runtime_assessment.md](../agentic_core_agent_inventory_runtime_assessment.md) |
| Runtime assessment (JSON) | [agentic_core_agent_inventory_runtime_assessment.json](../agentic_core_agent_inventory_runtime_assessment.json) |
| Spine harness artifacts | [\_spine_proof_run/](../../artifacts/reports/agent_inventory/_spine_proof_run/) |

## Plan summary

Two **non-equivalent** tracks:

1. **Product spine truth** — function/stage spine; E2E invoked `*Agent` count = 0; **A1** invariant for runtime spine-invoked claims.
2. **Inventory / taxonomy cleanup** — four orthogonal axes on every row; **A2**: registration ≠ invocation; W1 gap fill is inventory-only (`NOT_ARTIFACT_PROVEN`, `runtime_proof_class=NONE`).

**Taxonomy axes:** `agenthood_status` · `inventory_role` · `product_spine_invocation_status` · `runtime_proof_class`

Waves: **W0** ADR · **W1** four-axis schema + CI · **W2** RootCustoms archive · **W3** live spine (`run_w3_live_spine_proof.py`; no mock backfill; Decision 1 defer).
