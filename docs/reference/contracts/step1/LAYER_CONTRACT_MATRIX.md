# Layer Contract Matrix — Unified Cross-Layer Handoff Reference

**Date**: 2026-05-12  
**Plan**: agentic-core-spine-contract-hardening-a7d4e1  
**Scope**: W5.P2 — Unified contract matrix for all 12 runtime surfaces

---

## Overview

This matrix defines the complete contract handoff surface for the agentic_core runtime. It specifies:
- **12 runtime surfaces**: U0, L1, L0, C0, PA, L3, L2, Exit, UWG, L4, L6, 99 Proof Auditor
- **L5**: Cross-cutting certification and governance refs (not a sequential runtime surface)
- **Contract chains**: Full end-to-end and route-specific variants

---

## L5 — Cross-Cutting Certification and Governance

L5 is **not** a sequential runtime surface. It provides certification refs, governance context, and trust anchors used across all layers.

| L5 Ref | Usage Context |
|--------|---------------|
| l5_certification_refs | All contract validations |
| l5_certification_result_ref | 99 Proof Auditor acceptance |
| l5_governance_context_digest | All layer handoffs |
| policy_hash | U0, L1, L0, L3, L2, Exit, UWG, L4 |
| blueprint_hash | U0, L1, L0, C0, PA, L3, L2, Exit, UWG, L4 |
| registry_digest_set | U0, L1, L0, C0, PA, L2, Exit, UWG, L4 |
| origin_trust_manifest_ref | C0, PA, 99 Proof Auditor |
| capability_token_ref | L2, Exit, UWG |
| sandbox_envelope_ref | L2, Exit, UWG |
| egress_certification_receipt_refs | L2, Exit, 99 Proof Auditor |
| hitl_reclearance_receipt_refs | Exit, 99 Proof Auditor |
| replay_key | L2, L4, L6, UWG, 99 Proof Auditor |
| replay_envelope_ref | 99 Proof Auditor |
| replay_manifest | Exit, UWG, L4, L6 |
| replay_proof_ref | L6 |
| regression_proof_ref | L6 |
| safety_proof_ref | L6 |
| calibration_proof_ref | L6 |
| observer_law_receipt | L6 |
| eval_record_seal | L6 |
| gauntlet_receipt | L6 |
| audit_manifest_ref | All surfaces |
| rollback_plan_ref | UWG |
| exit_disposition_receipt_ref | UWG (with X3C) |
| proposed_state_diff_ref | UWG |
| runtime_exhaust_bundle_ref | L6 |

---

## Runtime Surface Definitions

### 1. U0 — Intake and Normalization

| Aspect | Specification |
|--------|---------------|
| **purpose** | Receive external request; normalize into IntakeContract; validate schema and identity; emit bounded authority context |
| **incoming_contracts** | ExternalRequest, IdentityContext |
| **outgoing_contracts** | IntakeContract, RequestEnrichment |
| **required_l5_refs** | l5_certification_refs, policy_hash, blueprint_hash, registry_digest_set, audit_manifest_ref, l5_governance_context_digest |
| **required_contract_gates** | identity_schema_gate, tenant_boundary_gate, request_sanitization_gate, ingestion_rate_gate, protocol_translation_gate, version_negotiation_gate |
| **required_receipts** | intake_receipt, enrichment_receipt, authority_context_receipt |
| **required_otel_spans** | u0.intake_receive, u0.identity_normalize, u0.schema_validate, u0.request_sanitize, u0.authority_emit |
| **fail_closed_if** | identity validation fails, schema violation, tenant boundary crossed, request malformed, protocol unsupported, version incompatible |
| **must_not boundary** | Must not route, plan, retrieve, assemble prompts, execute, emit X3, write L4, or learn |
| **next authorized consumer** | L1 |

---

### 2. L1 — Plan and Decompose

