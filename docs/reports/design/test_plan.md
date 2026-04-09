# Test Plan
**Phase**: Design Only — No code changes permitted  
**Date**: 2026-04-09  
**Coverage target**: 100% of new/modified code from implementation plan; zero weakening of existing tests

---

## T1 — Ingress Envelope (REQ-001, REQ-002, GAP-001)

**Module**: `L5_safety/enforcement/ingress_envelope_check.py` (new per B01)

| test_id | test_name | test_type | input | expected_result | critical |
|---|---|---|---|---|---|
| T1-01 | valid_request_passes_all_six_checks | unit | Well-formed request with valid auth, quota headroom, valid schema | `StampedRequest` returned with request_id, session_id, trace_root, caller_scope_baseline | YES |
| T1-02 | malformed_schema_rejected | unit | Request missing required fields | `RejectionSlip(reason_code="SCHEMA_VIOLATION")` raised | YES |
| T1-03 | auth_failure_rejected | unit | Request with invalid/expired auth token | `RejectionSlip(reason_code="AUTH_FAILURE")` | YES |
| T1-04 | rate_limit_exceeded_rejected | unit | Request exceeding quota limit | `RejectionSlip(reason_code="QUOTA_EXCEEDED")` | YES |
| T1-05 | tenant_mismatch_rejected | unit | Auth token tenant_id != request tenant_id | `RejectionSlip(reason_code="TENANT_MISMATCH")` | YES |
| T1-06 | trace_root_stamped_before_l1 | integration | Valid request submitted | trace_root present in all downstream L1 spans | YES |
| T1-07 | duplicate_request_id_suppressed | unit | Same request_id submitted twice | Second request rejected or deduplicated | YES |
| T1-08 | no_downstream_invocation_on_reject | unit | Any rejection case | L1 never called; no side-effects before gate | YES |

---

## T2 — L1 Plan Contract (REQ-003, REQ-004, GAP-002)

**Module**: `L1_cognition/types/plan_contract_types.py` (new per B04); `L1_cognition/enforcement/reasoning_chokepoint.py`

| test_id | test_name | test_type | input | expected_result | critical |
|---|---|---|---|---|---|
| T2-01 | valid_plan_contract_produced | unit | Valid user request through cognitive_engine | `L1PlanContract` returned with all seven fields populated | YES |
| T2-02 | missing_field_raises_violation | unit | cognitive_engine returns dict missing confidence | `PlanContractViolation` raised at chokepoint | YES |
| T2-03 | grounding_required_true_triggers_c0 | integration | Plan with grounding_required=True | C0 retrieval pipeline invoked | YES |
| T2-04 | grounding_required_false_bypasses_c0 | integration | Plan with grounding_required=False | C0 retrieval pipeline NOT invoked | YES |
| T2-05 | policy_constraints_reflected_in_plan | unit | Disallowed action type in user request | Plan does not propose the disallowed action | YES |
| T2-06 | l1_cannot_call_tools | unit | L1 reasoning execution | No tool invocations recorded during L1 phase | YES |
| T2-07 | l1_reads_l4_policy_before_synthesis | integration | L1 execution trace | policy_hash bound to L1PlanContract matches L4 active policy | YES |

---

## T3 — L0 Routing (REQ-005, REQ-006, GAP-010)

**Module**: `L0_routing/enforcement/`, `L0_routing/reasoning/agentic_router.py`

| test_id | test_name | test_type | input | expected_result | critical |
|---|---|---|---|---|---|
| T3-01 | exact_cache_hit_routes_r1a | unit | Request matching exact cache entry | Route=R1A; deep pipeline not invoked | YES |
| T3-02 | semantic_cache_hit_routes_r1b | unit | Request semantically similar to cached | Route=R1B with policy-approval threshold check | YES |
| T3-03 | grounding_required_routes_r3 | unit | Plan with grounding_required=True | Route=R3; C0 retrieval invoked | YES |
| T3-04 | external_dispatch_routes_r4 | unit | Plan requiring external action | Route=R4; dispatch packet produced | YES |
| T3-05 | no_path_routes_r5_abstain | unit | Plan with no viable route | Route=R5; safe fallback response | YES |
| T3-06 | no_implicit_default_route | unit | Route decision with ambiguous input | Exception raised (no silent default) | YES |
| T3-07 | pre_routing_gate_fires_before_cache | integration | Request with expired tenant scope | Gate DENY before R1A/R1B lookup; cache not consulted | YES |
| T3-08 | cross_tenant_request_blocked_at_routing | integration | Request with cross-tenant ACL | Gate DENY; route decision never made | YES |

---

