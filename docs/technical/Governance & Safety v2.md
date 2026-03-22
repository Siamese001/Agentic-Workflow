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
|                                                                                         |             ||
| GOVERNANCE VALIDATORS:                                                                  |             ||
| - GovernanceShieldValidator: scan_risk_level, detect_privacy_language,                  |             ||
|   check_forbidden_patterns, generate_safety_protocol, audit_content_compliance          |             ||
|   Returns: GovernanceResult [passed, issues, risk_level, score, protocol, metadata]     |             ||
| - SSOTStructureValidator: validate_agent, validate_structure, generate_report           |             ||
|   Validates: base_agent_location, layer_assignment, depth, territory, forbidden_patterns|             ||
|   Returns: StructureValidationResult [total_agents, compliant_agents, violations]       |             ||
| - LazySeamEnforcer: Governs upward imports (L_lower → L_higher)                         |             ||
|   scan_file, scan_codebase, enforce, LazyUpwardImport detection                         |             ||
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
|                                                                                         |             ||
| L2 ENFORCEMENT LAYER:                                                                   |             ||
| - CapabilityChokepoint: Central control for capability access and authorization         |             ||
|   Methods: issue_token, authorize_and_execute, freeze, decisions                        |             ||
| - L2BoundaryVerifier: Validates cross-layer boundaries and L5 certification             |             ||
|   Methods: verify_instruction_packet, verify_l5_certification, verify_sandbox_envelope  |             ||
|   verify_packet, verify_envelope, is_packet_valid, is_l5_certified, is_envelope_valid   |             ||
+-----------------------------------------------------------------------------------------+             ||
                          |                                                                             ||
                          v (Applies HITL / Context Freeze / Learning)                                  ||
========================================================================================================||============================================================
  [ HITL ADG OVERLAY (v2) — GOVERNANCE & SAFETY EXPANSION ]                                             ||
+-----------------------------------------------------------------------------------------+             ||
| HITL ADG OVERLAY & LIFECYCLE CONTROLS                                                   |             ||
|-----------------------------------------------------------------------------------------|             ||
| ADG & LIFECYCLE SIGNALS:                                                                |             ||
| - ADG HITL Signals: escalates_to_human=1182 | requires_human_review=5 |                 |             ||
|   routes_path=183 | reenters_safety=11 | gated_by_confidence=37                         |             ||
| - Lifecycle Signals: enters_sandbox=39 | freezes_context=5 | unfreezes_context=2        |             ||
| - Learning Linkage: builds_dpo_batch=43 | produces_preference_pair=13                   |             ||
|                                                                                         |             ||
| GOVERNANCE HARDENING ADDITIONS:                                                         |             ||
| - Four distinct HITL use cases apply: governance escalation, Path D decision airlock,   |             ||
|   learning feedback, and confidence-gated escalation.                                   |             ||
| - Confidence gating is a separate upstream trigger to human review; it is not           |             ||
|   reducible to privileged-action review only.                                           |             ||
| - Safety invariants require freeze -> decision -> L5 re-clear -> unfreeze before        |             ||
|   reentry to execution for all MODIFY_DIFF or confidence-routed paths.                  |             ||
+-----------------------------------------------------------------------------------------+             ||

======================================================================================================================================================================
  CORE GOVERNANCE & SAFETY DATA CONTRACTS
======================================================================================================================================================================
| [STMP] Compliance Hash       : Immutable cryptographically signed stamp proving the exact plan hash passed the exact policy hash at a specific semantic time.      |
| [2] SandboxEnvelope          : [InstructionPacket, ToolBudget] -> Cannot be generated without L5 [AUTH] Stamp.                                                   |
| [5] HumanDecision            : MODIFY_DIFF MUST reference original plan_hash, use allowlist tools, and re-clear L5 before execution.                             |
| [18] GovernanceResult        : [passed:bool, issues:list[str], risk_level:str, score:float, protocol:str, metadata:dict] -> Risk classification output          |
| [19] StructureViolation      : [agent_class, agent_path, violation_type, message, severity, suggested_fix] -> SSOT structure violation                          |
| [20] StructureValidationResult: [total_agents, compliant_agents, violations, base_agent_violations, layer_violations, depth_violations, territory_violations]   |
| [21] LazyUpwardImport        : [source_file, source_layer, target_layer, import_statement, line_number, context] -> Upward import detection                     |
======================================================================================================================================================================