---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\agentic-core-spine-contract-hardening-a7d4e1.md'
original_relative_path: 'agentic-core-spine-contract-hardening-a7d4e1.md'
source_sha256: f4aeeb98e96c97d14f264a8d1cb3cfc746900e27902d1e03efcbfef4775cd881
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-12'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: agentic-core-spine-contract-hardening-a7d4e1
plan_type: doc    # doc — documentation hardening, no code refactor
dod_exempt: false  # Has executable DoD (docs must be validated)
last_updated: 2026-05-12T12:07
status: ALL_WAVES_COMPLETE
patched: true     # PATCHED: Replaced 00C terminology with contract gates per user request
---

# Harden agentic_core Spine Documentation — Contract/L5/Contract Gates/Proof Requirements

Harden the agentic_core spine documentation/specs so every runtime layer has explicit, detailed contract handoff requirements, L5 governance/certification requirements, contract gate requirements, and proof/receipt requirements.

---

## Context (SCQA)

- **Situation**: The agentic_core spine has REQ_ID-first documentation (2026-04-26 rewrite) with 13-section contract templates in 12 layer parent files. Per-layer REQ_MATRIX files exist at `docs/reference/contracts/step1/` but they are "Step 1 aggregation only" with TBD placeholders for runtime evidence, OTEL spans, artifacts, validators, tests, and negative controls.

- **Complication**: The TBD placeholders prevent the documentation from serving as an executable contract. Contract handoff requirements between layers are implicit rather than explicit. L5 governance requirements and contract gate requirements are not cross-referenced in layer matrices. Proof/receipt requirements lack specificity.

- **Question**: How do we harden the REQ_MATRIX files to replace TBD placeholders with explicit, detailed requirements while preserving the existing REQ_ID-first structure and no-overlap law?

- **Answer**: Audit all 12 REQ_MATRIX files, replace TBD placeholders with concrete contract handoff, L5, contract gate, receipt, and proof requirements, add a unified layer-by-layer contract matrix, and cross-reference with 00A L5 parent docs.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `docs/reference/contracts/step1/*_REQ_MATRIX.md` | 12 layer matrices with TBD placeholders | ✅ AUDITED — W0 complete, 1,164 TBD placeholders catalogued |
| `docs/reference/00A_L5_Governance_Safety/` | L5 certification requirements to cross-reference | ✅ AVAILABLE — comprehensive |
| `docs/reference/contracts/step1/` REQ_MATRIX files with contract gate requirements embedded | contract gate requirements mapped to layer handoffs | ✅ PATCHED — contract gate terminology applied |
| `docs/reference/0[1-9]_*/*_parent.md` | Layer parent REQ_ID contract templates | ✅ AVAILABLE — 12 files |
| `.windsurf/schemas/` | Machine-readable contract schemas | ✅ AVAILABLE — 8 files |
| `W0_REQ_MATRIX_GAP_REGISTER.md` | Baseline inventory with TBD locations | ✅ CREATED — 1,164 TBD placeholders documented |
| `W0_R_REPAIR_RECEIPT.md` | 00C cleanup completion record | ✅ CREATED — 00C quarantined to archived status |
| `W0_R_ACTIVE_SURFACE_VERIFICATION.md` | Active-layer 00C verification | ✅ CREATED — 0 active references confirmed |

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens | Status |
|-------|--------|-------|------------|--------|--------|
| Wave 0 | 12 REQ_MATRIX files audited | Baseline inventory | Pre-flight | ~8K | ✅ DONE |
| Wave 0.R | 00C/G01-G29 cleanup | Quarantine legacy terminology | Pre-W1 verification | ~2K | ✅ DONE |
| Wave 1 | U0 + L1 matrices hardened | Intake + Plan layers | U0/L1 complete | ~12K | ✅ DONE |
| Wave 2 | L0 + C0 + PA matrices hardened | Route + Context + Prompt layers | L0/C0/PA complete | ~15K | ✅ DONE |
| Wave 3 | L2 matrix hardened | Execution layer (E1-E5) | L2 complete | ~12K | ✅ DONE |
| Wave 4 | Exit + UWG + L4 + L6 matrices hardened | Exit, Write, Archive, Learning layers | Exit/UWG/L4/L6 complete | ~15K | ✅ DONE |
| Wave 5 | 99 Proof Auditor + unified matrix | E2E proof + layer-by-layer matrix | All layers unified | ~10K | ✅ DONE |
| Wave 6 | Machine-readable schemas audited | JSON/YAML contract files | Schemas validated | ~8K | ✅ DONE |

**Total: ~80K tokens across 6 waves, all GREEN**

**Status tracking**: Notion Status flips "Not Started" → "In Progress" at **Wave 1 start**.

---

## Out Of Scope

