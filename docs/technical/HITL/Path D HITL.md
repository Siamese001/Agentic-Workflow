======================================================================================================================================================================
                                          AGENTIC SYSTEM — PATH D: HUMAN-IN-THE-LOOP & DPO FLOW (WIDESCREEN)
======================================================================================================================================================================
  ADG SNAPSHOT OVERLAY (SOURCE OF TRUTH: artifacts/adg/adg_snapshot_03162026_0931.json)
======================================================================================================================================================================
| modules=8,591 | symbols=60,196 | relations=815,826 | layer_violations=0 | scanner_digest=30192334d3137825b8bbc050d59f83f3ea7c3a6561f334181d32d287acd49d6d |
| HITL/Path-D signal counts: escalates_to_human=1182 | requires_human_review=5 | routes_path=183 | reenters_safety=11 | builds_dpo_batch=43 | produces_preference_pair=13 |
| Confidence + Airlock lifecycle: gated_by_confidence=37 | enters_sandbox=39 | freezes_context=5 | unfreezes_context=2                                                  |
| Learning-loop linkage: proposal_commits_routing=3029 | updates_routing_strategy=3011                                                                                         |
======================================================================================================================================================================
  [ L3: ESCALATION TO PATH D ]                       [ THE HUMAN ISOLATION AIRLOCK ]                              [ DOWNSTREAM ROUTING & FEEDBACK ]
======================================================================================================================================================================
+-----------------------------------------+        +--------------------------------------------------------------+ +------------------------------------------------+
| L3: ORCHESTRATOR (REVIEW INITIATION)    |        | HUMAN DECISION GATE (Zero Authority Sandbox)                 | | L5: THE SAFETY GUARD (RE-CLEARANCE)            |
|-----------------------------------------|        |--------------------------------------------------------------| |------------------------------------------------|
| - Prepares HumanDecisionArtifact.       |=======>| - [ISOLATE] Admin has zero authority to mutate tool          | | - [RE-CLR] All MODIFY_DIFF patches MUST be     |
| - Emits `original_plan_hash`.           |        |   permissions or bypass system invariants directly.          |=|   re-evaluated by the active L5 policies.      |
| - Freezes execution pending decision.   |        |                                                              | | - l5_reclear_required=True enforced by         |
+-----------------------------------------+        | [ THE DECISION MATRIX ]                                      | |   HumanDecisionArtifact.__post_init__().       |
                                                   | 1. [APPROVE]     -> Fast-tracks to L5 [AUTH] Stamp.          | | - If Approved -> Mints [AUTH] Stamp.           |
                                                   | 2. [REJECT]      -> Aborts wave, re-routes to L1.            | | - Routes to L2 PTC Sandbox for execution.      |
                                                   | 3. [MODIFY_DIFF] -> Human provides `structured_patch_schema`.| +------------------------------------------------+
                                                   |                     MUST reference `original_plan_hash`.     |                       | (Executes)
                                                   |                     MUST use only allowlisted tools.         |                       v
                                                   |                     Sets l5_reclear_required=True.           | +------------------------------------------------+
                                                   +--------------------------------------------------------------+ | L6 / PATH D FEEDBACK: RLHF DPO GENERATION      |
                                                   | [ THE FORCED ROUTING INVARIANT ]                             | +------------------------------------------------+
                                                   |--------------------------------------------------------------| | 1. Extracts `original_plan` (Control) and      |
                                                   | - Humans CANNOT push patches directly to L2 Sandbox.         | |    `human_patch` (Candidate).                  |
                                                   | - Output strictly routed to L5 for Mandatory Re-Clear.       | | 2. DefaultDeterministicDPOPairGenerator        |
                                                   +--------------------------------------------------------------+ |    .generate(control_output_bytes,             |
                                                                     | (Forces Patch down the Elevator Shaft)         |    candidate_output_bytes, human_decision,      |
                                                                     v                                              |    reason_codes) -> DPOPair:                    |
                                                   +--------------------------------------------------------------+ |    - SHA-256(control_output_bytes)             |
                                                   | HITL DECISION LOGGER (Thread-Safe, Stdlib-Only)              | |    - SHA-256(candidate_output_bytes)           |
                                                   | system_learning/engines/hitl_decision_logger.py              | |    - Validates APPROVE/REJECT decision         |
                                                   |--------------------------------------------------------------| |    - Creates DPOExampleId(control_hash,        |
                                                   | - log_hitl_decision(agent, file_path, violation, proposed,   | |      candidate_hash)                           |
                                                   |   decision, extra) -> decision_number                        | | 3. log_hitl_decision():                        |
                                                   | - Evidence path: docs/reports/evidence/wave6_evidence.md     | |    - Appends to evidence file                  |
                                                   | - Format: HITL_DECISION_N: Agent=X | File=Y                  | |    - Thread-safe via module-level _lock        |
                                                   |   Violation=Z | Proposed=W | Decision=D                       | |    - ASCII-only output (byte-scan invariant)   |
                                                   | - Deterministic record format for replay                     | |    - No wall-clock timestamps in keys          |
                                                   | - HITLDecisionLogger class:                                   | | 4. Routes to Stage 6 Meta-Learning Pipeline.   |
                                                   |   agentic_core/L5_safety/hitl/decision_logger.py             | | 5. RLHFOptimizer.propose_from_dpo(             |
                                                   |   HITLDecision: [decision_number, agent, file, violation,    | |      dpo_batch_bytes,                          |
                                                   |   proposed, decision, reviewer_signature, metadata]          | |      current_threshold_config_bytes,           |
                                                   +--------------------------------------------------------------+ |      embedding_context_hash) -> ChangePackage  |
                                                   +--------------------------------------------------------------+ |    Impl: DefaultDeterministicRLHFOptimizer     |
                                                                     | (Forces Patch down the Elevator Shaft)         |    system_learning/engines/rlhf_optimizer.py   |
                                                                     v                                              +------------------------------------------------+
