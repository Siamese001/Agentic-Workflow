# 04 L2 Execute — REQ Matrix (Step 1 Aggregation)

Step 1 aggregation only. Implementation mapping and proof are Phase 2.

Hardened: 2026-05-12 (W3) — All 102 TBD placeholders replaced with concrete contract requirements including E1-E5 sub-sections.

---

## Layer Contract Summary

| Aspect | Specification |
|--------|---------------|
| **incoming_contracts** | RouteContract, L3ToL2StepContract, PromptEnvelope / CompiledPromptArtifact (when model execution required), L2ExecutionPacket |
| **outgoing_contracts** | FrozenExecutionContext, ExecutionValidationReceipt, AttemptReceipt, HealReceipt (when repair occurs), SealedL2Artifact |
| **required_l5_refs** | capability_token, sandbox_envelope, policy_hash, blueprint_hash, registry_digest_set, provider/model/tool certification refs, egress certification refs (when provider/tool/network used), replay_key, audit_manifest_ref, l5_governance_context_digest |
| **required_contract_gates** | tool_model_registry_gate, tool_argument_gate, external_egress_gate, sandbox_filesystem_shell_gate, memory_access_gate, privacy_cross_context_gate, output_schema_gate, replay_determinism_gate, audit_trace_completeness_gate |
| **receipts** | prep_receipt, validation_receipt, attempt_receipt, optional_ptc_receipt, heal_receipt, seal_receipt |
| **otel_spans** | l2.e1_prep, l2.e2_validate, l2.e3_execute, l2.e4_heal, l2.e5_seal, l2.handoff_to_exit |
| **artifacts** | frozen_execution_context.json, execution_validation_receipt.json, attempt_receipt.json, heal_receipt.json (when applicable), sealed_l2_artifact.json, l2_observability.json |
| **fail_closed_if** | authority missing/expired, capability scope exceeded, sandbox escape, policy/registry mismatch, egress without certification, schema violation, replay non-deterministic, audit trace incomplete, direct L4 write attempted |

**L2 Boundary**: L2 receives authority and cannot create authority. L2 may execute exactly the bounded work order. L2 may emit proposed_state_diff only. L2 must not choose route, expand workflow, retrieve opportunistically, ask humans directly, approve egress, commit L4, or learn.

---

## E1-E5 Sub-Sections

### E1 Prep — Frozen Execution Room

| Element | Requirement |
|---------|-------------|
| **Freezes** | route, step, capability_token, sandbox_envelope, policy_hash, blueprint_hash, registry_digest_set, provider/model/tool lanes, filesystem/network/credential scope, replay_key, attempt_seed, budget, idempotency |
| **Emits** | FrozenExecutionContext, prep_receipt |
| **OTEL Span** | l2.e1_prep |
| **Gate** | tool_model_registry_gate (registry_digest_set verification) |

### E2 Valid — Work Order Validation

| Element | Requirement |
|---------|-------------|
| **Validates** | signature chain, capability scope, sandbox scope, schema, side-effect class, budget, safety, route match, ACL, provider/tool/model/connector registry status |
| **Emits** | ExecutionValidationReceipt |
| **Blocking** | anything other than PASS_EXECUTE blocks E3 |
| **OTEL Span** | l2.e2_validate |
| **Gates** | tool_argument_gate, external_egress_gate, sandbox_filesystem_shell_gate, memory_access_gate, privacy_cross_context_gate |
| **Required L5** | capability_token, sandbox_envelope, policy_hash, egress certification refs (when applicable) |

### E3 Exec — Execution Attempt Lanes

| Element | Requirement |
|---------|-------------|
| **Executes** | one approved lane only: READ_ANALYSIS, MODEL, TOOL, ACTION, ARTIFACT, OPTIONAL_PTC_SANDBOX |
| **Captures** | AttemptReceipt, telemetry, output payload, raw result, errors, proposed_state_diff (if produced) |
| **PTC** | remains inside E3 only; uses same capability, sandbox, policy, blueprint, replay, budget |
| **OTEL Span** | l2.e3_execute |
| **Gates** | output_schema_gate, replay_determinism_gate |

### E4 Heal — Same-Authority Repair

| Element | Requirement |
|---------|-------------|
| **Same-authority only** | repairs occur under bounded authority; no authority expansion |
| **Allowed repairs** | schema repair, output reformat, transient retry, checkpoint resume, deterministic trim |
| **Disallowed repairs** | missing authority, blocked ACL, policy conflict, route mismatch, stale policy/registry, sandbox gap, HITL need, provider/tool substitution, direct write bypass |
| **Emits** | HealReceipt |
| **OTEL Span** | l2.e4_heal |
| **Required L5** | replay_key, audit_manifest_ref |

### E5 Seal — Artifact Sealing