| Aspect | Specification |
|--------|---------------|
| **purpose** | Consume IntakeContract; produce canonical PlanContract; decompose into step contracts; emit L0/L3 routing directives |
| **incoming_contracts** | IntakeContract, RequestEnrichment |
| **outgoing_contracts** | PlanContract, L0RoutingDirective, L3RoutingDirective, StepContracts |
| **required_l5_refs** | l5_certification_refs, policy_hash, blueprint_hash, registry_digest_set, capability_token, sandbox_requirement, audit_manifest_ref, l5_governance_context_digest |
| **required_contract_gates** | decomposition_validity_gate, step_contract_bound_gate, capability_demand_gate, retry_budget_gate, schema_binding_gate, escalation_policy_gate |
| **required_receipts** | plan_digest_receipt, step_decomposition_receipt, capability_ceiling_receipt, retry_budget_receipt |
| **required_otel_spans** | l1.plan_compose, l1.step_decompose, l1.routing_directive_emit |
| **fail_closed_if** | decomposition invalid, step contracts unbound, capability demand exceeds ceiling, schema binding fails, escalation policy missing |
| **must_not boundary** | Must not route, retrieve, assemble prompts, execute, emit X3, write L4, or learn |
| **next authorized consumer** | L0 (route selection) or L3 (managed workflow) |

---

### 3. L0 — Route Decision

| Aspect | Specification |
|--------|---------------|
| **purpose** | Choose exactly one route from L1 PlanContract; validate route against registry; emit RouteContract with authority bindings |
| **incoming_contracts** | L0RoutingDirective, PlanContract, StepContracts |
| **outgoing_contracts** | RouteContract, RETTerminalPacket (when applicable), GroundingRouteContract (when C0 required), ManagedWorkflowRouteContract (when L3 required), RouteRejected |
| **required_l5_refs** | l5_certification_refs, policy_hash, blueprint_hash, registry_digest_set, l5_governance_context_digest, capability_ceiling, sandbox_requirement, replay_key, audit_manifest_ref |
| **required_contract_gates** | route_selection_gate, route_determinism_gate, cache_reuse_gate, grounding_requirement_gate, cost_latency_budget_gate, hitl_posture_gate |
| **required_receipts** | route_digest_receipt, route_telemetry_receipt, route_replay_receipt |
| **required_otel_spans** | l0.route_preflight, l0.route_selection, l0.route_handoff |
| **fail_closed_if** | no L1 PlanContract, multiple routes emitted, route not replayable, registry digest missing, route widens authority |
| **must_not boundary** | Must not retrieve, assemble prompts, execute, call tools/models, write L4, or learn |
| **next authorized consumer** | C0 (if grounding_required), PA (if prompt_assembly), L3 (if managed_workflow), Exit (if RET) |

---

### 4. C0 — Context Engine (Retrieval)

| Aspect | Specification |
|--------|---------------|
| **purpose** | Retrieve, hydrate, score, stratify, verify evidence per RouteContract grounding requirements |
| **incoming_contracts** | RouteContract with grounding_required = true |
| **outgoing_contracts** | FinalEvidenceContract, EvidenceBlockedContract |
| **required_l5_refs** | origin_trust_manifest_ref, source_lineage_map, acl_verification_receipts, freshness_receipts, contradiction_report, l5_governance_context_digest, audit_manifest_ref |
| **required_contract_gates** | retrieval_legality_gate, evidence_quality_gate, acl_freshness_lineage_gate, contradiction_support_gate, retrieved_content_trust_gate, privacy_cross_context_gate |
| **required_receipts** | evidence_receipt, citation_map, contradiction_report, support_status |
| **required_otel_spans** | c0.preflight_grounding, c0.retrieval_plan, c0.evidence_fetch, c0.graph_rag, c0.shape_rerank, c0.weak_support_check, c0.final_evidence_seal |
| **fail_closed_if** | evidence required but unavailable, blocked source included, retrieved text becomes instruction, ACL/freshness/source lineage missing, support_status UNKNOWN treated as PASS |
| **must_not boundary** | Must not answer, route, assemble prompts, execute, write L4, or inflate support |
| **next authorized consumer** | PA |

---

### 5. PA — Prompt Assembly