## T4 — C0 Evidence and Prompt Assembly (REQ-007, REQ-008, GAP-007, GAP-003)

**Modules**: `L3_orchestration/types/c0_evidence_contract_types.py` (new per B05); `prompt_governance/core/prompt_assembler.py`

| test_id | test_name | test_type | input | expected_result | critical |
|---|---|---|---|---|---|
| T4-01 | c0_contract_has_all_six_fields | unit | Retrieval pipeline output | `C0EvidenceContract` with verified_chunks, cited_spans, source_ids, coverage_score, abstain_hint, contradiction_flags | YES |
| T4-02 | low_coverage_sets_abstain_hint | unit | Coverage_score below threshold | abstain_hint=True in C0EvidenceContract | YES |
| T4-03 | abstain_hint_triggers_abstain_disposition | integration | C0 output with abstain_hint=True | Prompt assembler emits ABSTAIN exit disposition | YES |
| T4-04 | c0_slotted_before_u0 | unit | PromptEnvelope produced | C0 evidence appears before U0 policy in slot order | YES |
| T4-05 | token_overflow_triggers_abstain | unit | Token budget exceeded by context | Overflow → ABSTAIN (not silent truncation) | YES |
| T4-06 | prompt_envelope_hmac_verifiable | unit | PromptEnvelope produced | HMAC recomputed from same inputs produces same signature | YES |
| T4-07 | cross_tenant_chunks_not_returned | unit | Retrieval with cross-tenant ACL | No cross-tenant chunks in C0EvidenceContract | YES |
| T4-08 | stale_chunks_filtered | unit | Retrieval with expired chunks | Expired chunks not present in output | YES |

---

## T5 — L2 Execution Chokepoint and Heal Loop (REQ-009, REQ-010, REQ-011, GAP-006)

**Modules**: `L2_execution/enforcement/execution_guardrail_chokepoint.py`; `L5_safety/enforcement/HealingStrategy.py`

| test_id | test_name | test_type | input | expected_result | critical |
|---|---|---|---|---|---|
| T5-01 | missing_capability_token_raises_permission_error | unit | authorize_and_execute without token | `PermissionError` raised before execution | YES |
| T5-02 | deny_verdict_aborts_with_trace | unit | Guardrail returns DENY | Execution aborted; reenters_safety emitted; trace recorded | YES |
| T5-03 | human_gated_without_approval_blocks | unit | HUMAN_GATED action without human_approved=True | `HumanReviewRequired` raised | YES |
| T5-04 | mutation_routes_through_uwg | unit | MUTATION action | execution_terminates_at_uwg edge emitted; no direct write | YES |
| T5-05 | error_unknown_timeout_fail_closed | unit | Guardrail returns ERROR/TIMEOUT/UNKNOWN | Execution aborted (fail-closed) | YES |
| T5-06 | heal_loop_binds_same_policy_hash | unit | Heal request with different policy_hash than original | `SnapshotMismatchError` raised | YES |
| T5-07 | repair_count_threshold_escalates | unit | repair_count > threshold | `FAIL_TERMINAL` result; escalation triggered | YES |
| T5-08 | sealed_artifact_has_terminal_class | unit | L2 execution completes | `terminal_class` in sealed artifact is one of SUCCESS/FAIL/ESCALATE/REJECTED | YES |
| T5-09 | no_direct_write_from_l2 | unit | L2 execution attempts direct write | Write blocked; `GravityBreachError` raised | YES |

---

## T6 — Exit Control Gate (REQ-012, GAP-004)

**Module**: `L5_safety/enforcement/exit_control_gate.py` (new per B02)

| test_id | test_name | test_type | input | expected_result | critical |
|---|---|---|---|---|---|
| T6-01 | secrets_in_output_deny | unit | L2 artifact containing secret/PII | `ExitDisposition.DENY_RETURN` | YES |
| T6-02 | policy_fail_deny | unit | L2 artifact failing X1C policy check | `ExitDisposition.DENY_RETURN` | YES |
| T6-03 | grounded_safe_allow | unit | Grounded, policy-pass artifact | `ExitDisposition.ALLOW_RESPONSE` | YES |
| T6-04 | commit_payload_routes_to_uwg | unit | Artifact containing durable commit payload | `ExitDisposition.COMMIT_TO_UWG` | YES |
| T6-05 | low_confidence_escalates | unit | Artifact with confidence below threshold | `ExitDisposition.ESCALATE_TO_HITL` | YES |
| T6-06 | error_disposition_fail_closed | unit | Evaluation error/exception during X1 evaluation | `ExitDisposition.DENY_RETURN` (not silent fallback) | YES |
| T6-07 | no_silent_fallback_path | unit | Every code path in gate | All paths produce non-null explicit ExitDisposition | YES |
| T6-08 | bus_d_e_received_at_gate | integration | C2 observability anomaly detected | BUS_D/BUS_E signals received by exit gate and processed | YES |

