======================================================================================================================================================================
                                          AGENTIC SYSTEM — PATH D: HUMAN-IN-THE-LOOP & DPO FLOW (WIDESCREEN)
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
| [RLHF] DPO Integration    : RLHFOptimizer.propose_from_dpo(dpo_batch_bytes, current_threshold_config_bytes, embedding_context_hash) -> ChangePackage            |
|   Impl: DefaultDeterministicRLHFOptimizer  [system_learning/engines/rlhf_optimizer.py]                                                                           |
|   Emits bounded threshold ChangePackage (MEDIUM authority_sensitivity) in Stage 6 Meta-Learning Pipeline.                                                        |
======================================================================================================================================================================