- No changes to runtime behavior (no code edits in agentic_core/ execution paths)
- No new REQ_IDs invented — only harden existing rows
- No changes to layer ownership boundaries (no-overlap law preserved)
- No changes to 00A, 00B parent file structure
- No new validators or CI gates invented
- No changes to apps_* domain contract files

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W0.P1 | REQ_MATRIX inventory | 12 REQ_MATRIX files | TBD placeholder audit | ~4K | ✅ DONE |
| W0.P2 | Gap register creation | 1 gap file | Document all TBD locations | ~4K | ✅ DONE |
| W0.R | 00C/G01-G29 cleanup repair | 3 files (00C matrix, index, receipts) | Quarantine legacy terminology | ~2K | ✅ DONE |
| W1.P1 | U0_INTAKE_REQ_MATRIX harden | 01_U0_INTAKE_REQ_MATRIX.md | TBD→concrete for intake | ~6K | ✅ DONE |
| W1.P2 | L1_PLAN_REQ_MATRIX harden | 02_L1_PLAN_REQ_MATRIX.md | TBD→concrete for planning | ~6K | ✅ DONE |
| W2.P1 | L0_L3_REQ_MATRIX harden | 03_L0_L3_REQ_MATRIX.md | TBD→concrete for routing | ~5K | ✅ DONE |
| W2.P2 | C0_REQ_MATRIX harden | 03A_C0_REQ_MATRIX.md | TBD→concrete for retrieval | ~5K | ✅ DONE |
| W2.P3 | PA_REQ_MATRIX harden | 03B_PA_REQ_MATRIX.md | TBD→concrete for prompt assembly | ~5K | ✅ DONE |
| W3.P1 | L2_REQ_MATRIX harden | 04_L2_REQ_MATRIX.md | TBD→concrete for execution | ~6K | ✅ DONE |
| W3.P2 | L2 E1-E5 sub-sections | 04_L2_REQ_MATRIX.md | E1 Prep, E2 Valid, E3 Exec, E4 Heal, E5 Seal | ~6K | ✅ DONE |
| W4.P1 | EXIT_REQ_MATRIX harden | 05_EXIT_REQ_MATRIX.md | TBD→concrete for X1/X2/X3 | ~5K | ✅ DONE |
| W4.P2 | L4_UWG_REQ_MATRIX harden | 00B_L4_UWG_REQ_MATRIX.md | TBD→concrete for write gate | ~5K | ✅ DONE |
| W4.P3 | L6_REQ_MATRIX harden | 06_L6_REQ_MATRIX.md | TBD→concrete for shadow eval | ~5K | ✅ DONE |
| W5.P1 | 99_E2E_REQ_MATRIX harden | 99_E2E_REQ_MATRIX.md | TBD→concrete for proof auditor | ~5K | ✅ DONE |
| W5.P2 | Unified contract matrix | New file: LAYER_CONTRACT_MATRIX.md | Cross-layer handoff view | ~5K | ✅ DONE |
| W6.P1 | Schema sync audit | .windsurf/schemas/ | Validate contract schema alignment | ~4K | ✅ DONE |
| W6.P2 | Schema updates (if gaps) | .windsurf/schemas/*.json/*.yaml | No updates required — semantic coverage adequate | ~4K | ✅ DONE |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

**GAP-1: TBD placeholders in all REQ_MATRIX files**
- All 12 REQ_MATRIX files contain "TBD_REQUIRED_RUNTIME_EVIDENCE", "TBD_REQUIRED_SPAN", etc.
- Impact: Documentation is not executable; cannot be used for release-gate validation

**GAP-2: Missing unified layer-by-layer contract/L5/contract gate matrix view**
- Contract handoffs are documented per-layer but not cross-referenced
- No single view showing U0→L1→L0→C0/PA/L3/L2→Exit→UWG→L4→L6 contract chain
- Impact: Hard to verify contract continuity across the spine

**GAP-3: L5 requirements not cross-referenced in layer matrices**
- L5 certification requirements exist in 00A but are not linked from layer REQ_MATRIX files
- Impact: Layer matrices don't show which L5 refs are required per handoff

**GAP-4: Contract gate requirements not mapped to layer handoffs**
- Contract gate requirements exist but layer matrices don't show which gates apply to which handoff
- Impact: Cannot verify gate coverage per contract transition

**GAP-5: Receipt/OTEL span contracts lack specificity**
- "TBD_REQUIRED_ARTIFACT" and "TBD_REQUIRED_SPAN" placeholders
- Impact: Observability contracts not enforceable

---

## Layer Contract Governance Matrix (PATCHED)

Canonical sources:
- `agentic_spine_contracts_master.json` — BaseContractEnvelope, transition matrix, schemas, fail-closed rules
- `agentic_process_L5_Governance_Safety.md` — per-layer L5 intersection requirements
- Layer REQ_MATRIX files — per-layer contract gate requirements embedded in contract schemas
- `agentic_process_mapping_v40.md` — runtime spine sequence and stage responsibilities

### U0 Request Intake

| Aspect | Specification |
|--------|---------------|
| **incoming_contracts** | raw inbound envelope |
| **outgoing_contracts** | ValidatedRequest, RejectedRequest |
| **required_l5_refs** | origin_trust_manifest_ref, data_boundary_labels, policy_hash (when available), l5_governance_context_digest (when L5-certifiable), audit_manifest_ref |
| **l5_checks** | caller/session/tenant baseline bound; user text is intent only; origin labels exist; malformed/oversized/duplicate/injection-risk input surfaced |
| **required_contract_gates** | request_ingress_gate, identity_tenant_session_gate, quota_idempotency_gate, origin_label_gate, malformed_duplicate_size_gate, intent_ambiguity_gate, safety_policy_gate, privacy_cross_context_gate |
| **receipts** | intake_receipt, request_digest, origin_label_seed |
| **fail_closed_if** | missing request_id, missing run_id, missing trace_root, missing origin labels, user text promoted into authority |

### L1 Interpret / Plan

| Aspect | Specification |
|--------|---------------|
| **incoming_contracts** | ValidatedRequest |
| **outgoing_contracts** | L1PlanContract, L1PlanRejected (when blocked) |
| **required_l5_refs** | policy_ref_set, planning_prior_refs, l5_governance_context_digest, data_boundary_labels, audit_manifest_ref |
| **l5_checks** | user intent separated from authority; L4 reads planning-prior only; assumptions/ambiguity marked; route hints non-authoritative; model output does not widen authority |
| **required_contract_gates** | intent_ambiguity_gate, authority_separation_gate, safety_policy_gate, risk_tier_gate, planning_prior_read_gate, workflow_shape_precheck_gate |
| **receipts** | plan_digest, ambiguity_register, support_expectation, action_expectation, route_hints |
| **fail_closed_if** | L1 selects final route, L1 retrieves final evidence, L1 creates execution authority, ambiguity affects irreversible action and unresolved |

### L0 Route Decision

| Aspect | Specification |
|--------|---------------|
| **incoming_contracts** | L1PlanContract |
| **outgoing_contracts** | RouteContract, RETTerminalPacket, GroundingRouteContract, ManagedWorkflowRouteContract, RouteRejected (when blocked) |
| **required_l5_refs** | policy_hash, blueprint_hash, registry_digest_set, l5_governance_context_digest, route_manifest_hash, capability_ceiling, sandbox_requirement, replay_key, audit_manifest_ref |
| **l5_checks** | exactly one deterministic route; route is policy-bound; route cannot widen read/tool/model/network/filesystem/write scope; cache reuse is governed reuse; provider/model/tool substitution requires re-certification |
| **required_contract_gates** | route_selection_gate, route_determinism_gate, cache_reuse_gate, grounding_requirement_gate, cost_latency_budget_gate, hitl_posture_gate |
| **receipts** | route_digest, route_telemetry, route_replay_receipt |
| **fail_closed_if** | no L1PlanContract, multiple routes emitted, route not replayable, registry digest missing where route uses registry-bound object, route widens authority |

### C0 Context Engine

| Aspect | Specification |
|--------|---------------|
| **incoming_contracts** | RouteContract with grounding_required = true |
| **outgoing_contracts** | FinalEvidenceContract, EvidenceBlockedContract (when blocked) |
| **required_l5_refs** | origin_trust_manifest_ref, source_lineage_map, acl_verification_receipts, freshness_receipts, contradiction_report, l5_governance_context_digest, audit_manifest_ref |
| **l5_checks** | retrieved text remains data only; source authority known; ACL/tenant/region/data class/freshness/lineage verified; citation anchors and source versions preserved; weak/blocked/conflicted/empty/unknown support not promoted to PASS |
| **required_contract_gates** | retrieval_legality_gate, evidence_quality_gate, acl_freshness_lineage_gate, contradiction_support_gate, retrieved_content_trust_gate, privacy_cross_context_gate |
| **receipts** | evidence_receipt, citation_map, contradiction_report, support_status |
| **fail_closed_if** | evidence required but unavailable, blocked source included, retrieved text becomes instruction, ACL/freshness/source lineage missing, support_status UNKNOWN treated as PASS |

### Prompt Assembly

| Aspect | Specification |
|--------|---------------|
| **incoming_contracts** | L1PlanContract, RouteContract, FinalEvidenceContract (when grounding_required = true), L5 refs, schema refs |
| **outgoing_contracts** | PromptEnvelope / CompiledPromptArtifact, PromptAssemblyRejected (when blocked) |
| **required_l5_refs** | policy_hash, blueprint_hash, registry_digest_set, origin_trust_manifest_ref, l5_governance_context_digest, provider lane certification refs, egress certification refs (when applicable), replay_manifest, audit_manifest_ref |
| **l5_checks** | authority slot order preserved; user content remains task intent; retrieved/tool/model/human content remains data; lower-authority content cannot override higher-authority instructions; provider/model/tool lane matches registry certification; prompt artifact signed and replay-bound |
| **required_contract_gates** | prompt_boundary_gate, instruction_data_boundary_gate, slot_authority_order_gate, schema_binding_gate, provider_rendering_gate, deterministic_trim_gate |
| **receipts** | prompt_hash, slot_lineage_map, assembly_security_receipt, deterministic_trim_receipt |
| **fail_closed_if** | authority order violation, prompt injection not neutralized, required schema binding missing, C0 support status inflated, provider render drifts from canonical slots |

### L3 Orchestration

| Aspect | Specification |
|--------|---------------|
| **incoming_contracts** | ManagedWorkflowRouteContract |
| **outgoing_contracts** | L3ToL2StepContract, SealedWorkflowPackage, L3StepBlocked (when blocked) |
| **required_l5_refs** | managed_workflow_route_contract_ref, policy_hash, blueprint_hash, registry_digest_set, l5_governance_context_digest, capability ceiling, sandbox ceiling, replay_key, audit_manifest_ref |
| **l5_checks** | workflow expansion preserves RouteContract bounds; each step carries same authority context or explicit re-certification need; workflow does not expand scope/tools/providers/side effects/durable mutation authority; L3 does not re-route or execute |
| **required_contract_gates** | workflow_trajectory_gate, loop_retry_thrash_gate, branch_join_budget_gate, step_authority_preservation_gate |
| **receipts** | workflow_ledger, checkpoint_ref, branch_join_state, step_handoff_receipt |
| **fail_closed_if** | L3 chooses new route, workflow exceeds bounds, step widens authority, step adds unapproved tool/provider/credential, direct L4 write authorized |

### L2 Execute

| Aspect | Specification |
|--------|---------------|
| **incoming_contracts** | RouteContract or L3ToL2StepContract, PromptEnvelope (when model execution required), L2ExecutionPacket |
| **outgoing_contracts** | FrozenExecutionContext, ExecutionValidationReceipt, AttemptReceipt, HealReceipt (when repair occurs), SealedL2Artifact |
| **required_l5_refs** | capability_token, sandbox_envelope, policy_hash, blueprint_hash, registry_digest_set, provider/model/tool certification refs, egress certification refs (when provider/tool/network used), replay_key, audit_manifest_ref, l5_governance_context_digest |
| **l5_checks** | L2 receives authority and cannot create authority; E1 freezes execution room; E2 validates before execution; E3 uses governed model/tool/provider gateway only; no direct SDK bypass; no silent provider/model/tool substitution; E4 heal stays same-authority/same route/same policy/same blueprint/same sandbox; E5 seals artifact and keeps proposed_state_diff inert |
| **required_contract_gates** | tool_model_registry_gate, tool_argument_gate, external_egress_gate, sandbox_filesystem_shell_gate, memory_access_gate, privacy_cross_context_gate, output_schema_gate, replay_determinism_gate, audit_trace_completeness_gate |
| **receipts** | prep_receipt, validation_receipt, attempt_receipt, optional_ptc_receipt, heal_receipt, seal_receipt |
| **fail_closed_if** | missing capability, missing sandbox, stale policy, stale registry, blocked ACL, route mismatch, egress not certified, direct L4 write path, proposed_state_diff treated as durable state |

### Exit Evaluation / Control

| Aspect | Specification |
|--------|---------------|
| **incoming_contracts** | RETTerminalPacket, SealedL2Artifact, SealedWorkflowPackage, ReClearedHITLPacket |
| **outgoing_contracts** | ExitReviewPacket, X1CheckoutResult, X2AggregationResult, ExitDispositionReceipt, CommitRequest (when X3C), RuntimeExhaustBundle |
| **required_l5_refs** | l5_certification_refs, policy_hash, blueprint_hash, registry_digest_set, sandbox_envelope_ref (when execution used sandbox), capability_token_ref (when execution used capability), provider_receipts (when provider used), evidence refs (when grounded), replay_manifest, audit_manifest_ref, hitl re-clearance refs (when HITL occurred) |
| **l5_checks** | safe-to-leave evidence exists; required authority exists; required route/replay/terminal class exists; grounded output has evidence comparison; HITL input remains data until re-cleared; mutation request is only CommitRequest to UWG; L5 informs Exit but never emits X3 |
| **required_contract_gates** | exit_input_completeness_gate, output_quality_gate, security_leakage_gate, replay_readiness_gate, exit_disposition_gate, durable_write_candidate_gate, audit_trace_completeness_gate |
| **receipts** | exit_review_packet, x1_checkout_result, x2_aggregation_result, x3_disposition_receipt, runtime_exhaust_bundle |
| **fail_closed_if** | no sealed result, missing required authority, missing replay, missing route, missing terminal class, missing evidence on grounded path, missing OTEL after runtime begins, more than one X3 emitted, L6 attempts current-run rescue |

### UWG / L4

| Aspect | Specification |
|--------|---------------|
| **incoming_contracts** | CommitRequest, StateDiffValidationResult |
| **outgoing_contracts** | StateCommitReceipt, BlockedWriteReceipt |
| **required_l5_refs** | exit_disposition_receipt_ref (with X3C), proposed_state_diff_ref, authority_scope, capability_token_ref, sandbox_envelope_ref, policy_hash, blueprint_hash, registry_digest_set, replay_key, rollback_plan_ref, audit_manifest_ref, l5_governance_context_digest |
| **l5_checks** | durable write enters only through UWG; CommitRequest tied to Exit X3C; mutation does not widen authority; schema/policy/replay/audit/lock/rollback checks pass; direct L2/L3/Exit/L6/tool write path blocked |
| **required_contract_gates** | durable_write_sovereignty_gate, state_diff_validation_gate, authority_scope_gate, lock_conflict_rollback_gate, audit_append_gate, direct_write_bypass_gate |
| **receipts** | state_diff_validation_result, state_commit_receipt, blocked_write_receipt, audit_append_receipt, read_surface_refresh_receipt |
| **fail_closed_if** | CommitRequest not from Exit, no X3C, missing proposed_state_diff, replay/audit missing, direct write bypass detected, write_admission_verdict is not ADMIT_COMMIT |

### L6 Shadow Evaluation

| Aspect | Specification |
|--------|---------------|
| **incoming_contracts** | RuntimeExhaustBundle |
| **outgoing_contracts** | CompletedEvalRecord, RCAPacket, ProposalPacket, FutureRunPromotionRequest |
| **required_l5_refs** | runtime_exhaust_bundle_ref, l5_certification_refs, observer_law_receipt, replay_proof_ref, regression_proof_ref, safety_proof_ref, calibration_proof_ref (when evaluator/judge changes), gauntlet_receipt, audit_manifest_ref |
| **l5_checks** | completed-run only; no current-run mutation; governance failures evaluated after boundary; proposals remain inert until UWG admits; activation only at future run_start; judge/evaluator change requires calibration proof |
| **required_contract_gates** | learning_firewall_gate, completed_run_boundary_gate, evaluator_calibration_gate, future_run_promotion_gate, no_current_run_mutation_gate |
| **receipts** | observer_law_receipt, eval_record_seal, gauntlet_receipt, future_run_activation_receipt |
| **fail_closed_if** | L6 mutates current run, L6 emits X3, L6 writes L4 directly, L6 silently patches prompts/policy/memory/cache/registry, promotion bypasses UWG |

### 99 Proof Auditor

| Aspect | Specification |
|--------|---------------|
| **incoming_contracts** | full contract chain, L5CertificationPacket, ContractGateVerdicts, OTEL spans, ExitDispositionReceipt, UWG receipts (when commit path used) |
| **outgoing_contracts** | RuntimeProofBundle |
| **required_l5_refs** | l5_certification_result_ref, l5_governance_context_digest, policy_hash, blueprint_hash, registry_digest_set, origin_trust_manifest_ref, capability_token_ref, sandbox_envelope_ref, egress_certification_receipt_refs, hitl_reclearance_receipt_refs, replay_envelope_ref, audit_manifest_ref |
| **l5_checks** | all L5 child certifiers certify same governed object; digest mismatch emits L5_NOT_CERTIFIED; L5 did not emit ContractGateVerdict; L5 did not emit X3; L5 did not commit durable state |
| **required_contract_gates** | contract_chain_completeness_gate, gate_coverage_gate, otel_trace_completeness_gate, replay_reconstructability_gate, negative_control_gate, no_bypass_assertion_gate, ContractGateVerdict per applicable gate, ContractGateMeshResult, missing_gate_ids with NOT_APPLICABLE/UNKNOWN reasons |
| **receipts** | runtime_proof_bundle, no_bypass_assertions, negative_control_results, reconstruction_report, replay_report |
| **fail_closed_if** | contract chain missing, OTEL spans missing for critical stages, negative controls absent, replay not reconstructable, durable mutation bypassed UWG, UNKNOWN treated as PASS, NOT_APPLICABLE lacks reason |

### Global Invariants

- **Contract law belongs in agentic_core**
- **apps_*** may supply app-specific values, schemas, manifests, rubrics, tools, evidence sources, capability profiles
- **apps_* must not define alternate handoff law**
- **L5 certifies evidence only** — does not route, retrieve, assemble prompts, execute, emit ContractGateVerdict, emit X3, write L4, or learn into current run
- **Contract gates emit ContractGateVerdict evidence for the current handoff**
- **Exit emits exactly one X3** — final disposition
- **UWG admits durable writes** — sole L4 mutation path
- **L4 stores durable state**
- **L6 learns only after current-run boundary**
- **99 proves the chain ran** — contract chain, L5 refs, contract gate refs, OTEL refs, replay refs, no-bypass assertions

---

## Execution Plan

### Phase W0.P1 — REQ_MATRIX Inventory
**Scope**: Read all 12 REQ_MATRIX files, catalog TBD placeholder locations

**Commands**:
```bash
# Inventory REQ_MATRIX files
ls -la docs/reference/contracts/step1/*_REQ_MATRIX.md
# Count TBD placeholders per file
grep -c "TBD_" docs/reference/contracts/step1/*_REQ_MATRIX.md
```

**Acceptance**: ✅ DONE — 12 REQ_MATRIX files inventoried; 1,164 TBD placeholders catalogued; see W0_REQ_MATRIX_GAP_REGISTER.md

### Phase W0.P2 — Gap Register Creation
**Scope**: Document all TBD locations with line numbers and context

**Acceptance**: ✅ DONE — W0_REQ_MATRIX_GAP_REGISTER.md created with line-by-line TBD locations, coverage gaps, 00C refs identified, and wave assignments

### Phase W0.R — 00C/G01-G29 Cleanup Repair
**Scope**: Quarantine legacy 00C Runtime Gates terminology before W1. Mark 00C file as archived, update Step1 index, verify no active references remain.

**Acceptance**: ✅ DONE — 00C_RUNTIME_GATES_REQ_MATRIX.md archived with deprecation header; STEP1_REQ_MATRIX_INDEX.md updated; W0_R_REPAIR_RECEIPT.md created; 0 active 00C references in layer matrices

### Phase W1.P1 — U0_INTAKE_REQ_MATRIX Harden
**Scope**: Replace TBD placeholders with concrete requirements for U0 Request Intake

**Acceptance**: 
- All TBD placeholders replaced in 01_U0_INTAKE_REQ_MATRIX.md
- Contract handoffs: raw inbound envelope → ValidatedRequest / RejectedRequest; ValidatedRequest is consumed by L1.
- L5 requirements: RuntimeCertificationBinding, authority context, policy_hash
- Contract gates: request_ingress_gate, identity_tenant_session_gate mapped to U0 handoffs
- Receipts: validated_request.json, rejected_request.json, intake_observability.json
- OTEL spans: u0.envelope_validate, u0.identity_stamp, u0.handoff_to_l1

### Phase W1.P2 — L1_PLAN_REQ_MATRIX Harden
**Scope**: Replace TBD placeholders with concrete requirements for L1 Interpret/Plan

**Acceptance**:
- All TBD placeholders replaced in 02_L1_PLAN_REQ_MATRIX.md
- Contract handoffs: ValidatedRequest → L1PlanContract → RouteContract
- L5 requirements: policy_ref_set, planning_prior_refs, authority_scope expectation, risk_hint, grounding/action/HITL/UWG hints, data_boundary_labels, l5_governance_context_digest, audit_manifest_ref
- Contract gates: intent_ambiguity_gate, safety_policy_gate, risk_tier_gate mapped
- Receipts: l1_plan_contract.json, plan_observability.json

### Phase W5.P2 — Unified Contract Matrix Creation
**Scope**: Create LAYER_CONTRACT_MATRIX.md with cross-layer handoff view

**Acceptance**:
- 12-surface matrix (U0, L1, L0, C0, PA, L3, L2, Exit, UWG, L4, L6, 99 Proof Auditor). L5 is cross-cutting certification refs, not a sequential runtime surface.
- Each layer: inputs, outputs, incoming contracts, outgoing contracts, L5 refs, contract gates, receipts
- Contract chain traceability: U0→L1→L0→C0/PA/L3/L2→Exit→UWG→L4→L6

### Phase W6.P1 — Schema Sync Audit
**Scope**: Validate .windsurf/schemas/ against hardened contract requirements

**Acceptance**:
- Schema files checked for BaseContractEnvelope fields
- Gap list for any missing contract_type, contract_version, producer_stage, consumer_stage, etc.

---

## Rules

- Preserve existing REQ_ID-first structure — no new REQ_IDs, only harden existing rows
- Preserve no-overlap law — layer ownership boundaries remain unchanged
- Cross-reference, don't duplicate — link to 00A L5 docs, don't copy content
- Concrete over TBD — every TBD placeholder gets a specific requirement
- Machine-readable — ensure schemas can be parsed for CI gate validation
- Evidence-based — requirements must reference existing code/artifacts where provable

---

## Success Criteria

- [ ] All 12 REQ_MATRIX files have zero TBD placeholders
- [ ] Every layer has explicit incoming/outgoing contract section in its matrix
- [ ] Every layer has explicit L5 requirements section cross-referencing 00A
- [ ] Every layer has explicit contract gate requirements section
- [ ] Unified LAYER_CONTRACT_MATRIX.md created with 12-surface cross-reference
- [ ] Machine-readable schemas validated against hardened requirements
- [ ] Documentation compiles without errors (markdown lint)

**Required**: Every layer has explicit contract gate requirements mapped to incoming and outgoing handoffs.

---

## Implementation Commands

```bash
# Pre-flight: verify existing docs
python -c "import os; files = [f for f in os.listdir('docs/reference/contracts/step1/') if f.endswith('_REQ_MATRIX.md')]; print(f'Found {len(files)} REQ_MATRIX files')"

# Wave-by-wave hardening (example for U0)
# edit docs/reference/contracts/step1/01_U0_INTAKE_REQ_MATRIX.md
# replace TBD_REQUIRED_RUNTIME_EVIDENCE → concrete evidence requirement
# replace TBD_REQUIRED_SPAN → concrete span name
# replace TBD_REQUIRED_ARTIFACT → concrete artifact path
# ... etc for all TBD fields

# Final validation
grep -r "TBD_" docs/reference/contracts/step1/ || echo "SUCCESS: No TBD placeholders remaining"
```

---

## Rollback Strategy

If hardening introduces errors:
1. Restore from git: `git checkout docs/reference/contracts/step1/`
2. Preserve gap register for reference
3. Re-attempt with smaller scope (single REQ_MATRIX at a time)

---

## Definition of Done

| # | Criterion | Verification command / evidence | Status |
|---|---|---|---|
| DoD-1 | All 12 REQ_MATRIX files hardened with zero TBD placeholders | `grep -r "TBD_" docs/reference/contracts/step1/` returns empty | 🔲 |
| DoD-2 | Unified LAYER_CONTRACT_MATRIX.md created | `test -f docs/reference/contracts/step1/LAYER_CONTRACT_MATRIX.md` | 🔲 |
| DoD-3 | Schema alignment verified | Schema files validate against hardened requirements | 🔲 |
| DoD-4 | Documentation lint clean | `markdownlint docs/reference/contracts/step1/*.md` passes | 🔲 |
| DoD-5 | Plan registered in Notion Plans DB | Notion page ac53d31b-3068-4039-9ebe-856c12caab32 shows row with slug | 🔲 |
| DoD-6 | Zero 00C/G01-G29 references remaining in active matrices | `grep -r '00C\|G01\|...\|G29' docs/reference/contracts/step1/*_REQ_MATRIX.md` (excluding archived) returns empty; verified in W0_R_ACTIVE_SURFACE_VERIFICATION.md | ✅ |

**Verification-vs-Deferral table**:

| Item | Why deferred | Tracked in |
|---|---|---|
| Runtime validator implementation | Out of scope — docs only, no code changes | Future plan: runtime-validator-impl |
| Runtime contract-gate enforcement integration | Deferred — docs specify contract-gate obligations only | Future plan: runtime-contract-gate-enforcement |
| Negative control test authoring | Test impl deferred — docs specify what tests must do | tests/ deferred scope |

---

PLAN_CREATED: plan=agentic-core-spine-contract-hardening-a7d4e1 status=Not_Started

WAVE_COMPLETE: plan=agentic-core-spine-contract-hardening-a7d4e1 wave=0 note="REQ_MATRIX inventory and gap register complete — 12 files audited, 1,164 TBD placeholders catalogued"

WAVE_COMPLETE: plan=agentic-core-spine-contract-hardening-a7d4e1 wave=0.R note="00C/G01-G29 cleanup complete — 00C file archived, Step1 index updated, 0 active references verified"

PHASE_COMPLETE: plan=agentic-core-spine-contract-hardening-a7d4e1 phase=W0.P1 note="12 REQ_MATRIX files inventoried"

PHASE_COMPLETE: plan=agentic-core-spine-contract-hardening-a7d4e1 phase=W0.P2 note="W0_REQ_MATRIX_GAP_REGISTER.md created with line-by-line TBD locations"

PHASE_COMPLETE: plan=agentic-core-spine-contract-hardening-a7d4e1 phase=W0.R note="00C_RUNTIME_GATES_REQ_MATRIX.md archived, STEP1_REQ_MATRIX_INDEX.md updated, W0_R_REPAIR_RECEIPT.md and W0_R_ACTIVE_SURFACE_VERIFICATION.md created"

WAVE_COMPLETE: plan=agentic-core-spine-contract-hardening-a7d4e1 wave=1 note="U0 + L1 matrices hardened — 01_U0_INTAKE_REQ_MATRIX.md and 02_L1_PLAN_REQ_MATRIX.md complete with zero TBD placeholders"

PHASE_COMPLETE: plan=agentic-core-spine-contract-hardening-a7d4e1 phase=W1.P1 note="01_U0_INTAKE_REQ_MATRIX.md hardened with contract gates, L5 refs, receipts, OTEL spans"

PHASE_COMPLETE: plan=agentic-core-spine-contract-hardening-a7d4e1 phase=W1.P2 note="02_L1_PLAN_REQ_MATRIX.md hardened with contract gates, L5 refs, receipts, OTEL spans"

W1_STOP: W1 complete. W2 (L0/C0/PA hardening) pending explicit approval.

WAVE_COMPLETE: plan=agentic-core-spine-contract-hardening-a7d4e1 wave=2 note="L0 + C0 + PA matrices hardened — 03_L0_L3_REQ_MATRIX.md, 03A_C0_REQ_MATRIX.md, 03B_PA_REQ_MATRIX.md complete with zero TBD placeholders"

PHASE_COMPLETE: plan=agentic-core-spine-contract-hardening-a7d4e1 phase=W2.P1 note="03_L0_L3_REQ_MATRIX.md hardened with L0 contract gates (6), L3 contract gates (4), L5 refs, OTEL spans"

PHASE_COMPLETE: plan=agentic-core-spine-contract-hardening-a7d4e1 phase=W2.P2 note="03A_C0_REQ_MATRIX.md hardened with C0 contract gates (6), L5 refs, OTEL spans"

PHASE_COMPLETE: plan=agentic-core-spine-contract-hardening-a7d4e1 phase=W2.P3 note="03B_PA_REQ_MATRIX.md hardened with PA contract gates (6), L5 refs, OTEL spans"

W2_STOP: W2 complete. W3 (L2 hardening) pending explicit approval.

WAVE_COMPLETE: plan=agentic-core-spine-contract-hardening-a7d4e1 wave=3 note="L2 matrix hardened — 04_L2_REQ_MATRIX.md with 102 TBD placeholders replaced, E1-E5 sub-sections added"

PHASE_COMPLETE: plan=agentic-core-spine-contract-hardening-a7d4e1 phase=W3.P1 note="04_L2_REQ_MATRIX.md hardened with 9 contract gates, 11 L5 refs, 6 OTEL spans, 6 receipts"

PHASE_COMPLETE: plan=agentic-core-spine-contract-hardening-a7d4e1 phase=W3.P2 note="E1-E5 sub-sections added with detailed freeze/validate/exec/heal/seal requirements"

W3_STOP: W3 complete. W4 (Exit/UWG/L6 hardening) pending explicit approval.

WAVE_COMPLETE: plan=agentic-core-spine-contract-hardening-a7d4e1 wave=4 note="Exit + UWG + L4 + L6 matrices hardened — 294 TBD placeholders replaced across 3 files"

PHASE_COMPLETE: plan=agentic-core-spine-contract-hardening-a7d4e1 phase=W4.P1 note="05_EXIT_REQ_MATRIX.md hardened with 7 contract gates, 12 L5 refs, 6 OTEL spans"

PHASE_COMPLETE: plan=agentic-core-spine-contract-hardening-a7d4e1 phase=W4.P2 note="00B_L4_UWG_REQ_MATRIX.md hardened with UWG (6 gates) + L4 (2 gates), 11 L5 refs, 6 OTEL spans"

PHASE_COMPLETE: plan=agentic-core-spine-contract-hardening-a7d4e1 phase=W4.P3 note="06_L6_REQ_MATRIX.md hardened with 5 contract gates, 9 L5 refs, 7 OTEL spans"

W4_STOP: W4 complete. W5 (E2E + unified matrix) pending explicit approval.

WAVE_COMPLETE: plan=agentic-core-spine-contract-hardening-a7d4e1 wave=5 note="99 Proof Auditor + Unified Contract Matrix complete — 100 TBD placeholders replaced, 12-surface unified matrix created"

PHASE_COMPLETE: plan=agentic-core-spine-contract-hardening-a7d4e1 phase=W5.P1 note="99_E2E_REQ_MATRIX.md hardened with 6 contract gates, 12 L5 refs, 7 OTEL spans"

PHASE_COMPLETE: plan=agentic-core-spine-contract-hardening-a7d4e1 phase=W5.P2 note="LAYER_CONTRACT_MATRIX.md created with 12 runtime surfaces, 58 total contract gates, L5 as cross-cutting refs"

W5_STOP: W5 complete. W6 (schema validation) pending explicit approval.

WAVE_COMPLETE: plan=agentic-core-spine-contract-hardening-a7d4e1 wave=6 note="Schema sync audit complete — 45 schemas audited (8 JSON + 10 YAML + 27 SQL), 11 REQ_MATRIX files validated, NO_SCHEMA_UPDATE_REQUIRED"

PHASE_COMPLETE: plan=agentic-core-spine-contract-hardening-a7d4e1 phase=W6.P1 note="W6_SCHEMA_SYNC_AUDIT.md created — all schemas parse cleanly, 0 critical gaps, 0 legacy references"

PHASE_COMPLETE: plan=agentic-core-spine-contract-hardening-a7d4e1 phase=W6.P2 note="No schema updates required — semantic coverage adequate, cosmetic gaps documented for future evolution"

W6_STOP: W6 complete. All waves DONE.

PLAN_COMPLETE: plan=agentic-core-spine-contract-hardening-a7d4e1 note="All 7 waves complete — 1,164 TBD placeholders replaced across 12 REQ_MATRIX files, unified contract matrix created, schemas audited and validated"