======================================================================================================================================================================
  CORE PATH D & DPO DATA CONTRACTS
======================================================================================================================================================================
| ADG-BASED FOUR-USE-CASE MAPPING (PARALLEL, NOT SEQUENTIAL)                                                                                                          |
| 1) Governance escalation gate (authority routing): requires_human_review + escalates_to_human + reenters_safety                                                     |
| 2) Path D decision airlock (human decision topology): routes_path + reenters_safety                                                                                  |
| 3) Learning feedback optimization loop: produces_preference_pair + builds_dpo_batch + proposal_commits_routing + updates_routing_strategy                           |
| 4) Confidence-gated escalation trigger: gated_by_confidence + escalates_to_human (low-confidence/policy-ambiguous actions route to HITL review).                   |
| Note: Cases (1) and (4) are independent escalation triggers; Case (2) is the execution airlock; Case (3) is the downstream learning loop.                           |
======================================================================================================================================================================
| [5] HumanDecisionArtifact : [trace_id, policy_hash, reviewer_id, action:ReviewAction, original_plan_hash, structured_patch_schema, reviewer_sig]                |
|   L3: agentic_core/L3_orchestration/types/human_decision_artifact_types.py                                                                                       |
|   L5: agentic_core/L5_safety/types/human_decision_artifact_types.py                                                                                              |
|   ReviewAction = Literal["APPROVE", "MODIFY_DIFF", "REJECT"]                                                                                                     |
|   MODIFY_DIFF sets l5_reclear_required=True (enforced via __post_init__). MODIFY_DIFF requires non-empty structured_patch_schema.                                |
| [22] DPOExampleId         : [control_hash:str, candidate_hash:str] -> Deterministic SHA-256 hashes (frozen dataclass)                                           |
|   agentic_core/L6_observability/types/dpo_types.py                                                                                                               |
| [23] DPOPair              : [example_id:DPOExampleId, control_output_hash:str, candidate_output_hash:str, human_decision:str, reasons:tuple[str,...]]            |
|   -> Built via DefaultDeterministicDPOPairGenerator.generate(control_output_bytes, candidate_output_bytes, human_decision, reason_codes)                         |
|   -> human_decision MUST be "APPROVE" or "REJECT" (ValueError otherwise)                                                                                         |
|   agentic_core/L6_observability/engines/hitl_dpo_pair_generator.py                                                                                               |
| [23b] DPOBatch            : [pairs:tuple[DPOPair,...]] -> Batch container; canonical_bytes() for deterministic serialization                                     |
|   agentic_core/L6_observability/types/dpo_types.py                                                                                                               |
| [24] HITL Decision Record : HITL_DECISION_N: Agent=X | File=Y | Violation=Z | Proposed=W | Decision=D -> Thread-safe, ASCII-only, no timestamps in keys         |
|   log_hitl_decision(agent, file_path, violation, proposed, decision, extra) -> int  [system_learning/engines/hitl_decision_logger.py]                            |
|   HITLDecisionLogger.log(agent, file, violation, proposed, decision, reviewer_signature, metadata) -> HITLDecision  [agentic_core/L5_safety/hitl/decision_logger.py]|
| [Path D Lifecycle Hardening] enters_sandbox -> freezes_context -> (human decision + L5 re-clear) -> unfreezes_context                                               |
|   Runtime anchors: agentic_core/L0_routing/enforcement/policy_hash_enforcer.py | agentic_core/L0_routing/meta_control/meta_apply.py | agentic_core/L2_execution/determinism/replay_guard.py |
| [RLHF] DPO Integration    : RLHFOptimizer.propose_from_dpo(dpo_batch_bytes, current_threshold_config_bytes, embedding_context_hash) -> ChangePackage            |
|   Impl: DefaultDeterministicRLHFOptimizer  [system_learning/engines/rlhf_optimizer.py]                                                                           |
|   Emits bounded threshold ChangePackage (MEDIUM authority_sensitivity) in Stage 6 Meta-Learning Pipeline.                                                        |
======================================================================================================================================================================