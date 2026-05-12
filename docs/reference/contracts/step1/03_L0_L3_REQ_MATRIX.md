# 03 L0 Route Decision and L3 Orchestration — REQ Matrix (Step 1 Aggregation)

Step 1 aggregation only. Implementation mapping and proof are Phase 2.

Hardened: 2026-05-12 (W2.P1) — All TBD placeholders replaced with concrete contract requirements.

---

## Layer Contract Summary

### L0 Route Decision

| Aspect | Specification |
|--------|---------------|
| **incoming_contracts** | L1PlanContract |
| **outgoing_contracts** | RouteContract, RETTerminalPacket, GroundingRouteContract, ManagedWorkflowRouteContract, RouteRejected |
| **required_l5_refs** | policy_hash, blueprint_hash, registry_digest_set, l5_governance_context_digest, route_manifest_hash, capability_ceiling, sandbox_requirement, replay_key, audit_manifest_ref |
| **required_contract_gates** | route_selection_gate, route_determinism_gate, cache_reuse_gate, grounding_requirement_gate, cost_latency_budget_gate, hitl_posture_gate |
| **receipts** | route_digest, route_telemetry, route_replay_receipt |
| **otel_spans** | l0.route_preflight, l0.route_selection, l0.route_handoff |
| **artifacts** | route_contract.json, route_telemetry.json |
| **fail_closed_if** | no L1PlanContract, multiple routes emitted, route not replayable, registry digest missing, route widens authority |

**L0 Boundary**: L0 chooses exactly one route. L0 must not retrieve, assemble prompts, execute, call tools/models, write L4, or learn.

### L3 Orchestration

| Aspect | Specification |
|--------|---------------|
| **incoming_contracts** | ManagedWorkflowRouteContract |
| **outgoing_contracts** | L3ToL2StepContract, SealedWorkflowPackage, L3StepBlocked |
| **required_l5_refs** | managed_workflow_route_contract_ref, policy_hash, blueprint_hash, registry_digest_set, l5_governance_context_digest, capability_ceiling, sandbox_ceiling, replay_key, audit_manifest_ref |
| **required_contract_gates** | workflow_trajectory_gate, loop_retry_thrash_gate, branch_join_budget_gate, step_authority_preservation_gate |
| **receipts** | workflow_ledger, checkpoint_ref, branch_join_state, step_handoff_receipt |
| **otel_spans** | l3.workflow_init, l3.step_scheduling, l3.handoff_to_l2 |
| **artifacts** | workflow_package.json, l3_ledger.json |
| **fail_closed_if** | L3 chooses new route, workflow exceeds bounds, step widens authority, step adds unapproved tool/provider/credential, direct L4 write authorized |

**L3 Boundary**: L3 sequences approved managed workflow steps only. L3 must not re-route, retrieve directly, assemble prompts, execute, approve output, write L4, or learn.

---