| Aspect | Specification |
|--------|---------------|
| **purpose** | Compose, render, hash, sign, and package prompt per validated contracts |
| **incoming_contracts** | L1 PlanContract, RouteContract, FinalEvidenceContract (when grounding_required = true), L5 refs, schema refs |
| **outgoing_contracts** | PromptEnvelope / CompiledPromptArtifact, PromptAssemblyRejected |
| **required_l5_refs** | policy_hash, blueprint_hash, registry_digest_set, origin_trust_manifest_ref, l5_governance_context_digest, provider lane certification refs, egress certification refs (when applicable), replay_manifest, audit_manifest_ref |
| **required_contract_gates** | prompt_boundary_gate, instruction_data_boundary_gate, slot_authority_order_gate, schema_binding_gate, provider_rendering_gate, deterministic_trim_gate |
| **required_receipts** | prompt_envelope, compiled_prompt_artifact, slot_validity_receipt, provider_manifest_ref |
| **required_otel_spans** | pa.bom_load, pa.slot_composition, pa.airlock_security, pa.slot_validation, pa.token_budget, pa.provider_rendering, pa.final_emit |
| **fail_closed_if** | PA retrieves non-C0 evidence, user text becomes instruction, slot order violates authority, airlock allows unauthorized slot, provider/egress binding missing, provider variance non-deterministic, instruction/data boundary violated |
| **must_not boundary** | Must not retrieve, route, execute, approve L2 execution, write L4, or learn |
| **next authorized consumer** | L2 |

---

### 6. L3 — Orchestration (Managed Workflow)

| Aspect | Specification |
|--------|---------------|
| **purpose** | Sequence approved managed workflow steps; coordinate L2 executions; preserve authority invariants |
| **incoming_contracts** | ManagedWorkflowRouteContract |
| **outgoing_contracts** | L3ToL2StepContract, SealedWorkflowPackage, L3StepBlocked |
| **required_l5_refs** | managed_workflow_route_contract_ref, policy_hash, blueprint_hash, registry_digest_set, l5_governance_context_digest, capability_ceiling, sandbox_ceiling, replay_key, audit_manifest_ref |
| **required_contract_gates** | workflow_trajectory_gate, loop_retry_thrash_gate, branch_join_budget_gate, step_authority_preservation_gate |
| **required_receipts** | workflow_ledger, checkpoint_ref, branch_join_state, step_handoff_receipt |
| **required_otel_spans** | l3.workflow_init, l3.step_scheduling, l3.handoff_to_l2 |
| **fail_closed_if** | L3 chooses new route, workflow exceeds bounds, step widens authority, step adds unapproved tool/provider/credential, direct L4 write authorized |
| **must_not boundary** | Must not re-route, retrieve directly, assemble prompts, execute, approve output, write L4, or learn |
| **next authorized consumer** | L2 |

---

### 7. L2 — Execute

| Aspect | Specification |
|--------|---------------|
| **purpose** | Execute bounded work order through E1-E5 sequencer; emit sealed result or repair under same authority |
| **incoming_contracts** | RouteContract, L3ToL2StepContract, PromptEnvelope / CompiledPromptArtifact (when model execution required), L2ExecutionPacket |
| **outgoing_contracts** | FrozenExecutionContext, ExecutionValidationReceipt, AttemptReceipt, HealReceipt (when repair occurs), SealedL2Artifact |
| **required_l5_refs** | capability_token, sandbox_envelope, policy_hash, blueprint_hash, registry_digest_set, provider/model/tool certification refs, egress certification refs (when provider/tool/network used), replay_key, audit_manifest_ref, l5_governance_context_digest |
| **required_contract_gates** | tool_model_registry_gate, tool_argument_gate, external_egress_gate, sandbox_filesystem_shell_gate, memory_access_gate, privacy_cross_context_gate, output_schema_gate, replay_determinism_gate, audit_trace_completeness_gate |
| **required_receipts** | prep_receipt, validation_receipt, attempt_receipt, optional_ptc_receipt, heal_receipt, seal_receipt |
| **required_otel_spans** | l2.e1_prep, l2.e2_validate, l2.e3_execute, l2.e4_heal, l2.e5_seal, l2.handoff_to_exit |
| **fail_closed_if** | authority missing/expired, capability scope exceeded, sandbox escape, policy/registry mismatch, egress without certification, schema violation, replay non-deterministic, audit trace incomplete, direct L4 write attempted |
| **must_not boundary** | Must not choose route, expand workflow, retrieve opportunistically, ask humans directly, approve egress, commit L4, or learn |
| **next authorized consumer** | Exit |

