============================================================================================================================================================
                              DRILL-DOWN 7: PATH D — THE HUMAN-IN-THE-LOOP (HITL) PROTOCOL (QUINTUPLE-CLICK)
    (TENSOR-LEVEL VIEW: EVIDENCE PACK ASSEMBLY, HUMAN DECISION ARTIFACTS, DPO FEEDBACK LOOPS, & CRYPTOGRAPHIC OVERRIDES)
============================================================================================================================================================

                                   [ FROM: MULTIPLE ESCALATION VECTORS ]
                                   +---------------------------------------------------------------------------------+
                                   | L0: Guardian Override (Injection Detected / High Ambiguity)                     |
                                   | L3: Budget Ceiling Exceeded / Capability Missing                                |
                                   | L5: Risk Tier 4-5 / Hard Stop Policy Violation                                  |
                                   | L2.3: Healer Exhaustion (Retries > 3)                                           |
                                   +---------------------------------------------------------------------------------+
                                                         ||
                                                         || (Push: Escalation Payload -> trace_id, reason, state_dump)
                                                         v
+==========================================================================================================================================================+
| \\\ PATH D: THE HUMAN REVIEW GATE (HITL)                                                                                                            /// |
| \\\ Authority: OVERRIDE. Can manually sign execution plans, but modified plans must still clear the L5 structural safety gate.                      /// |
|==========================================================================================================================================================|
|                                                                                                                                                          |
|  +-------------------------------------------------------------------------------------------+                                                           |
|  | 1.0 EVIDENCE PACK ASSEMBLY (THE DIAGNOSTIC CONTEXT BUILDER)                               |                                                           |
|  |-------------------------------------------------------------------------------------------|                                                           |
|  | [1.1] Trace Aggregation: Pulls the full lifecycle of `trace_id` from L4 Immutable Ledger. |                                                           |
|  | [1.2] State Snapshot: Captures the exact `boundary_snapshot.json` to show the human what  |                                                           |
|  |       the system looks like right now.                                                    |                                                           |
|  | [1.3] Logic Unrolling: Translates the L1 `raw_reasoning` (CoT/ToT) into a visual DAG for  |                                                           |
|  |       the reviewer.                                                                       |                                                           |
|  | [1.4] Risk Highlighting: Overlays the specific L5 Policy markers that triggered the halt. |                                                           |
|  |       Emits -> `EvidencePack Artifact` (Read-only UI payload).                            |                                                           |
|  +-------------------------------------------------------------------------------------------+                                                           |
|                                         ||                                                                                                               |
|                                         v (Rendered to Admin Console)                                                                                    |
|  +-------------------------------------------------------------------------------------------+                                                           |
|  | 2.0 THE REVIEWER INTERFACE & DECISION MATRIX                                              |                                                           |
|  |-------------------------------------------------------------------------------------------|                                                           |
|  | Human reviewer authenticates (MFA / SSO) and evaluates the `EvidencePack`.                |                                                           |
|  | They MUST select one of three strict actions:                                             |                                                           |
|  |                                                                                           |                                                           |
|  | [OPTION A: APPROVE] -> Reviewer determines L5/L0 was overly strict (False Positive).      |                                                           |
|  |                        Original payload is marked for execution.                          |                                                           |
|  | [OPTION B: REJECT]  -> Reviewer agrees with system halt (True Positive).                  |                                                           |
|  |                        Payload is killed. Task fails gracefully back to user.             |                                                           |
|  | [OPTION C: MODIFY]  -> Reviewer provides a JSON Patch (RFC 6902) or edits the prompt/diff |                                                           |
|  |                        manually to correct the agent's trajectory.                        |                                                           |
|  +-------------------------------------------------------------------------------------------+                                                           |
|                                         ||                                                                                                               |
|                                         v                                                                                                                |
|  +-------------------------------------------------------------------------------------------+                                                           |
|  | 3.0 CRYPTOGRAPHIC PACKAGING (THE HUMAN DECISION ARTIFACT)                                 |                                                           |
|  |-------------------------------------------------------------------------------------------|                                                           |
|  | [3.1] Schema Enforcement: The decision is packaged into the strict ARB contract:          |                                                           |
|  |       `HumanDecisionArtifact: [trace_id, policy_hash, reviewer_id,                        |
|  |                                action:[APPROVE|MODIFY_DIFF|REJECT], reviewer_signature]`  |                                                           |
|  | [3.2] Human Signature: The artifact is signed using the human reviewer's unique HSM-      |                                                           |
|  |       backed key (or short-lived JWT).                                                    |                                                           |
|  | [3.3] Dual-Emission: The artifact is simultaneously emitted to two separate buses:        |                                                           |
|  |       -> The Control Spine (for immediate execution/rejection).                           |                                                           |
|  |       -> The Meta-Learning Bus (for future system optimization).                          |                                                           |
|  +-------------------------------------------------------------------------------------------+                                                           |
|                                         ||                                                                                                               |
|                   +---------------------++---------------------+                                                                                         |
|                   | (If REJECT)                                | (If APPROVE or MODIFY)                                                                  |
|                   v                                            v                                                                                         |
|  +-----------------------------------+      +-----------------------------------------------------------------+                                          |
|  | 4.0 GRACEFUL TERMINATION          |      | 5.0 THE RE-ENTRY AIRLOCK (L5 ZERO-TRUST RE-VERIFICATION)        |                                          |
|  |-----------------------------------|      |-----------------------------------------------------------------|                                          |
|  | [4.1] UWG Mutex Release: Any      |      | [5.1] Human Fallibility Check: Humans can make typos or be      |                                          |
|  |       stale locks held by the     |      |       coerced. A human `MODIFY` does NOT bypass structural      |                                          |
|  |       trace are dropped.          |      |       safety.                                                   |                                          |
|  | [4.2] L4 Commit: REJECT is logged |      | [5.2] L5 AST Fencing: The human-modified script is passed back  |                                          |
|  |       to the Immutable Ledger.    |      |       through L5 to ensure no `os.system` or syntax breaking    |                                          |
|  | [4.3] Session End: System halts.  |      |       changes were introduced.                                  |                                          |
|  +-----------------------------------+      | [5.3] L2 Execution: If L5 passes, the payload enters L2 UWG     |                                          |
|                                             |       with the `reviewer_signature` attached as proof of auth.  |                                          |
|                                             +-----------------------------------------------------------------+                                          |
|                                                                                                                                                          |
+==========================================================================================================================================================+
                                         ||
                                         || (Simultaneous Asynchronous Fire: To L6 Meta-Learning Bus)
                                         v
