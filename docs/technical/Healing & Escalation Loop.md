======================================================================================================================================================================
                                          AGENTIC SYSTEM — ZERO-LOSS HEALING & ESCALATION LOOP (VERTICAL TOPOLOGY)
======================================================================================================================================================================
  [ THE TOP LAYER: INGESTION & OBSERVABILITY ]                                [ THE SIDE LAYER: THE POLICY OPTIMIZATION BUS & STATE ]
+---------------------------------------------------+                         +--------------------------------------------------------------------------------------+
| L6: OBSERVABILITY & META-LEARNING INTEGRATION     |                         | L4: STATE BUS / AUDIT LEDGER                                                         |
|---------------------------------------------------|                         |--------------------------------------------------------------------------------------|
| 1. HealingOutcomeIntakeAdapter builds record.     |<====(Audit Egress)======| 2. Persists to L4B Healing Snapshots.                                                |
| 3. MetaLearningPipeline (Stage 8.5/8.6)           |                         | 4. Appends deterministic audit note to HealCheckResult.notes:                        |
|    consumes snapshots to tune future routing.     |                         |    "tier_escalation: check_id=X tier=Y..."                                           |
+---------------------------------------------------+                         +--------------------------------------------------------------------------------------+
                          ^                                                                             ||
                          | (Tunes Confidence Thresholds & Healer Logic Rules)                          || (Read Active Rules)
==========================|=============================================================================||============================================================
  [ THE EXTERNAL BOUND ]  |                                                                             ||
+-------------------------|---------------------------------------------------------------+             ||
| SOVEREIGN LLM GATEWAY   |                                                               |             ||
|-------------------------|---------------------------------------------------------------|             ||
| - HealingProviderInvoker requests resolution.                                           |             ||
| - Gateway performs concrete binding to SDK.                                             |             ||
| - Executes LLM repair logic.                                                            |             ||
| - Returns `InvocationRecord` to sandbox.                                                |             ||
+-----------------------------------------------------------------------------------------+             ||
                          ^                      | (InvocationRecord)                                   ||
                          | (Request Repair)     v                                                      ||
==========================|=============================================================================||============================================================
  [ L2 / L2.3: UNIFIED EXECUTION CORE & HEALING SUBSYSTEM ]                                             ||
+-----------------------------------------------------------------------------------------+             ||
| [P2: PTC EXECUTION ENGINE] -> [UWG] UNIVERSAL WRITE GATEWAY                             |<============||
|-----------------------------------------------------------------------------------------|             ||
| - Intercepts ALL FS/DB/Vector writes. Any un-transcripted I/O -> HARD FAIL.             |             ||
| - Non-UWG mutation -> SovereigntyError.                                                 |             ||
| - [FREEZE] STRICT ZERO-LOSS ISOLATION: Execution halts immediately upon error.          |             ||
| - UWG locks all pending state diffs. Prevents ghost mutations.                          |             ||
| - FAILED status emitted to L2.3 Router.                                                 |             ||
+-----------------------------------------------------------------------------------------+             ||
                          |                                                                             ||
                          v (SovereigntyError / Logic Violation)                                        ||
+-----------------------------------------------------------------------------------------+             ||
| L2.3: CONFIDENCE-TIER HEALING ENGINE                                                    |             ||
|-----------------------------------------------------------------------------------------|             ||
| [REMEDIATION DISPATCHER] (remediation_dispatcher.py)                                    |             ||
| 1. _invoke_healer(): Attempts deterministic rule-based fix.                             |             ||
|    [!] On exception -> auto-sets `needs_llm_escalation=True`                            |             ||
| 2. _tier_escalate() (Triggered on FAILED status):                                       |             ||
|    [G1] Is `check_id` in HEALER_ESCALATION_ALLOWLIST?                                   |             ||
|         (drift_detection, import_boundary, layer_inversion, ssot_drift)                 |             ||
|    [G2] Does `result.needs_llm_escalation == True`?                                     |             ||
|    -> If Guards pass, builds [SSOT] EscalationContext.                                  |             ||
|                                                                                         |             ||
|                           | (Emits FailureSignal)                                       |             ||
|                           v                                                             |             ||
| [HEALING TIER ROUTER] (healing_tier_router) [CHOKE POINT]                               |             ||
| - Consumes FailureSignal (Built ONLY from Context).                                     |             ||
| - Restricts escalation strictly to TIERING_ALLOWLIST.                                   |             ||
| - Calculates `heal_confidence` based on error/history:                                  |             ||
|   * >= 0.75 : LOCAL_AGENT    (Deterministic/Light)                                      |             ||
|   * >= 0.40 : QWEN_VLLM      (Open-weights/Medium)                                      |             ||
|   * < 0.40  : GEMINI_2_5_PRO (Heavy RCA / retry>=3)                                     |             ||
| - [!] INVARIANT: Returns *symbolic* `model_id` only.                                    |             ||
+-----------------------------------------------------------------------------------------+             ||
======================================================================================================================================================================
  CORE ZERO-LOSS & HEALING DATA CONTRACTS
======================================================================================================================================================================
| [UWG] Sovereignty Proof : Any un-transcripted network call -> HARD FAIL. Transcript must fully reconstruct all side-effects.                                         |
| [6] HealCheckResult     : [check_id, status, changes_made, rollback_info, notes, needs_llm_escalation:bool, escalation_hint:str] (CONTRACT_VERSION=2)                  |
| [7] EscalationContext   : [check_id, healer_name, retry_count, failure_type, blast_radius_estimate, summary, trace_id] (SSOT - Built from HealCheckResult)             |
| [8] FailureSignal       : [source_agent, failure_type, error_signature, trace_id, context, retry_count, blast_radius_estimate] -> Converts to HealingInput.            |
| [9] HealingDecision     : [heal_confidence:float, tier:HealingTier, reason_codes:tuple] -> Drives the routing logic thresholds (X=0.75, Y=0.40).                       |
| [10] InvocationRecord   : [tier, model_id, agent_name, trace_id, heal_confidence, method_called] -> Immutable audit record.                                            |
======================================================================================================================================================================