---

### 8. Exit — Evaluation and Control

| Aspect | Specification |
|--------|---------------|
| **purpose** | Consume sealed result; run X1 checks; aggregate X2; emit exactly one X3; hand off to UWG when X3C; emit runtime exhaust |
| **incoming_contracts** | RETTerminalPacket, SealedL2Artifact, SealedWorkflowPackage, ReClearedHITLPacket |
| **outgoing_contracts** | ExitReviewPacket, X1CheckoutResult, X2AggregationResult, ExitDispositionReceipt, CommitRequest (when X3C), RuntimeExhaustBundle |
| **required_l5_refs** | l5_certification_refs, policy_hash, blueprint_hash, registry_digest_set, sandbox_envelope_ref (when execution used sandbox), capability_token_ref (when execution used capability), provider_receipts (when provider used), evidence refs (when grounded), replay_manifest, audit_manifest_ref, hitl_reclearance_refs (when HITL occurred) |
| **required_contract_gates** | exit_input_completeness_gate, output_quality_gate, security_leakage_gate, replay_readiness_gate, exit_disposition_gate, durable_write_candidate_gate, audit_trace_completeness_gate |
| **required_receipts** | exit_review_packet, x1_checkout_result, x2_aggregation_result, x3_disposition_receipt, runtime_exhaust_bundle |
| **required_otel_spans** | exit.input_normalize, exit.x1_checkout, exit.x2_aggregate, exit.x3_disposition, exit.handoff_to_uwg, exit.runtime_exhaust_emit |
| **fail_closed_if** | X3 not emitted, multiple X3s emitted, L4 mutated directly, input incomplete, quality check fails, security leakage detected, replay evidence missing, audit trace incomplete |
| **must_not boundary** | Must not execute, retrieve, assemble prompts, mutate L4, or let L6 rescue the current run |
| **next authorized consumer** | UWG (when X3C), L6 (via RuntimeExhaustBundle) |

---

### 9. UWG — Universal Write Gateway

| Aspect | Specification |
|--------|---------------|
| **purpose** | Sole durable write admission path; validate CommitRequest; atomically commit to L4; emit receipts |
| **incoming_contracts** | CommitRequest, StateDiffValidationResult |
| **outgoing_contracts** | StateCommitReceipt, BlockedWriteReceipt |
| **required_l5_refs** | exit_disposition_receipt_ref (with X3C), proposed_state_diff_ref, authority_scope, capability_token_ref, sandbox_envelope_ref, policy_hash, blueprint_hash, registry_digest_set, replay_key, rollback_plan_ref, audit_manifest_ref, l5_governance_context_digest |
| **required_contract_gates** | durable_write_sovereignty_gate, state_diff_validation_gate, authority_scope_gate, lock_conflict_rollback_gate, audit_append_gate, direct_write_bypass_gate |
| **required_receipts** | state_diff_validation_result, state_commit_receipt, blocked_write_receipt, audit_append_receipt |
| **required_otel_spans** | uwg.commit_request_validate, uwg.state_diff_validate, uwg.write_lock, uwg.atomic_commit, uwg.block_commit, uwg.audit_append |
| **fail_closed_if** | CommitRequest not tied to Exit X3C, direct L2/L3/Exit/L6/tool write attempted, UWG receipt missing, audit trace incomplete, rollback plan invalid |
| **must_not boundary** | Must not route, retrieve, execute tools, approve final answer, or learn |
| **next authorized consumer** | L4 |

---

