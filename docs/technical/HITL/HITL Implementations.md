████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
█  AGENTIC SYSTEM — PATH D & HITL IMPLEMENTATIONS (WIDESCREEN CONSOLIDATED)                                                      [ LATEST ADG: 03162026_0931 ]  █
████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ADG SNAPSHOT OVERLAY (Source: artifacts/adg/adg_snapshot_03162026_0931.json)                                                                                     │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Modules: 8,591  |  Symbols: 60,196  |  Relations: 815,826  |  Layer Violations: 0                                                                                │
│ HITL/Path-D Signal Counts:                                                                                                                                       │
│ - escalates_to_human: 1,182    - requires_human_review: 5       - routes_path: 183                                                                               │
│ - reenters_safety: 11          - builds_dpo_batch: 43           - produces_preference_pair: 13                                                                     │
│ - gated_by_confidence: 37      - enters_sandbox: 39             - freezes_context: 5     - unfreezes_context: 2                                                   │
│ Learning-Loop Linkage:                                                                                                                                           │
│ - proposal_commits_routing: 3,029                               - updates_routing_strategy: 3,011                                                                │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ USE CASE #1 — HITL AS GOVERNANCE ESCALATION GATE                                                                                                                 │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [PURPOSE] Authority arbitration and privileged action classification.                                                                                            │
│ [ENTRYPOINTS]                                                                                                                                                    │
│ - agentic_core/L5_safety/enforcement/policy_action_contract.py                                                                                                   │
│ - agentic_core/L5_safety/enforcement/tool_safety_contract.py                                                                                                     │
│ - agentic_core/L2_execution/enforcement/execution_guardrail_chokepoint.py                                                                                        │
│ [LOGIC FLOW]                                                                                                                                                     │
│   1. Action classified as HUMAN_GATED/PRIVILEGED.                                                                                                                │
│   2. System emits `requires_human_review` & `escalates_to_human`.                                                                                                │
│   3. L3 Orchestrator freezes execution and prepares `HumanDecisionArtifact`.                                                                                     │
│   4. If not approved, system fail-closed and emits `reenters_safety`.                                                                                            │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ USE CASE #2 — HITL AS PATH D DECISION AIRLOCK                                                                                                                    │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [PURPOSE] Safe human intervention via a Zero-Authority Sandbox.                                                                                                  │
│ [TOPOLOGY]                                                                                                                                                       │
│   L3: ORCHESTRATOR =======> [ HUMAN DECISION GATE ] =======> L5: SAFETY RE-CLEARANCE =======> L2: EXECUTION                                                       │
│                                                                                                                                                                  │
│ [THE DECISION MATRIX]                                                                                                                                            │
│   1. APPROVE     -> Fast-tracks to L5 [AUTH] Stamp.                                                                                                              │
│   2. REJECT      -> Aborts wave, re-routes to L1.                                                                                                                │
│   3. MODIFY_DIFF -> Human provides `structured_patch_schema`. Must use allowlisted tools. Sets `l5_reclear_required=True`.                                       │
│                                                                                                                                                                  │
│ [FORCED INVARIANT]                                                                                                                                               │
│   - Humans CANNOT push patches directly to L2 Sandbox.                                                                                                           │
│   - Output strictly routed through L5 for Mandatory Re-Clearance via `HumanDecisionArtifact.__post_init__()`.                                                    │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ USE CASE #3 — HITL AS LEARNING FEEDBACK (DPO OPTIMIZATION)                                                                                                       │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [PURPOSE] Converting human outcomes into preference signals to tune future routing.                                                                               │
│ [ENTRYPOINTS]                                                                                                                                                    │
│ - agentic_core/L6_observability/engines/hitl_dpo_pair_generator.py                                                                                               │
│ - system_learning/engines/hitl_decision_logger.py                                                                                                                │
│                                                                                                                                                                  │
│ [DPO GENERATION FLOW]                                                                                                                                            │
│   1. Extract `original_plan` (Control) vs `human_patch` (Candidate).                                                                                             │
│   2. `DefaultDeterministicDPOPairGenerator` generates `DPOPair` using deterministic SHA-256 hashes.                                                              │
│   3. Outcome logged via `log_hitl_decision()` to `docs/reports/evidence/wave6_evidence.md`.                                                                      │
│   4. `RLHFOptimizer` proposes changes based on DPO batch -> `updates_routing_strategy`.                                                                          │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ USE CASE #4 — HITL AS CONFIDENCE-GATED ESCALATION                                                                                                                 │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [PURPOSE] Route low-confidence or policy-ambiguous actions to human authority before mutation or privileged execution.                                           │
│ [SIGNALS]                                                                                                                                                        │
│ - `gated_by_confidence` (37) + `escalates_to_human` (1,182) establish confidence-triggered human escalation pathways.                                           │
│ [RUNTIME ANCHORS]                                                                                                                                                │
│ - agentic_core/L0_routing/enforcement/policy_hash_enforcer.py                                                                                                   │
│ - agentic_core/L0_routing/meta_control/meta_apply.py                                                                                                             │
│ - agentic_core/L2_execution/determinism/replay_guard.py                                                                                                         │
│ [LOGIC FLOW]                                                                                                                                                     │
│   1. Confidence/policy gate fails closed (`POLICY_HASH_MISMATCH_*`, capability missing, or blast-radius violation).                                             │
│   2. Request is escalated to HITL review path instead of direct mutable apply.                                                                                  │
│   3. Approved outcomes can proceed through controlled apply seams; rejected outcomes remain non-mutating.                                                       │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ AIRLOCK LIFECYCLE HARDENING (ADG-BACKED)                                                                                                                         │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [LIFECYCLE EDGES]                                                                                                                                                │
│ - `enters_sandbox` (39) records boundary entry into constrained execution surface.                                                                               │
│ - `freezes_context` (5) enforces immutable context during review/decision windows.                                                                               │
│ - `unfreezes_context` (2) re-opens context only after guardrail-complete transitions.                                                                            │
│ [HARDENING IMPLICATION]                                                                                                                                           │
│ - Path D is not only a decision gate; it is also a state-lifecycle protocol with explicit freeze/unfreeze controls.                                             │
│ - Any HITL patch path must preserve the freeze -> decision -> re-clear -> unfreeze sequence.                                                                     │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ CORE PATH D & DPO DATA CONTRACTS                                                                                                                                │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ADG-BASED FOUR-USE-CASE MAPPING (PARALLEL, NOT SEQUENTIAL)                                                                                                     │
│ 1) Governance escalation gate (authority routing): requires_human_review + escalates_to_human + reenters_safety                                               │
│ 2) Path D decision airlock (human decision topology): routes_path + reenters_safety                                                                            │
│ 3) Learning feedback optimization loop: produces_preference_pair + builds_dpo_batch + proposal_commits_routing + updates_routing_strategy                     │
│ 4) Confidence-gated escalation trigger: gated_by_confidence + escalates_to_human (low-confidence/policy-ambiguous actions route to HITL review).             │
│ Note: Cases (1) and (4) are independent escalation triggers; Case (2) is the execution airlock; Case (3) is the downstream learning loop.                     │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [5] HumanDecisionArtifact : [trace_id, policy_hash, reviewer_id, action:ReviewAction, original_plan_hash, structured_patch_schema, reviewer_sig]                 │
│      -> Path: agentic_core/L3_orchestration/types/human_decision_artifact_types.py                                                                                │
│ [22] DPOExampleId         : [control_hash:str, candidate_hash:str] (Frozen Dataclass)                                                                            │
│      -> Path: agentic_core/L6_observability/types/dpo_types.py                                                                                                   │
│ [23] DPOPair              : [example_id, control_output_hash, candidate_output_hash, human_decision, reasons:tuple[str,...]]                                     │
│      -> Generates only if decision is "APPROVE" or "REJECT".                                                                                                     │
│ [23b] DPOBatch            : [pairs:tuple[DPOPair,...]] -> Batch container; canonical_bytes() for deterministic serialization                                    │
│      -> Path: agentic_core/L6_observability/types/dpo_types.py                                                                                                   │
│ [24] HITL Decision Record : HITL_DECISION_N: Agent=X | File=Y | Violation=Z | Proposed=W | Decision=D                                                            │
│      -> Thread-safe, ASCII-only, no timestamps in keys to maintain replayability.                                                                                │
│ [Path D Lifecycle Hardening] enters_sandbox -> freezes_context -> (human decision + L5 re-clear) -> unfreezes_context                                          │
│      -> Runtime anchors: agentic_core/L0_routing/enforcement/policy_hash_enforcer.py | agentic_core/L0_routing/meta_control/meta_apply.py | agentic_core/L2_execution/determinism/replay_guard.py │
│ [RLHF] DPO Integration    : RLHFOptimizer.propose_from_dpo(dpo_batch_bytes, current_threshold_config_bytes, embedding_context_hash) -> ChangePackage            │
│      -> Impl: DefaultDeterministicRLHFOptimizer  [system_learning/engines/rlhf_optimizer.py]                                                                     │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

[ARCHITECTURAL NOTE]: There are four distinct HITL use cases in this architecture.
Cases 1 and 4 are independent escalation triggers (policy/authority and confidence gating).
Case 2 is the decision airlock for human intervention execution safety.
Case 3 is the downstream learning loop fed by decided outcomes.