# L1 Reasoning v5 — Gap Implementation Plan

Plan ID: `l1-reasoning-v5-gap-implementation-7e2c4f`
Status: In progress
Owner: Cascade
Source SSOT: `docs/reference/02_L1_Reasoning/02_L1_Reasoning_Plan_Generation_v5.md`
Scope: Pure additive over v4 — no v4 contract breakage.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| W1 | W1.1 | Intent enrichment: 3 new requirement enums + parse_intent inference | ~5k | done | `FreshnessClass`, `ActionRequirement`, `ArtifactRequirement` exported; parse_intent populates them |
| W2 | W2.1, W2.2 | Route enrichment: `R3R4_MANAGED_WORKFLOW`, `Confidence` enum | ~3k | done | New route accepted by validators; `confidence` discrete enum on plan |
| W3 | W3.1 | First Safety/Authority Reading (10-question gate) | ~6k | done | `first_safety_reading()` produces structured `FirstSafetyReading`; 12+ tests |
| W4 | W4.1 | V3A Plan Consistency Audit (9-check gate between V3 and V4) | ~6k | done | New gate `V3A`; aggregator returns 6 gates not 5 |
| W5 | W5.1 | V6 Self-Repair Loop (bounded 1-2 refinements) | ~5k | done | `repair_plan_once`; loop cap at 2; falls back to clarify/abstain |
| W6 | W6.1 | v5 Output Contract sidecar groups + builder | ~7k | done | `build_l1_v5_contract_dict()` produces v5 JSON shape with all 10 sections |
| W7 | W7.1 | Failure-mode test matrix + harden | ~6k | done | One test per failure-mode row; aggregate 270+/270+ passing |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.1 | Intent requirement enums | `intent_frame_types.py`, `intent_parser.py` | Backward compat for IntentFrame defaults | 5k | done |
| W2.1 | R3R4 route + Confidence enum | `plan_contract_types.py` | Make sure existing R3/R4 stays valid | 3k | done |
| W3.1 | First-safety-reading module | new `first_safety_reading.py` + tests | Heuristic accuracy on injection markers | 6k | done |
| W4.1 | V3A consistency audit | `plan_semantic_validators.py` + tests | Aggregator wiring | 6k | done |
| W5.1 | V6 self-repair loop | new `plan_self_repair.py` + tests | Bounded loop semantics | 5k | done |
| W6.1 | v5 contract builder | new `l1_v5_contract_builder.py` + tests | 10-section contract with 6 nested groups | 7k | done |
| W7.1 | Failure-mode coverage | new `test_l1_v5_failure_modes.py` | Map 17 rows → tests | 6k | done |

## ADG_GRAPH_LAYER_EVIDENCE

This is a pure-additive doctrine implementation; no SC/AP defects added.
- `mv_graph_reverse_dependency_hotspots`: no L1 module enters top-50 fan-in
- `v_p1_zero_caller_infra`: not relevant (these are types/utilities consumed by future L0)
- semantic edges: only `imports` added (zero new `flows_to`/`writes_to`/`emits_side_effect`)

## Gap Register

None — full v5 doctrine surface mapped to waves.

## Verification

`python -m pytest tests/unit/agentic_core/L1_cognition/ -q` reports ≥ 270 passing.