### 10. L4 — State Archive

| Aspect | Specification |
|--------|---------------|
| **purpose** | Store durable state only after UWG receipt; maintain versioned read surface; produce audit ledger |
| **incoming_contracts** | StateCommitReceipt, BlockedWriteReceipt, read_surface_refresh_receipt, audit_append_receipt |
| **outgoing_contracts** | durable_state_ref, versioned_read_surface_ref, replay/audit/state refs for future reads |
| **required_l5_refs** | policy_hash, blueprint_hash, registry_digest_set, replay_key, audit_manifest_ref, l5_governance_context_digest |
| **required_contract_gates** | audit_append_gate, direct_write_bypass_gate |
| **required_receipts** | durable_state_ref, versioned_read_surface_ref, audit_append_receipt, read_surface_refresh_receipt |
| **required_otel_spans** | l4.store_durable_state, l4.refresh_read_surface |
| **fail_closed_if** | CommitRequest not tied to Exit X3C, direct L2/L3/Exit/L6/tool write attempted, UWG receipt missing, audit trace incomplete |
| **must_not boundary** | Must not route, retrieve, execute, approve, write directly from non-UWG paths, or learn |
| **next authorized consumer** | Future runs (read-only) |

---

### 11. L6 — Shadow Evaluation / System Learning

| Aspect | Specification |
|--------|---------------|
| **purpose** | Evaluate completed runs only; produce sealed eval records; draft future-run proposals; publish via UWG |
| **incoming_contracts** | RuntimeExhaustBundle |
| **outgoing_contracts** | CompletedEvalRecord, RCAPacket, ProposalPacket, FutureRunPromotionRequest |
| **required_l5_refs** | runtime_exhaust_bundle_ref, l5_certification_refs, observer_law_receipt, replay_proof_ref, regression_proof_ref, safety_proof_ref, calibration_proof_ref (when evaluator/judge changes), gauntlet_receipt, audit_manifest_ref |
| **required_contract_gates** | learning_firewall_gate, completed_run_boundary_gate, evaluator_calibration_gate, future_run_promotion_gate, no_current_run_mutation_gate |
| **required_receipts** | observer_law_receipt, eval_record_seal, gauntlet_receipt, future_run_activation_receipt |
| **required_otel_spans** | l6.exhaust_ingest, l6.observer_law_check, l6.completed_eval_record, l6.rca_packet, l6.proposal_packet, l6.gauntlet, l6.future_run_promotion_request |
| **fail_closed_if** | current-run mutation attempted, direct L4 write attempted, current-run rescue attempted, evaluator calibration missing, future-run promotion without gauntlet, proposal admission failed |
| **must_not boundary** | Must not mutate current run, emit X3, write L4 directly, rescue current run, or silently patch prompts/policy/memory/cache/registry |
| **next authorized consumer** | UWG (for future-run promotion) |

---

### 12. 99 Proof Auditor

| Aspect | Specification |
|--------|---------------|
| **purpose** | Prove the chain ran; validate contracts, L5 refs, gate refs, OTEL refs, replay refs, no-bypass assertions |
| **incoming_contracts** | Full contract chain (U0→L1→L0→C0→PA→L3→L2→Exit), L5CertificationPacket, ContractGateVerdicts, OTEL spans, ExitDispositionReceipt, UWG receipts (when commit path used) |
| **outgoing_contracts** | RuntimeProofBundle |
| **required_l5_refs** | l5_certification_result_ref, l5_governance_context_digest, policy_hash, blueprint_hash, registry_digest_set, origin_trust_manifest_ref, capability_token_ref, sandbox_envelope_ref, egress_certification_receipt_refs, hitl_reclearance_receipt_refs, replay_envelope_ref, audit_manifest_ref |
| **required_contract_gates** | contract_chain_completeness_gate, gate_coverage_gate, otel_trace_completeness_gate, replay_reconstructability_gate, negative_control_gate, no_bypass_assertion_gate |
| **required_receipts** | runtime_proof_bundle, no_bypass_assertions, negative_control_results, reconstruction_report, replay_report |
| **required_otel_spans** | proof.contract_chain_validate, proof.l5_refs_validate, proof.contract_gate_coverage_validate, proof.otel_trace_validate, proof.replay_reconstruct, proof.no_bypass_assert, proof.runtime_bundle_emit |
| **fail_closed_if** | contract chain incomplete, L5 refs missing, contract gate evidence missing, OTEL traces incomplete, replay non-reconstructable, no-bypass assertion failed, UNKNOWN treated as PASS, NOT_APPLICABLE without reason |
| **must_not boundary** | Must not route, retrieve, assemble prompts, execute, emit X3, admit writes, write L4, or learn into current run |
| **next authorized consumer** | N/A (terminal proof surface) |

