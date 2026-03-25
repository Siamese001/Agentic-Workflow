+=================================================================================================+
|                  AGENTIC SYSTEM: PATH D (HITL & DPO FLOW) — LIBRARY GOVERNANCE                  |
+=================================================================================================+
| 1. ESCALATION                 2. THE AIRLOCK                       3. ROUTING & LEARNING        |
|                                                                                                 |
| [L3 ORCHESTRATOR]             [HUMAN DECISION GATE]                [L5 SAFETY GUARD]            |
| (Reference Desk)              (Chief Librarian Airlock)            (Governance Archivist)       |
| - Prepares Artifact           - [ISOLATE] Zero Auth Sandbox        - Re-evaluates patches       |
| - Emits original_plan_hash    - The Decision Matrix:               - l5_reclear_required=True   |
| - Freezes context pending        |                                   enforced here.             |
|   decision                       +-- 1. [APPROVE] ---------------->| - Mints [AUTH] stamp       |
|         |                        |      Fast-tracks to L5          | - Routes to L2 Sandbox     |
|         |                        |                                 +-------------+--------------+
|         +----------------------> +-- 2. [REJECT]                                 | (Executes)
|                                  |      Aborts wave, re-routes L1                v
|                                  |                                       [L6 DPO FEEDBACK]
|                                  +-- 3. [MODIFY_DIFF] ---------------->  (Cataloging Board)
|                                         - Provide structured_patch_schema- Extracts DPOPair
|                                         - MUST ref original_plan_hash    - Hashes: Control vs
|                                         - MUST use allowlisted tools       Candidate bytes
|                                         - Sets l5_reclear_required=True  - Validates decision
|                                                                          - RLHFOptimizer loops
|                               [HITL DECISION LOGGER]                       to Stage 6 Pipeline
|                               (Audit Receipt Ledger)
|                               - ASCII-only / Thread-safe
|                               - Deterministic replay format
|                               - Forces patch down elevator shaft
+=================================================================================================+
| HIGH-SIGNAL DATA CONTRACTS (LIBRARY RULES & RECEIPTS):                                          |
| * HumanDecisionArtifact: [trace_id, action, patch_schema, original_hash]                        |
|   -> MODIFY_DIFF enforces l5_reclear_required=True via __post_init__()                          |
| * DPOPair: [example_id(SHA-256 Control & Candidate hashes), human_decision]                     |
| * HITL Decision Record: HITL_DECISION_N: Agent=X | File=Y | Violation=Z | Proposed=W | Dec=D  |
| * RLHFOptimizer: propose_from_dpo(batch, config, context) -> ChangePackage                      |
+=================================================================================================+