---

## T7 — HITL Re-Clearance (REQ-013, GAP-005)

**Module**: exit-control HITL path (per B03)

| test_id | test_name | test_type | input | expected_result | critical |
|---|---|---|---|---|---|
| T7-01 | modify_diff_without_re_clear_blocked | unit | Human provides MODIFY_DIFF; re-clear gate bypassed | Blocked; `ReClearRequiredError` raised | YES |
| T7-02 | authority_state_frozen_during_review | unit | HITL escalation triggered | `authority_state == FROZEN` and `write_auth == NONE` asserted | YES |
| T7-03 | bounded_packet_only_exposed | unit | HITL packet contents | Packet contains only materialized data; no live state references | YES |
| T7-04 | human_approve_routes_via_l5_re_clear | integration | APPROVE decision | Output re-enters L5 policy validation before ALLOW/COMMIT | YES |
| T7-05 | human_reject_blocks_commit | unit | REJECT decision | No ALLOW_RESPONSE or COMMIT_TO_UWG produced | YES |
| T7-06 | no_concurrent_mutations_during_hitl | integration | HITL active + concurrent write attempt | Concurrent write blocked by authority_state=FROZEN | YES |

---

## T8 — UWG Write Governance (REQ-014, GAP-013)

**Module**: `L2_execution/enforcement/UniversalWriteGateway.py`; `L4_state/enforcement/proof_of_ledger.py` (new per B07)

| test_id | test_name | test_type | input | expected_result | critical |
|---|---|---|---|---|---|
| T8-01 | direct_write_from_l2_blocked | unit | L2 module attempts direct L4 write | Blocked by UWG; `GravityBreachError` | YES |
| T8-02 | direct_write_from_l6_blocked | unit | L6 module attempts direct L4 write | Blocked by UWG | YES |
| T8-03 | missing_signature_rejected | unit | Write request without compliance_hash | `AuthorizationError` raised at UWG | YES |
| T8-04 | concurrent_writes_serialized | integration | Two simultaneous write requests | Serialized; no race condition; second waits for write lock | YES |
| T8-05 | hash_chain_verifiable_post_commit | unit | Commit completes | hash_chain_entry verifiable without live state | YES |
| T8-06 | proof_of_ledger_produced_per_commit | unit | UWG commit | `ProofOfLedger` artifact produced with all five fields | YES |
| T8-07 | proof_knowledge_state_changes_on_mutation | unit | Two successive writes | knowledge_state_digest differs between commits | YES |
| T8-08 | promotion_without_gauntlet_approval_blocked | unit | PromotionToken without gauntlet signature | Rejected at UWG | YES (depends on B11) |

---

## T9 — Governance / Safety Plane (REQ-015, REQ-028)

**Modules**: `L5_safety/enforcement/policy_enforcement_point.py`; `L5_safety/enforcement/circuit_breaker_gate.py`; `L5_safety/validators/global_mutation_validator.py`

| test_id | test_name | test_type | input | expected_result | critical |
|---|---|---|---|---|---|
| T9-01 | prompt_injection_detected_and_blocked | unit | Request containing injection attempt | Injection detected; `REJECT` disposition | YES |
| T9-02 | disallowed_model_rejected | unit | Capability request for model not on allowlist | `REJECT` disposition | YES |
| T9-03 | layer_inversion_blocked | unit | L2 attempting L0-layer operation | Blocked with layer violation error | YES |
| T9-04 | ghost_write_blocked_and_frozen | unit | L2 ghost write attempt | Freeze triggered; UWG lock; audit note emitted | YES |
| T9-05 | compliance_hash_attached_to_approved | unit | Approved execution | compliance_hash present in execution context | YES |

---

## T10 — Determinism / Replay (REQ-017, GAP-011)

**Modules**: replay guard chain

| test_id | test_name | test_type | input | expected_result | critical |
|---|---|---|---|---|---|
| T10-01 | same_inputs_produce_same_digest | property | Identical inputs replayed twice | determinism_digest identical | YES |
| T10-02 | wall_clock_access_raises_violation | unit | Tool call accessing datetime.now() | `DeterminismViolation` raised | YES |
| T10-03 | raw_random_raises_violation | unit | Tool call accessing random.random() | `DeterminismViolation` raised | YES |
| T10-04 | uuid4_raises_violation | unit | Tool call calling uuid.uuid4() without guard | `DeterminismViolation` raised | YES |
| T10-05 | live_network_raises_violation | unit | Tool call making unguarded HTTP request | `DeterminismViolation` raised | YES |
| T10-06 | replay_mismatch_emits_fault_telemetry | unit | Replay produces different result | `FAULT_TELEMETRY` emitted; no silent continuation | YES |