+==========================================================================================================================================================+
| \\\ META-LEARNING FEEDBACK LOOP (HOW THE SYSTEM LEARNS FROM HUMANS)                                                                                 /// |
|==========================================================================================================================================================|
|                                                                                                                                                          |
|  +-------------------------------------------------------------------------------------------+                                                           |
|  | 6.0 DPO PAIR GENERATION & ROUTING OPTIMIZATION                                            |                                                           |
|  |-------------------------------------------------------------------------------------------|                                                           |
|  | [6.1] Labeling the Signal:                                                                |                                                           |
|  |       -> IF APPROVE (False Positive): The L5 threshold was too strict, or L0 routed       |                                                           |
|  |          badly. The `risk_score` for this `intent_vector` is flagged for downgrade.       |                                                           |
|  |       -> IF REJECT (True Positive): The L5/L0 guardrails worked perfectly. The anomaly    |                                                           |
|  |          classifier weights are reinforced.                                               |                                                           |
|  |       -> IF MODIFY (Correction): The Agent's plan was flawed.                             |                                                           |
|  | [6.2] RLHF / DPO Extraction: For `MODIFY` actions, L6 automatically generates a Direct    |                                                           |
|  |       Preference Optimization (DPO) pair:                                                 |                                                           |
|  |       `{ "prompt": [U0], "rejected": [Agent_Original_Plan], "chosen": [Human_Plan] }`     |                                                           |
|  | [6.3] Commit to L4 Vault: The DPO pairs and threshold adjustments are committed via the   |                                                           |
|  |       Meta-Learning Bus to the L4 Anchor (as detailed in Drill-Downs 4 & 5), allowing     |                                                           |
|  |       the router to adapt its behavior in Run t+1.                                        |                                                           |
|  +-------------------------------------------------------------------------------------------+                                                           |
|                                                                                                                                                          |
+==========================================================================================================================================================+