---

## Contract Chains

### Full End-to-End Contract Chain

```
U0(IntakeContract)
  → L1(PlanContract, L0RoutingDirective/L3RoutingDirective)
    → L0(RouteContract)
      → C0(FinalEvidenceContract) [if grounding_required]
        → PA(PromptEnvelope/CompiledPromptArtifact)
          → L2(SealedL2Artifact)
            → Exit(X3, RuntimeExhaustBundle)
              → UWG(StateCommitReceipt) [if X3C]
                → L4(durable_state_ref)
              → L6(RuntimeExhaustBundle)
                → UWG(FutureRunPromotionRequest) [optional]
                  → L4(future-run state)
99(RuntimeProofBundle) ← validates entire chain
```

### Route-Specific Contract Chains

#### R1A — Exact Cache Hit
```
U0 → L1 → L0(exact_cache_route) → Exit(RETTerminalPacket) → L6 → 99
```

#### R1B — Semantic Cache Hit
```
U0 → L1 → L0(semantic_cache_route) → Exit(RETTerminalPacket) → L6 → 99
```

#### R5 — Fallback (No Grounding)
```
U0 → L1 → L0(fallback_route) → PA → L2 → Exit → UWG → L4, L6 → 99
```

#### R3 — Simple Grounded Read
```
U0 → L1 → L0(grounded_read_route) → C0 → PA → L2 → Exit → UWG → L4, L6 → 99
```

#### R4 — Single Action
```
U0 → L1 → L0(action_route) → PA → L2(action_lane) → Exit → UWG → L4, L6 → 99
```

#### R3R4 — Managed Workflow (L3 Orchestrated)
```
U0 → L1 → L0(managed_workflow_route) → L3(SealedWorkflowPackage)
  → [C0 → PA → L2]* (multiple steps)
    → Exit → UWG → L4, L6 → 99
```

#### HITL Path
```
U0 → L1 → L0 → [C0 → PA →] L2 → Exit(hitl_escalation) → HITL
  → ReClearedHITLPacket → Exit → UWG → L4, L6 → 99
```

#### L6 Future-Run Promotion Path
```
... → Exit → L6(ProposalPacket) → Gauntlet → UWG(FutureRunPromotionRequest) → L4
```

---

## No-Overlap Law Enforcement

Each surface has explicit **must_not** boundaries. Cross-layer overlap is prohibited:

| Prohibited Overlap | Enforced By |
|--------------------|-------------|
| U0 routing | L0 owns routing |
| C0 answering | Exit owns X3 |
| PA retrieving | C0 owns retrieval |
| L2 choosing route | L0 owns routing |
| L3 re-routing | L0 owns routing |
| Exit executing | L2 owns execution |
| UWG executing/routing | L2/L0 owns execution/routing |
| L4 direct writes | UWG owns all durable writes |
| L6 current-run mutation | Current-run boundary at Exit |
| 99 runtime modification | 99 is read-only proof surface |

---

## Verification

| Criterion | Status |
|-----------|--------|
| 12 runtime surfaces defined | ✅ |
| L5 as cross-cutting refs | ✅ |
| Full contract chain diagram | ✅ |
| Route-specific contract chains | ✅ |
| No-overlap law explicit | ✅ |
| Zero 00C/G01-G29 references | ✅ |