---

## T11 — Observability and Learning (REQ-018, REQ-019, REQ-020, REQ-021)

**Modules**: `L6_observability/enforcement/verify_spine.py` (new per B08); `knowledge/lifecycle/index_eval_feedback.py` (new per B14)

| test_id | test_name | test_type | input | expected_result | critical |
|---|---|---|---|---|---|
| T11-01 | drift_detected_emits_bus_d | unit | drift_detector fires | BUS_D signal emitted with anomaly_flags | YES |
| T11-02 | l6_evidence_bundle_all_fields | unit | verify_spine run | `L6EvidenceBundle` has five required fields | YES |
| T11-03 | shadow_eval_read_only | unit | L6 eval accessing L4 | No write operations; read-only enforced | YES |
| T11-04 | recall_at_k_below_threshold_triggers_reindex | unit | Recall@K=0.5 with threshold=0.7 | `reindex_trigger` signal emitted | YES |
| T11-05 | commandant_gauntlet_blocks_without_sme | unit | Promotion without SME sign-off | Gauntlet gate blocks; promotion_token not issued | YES (depends on B11) |
| T11-06 | promotion_shadow_replay_failure_blocks | unit | Shadow replay of proposed rule change fails | Promotion blocked by gauntlet | YES (depends on B11) |
| T11-07 | live_run_unaffected_by_promotion | integration | Promotion in progress | Active live run unaffected (async isolation) | YES |

---

## T12 — Security / ACL / Tenancy (REQ-022, REQ-023, GAP-014)

**Modules**: `knowledge/ingestion/modality_types.py`; `knowledge/gates/preretrieval_gate.py`

| test_id | test_name | test_type | input | expected_result | critical |
|---|---|---|---|---|---|
| T12-01 | chunk_missing_tenant_id_rejected | unit | ContentMetadata without tenant_id | Ingestion validation error | YES |
| T12-02 | chunk_missing_expiry_rejected | unit | ContentMetadata without expiry_date | Ingestion validation error | YES |
| T12-03 | cross_tenant_chunk_high_similarity_blocked | unit | Cross-tenant chunk with cosine_similarity=0.99 | Filtered; not returned | YES |
| T12-04 | expired_chunk_filtered_at_retrieval | unit | Chunk past expiry_date | Filtered; not returned | YES |
| T12-05 | acl_filter_fires_before_vector_search | integration | Cross-tenant request | Gate DENY before vector search invoked | YES |

---

## T13 — Capability Gating (REQ-016, GAP partial)

**Module**: `L3_orchestration/utils/registry/capability_registry.py`; `L2_execution/enforcement/capability_chokepoint.py`

| test_id | test_name | test_type | input | expected_result | critical |
|---|---|---|---|---|---|
| T13-01 | unregistered_tool_blocked | unit | Tool invocation not in registry | `UnregisteredToolError` raised | YES |
| T13-02 | capability_token_expiry_enforced | unit | Expired capability_token | `CapabilityExpiredError` raised | YES |
| T13-03 | network_access_without_ticket_denied | unit | Network call without capability_token | Denied at sovereign egress | YES |
| T13-04 | invocation_record_in_replay_envelope | unit | Successful tool call | invocation_record appended to replay_envelope | YES |

---

## Test Execution Priority

| Wave | Batches | Required tests | Blocking |
|---|---|---|---|
| Pre-wave (HITL) | HITL-001–005 | HITL decisions logged | YES — no Wave 1/4 coding without HITL resolution |
| Wave 1 | B01, B02, B03 | T1, T6, T7 | YES — P0 gaps |
| Wave 2 | B04–B07 | T2, T4, T5, T8 | YES — foundational contracts |
| Wave 3 | B08–B10 | T3, T8, T10, T11-01–03 | YES — infrastructure |
| Wave 4 | B11, B12 | T11-05/06/07, T13 | HITL-gated |
| Wave 5 | B13–B15 | T11-04, T12 | Low priority |

---

## Regression Guard

All existing tests in `tests/unit/agentic_core/L2_execution/`, `tests/e2e/data/test_uwg_determinism_e2e.py`, `tests/e2e/data/test_hitl_lifecycle_e2e.py`, and `tests/unit/agentic_core/L0_routing/` MUST continue to pass after every batch. No weakening of assertions permitted per Constitutional §1.1.