| REQ_ID | Source_File | Source_Section | Owner_Layer | Owner_Subsystem | Requirement_Type | Requirement_Text | Requirement_Strength | Required_Runtime_Evidence | Required_OTEL_Span | Required_Artifact_Receipt | Required_Validator | Required_Test | Required_Negative_Control | Expected_Fail_Reason | Required_Replay_Check | Release_Gate_Rule | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| REQ-L0-ROUTE-EXACTLY-ONE-001 | 03.2_L0_Deterministic_Route_Selection.md | Deterministic Route Selection | L0 | RouteSelection | contract | L0 MUST select exactly one route per ValidatedRequest. | ONLY | Route selection trace; route_selection_gate verdict | l0.route_selection | route_contract.json | RouteSelectionValidator | test_l0_route_exactly_one.py | Multiple routes selected | RouteSelectionError: multiple routes emitted | Replay with same L1PlanContract; expect identical route | RELEASE_BLOCKING | route_determinism_gate validates single route |
| REQ-L0-ROUTE-INPUT-PREFLIGHT-001 | 03.1_L0_Route_Input_and_Preflight.md | Route Input / Preflight | L0 | RoutePreflight | contract | L0 MUST run preflight validation on the L1PlanContract before route selection. | MUST | Preflight validation trace; route_selection_gate verdict | l0.route_preflight | route_contract.json preflight section | RoutePreflightValidator | test_l0_route_preflight.py | Preflight validation skipped | PreflightBypassError: validation bypassed | Replay with same input; expect identical preflight | RELEASE_BLOCKING | Required L5: policy_hash, blueprint_hash |
| REQ-L0-CACHE-FALLBACK-HITL-001 | 03.3_L0_Cache_Fallback_HITL_Routes.md | Cache / Fallback / HITL Routes | L0 | RouteFallback | contract | L0 MUST honor declared cache, fallback, and HITL route classes. | MUST | Cache/fallback/HITL evaluation trace; cache_reuse_gate verdict | l0.route_selection cache field | route_contract.json route_class section | RouteClassValidator | test_l0_route_classes.py | Route class violated (e.g., cache miss not handled) | RouteClassError: cache/fallback/HITL violation | Replay with same route class; expect identical handling | RELEASE_BLOCKING | cache_reuse_gate governs cache eligibility |
| REQ-L0-GROUNDED-ACTION-HANDOFF-001 | 03.4_L0_Grounded_and_Action_Route_Handoffs.md | Grounded / Action Route Handoffs | L0 | RouteHandoff | contract | L0 MUST hand off grounded and action routes via the canonical RouteContract. | MUST | Handoff contract trace; grounding_requirement_gate verdict | l0.route_handoff | route_contract.json | RouteContractHandoffValidator | test_l0_route_handoff.py | Non-canonical handoff or ad-hoc payload | HandoffViolationError: non-contract payload | Replay handoff; expect identical contract validation | RELEASE_BLOCKING | Required L5: registry_digest_set, route_manifest_hash |
| REQ-L0-ROUTECONTRACT-TELEMETRY-001 | 03.5_L0_RouteContract_Telemetry_Replay.md | RouteContract Telemetry / Replay | L0 | RouteTelemetry | otel | RouteContract MUST emit telemetry sufficient for deterministic replay. | MUST | OTEL span completeness; replay evidence | l0.route_preflight, l0.route_selection, l0.route_handoff | route_telemetry.json | RouteTelemetryValidator | test_l0_route_telemetry.py | Telemetry missing or insufficient for replay | TelemetryGapError: replay evidence incomplete | Replay and compare span sequence; expect identical coverage | RELEASE_BLOCKING | Required L5: replay_key, audit_manifest_ref |
| REQ-L3-MANAGED-WORKFLOW-001 | 03.6_L3_Managed_Workflow_Eligibility_and_DAG.md | Managed Workflow Eligibility / DAG | L3 | ManagedWorkflow | contract | L3 managed-workflow eligibility MUST be evaluated before DAG admission. | MUST | Workflow eligibility trace; workflow_trajectory_gate verdict | l3.workflow_init | workflow_package.json eligibility_section | WorkflowEligibilityValidator | test_l3_workflow_eligibility.py | Ineligible workflow admitted to DAG | WorkflowEligibilityError: eligibility check failed | Replay with same workflow; expect identical eligibility | RELEASE_BLOCKING | Required L5: managed_workflow_route_contract_ref |
| REQ-L3-STEP-READINESS-LEDGER-001 | 03.7_L3_Step_Readiness_State_Ledger_and_Context_Bus.md | Step Readiness / State Ledger / Context Bus | L3 | StepLedger | contract | L3 step readiness MUST be tracked in a state ledger and projected via the context bus. | MUST | Step readiness trace; ledger state evidence | l3.step_scheduling | l3_ledger.json step_readiness section | StepReadinessValidator | test_l3_step_readiness.py | Step readiness not tracked or ledger missing | StepReadinessError: readiness tracking failed | Replay with same steps; expect identical ledger | RELEASE_BLOCKING | step_authority_preservation_gate validates step bounds |
| REQ-L3-CONCURRENCY-FALLBACK-001 | 03.8_L3_Concurrency_Quality_Fallback_Completion_ExitPkg.md | Concurrency / Quality Fallback / ExitPkg | L3 | Concurrency | contract | L3 concurrency, quality fallback, and ExitPkg MUST follow declared completion rules. | MUST | Concurrency/fallback trace; loop_retry_thrash_gate verdict | l3.step_scheduling concurrency field | l3_ledger.json completion_rules | ConcurrencyRulesValidator | test_l3_concurrency_fallback.py | Completion rules violated (e.g., premature exit) | CompletionRulesError: rules violation | Replay with same concurrency profile; expect identical behavior | RELEASE_BLOCKING | branch_join_budget_gate governs concurrency limits |
| REQ-L3-L2-STEP-HANDOFF-001 | 03.9_L3_L2_Step_Handoff_Checkpoint_Resume.md | L3→L2 Step Handoff / Checkpoint / Resume | L3 | StepHandoff | contract | L3→L2 step handoff MUST be checkpointed for deterministic resume. | MUST | Handoff checkpoint trace; checkpoint_ref evidence | l3.handoff_to_l2 | step_handoff_receipt | StepHandoffValidator | test_l3_l2_handoff.py | Handoff not checkpointed or resume fails | HandoffCheckpointError: checkpoint missing | Replay handoff; expect identical checkpoint | RELEASE_BLOCKING | Required L5: capability_ceiling, sandbox_ceiling, replay_key |
| REQ-L0-NO-RETRIEVAL-001 | 03_L0_Route_Decision_Switching_L3.md | L0 Authority Boundaries | L0 | Authority | boundary | L0 MUST NOT perform retrieval; retrieval is C0's authority. | MUST_NOT | L0 stage trace showing no retrieval calls | l0.route_selection (no retrieval span) | route_contract.json (no evidence section) | NoRetrievalValidator | test_l0_no_retrieval.py | L0 calls retrieval or includes evidence | RetrievalViolationError: L0 performed retrieval | Replay; confirm no retrieval spans | RELEASE_BLOCKING | C0 owns FinalEvidenceContract; L0 must not retrieve |
| REQ-L0-NO-EXECUTE-001 | 03_L0_Route_Decision_Switching_L3.md | L0 Authority Boundaries | L0 | Authority | boundary | L0 MUST NOT execute tools or models; execution is L2's authority. | MUST_NOT | L0 stage trace showing no execution calls | l0.route_handoff (no execution span) | route_contract.json (no execution artifacts) | NoExecutionValidator | test_l0_no_execution.py | L0 calls tools, models, or executes | ExecutionViolationError: L0 performed execution | Replay; confirm no execution spans | RELEASE_BLOCKING | L2 owns execution; L0 routing only |
| REQ-L0-OVERVIEW-REFERENCE-001 | 03_L0_Route_Decision_Switching_L3.md | L0/L3 Overview | L0 | Overview | reference | L0/L3 parent file is reference for parent/child traceability. | REFERENCE | Parent traceability link | N/A: parent reference | route_digest | N/A: parent reference | test_l0_l3_parent_linkage.py | NOT_APPLICABLE: parent overview | NOT_APPLICABLE: same reason as negative control (parent overview) | N/A: parent reference | NON_BLOCKING_REFERENCE | Required L5: capability_ceiling, sandbox_requirement |
