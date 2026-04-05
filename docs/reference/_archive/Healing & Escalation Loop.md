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
| (SovereignLLMGateway.py)|                                                               |             ||
|-------------------------|---------------------------------------------------------------|             ||
| - Unified LLM provider operations (OpenAI, Anthropic, Google)                           |             ||
| - HealingProviderInvoker requests resolution from tier router                           |             ||
| - Provider health monitoring + centralized audit logging                                |             ||
| - Tool Adapter Layer (Dict -> SDK Type Casting)                                         |             ||
| - Returns `InvocationRecord` with deterministic audit trail                             |             ||
+-----------------------------------------------------------------------------------------+             ||
                          ^                      | (InvocationRecord)                                   ||
                          | (Request Repair)     v                                                      ||
==========================|=============================================================================||============================================================
  [ L2 / L2.3: UNIFIED EXECUTION CORE & HEALING SUBSYSTEM ]                                             ||
+-----------------------------------------------------------------------------------------+             ||
| [P2: EXECUTION GATEWAY] -> [UWG] UNIVERSAL WRITE GATEWAY                             |<============||
| (execution_gateway.py)    (UniversalWriteGateway.py)                                   |             ||
|-----------------------------------------------------------------------------------------|             ||
| EXECUTION GATEWAY:                                                                  |             ||
| - Builds ExecutionTrace with deterministic replay key computation                     |             ||
| - Enforces budget limits via BudgetEnforcer                                           |             ||
| - SandboxEnvelope signature verification (fail-closed boundary)                      |             ||
|                                                                                      |             ||
| UNIVERSAL WRITE GATEWAY:                                                             |             ||
| - Intercepts ALL FS/DB/Vector writes. Any un-transcripted I/O -> HARD FAIL.          |             ||
| - Non-UWG mutation -> SovereigntyError.                                              |             ||
| - [FREEZE] STRICT ZERO-LOSS ISOLATION: Execution halts immediately upon error.       |             ||
| - UWG locks all pending state diffs. Prevents ghost mutations.                       |             ||
| - FAILED status emitted to L2.3 Router.                                              |             ||
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
|                                                                                         |             ||
| [HEALING TIER DISPATCHER] (healing_tier_dispatcher.py)                                 |             ||
| - SINGLE production point: consumes HealingDecision.tier -> invokes provider           |             ||
| - LOCAL_AGENT -> invoke_local() (no external LLM call)                                  |             ||
| - QWEN_VLLM -> invoke_qwen_vllm() (Qwen vLLM provider)                                  |             ||
| - GEMINI_2_5_PRO -> invoke_gemini() (Gemini 2.5 Pro provider)                          |             ||
| - Injectable HealingProviderInvoker for test isolation                                 |             ||
+-----------------------------------------------------------------------------------------+             ||
======================================================================================================================================================================
  L2.3 HEALING TIER ROUTER — FULL SCORING & DETERMINISM INTERNALS
======================================================================================================================================================================
+-----------------------------------------------------------------------------------------+
| ESCALATION CONTEXT BUILDER [SSOT]                                                       |
|-----------------------------------------------------------------------------------------|
| EscalationContext.from_result()                                                         |
|   -> Parses escalation_hint key=value pairs from HealCheckResult                       |
|   -> Deterministic: same inputs -> same output always                                  |
|   -> Fields: [check_id, healer_name, retry_count, failure_type,                        |
|               blast_radius_estimate, summary(notes[:120]),                             |
|               trace_id("disp-"+sha256(check_id:retry_count)[:12])]                     |
|                                                                                         |
| FailureSignal (built from EscalationContext ONLY)                                       |
|   -> .to_healing_input() -> HealingInput consumed by route_healing_tier()              |
|   -> Fields: [source_agent, failure_type, error_signature, trace_id,                   |
|               context={healer_name,summary}, retry_count, blast_radius_estimate]       |
|   -> Agents in NO_TIERING class MUST emit FailureSignal;                               |
|      L2.3 selects tier on their behalf                                                  |
+-----------------------------------------------------------------------------------------+
                          |
                          v
