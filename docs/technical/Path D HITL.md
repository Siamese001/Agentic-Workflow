======================================================================================================================================================================
                                          AGENTIC SYSTEM — PATH D: HUMAN-IN-THE-LOOP & DPO FLOW (WIDESCREEN)
======================================================================================================================================================================
  [ L3: ESCALATION TO PATH D ]                       [ THE HUMAN ISOLATION AIRLOCK ]                              [ DOWNSTREAM ROUTING & FEEDBACK ]
======================================================================================================================================================================
+-----------------------------------------+        +--------------------------------------------------------------+ +------------------------------------------------+
| L3: ORCHESTRATOR (REVIEW INITIATION)    |        | HUMAN DECISION GATE (Zero Authority Sandbox)                 | | L5: THE SAFETY GUARD (RE-CLEARANCE)            |
|-----------------------------------------|        |--------------------------------------------------------------| |------------------------------------------------|
| - Prepares Review Artifact.             |=======>| - [ISOLATE] Admin has zero authority to mutate tool          | | - [RE-CLR] All MODIFY_DIFF patches MUST be     |
| - Emits `original_plan_hash`.           |        |   permissions or bypass system invariants directly.          |=|   re-evaluated by the active L5 policies.      |
| - Freezes execution pending decision.   |        |                                                              | | - If Approved -> Mints [AUTH] Stamp.           |
+-----------------------------------------+        | [ THE DECISION MATRIX ]                                      | | - Routes to L2 PTC Sandbox for execution.      |
                                                   | 1. [APPROVE]     -> Fast-tracks to L5 [AUTH] Stamp.          | +------------------------------------------------+
                                                   | 2. [REJECT]      -> Aborts wave, re-routes to L1.            |                      | (Executes)
                                                   | 3. [MODIFY_DIFF] -> Human provides `structured_patch_schema`.|                      v
                                                   |                     MUST reference `original_plan_hash`.     | +------------------------------------------------+
                                                   |                     MUST use only allowlisted tools.         | | L6 / PATH D FEEDBACK: RLHF DPO GENERATION      |
                                                   +--------------------------------------------------------------+ +------------------------------------------------+
                                                   | [ THE FORCED ROUTING INVARIANT ]                             |=| 1. Extracts `original_plan` (Control) and      |
                                                   |--------------------------------------------------------------| |    `human_patch` (Candidate).                  |
                                                   | - Humans CANNOT push patches directly to L2 Sandbox.         | | 2. DPOPairGenerator.generate():                |
                                                   | - Output strictly routed to L5 for Mandatory Re-Clear.       | |    - SHA-256(control_output_bytes)             |
                                                   +--------------------------------------------------------------+ |    - SHA-256(candidate_output_bytes)           |
                                                                     | (Forces Patch down the Elevator Shaft)         |    - Validates APPROVE/REJECT decision         |
                                                                     v                                              |    - Creates DPOExampleId(control_hash,        |
                                                   +--------------------------------------------------------------+ |      candidate_hash)                           |
                                                   | HITL DECISION LOGGER (Thread-Safe, Stdlib-Only)              | | 3. log_hitl_decision():                        |
                                                   |--------------------------------------------------------------| |    - Appends to evidence file                  |
                                                   | - log_hitl_decision(agent, file_path, violation, proposed,   | |    - Thread-safe via module-level lock         |
                                                   |   decision, extra) -> decision_number                        | |    - ASCII-only output (byte-scan invariant)   |
                                                   | - Evidence path: docs/reports/evidence/wave6_evidence.md     | |    - No wall-clock timestamps in keys          |
                                                   | - Format: HITL_DECISION_N: Agent=X | File=Y                  | | 4. Routes to Stage 6 Meta-Learning Pipeline.   |
                                                   |   Violation=Z | Proposed=W | Decision=D                       | | 5. `RLHFOptimizer.propose_from_dpo()` tunes    |
                                                   | - Deterministic record format for replay                     | |    future L3 orchestration weights.            |
                                                   +--------------------------------------------------------------+ +------------------------------------------------+
                                                   +--------------------------------------------------------------+
                                                                     | (Forces Patch down the Elevator Shaft)
                                                                     v
======================================================================================================================================================================
  CORE PATH D & DPO DATA CONTRACTS
======================================================================================================================================================================
| [5] HumanDecisionArtifact : [trace_id, policy_hash, reviewer_id, action:[APPROVE|MODIFY|REJECT], patch_schema, sig] -> MODIFY MUST re-clear L5.                 |
| [22] DPOExampleId         : [control_hash:str, candidate_hash:str] -> Deterministic SHA-256 hashes of control and candidate outputs                             |
| [23] DPOPair              : [example_id:DPOExampleId, control_output_hash, candidate_output_hash, human_decision:APPROVE|REJECT, reasons:tuple[str, ...]]       |
|                             -> Built deterministically via DefaultDeterministicDPOPairGenerator.generate()                                                        |
| [24] HITL Decision Record : HITL_DECISION_N: Agent=X | File=Y | Violation=Z | Proposed=W | Decision=D -> Thread-safe, ASCII-only, no timestamps in keys         |
| [RLHF] DPO Integration    : dpo_batch_bytes + RLHFOptimizer.propose_from_dpo() -> Emits threshold ChangePackage in Stage 6.                                      |
======================================================================================================================================================================
