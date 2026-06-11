---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\l1-reasoning-v4-gap-implementation-9c4d2a.md'
original_relative_path: 'l1-reasoning-v4-gap-implementation-9c4d2a.md'
source_sha256: 62a5d35d7db38181ee8224cce4b05c468e04736bd310a6288e258a1ed86f5d2b
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# L1 Reasoning v4 — Gap Implementation Plan

**Source doc**: `docs/reference/02_L1_Reasoning/02_L1_Reasoning_Plan_Generation_v4.md`
**Status**: in-progress
**Tier**: T3 (cross-module L1, multi-file, contract extension)

## Gap Summary

| Doc Concept | Current Repo | Gap → Action |
|---|---|---|
| I1-I4 Intent Frame | `WorkClass` enum + `classify_work_class` | **NEW** typed `IntentFrame`, `AmbiguityRegister`, `parse_intent()` |
| M1-M4 Plan Bundle | scattered | **NEW** typed `PlanBundle`, `RuleAwarePlanningFrame`, `load_plan_bundle()` |
| P4 Output Contract fields | `L1PlanContractV2` ~70% | **EXTEND** add `support_target`, `lowest_viable_agency`, `escalation_hint`, `clarify_or_abstain_marker` |
| V1-V5 semantic gates | only structural `validate()` | **NEW** `plan_semantic_validators.py` |
| T1-T4 model attention internals | N/A | not code-implementable |

## Wave Structure

| Wave | Phase IDs | Focus | Est Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| W1 | W1.1 | Intent Frame types + parser | 4000 | done | tests green; immutable typed `IntentFrame` |
| W2 | W2.1 | Plan Bundle aggregator | 3500 | done | tests green; immutable `PlanBundle` |
| W3 | W3.1 | L1PlanContractV2 extension (back-compat) | 4000 | done | new optional fields validated; v1 round-trip preserved |
| W4 | W4.1 | V1-V5 semantic validators | 4500 | done | each gate produces typed result; aggregator returns ValidationOutcome |
| W5 | W5.1 | Hardening, full tests, commit, push | 2000 | done | py_compile clean; targeted tests pass; pushed to origin/main |

## Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est Tokens | Status |
|---|---|---|---|---|---|
| W1.1 | IntentFrame + parse_intent | `types/intent_frame_types.py`, `reasoning/intent_parser.py` | doc terminology mapping | 4000 | done |
| W2.1 | PlanBundle | `types/plan_bundle_types.py`, `reasoning/plan_bundle_loader.py` | L4 read-only contract | 3500 | done |
| W3.1 | Contract extension | `types/plan_contract_types.py` | back-compat for frozen dataclass | 4000 | done |
| W4.1 | V1-V5 validators | `enforcement/plan_semantic_validators.py` | semantic vs structural | 4500 | done |
| W5.1 | Verify+commit+push | tests run, git ops | none | 2000 | done |

## ADG_GRAPH_LAYER_EVIDENCE

This is a *contract-extension* refactor (additive types, no graph topology change), not a hotspot remediation; full P-view / mv_* evidence does not gate it. Forward-compat tracked: `L1PlanContractV2` consumers in L0 (e.g., reasoning_chokepoint) read existing required fields only; new optional fields default `None` and do not affect `to_v1()` legacy projection. ADG `adg_edge_fanin` on `L1PlanContractV2` shows it is consumed by reasoning_chokepoint and 3 unit-test modules — no production-callsite breakage.

## ADG_HOTSPOT_REPORT

Not applicable — additive contract extension, archetype = STATE_NODE (contract object), L1 layer multiplier ×1.0, no anti-pattern instances introduced.

## Non-Authority Invariants Preserved

- L1 produces plan; no retrieval, no tool exec, no UWG mutation
- Scratchpad redaction canary preserved
- Frozen dataclasses throughout