+-----------------------------------------------------------------------------------------+
| HEALING TIER ROUTER [CHOKE POINT] (healing_tier_router.py)                              |
|-----------------------------------------------------------------------------------------|
| [DETERMINISM GUARANTEE] Mathematically deterministic:                                   |
|   - No environment variable access                                                      |
|   - No external data loading                                                            |
|   - Fixed precision arithmetic                                                          |
|   - Versioned historical data (HISTORICAL_DATA_VERSION)                                |
|   - Timestamp excluded from replay keys                                                 |
|                                                                                         |
| [SCORING COMPONENTS] (weights sum to 1.0):                                              |
|   FAILURE_CLASS_PRIORS:                                                                 |
|     syntax_error=0.90, import_error=0.85, test_discovery=0.80,                         |
|     runtime_error=0.70, unknown=0.50                                                    |
|   WEIGHT_FAILURE_PRIOR:      0.25                                                       |
|   WEIGHT_BLAST_RADIUS:       0.20                                                       |
|   WEIGHT_HISTORICAL_SUCCESS: 0.15                                                       |
|   WEIGHT_TOOL_READINESS:     0.15                                                       |
|   WEIGHT_RETRY_DECAY:        0.10                                                       |
|   WEIGHT_FAILURE_ENTROPY:    0.15                                                       |
|                                                                                         |
| [!] Restricts to TIERING_ALLOWLIST (YES_TIERING):                                       |
|     (CodeHealer, GravityLeakRepair, SafetyExec, etc.)                                  |
| [!] Non-allowlisted MUST emit FailureSignal instead                                     |
|                                                                                         |
| TIER THRESHOLDS:                                                                        |
|   heal_confidence >= 0.75  -> LOCAL_AGENT    (Deterministic/Light)                     |
|   0.40 <= score < 0.75     -> QWEN_VLLM      (Open-weights/Medium)                     |
|   score < 0.40             -> GEMINI_2_5_PRO (Heavy RCA)                               |
|   retry_count >= 3         -> GEMINI_2_5_PRO (forced, regardless of score)             |
+-----------------------------------------------------------------------------------------+
                          |
                          v
+-----------------------------------------------------------------------------------------+
| MODEL RESOLUTION INVARIANT                                                              |
|-----------------------------------------------------------------------------------------|
| - Tier router returns symbolic model_id ONLY                                            |
| - Concrete provider binding occurs exclusively in SovereignLLMGateway                  |
| - Direct SDK imports or hardcoded model literals in agents -> HARD FAIL (AST blocked)   |
+-----------------------------------------------------------------------------------------+
                          |
                          v
+-----------------------------------------------------------------------------------------+
| HealingProviderInvoker (injectable seam)                                                |
|-----------------------------------------------------------------------------------------|
| - Returns InvocationRecord: [tier, model_id, agent_name, trace_id,                     |
|   heal_confidence, method_called]                                                       |
| - Immutable audit record of every provider invocation                                  |
| - Appended to HealCheckResult.notes as deterministic audit string:                     |
|   "tier_escalation: check_id=X tier=Y model=Z..."                                      |
+-----------------------------------------------------------------------------------------+
                          |
                          v
+-----------------------------------------------------------------------------------------+
| HealingOutcomeIntakeAdapter (feedback loop closure)                                     |
|-----------------------------------------------------------------------------------------|
| - Receives InvocationRecord, builds IntakeRecord                                        |
| - Persists to L4B (consumed by MetaLearningPipeline Stage 8.5)                         |
| - Enables future tier routing improvements via meta-learning                            |
+-----------------------------------------------------------------------------------------+
======================================================================================================================================================================
  L2 ENFORCEMENT LAYER ADDITIONAL COMPONENTS
======================================================================================================================================================================
| BOUNDARY VERIFIER      : Validates cross-layer boundaries and prevents architectural violations                    |
| BUDGET ENFORCER        : Enforces resource budget limits and prevents resource exhaustion                          |
| CAPABILITY CHOKEPOINT  : Central control point for all capability access and authorization                        |
| NETWORK EGRESS GUARD   : Controls and monitors all outbound network communications                                |
| PROVIDER BINDING DETERMINISM : Ensures consistent provider binding and prevents substitution attacks               |
| RUNTIME INTERCEPTOR    : Intercepts runtime calls for audit and enforcement                                      |
| TOOL POLICY ENFORCER   : Enforces tool usage policies and prevents unauthorized tool access                       |
| WRITE SET ENFORCER     : Validates and controls write operations to prevent unauthorized mutations                 |
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
