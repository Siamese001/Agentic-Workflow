---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\agent-inventory-deferred-followup-c2a8f1.md'
original_relative_path: 'agent-inventory-deferred-followup-c2a8f1.md'
source_sha256: 4b56dae8dec5f810c7cdf7e7b987dabd157669bc7139779153efba44031b1c39
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: agent-inventory-deferred-followup-c2a8f1
plan_type: governance
touches_agentic_core: true
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: ""
dod_exempt: false
parent_plan: agent-inventory-spine-taxonomy-b4e9f2
parent_plan_status: Completed
---

# Agent Inventory — Deferred Follow-Up

Execute deferred work from [agent-inventory-spine-taxonomy-b4e9f2](agent-inventory-spine-taxonomy-b4e9f2.md) (W0–W3 **Completed** 2026-05-25). Parent delivered ADR-088, four-axis taxonomy, CI A1/A2, RootCustoms archive, and W3 live spine proof with **0** artifact-proven `*Agent` invocations. This plan owns **integrated product proof**, optional HOW class-identity (product-gated), and physical misplacement burndown.

> **plan_id discipline:** `plan=agent-inventory-deferred-followup-c2a8f1`

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: Not Started
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: none
LAST_UPDATED: 2026-05-25
PARENT_PLAN: agent-inventory-spine-taxonomy-b4e9f2
DEFERRED_REGISTER: docs/reports/cursor/agent_inventory_deferred_scope_register_20260525.md

PLAN_CREATED: slug=agent-inventory-deferred-followup-c2a8f1 path=.cursor/plans/agent-inventory-deferred-followup-c2a8f1.md status=Not Started notion_page=36b27693-f55c-81b7-869e-f5c752742ff9

NOTION_PAGE_ID: 36b27693-f55c-81b7-869e-f5c752742ff9
NOTION_PLAN_URL: https://www.notion.so/agent-inventory-deferred-followup-c2a8f1-36b27693f55c81b7869ef5c752742ff9

---

## Context (SCQA)

- **Situation** — Parent closed with function-based spine canon, 197 taxonomy entries, `ARTIFACT_PROVEN=0` for `agentic_core` agents, misplacement ledger documented.
- **Complication** — W3 live runner exercised production path but L2 modular R4 failed lane prerequisites; full `python -m apps_rg` green proof and physical moves remain open; Decision 1 (class on HOW) explicitly deferred.
- **Question** — How do we complete product proof and layout cleanup without conflating taxonomy with spine invocation?
- **Answer** — **Register-first (W0)**, then integrated live proof (W1), product-gated ADR for class identity (W2), Author-Gate physical moves (W3), shim removal (W4).

---

## Parent receipts (read-only)

| Wave | Receipt |
|------|---------|
| W0 | [agent_inventory_spine_taxonomy_w0_receipt.md](../docs/reports/cursor/agent_inventory_spine_taxonomy_w0_receipt.md) |
| W1 | [agent_inventory_spine_taxonomy_w1_receipt.md](../docs/reports/cursor/agent_inventory_spine_taxonomy_w1_receipt.md) |
| W2 | [agent_inventory_spine_taxonomy_w2_receipt.md](../docs/reports/cursor/agent_inventory_spine_taxonomy_w2_receipt.md) |
| W3 | [agent_inventory_spine_taxonomy_w3_receipt.md](../docs/reports/cursor/agent_inventory_spine_taxonomy_w3_receipt.md) |
| W3 eval | [agent_inventory_w3_class_identity_evaluation.md](../docs/reports/cursor/agent_inventory_w3_class_identity_evaluation.md) |

---

## Status tables

### Wave progress

| Wave | Focus | Status |
|------|-------|--------|
| W0 | Deferred register + plan linkage | Not Started |
| W1 | Integrated R4 live product proof (apps_rg) | Not Started |
| W2 | Decision 1 — class identity ADR (approve or permanent defer) | Not Started |
| W3 | Physical misplacement moves (Author-Gate per class) | Not Started |
| W4 | RootCustoms thin shim removal after burndown | Not Started |

### Deferred scope map

| ID | Title | Wave |
|----|-------|------|
| DS-1 | Full green `python -m apps_rg` integrated proof | W1 |
| DS-2 | Optional HOW `invoked_class` (product approval) | W2 |
| DS-3 | Misplacement ledger physical moves | W3 |
| DS-4 | RootCustoms shim delete | W4 |
| DS-5 | A2 maintenance — no `ARTIFACT_PROVEN` without proof | All waves |

---

## Out of scope

- Reopening parent W0–W3 taxonomy axis schema (frozen unless ADR).
- Bulk `NOT_AGENT` on L5/healing inventory rows.
- Using mock `_spine_proof_run/` to flip `product_spine_invocation_status`.
- Deleting L6 snapshot harness shim as misplacement cleanup.

---

## Wave summary

| Wave | Phase IDs | Focus | Est. tokens | Success criteria |
|------|-----------|-------|-------------|------------------|
| W0 | W0.1 | Publish/link deferred register | ~2k | Register on disk; parent Notion Completed |
| W1 | W1.1 | `PYTEST_APPS_RG_INTEGRATED_LIVE=1` or canonical CLI green | ~60k | Product proof receipt; still 0 `*Agent` unless DS-2 approved |
| W2 | W2.1 | ADR draft: class identity on HOW | ~8k | ACCEPTED ADR or explicit REJECTED + permanent defer marker |
| W3 | W3.1–W3.4 | One Author-Gate move per misplacement row | ~20k | ADG fan-in proof per move |
| W4 | W4.1 | Remove RootCustomsAgent.py shim | ~4k | Zero importers; tests green |

---

## Definition of done

DoD-1: Deferred register published and linked from parent closeout  
DoD-2: W1 integrated live proof receipt (PASS or honest BLOCKED with provider/lane evidence)  
DoD-3: W2 Decision 1 resolved in writing (ADR or defer permanent)  
DoD-4: W3 moves executed or each row has DEFERRED_SCOPE + P-Band  
DoD-5: `ARTIFACT_PROVEN` count unchanged unless DS-2 approved and proof artifacts exist  

---

## Related artifacts

| Artifact | Path |
|----------|------|
| Deferred register | [agent_inventory_deferred_scope_register_20260525.md](../docs/reports/cursor/agent_inventory_deferred_scope_register_20260525.md) |
| Misplacement ledger | [agent_inventory_layer_misplacement_ledger_20260525.md](../docs/reports/cursor/agent_inventory_layer_misplacement_ledger_20260525.md) |
| Live W3 runner | [run_w3_live_spine_proof.py](../tools/governance/run_w3_live_spine_proof.py) |
| Assessment | [agentic_core_agent_inventory_runtime_assessment.md](../docs/reports/agentic_core_agent_inventory_runtime_assessment.md) |

---

## Marker quick reference

```
WAVE_START: plan=agent-inventory-deferred-followup-c2a8f1 wave=0
PLAN_COMPLETE: plan=agent-inventory-deferred-followup-c2a8f1 note="<outcome>"
```
