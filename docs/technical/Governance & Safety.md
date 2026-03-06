======================================================================================================================================================================
                                          AGENTIC SYSTEM — VERTICAL GOVERNANCE & SAFETY FILTER (L0 -> L3 -> L5 -> L2)
======================================================================================================================================================================
  [ THE TOP LAYER: INGESTION & OBSERVABILITY ]                                [ THE SIDE LAYER: THE POLICY OPTIMIZATION BUS & STATE ]
+---------------------------------------------------+                         +--------------------------------------------------------------------------------------+
| L1: COGNITIVE STUDIO / L6: OBSERVABILITY          |                         | ML: POLICY OPTIMIZATION / L4: REGISTRY                                               |
|---------------------------------------------------|                         |--------------------------------------------------------------------------------------|
| - [L1] Emits Raw Intent & Proposes Plan.          |======(Telemetry)=======>| - [Track] False Positives & Negatives from L5 blocks.                                |
| - [L6] Monitors active drifts & safety anomalies. |                         | - [Analyze] Safety Block Accuracy.                                                   |
+---------------------------------------------------+                         | - [Adapt] Risk Threshold Configs (stored in L4).                                     |
                          |                                                   | - [Tune] Safety Rule Strictness dynamically based on drifts.                         |
                          |                                                   | - [Persist] Block logs to L4 Telemetry Ledger.                                       |
                          v                                                   +--------------------------------------------------------------------------------------+
========================================================================================================||============================================================
  [ L0: ROUTING & TRAFFIC CONTROL ]                                                                     ||
+-----------------------------------------------------------------------------------------+             ||
| L0: ROUTING (TRAFFIC CONTROL)                                                           |<============|| (Applies tuned thresholds & active configs)
|-----------------------------------------------------------------------------------------|             ||
| - Receives tuned thresholds from the ML Policy Bus.                                     |             ||
| - Updates routing logic for future requests based on active Risk Tier limits.           |             ||
+-----------------------------------------------------------------------------------------+             ||
                          |                                                                             ||
                          v (Routes to Execution Paths)                                                 ||
+-----------------------------------------------------------------------------------------+             ||
| L3: ORCHESTRATOR / HUMAN REVIEW (PATH B / PATH D)                                       |             ||
|-----------------------------------------------------------------------------------------|             ||
| - Proposes a fully sequenced DAG execution plan.                                        |             ||
| - Path B: Submits plan for automated L5 Policy Check.                                   |             ||
| - Path D: Submits human-patched `MODIFY_DIFF`.                                          |             ||
|   [!] Human patches MUST flow down to L5 for mandatory re-clear before execution.       |             ||
+-----------------------------------------------------------------------------------------+             ||
                          |                                                                             ||
                          v (Proposes Exec Plan / Patched Diff)                                         ||
========================================================================================================||============================================================
  [ L5: THE SAFETY CHOKEPOINT (COMPLIANCE GUARD) ]                                                      ||
+-----------------------------------------------------------------------------------------+             ||
| L5: SAFETY GUARD & COMPLIANCE [♦ I::IValidator ♦]                                       |============>|| (Emits telemetry & false-positive reports up to ML bus)
|-----------------------------------------------------------------------------------------|             ||
| - [RISK] RISK TIER CLASSIFY: Evaluates tool blast radius and payload severity.          |             ||
| - P1: VALIDATE Proposal vs active L4 Policy Configs.                                    |             ||
| - [RE-CLR] MANDATORY RE-CLEAR FOR HUMAN MODIFY_DIFF PLANS:                              |             ||
|   (Trusts no one, not even human admins. All patches must pass the validator).          |             ||
| - P2: ENFORCE Approve, Remediate, or Reject.                                            |             ||
| - P3: REMEDIATE Safety Retry/Fix (Auto-patch minor drifts).                             |             ||
| - [STOP] HARD STOP REJECTION (Violations block execution & re-route to L1).             |             ||
| - P4: CERTIFY Audit Logs & Hashes.                                                      |             ||
| - [STMP] COMPLIANCE HASH/STAMP (Immutable cryptographic approval proof).                |             ||
+-----------------------------------------------------------------------------------------+             ||
                          |                                                                             ||
                          v (Pass / Approve - Emits Hash-Stamped Plan)                                  ||
========================================================================================================||============================================================
  [ THE AIRLOCK (HANDOFF TO L2) ]                                                                       ||
+-----------------------------------------------------------------------------------------+             ||
| [AUTH] STAMP WORK CONTRACT (Sandbox Permission Granted)                                 |             ||
|-----------------------------------------------------------------------------------------|             ||
| - Generates the cryptographically signed `SandboxEnvelope`.                             |             ||
| - Binds `CapabilityToken` (scoped + unexpired).                                         |             ||
| - Hands off governed payload to L2 Unified Execution Core (PTC Sandbox).                |             ||
+-----------------------------------------------------------------------------------------+             ||
                          |                                                                             ||
                          v (Injects Signed `SandboxEnvelope` into Sandbox)                             ||
+-----------------------------------------------------------------------------------------+             ||
| L2: UNIFIED EXECUTION CORE (PTC SANDBOX)                                                |             ||
|-----------------------------------------------------------------------------------------|             ||
| - Receives Auth Stamp and Governed Payload.                                             |             ||
| - Safely executes the validated DAG within established blast radius.                    |             ||
+-----------------------------------------------------------------------------------------+             ||
======================================================================================================================================================================
  CORE GOVERNANCE & SAFETY DATA CONTRACTS
======================================================================================================================================================================
| [STMP] Compliance Hash  : Immutable cryptographically signed stamp proving the exact plan hash passed the exact policy hash at a specific semantic time.             |
| [2] SandboxEnvelope     : [InstructionPacket, ToolBudget] -> Cannot be generated without L5 [AUTH] Stamp.                                                          |
| [5] HumanDecision       : MODIFY_DIFF MUST reference original plan_hash, use allowlist tools, and re-clear L5 before execution.                                    |
======================================================================================================================================================================