| Element | Requirement |
|---------|-------------|
| **Emits** | SealedL2Artifact |
| **Packages** | payload, evidence refs, prompt refs, provider/tool/model receipts, telemetry refs, OTEL span refs, counters, errors, replay manifest, audit refs, terminal_class, decisive_reason |
| **Invariants** | proposed_state_diff remains inert; durable_commit_occurred must be false |
| **OTEL Span** | l2.e5_seal, l2.handoff_to_exit |
| **Gate** | audit_trace_completeness_gate |
| **Required L5** | l5_governance_context_digest, audit_manifest_ref, provider/model/tool certification refs |

---

| REQ_ID | Source_File | Source_Section | Owner_Layer | Owner_Subsystem | Requirement_Type | Requirement_Text | Requirement_Strength | Required_Runtime_Evidence | Required_OTEL_Span | Required_Artifact_Receipt | Required_Validator | Required_Test | Required_Negative_Control | Expected_Fail_Reason | Required_Replay_Check | Release_Gate_Rule | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| REQ-L2-EXECUTE-BOUNDED-PACKET-001 | 04.1_L2_Execution_Entry_Authority_and_Packet_Intake.md | Execution Entry / Packet Intake | L2 | PacketIntake | contract | L2 MUST execute only from a bounded execution packet handed off from L0/L3. | ONLY | Packet intake trace; L2ExecutionPacket validation | l2.e1_prep (packet_intake field) | frozen_execution_context.json packet_section | PacketIntakeValidator | test_l2_bounded_packet.py | Execution from unbounded or ad-hoc source | UnboundedExecutionError: packet validation failed | Replay with same L3ToL2StepContract; expect identical intake | RELEASE_BLOCKING | Required L5: capability_token, sandbox_envelope, replay_key |
| REQ-L2-WRITE-NO-DIRECT-L4-001 | 04.9_L2_StateDiffCandidate_and_Mutation_Intent.md | StateDiffCandidate / Mutation Intent | L2 | WriteSovereignty | write_sovereignty | L2 MUST NOT write directly to L4; L2 emits StateDiffCandidate and routes through UWG via Exit. | MUST_NOT | L2 stage trace showing no direct L4 writes | l2.e5_seal (no direct_write span) | sealed_l2_artifact.json (durable_commit_occurred=false) | NoDirectL4WriteValidator | test_l2_no_direct_l4.py | L2 performs direct L4 write | DirectL4WriteError: unauthorized write attempted | Replay; confirm durable_commit_occurred=false | RELEASE_BLOCKING | UWG owns all L4 writes; proposed_state_diff is inert |
| REQ-L2-SEQUENCER-CONTRACT-001 | 04.0_L2_Sequencer_Orchestrator_Contract.md | Sequencer / Orchestrator Contract | L2 | Sequencer | contract | L2 sequencer/orchestrator contract MUST be honored across E1–E5. | MUST | Sequencer contract trace; E1-E5 progression evidence | l2.e1_prep → l2.e2_validate → l2.e3_execute → l2.e4_heal → l2.e5_seal | l2_observability.json sequencer_section | SequencerContractValidator | test_l2_sequencer_contract.py | E1-E5 sequence violated | SequencerViolationError: sequence breach | Replay; expect identical E1-E5 progression | RELEASE_BLOCKING | Required L5: policy_hash, blueprint_hash, registry_digest_set |
| REQ-L2-E1-FROZEN-ROOM-001 | 04.2_L2_E1_Prep_Frozen_Execution_Room.md | E1 Prep Frozen Execution Room | L2 | FrozenRoom | contract | L2 E1 MUST freeze the execution room before E2 admission. | MUST | E1 freeze trace; frozen context evidence | l2.e1_prep | frozen_execution_context.json | FrozenRoomValidator | test_l2_e1_frozen_room.py | Execution room not frozen | FrozenRoomError: freeze incomplete | Replay with same inputs; expect identical frozen context | RELEASE_BLOCKING | Freezes: route, step, capability, sandbox, policy, blueprint, registry, lanes, scope, replay_key, seed, budget, idempotency |
| REQ-L2-E2-VALID-WORK-ORDER-001 | 04.3_L2_E2_Valid_Work_Order_and_Gate_Check.md | E2 Valid Work Order / Gate Check | L2 | WorkOrder | contract | L2 E2 MUST validate the work order and pass declared gate checks before E3. | MUST | E2 validation trace; gate check verdicts | l2.e2_validate | execution_validation_receipt.json | WorkOrderValidator | test_l2_e2_work_order.py | Work order validation fails | WorkOrderValidationError: validation failed | Replay; expect identical validation | RELEASE_BLOCKING | PASS_EXECUTE required for E3; Required L5: capability_token, sandbox_envelope, egress certification refs |
| REQ-L2-E3-EXEC-LANES-SANDBOX-001 | 04.4_L2_E3_Exec_Attempt_Lanes_and_Sandbox_Run.md | E3 Exec Attempt Lanes / Sandbox | L2 | ExecLanes | contract | L2 E3 attempt lanes MUST run inside the declared sandbox. | MUST | E3 execution trace; sandbox boundary evidence | l2.e3_execute | attempt_receipt.json | ExecLanesValidator | test_l2_e3_exec_lanes.py | Sandbox escape or unauthorized lane | SandboxEscapeError: execution outside bounds | Replay; expect identical sandbox confinement | RELEASE_BLOCKING | Lanes: READ_ANALYSIS, MODEL, TOOL, ACTION, ARTIFACT, OPTIONAL_PTC_SANDBOX |
| REQ-L2-E4-HEAL-SAME-AUTHORITY-001 | 04.5_L2_E4_Heal_Same_Authority_Repair_Governor.md | E4 Heal / Same-Authority Repair Governor | L2 | HealGovernor | contract | L2 E4 healing MUST occur under the same-authority repair governor. | MUST | E4 heal trace; authority preservation evidence | l2.e4_heal | heal_receipt.json | HealGovernorValidator | test_l2_e4_heal_governor.py | Authority expanded during heal | HealAuthorityError: authority violation | Replay with same repair; expect identical authority | RELEASE_BLOCKING | Allowed: schema repair, output reformat, transient retry, checkpoint resume, deterministic trim |
| REQ-L2-E5-SEAL-DISPATCH-001 | 04.6_L2_E5_Seal_Artifact_and_Dispatch.md | E5 Seal Artifact / Dispatch | L2 | SealDispatch | artifact | L2 E5 MUST seal the artifact and dispatch via the declared exit handoff. | MUST | E5 seal trace; artifact completeness evidence | l2.e5_seal, l2.handoff_to_exit | sealed_l2_artifact.json | SealDispatchValidator | test_l2_e5_seal_dispatch.py | Artifact incomplete or dispatch fails | SealError: artifact sealing failed | Replay; expect identical sealed artifact | RELEASE_BLOCKING | Packages: payload, evidence refs, prompt refs, receipts, telemetry, counters, errors, replay manifest, audit refs, terminal_class, decisive_reason |
| REQ-L2-PTC-SANDBOX-001 | 04.7_L2_Programmatic_Tool_Calling_PTC_Sandbox.md | PTC Sandbox | L2 | PTCSandbox | contract | Programmatic tool calling MUST occur inside the PTC sandbox. | MUST | PTC trace; sandbox boundary evidence | l2.e3_execute (ptc_subspan) | optional_ptc_receipt | PTCSandboxValidator | test_l2_ptc_sandbox.py | PTC outside sandbox | PTCSandboxError: sandbox violation | Replay with same PTC; expect identical sandbox confinement | RELEASE_BLOCKING | PTC uses same capability, sandbox, policy, blueprint, replay, budget |
| REQ-L2-OBS-ANTI-BYPASS-001 | 04.8_L2_Observability_Replay_Anti_Bypass_Tests.md | Observability / Replay / Anti-Bypass | L2 | AntiBypass | negative_control | Any L2 path that bypasses the sequencer or sandbox MUST be detected. | MUST_NOT | Anti-bypass detection trace; bypass assertions | l2.e1_prep (anti_bypass_check) | l2_observability.json bypass_checks | AntiBypassValidator | test_l2_anti_bypass.py | Sequencer/sandbox bypass not detected | BypassDetectedError: bypass undetected | Replay with bypass attempt; expect detection | RELEASE_BLOCKING | Required L5: audit_manifest_ref, l5_governance_context_digest |
| REQ-L2-VERIFY-THEN-EXECUTE-001 | 04.10_L2_Verify_Then_Execute_Local_Critique.md | Verify-Then-Execute / Local Critique | L2 | VerifyExecute | validator | L2 verify-then-execute local critique MUST run before binding the execution attempt. | MUST | Verify-then-execute trace; critique evidence | l2.e2_validate (verify_then_execute field) | execution_validation_receipt.json critique_section | VerifyThenExecuteValidator | test_l2_verify_then_execute.py | Critique skipped or fails | CritiqueError: verify-then-execute failed | Replay; expect identical critique | RELEASE_BLOCKING | Runs before E3 binding; Required L5: provider/model/tool certification refs |
| REQ-L2-RESOLUTION-CONTEXT-INVARIANT-001 | 04.5a_L2_Resolution_Context_Invariant.md | Resolution Context Invariant | L2 | ResolutionContext | contract | L2 resolution context invariant MUST hold across heal attempts. | MUST | Resolution context trace; invariant preservation | l2.e4_heal (resolution_context field) | heal_receipt.json resolution_section | ResolutionContextValidator | test_l2_resolution_invariant.py | Resolution context violated | ResolutionContextError: invariant breach | Replay with same heal sequence; expect identical context | RELEASE_BLOCKING | Required L5: replay_key |
| REQ-L2-COVERAGE-MATRIX-REF-001 | COVERAGE_MATRIX.md | L2 Coverage Matrix | L2 | Traceability | traceability | L2 coverage matrix is the reference parent/child surface (no claims carried into Step 1). | REFERENCE | Parent traceability link | N/A: reference matrix | prep_receipt | N/A: reference matrix | test_l2_coverage_linkage.py | NOT_APPLICABLE: reference matrix | NOT_APPLICABLE: same reason as negative control (reference matrix) | N/A: reference matrix | NON_BLOCKING_REFERENCE | Required L5: audit_manifest_ref |
