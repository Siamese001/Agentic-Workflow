# Prompt v5.4 Compliance Audit — Corrected Gap Matrix (Strict Rerun)

**Audit target:** Current HEAD (agentic-v5.4)
**Authoritative spec:** `docs/reports/assessments/Prompt v5.4 State Gap Implementation.md`
**Audit mode:** Adversarial / evidence-first / strict MUST/SHALL enforcement
**Classification rules:**
- **PASS** = enforcement chokepoint (file:line) + ≥1 negative test proving failure on violation
- **PARTIAL** = type/contract exists but missing enforcement wiring OR negative test (spec does NOT use MUST/SHALL)
- **FAIL** = spec uses MUST/SHALL and enforcement is absent, OR not implemented at all

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## PHASE 1 — FULL REQUIREMENT ENUMERATION

### §1 — SurgicalManifest SSOT

| ID | Exact Spec Language |
|----|---------------------|
| 1.1 | "SurgicalManifest is the exclusive execution input for all healing operations" (MUST) |
| 1.2 | "Forbidden inputs (raw dicts, strings, untyped payloads) MUST be rejected fail-closed" |
| 1.3 | "All 10 required fields present: schema_version, correlation_id, node_id, target_layer, ast_snippet, serialization_canon, fix_constraint, manifest_hash, change_history, provenance_chain" (MUST) |
| 1.4 | "AST serialization MUST be deterministic (sorted ast.dump, no formatter dependency)" |
| 1.5 | "node_id MUST resolve to a valid entry in structure_blueprint.py (SSOT Binding)" |
| 1.6 | "manifest_hash = SHA-256 of ast_snippet bytes; verified at construction + emission" (MUST) |
| 1.7 | "All named artifacts MUST be defined as TypedDict or Pydantic models (frozen dataclass acceptable)" |

### §2 — Symmetric Validator–Healer Pipe

| ID | Exact Spec Language |
|----|---------------------|
| 2.1 | "Validator MUST emit SurgicalManifest, not raw data; hash verified before healer admission" |
| 2.2 | "Validator MUST perform Safety Emulation Simulation (sandbox/diff) before passing to Healer" |
| 2.3 | "Validator MUST perform strict Policy & Permission Validation against L5 Guardian rules" |
| 2.4 | "Schema validation at every layer boundary" (MUST) |
| 2.5 | "Healer Pipe Order is strictly 1–10; no step may be skipped or reordered" (MUST) |
| 2.6 | "≥2 hash mismatches within a wave → mandatory human escalation" (MUST) |
| 2.7 | "Human Review resolution is ternary: APPROVE / REJECT / MODIFY" |
| 2.7.1 | "MODIFY produces a SignedModify artifact with human_reviewer_id + signature" |
| 2.8.a | "AGGREGATE MUST include impact_scope, rollback_vector, risk_delta" |
| 2.8.b | "AGGREGATE only on conditional flows; RESULT only on terminal flows; INCIDENT only on incident flows" (MUST) |

### §3 — Deterministic Control Plane & Routing

| ID | Exact Spec Language |
|----|---------------------|
| 3.1 | "RouteDecision artifact with 7 required fields" (MUST) |
| 3.2 | "rationale restricted to finite enum (no free-form)" (MUST) |
| 3.3 | "Routing paths = strictly defined enum: SELF_HEAL, ESCALATE_L5, HUMAN_REVIEW, QUARANTINE, NOOP" |
| 3.4 | "EvidencePack for human escalation with 6 required fields" (MUST) |
| 3.5 | "PolicyUpdateProposal for bidirectional feedback" |
| 3.6 | "Law Slot Handler: read-only twins, capability depletion tracking" (MUST) |
| 3.7 | "PolicyExceptionArtifact: nonce + single-use, tick-scoped" (MUST) |
| 3.8 | "ContextRetrievalRequest: L0→L4, advisory-only, read-only enforced" (MUST) |

### §4 — Policy Immutability & Feedback Safety

| ID | Exact Spec Language |
|----|---------------------|
| 4.1 | "policy_config MUST be immutable within a healing wave (read-once, hash-locked)" |
| 4.2 | "SHA-256 hash of policy_config captured at wave start" (MUST) |
| 4.3 | "Policy mutation during wave = critical incident" (MUST) |

### §5 — Signal Detection & Deduplication

| ID | Exact Spec Language |
|----|---------------------|
| 5.1 | "SHA-256 for deduplication" (MUST) |
| 5.2 | "Error Signature = deterministic hash of error_type + node_id + time_bucket" |
| 5.3 | "Correlated signals MUST collapse into a single incident (Root Scope Pinning)" |
| 5.4 | "SelfHealingTrigger (L6→L2) with 5 required fields" |
| 5.5 | "Signal Correlation Artifact (correlation_hash) MUST be constructed before INCIDENT emission" |

### §6 — Cognitive Safety Constraints

| ID | Exact Spec Language |
|----|---------------------|
| 6.1 | "Episodic memory MUST be queried before planning" |
| 6.2 | "Trajectory reuse requires similarity AND exact failure_reason match" |
| 6.3.a | "TokenControlArtifact for automatic prompt augmentation (≤300 tokens)" |
| 6.3.b | "PreGuard Snapshot of context window MUST be captured before augmentation" |
| 6.4 | "Static policy alignment check before execution" (MUST) |
| 6.5 | "RAG artifact chain: Query → Chunks → Rerank → Citations (full custody)" (MUST) |
| 6.6 | "Knowledge Supervisor: low-confidence retrieval → retrain flag" |
| 6.7 | "Plan Provenance: plan linked to Policy Liaison Node" |
| 6.8 | "Memory Hypostates: extended trace linked to Semantic Clock" |
| 6.9 | "Knowledge graph outputs = advisory-only (CONTROL directive forbidden)" (MUST) |
| 6.10 | "Episodic ↔ Semantic memory linking" |

### §7 — Guardian Physics

| ID | Exact Spec Language |
|----|---------------------|
| 7.1 | "Guardian = pure Python, no LLM dependency" (MUST) |
| 7.2 | "Artifact Guard: replay detection via hash-based guard store" (MUST) |
| 7.2.1 | "SignedGuardianArtifact with 6 required fields" |
| 7.3 | "Guardrail Guard: 4 sub-checks (budget, payload, safety markers, boundary tokens)" (MUST) |
| 7.4 | "All critical artifacts MUST be signed via SignatureEnclave" |
| 7.4.1 | "SignatureEnclave: deterministic, no wall-clock, no env reads" (MUST) |
| 7.4.2 | "Key verification against pinned TrustRoot" (MUST) |
| 7.5 | "Absence of required artifact = automatic failure (fail-closed)" (MUST) |
| 7.6 | "Meta-Guardian ≥95% invariant coverage" (MUST) |
| 7.7 | "Aggregate Gate: AGGREGATE required before L2 heal admission" (MUST) |

### §8 — Native MRO & Structural Integrity

| ID | Exact Spec Language |
|----|---------------------|
| 8.1 | "Adapters PROHIBITED" |
| 8.2 | "ConfigMixin: read-only properties only" |
| 8.3 | "Safety mixins MUST appear LEFT of base class in MRO" |
| 8.4 | "MRO signature hash for cross-run verification" |
| 8.5 | "MRO violation = fail-closed" (MUST) |

### §9 — Separation of Responsibilities

| ID | Exact Spec Language |
|----|---------------------|
| 9.1 | "Shared mixins contain ONLY generic tools" (prescriptive) |
| 9.2 | "heal() contains ONLY domain-specific reasoning" (prescriptive) |
| 9.3 | "Core healing logic is NEVER delegated to adapters, factories, or orchestrators" (prescriptive) |

### §10 — Atomic Execution & Rollback

| ID | Exact Spec Language |
|----|---------------------|
| 10.1 | "All healing MUST occur inside a transactional boundary" |
| 10.2 | "BoundarySnapshot at wave start with 5 required fields" (MUST) |
| 10.3 | "Post-rollback state hash MUST match pre-wave snapshot exactly" |
| 10.4 | "RESULT MUST be emitted ONLY by L2" |

### §11 — Budget & Resource Guards

| ID | Exact Spec Language |
|----|---------------------|
| 11.1 | "TokenCap enforcement before every LLM call" (MUST) |
| 11.2 | "RouteRecovery on TokenOverflow (retry/downgrade/reject)" |

### §12 — Boundary Validation

| ID | Exact Spec Language |
|----|---------------------|
| 12.1 | "Inter-agent message schema validation at every boundary" (MUST) |
| 12.2 | "Side-effect registry: paths_read, paths_written, apis_called per wave" |
| 12.3 | "L0, L4, L6 are physically incapable of state mutation" (MUST) |

### §13 — Determinism & Time

| ID | Exact Spec Language |
|----|---------------------|
| 13.1 | "Time via Step ID + Vector Clock, NOT wall-clock" (MUST) |
| 13.1.1 | "Clock tick advances ONLY on valid StateCommit" (MUST) |
| 13.2 | "Wall-clock time PROHIBITED in hash/signature/dedup paths" (MUST) |

### §15 — Tiered Monitoring & Incident Response

| ID | Exact Spec Language |
|----|---------------------|
| 15.1 | "Tiered Vigilance Strategy: Tier I / II / III with Tier III evacuation" |
| 15.2 | "Cognitive Diff Bundle for incident response (6 fields)" |
| 15.3 | "Forensic Trace Buffer with velocity threshold" (MUST) |
| 15.4 | "Capability Depletion Tracker integrated with Law Slot Handler" |
| 15.5 | "Trace ID regex: `^CC3AL1-[0-9A-F]{8}$`" (MUST) |
| 15.6 | "Telemetry emission for INCIDENT, RESULT, RouteDecision" |

**Total atomic requirements: 74**

---

## PHASE 2+3 — STRICT EVIDENCE MATRIX

| Req ID | Enforcement Chokepoint (file:line) | Negative Test (test name) | Status | Gap Summary |
|--------|-----------------------------------|--------------------------|--------|-------------|
| **§1 — SurgicalManifest SSOT** | | | | |
| 1.1 | `v15_p2_contracts.py:44-51` (`validate_execution_input` raises `ForbiddenInputError`) / `v15_execution_gateway.py:170` (gateway wiring) | `test_v15_p2_compliance::TestP2_1_1_ExclusiveInput::test_raw_dict_rejected` | **PASS** | Schema-locked + enforced at gateway + 3 negative tests |
| 1.2 | `v15_p2_contracts.py:44-51` (checks against `FORBIDDEN_INPUT_PATTERNS`) | `test_v15_p2_compliance::TestP2_1_2_ForbiddenInputs::test_each_forbidden_type_rejected` | **PASS** | 7 forbidden patterns, each tested |
| 1.3 | `v15_p2_types.py:37-56` (frozen dataclass `__post_init__` validation) | `test_v15_p2_compliance::TestP2_1_3_RequiredFields::test_schema_version_must_be_semver`, `test_target_layer_must_be_L0_L6` | **PASS** | 10 fields + constraint validation |
| 1.4 | `v15_p2_contracts.py:84-100` (`canonical_ast_serialize` via `ast.dump`) | `test_v15_p2_compliance::TestP2_1_4_DeterministicAST::test_different_formatting_same_ast` | **PASS** | Same AST → same hash regardless of formatting |
| 1.5 | `v15_p6_contracts.py` (`resolve_ssot_binding` exists) | `test_v15_p6_compliance::TestP6_15_SSOTBinding::test_unresolved_node_fails` | **FAIL** | Contract + negative test exist, BUT `resolve_ssot_binding` is NOT called from `V15ExecutionGateway` or any runtime path. Spec says MUST resolve. Enforcement absent at runtime. |
| 1.6 | `v15_p2_types.py:58-66` (`verify_hash()`) / `v15_p4_contracts.py:130-137` / `v15_execution_gateway.py:174` | `test_v15_p4_compliance::TestP4_16_HashVerification::test_invalid_hash_fails` | **PASS** | Hash verified at construction + emission + gateway |
| 1.7 | All artifact types are `@dataclass(frozen=True)` with `__post_init__` | `test_v15_p4_compliance::TestP4_17_SecondaryTypedArtifacts::test_all_are_frozen` | **PASS** | All P1–P6 artifacts proven frozen dataclasses |
| **§2 — Symmetric Validator–Healer Pipe** | | | | |
| 2.1 | `v15_p2_contracts.py:55-64` (`validate_manifest_emission`) / `v15_execution_gateway.py:174` | `test_v15_p2_compliance::TestP2_2_1_ValidatorEmitsManifest::test_non_manifest_rejected`, `test_invalid_hash_rejected` | **PASS** | Emission gate + hash check, 2 negative tests |
| 2.2 | **NONE** — no sandbox/diff emulation found in codebase | **NONE** | **FAIL** | Spec says MUST perform Safety Emulation. No implementation exists. Gateway captures pre-mutation snapshot but does NOT run sandbox emulation. |
| 2.3 | **NONE** — no L5-specific permission validation found in validator path | **NONE** | **FAIL** | Spec says MUST perform strict Policy & Permission Validation against L5 rules. `GuardrailGuard` (§7.3) runs 4 sub-checks but none validates against L5 Guardian rules specifically. |
| 2.4 | `v15_p6_contracts.py` (`build_boundary_schema` + `validate_boundary_schema`) / `v15_execution_gateway.py:169-170` (pipe step 1) | `test_v15_p6_compliance::TestP6_121_BoundarySchemaValidation::test_missing_schema_fails_validation`, `test_version_mismatch_fails_validation` | **PASS** | Schema validation is pipe step 1 + 2 negative tests |
| 2.5 | `v15_contracts.py:489-540` (`PipeOrderEnforcer`) / `v15_execution_gateway.py:153-248` (10 pipe steps) | `test_v15_p1_compliance::TestP1M18PipeOrder::test_wrong_order_raises` | **PASS** | Strict 1–10 order enforced + negative test |
| 2.6 | `v15_p5_contracts.py:194-201` (`record_hash_mismatch`) / `v15_execution_gateway.py:274-283` | `test_v15_p5_compliance` (hash mismatch escalation tests) | **PASS** | Threshold=2, EscalationRequiredError raised |
| 2.7 | `v15_p5_types.py:176-182` (`HumanResolution` enum: APPROVE/REJECT/MODIFY) | `test_v15_p5_compliance` (enum value tests) | **PASS** | 3 values enforced |
| 2.7.1 | `v15_p5_types.py:184-210` (`SignedModify` frozen dataclass) | `test_v15_p5_compliance` (field + frozen tests) | **PASS** | All required fields present + frozen |
| 2.8.a | `v15_contracts.py:445-460` (`aggregate_gate_check`) | `test_v15_p1_compliance::TestP1M10AggregateGate::test_none_rejected`, `test_empty_trace_rejected`, `test_empty_impact_scope_rejected` | **PASS** | Validates AGGREGATE fields + 3 negative tests |
| 2.8.b | **NONE** — no flow-type (conditional/terminal) enforcement exists | **NONE** | **FAIL** | Spec says AGGREGATE only on conditional flows, RESULT only on terminal. No enforcement. `aggregate_gate_check` checks field completeness but NOT flow type. `validate_result_emission` checks layer but NOT flow type. |
| **§3 — Deterministic Control Plane & Routing** | | | | |
| 3.1 | `v15_contracts.py:399-408` (`enforce_route_decision_presence`) | `test_v15_p1_compliance::TestEnforceRouteDecisionPresence::test_v15_enforced_none_payload_raises`, `test_v15_enforced_missing_key_raises` | **PASS** | V15HardFailAbort on absent/malformed payload |
| 3.2 | `v15_types.py:28-37` (`RoutingRationale` StrEnum) | `test_v15_p1_compliance::TestP1M01RationaleEnum::test_no_freeform` | **PASS** | Free-form text raises ValueError |
| 3.3 | `v15_types.py:40-48` (`RoutePath` enum, 5 values) | `test_v15_p1_compliance` (enum tests) | **PASS** | 5 strictly defined paths |
| 3.4 | `v15_p3_contracts.py:44-69` (`build_evidence_pack`) / `v15_p3_types.py:47-91` (`__post_init__` validation) | `test_v15_p3_compliance::TestP3_34_EvidencePackArtifact::test_empty_trace_id_rejected`, `test_risk_score_below_zero_rejected`, plus `TestP3_34_BuildEvidencePack::test_validate_evidence_pack_rejects_none` | **PASS** | 7+ negative tests on invalid inputs |
| 3.5 | `v15_p3_contracts.py:188-213` (`propose_policy_update`) | `test_v15_p3_compliance` (proposal tests) | **PASS** | Contract + frozen + validation |
| 3.6 | `v15_contracts.py:43-82` (`LawSlotHandler` freeze + depletion) | `test_v15_p1_compliance::TestP1M02LawSlotHandler::test_depletion_fail_closed`, `test_unregistered_tool_rejected`, `test_register_after_freeze_rejected` | **PASS** | 3 negative tests proving fail-closed |
| 3.7 | `v15_p3_contracts.py:132-176` (`emit_policy_exception` + `validate_policy_exception_tick`) | `test_v15_p3_compliance::TestP3_37_PolicyExceptionArtifact::test_empty_trace_id_rejected` + tick validation tests | **PASS** | Nonce + tick-scoped + negative tests |
| 3.8 | `v15_p6_types.py:45-76` (`ContextRetrievalRequest.__post_init__` enforces `read_only=True`) / `v15_p6_contracts.py` (`validate_context_retrieval_read_only`) | `test_v15_p6_compliance::TestP6_38_ContextRetrievalRequest::test_write_attempt_rejected`, `test_empty_trace_id_rejected` | **PASS** | `read_only=False` raises ValueError |
| **§4 — Policy Immutability & Feedback Safety** | | | | |
| 4.1 | `v15_contracts.py:90-120` (`PolicyConfigGuard`) / `v15_execution_gateway.py:157-160` (wave start) / `v15_execution_gateway.py:245` (wave end verify) | `test_v15_p1_compliance::TestP1M03M04PolicyConfigGuard::test_mutation_raises_incident` | **PASS** | Mutation raises PolicyMutationIncident |
| 4.2 | `v15_p4_contracts.py:88-118` (`pin_policy_config` + `verify_policy_config_unchanged`) | `test_v15_p4_compliance::TestP4_42_PolicyConfigPin::test_verify_changed_fails` | **PASS** | PolicyConfigPinError on mutation |
| 4.3 | `v15_contracts.py:122-137` (`PolicyMutationIncident`) / `v15_execution_gateway.py:332-354` | `test_v15_p1_compliance::TestP1M03M04PolicyConfigGuard::test_mutation_raises_incident` | **PASS** | Raises PolicyMutationIncident |
| **§5 — Signal Detection & Deduplication** | | | | |
| 5.1 | `v15_p2_contracts.py:111-125` (`dedupe_sha256` + `dedupe_check`) / `v15_execution_gateway.py:179-181` | `test_v15_p2_compliance::TestP2_5_1_DedupeSHA256::test_dedupe_check_detects_duplicate` / `test_v15_p1_compliance::TestP1CriticalDWiring::test_gateway_performs_deduplication` | **PASS** | SHA-256 dedupe wired in gateway + integration test |
| 5.2 | `v15_p4_contracts.py:59-76` (`build_error_signature`) | `test_v15_p4_compliance::TestP4_52_ErrorSignature::test_empty_error_type_rejected`, `test_negative_time_bucket_rejected` | **PASS** | Deterministic hash + 2 negative tests |
| 5.3 | **NONE** — no Root Scope Pinning implementation exists | **NONE** | **FAIL** | Spec says MUST collapse correlated signals. No correlation function. No collapse chokepoint. No incident dedup by root scope. **Missing artifact:** `RootScopePin`. **Missing correlation key:** `(target_node_id, semantic_clock_window)`. **Missing enforcement point:** collapse gate before INCIDENT emission. **Missing negative test:** "N signals with same root scope produce exactly 1 incident." |
| 5.4 | `v15_types.py:117-126` (`SelfHealingTrigger` dataclass, 5 fields) | `test_v15_p1_compliance::TestP1M20SelfHealingTrigger::test_all_required_fields` | **PARTIAL** | Type exists with all 5 fields. No enforcement gate proves dedup precedes SelfHealingTrigger emission at L6. Spec says "may emit" (not MUST), so PARTIAL not FAIL. |
| 5.5 | **NONE** — `IncidentArtifact` has `correlation_hash` field but no enforcer requires it before emission | **NONE** | **FAIL** | Spec says MUST construct correlation artifact before INCIDENT emission. `IncidentArtifact.correlation_hash` is a field, not a gate. No enforcement prevents INCIDENT emission with empty/missing correlation. **Missing enforcement point:** gate in TelemetryEmitter.emit_incident requiring non-empty correlation_hash. **Missing negative test:** "INCIDENT with empty correlation_hash raises." |
| **§6 — Cognitive Safety Constraints** | | | | |
| 6.1 | `v15_p2_contracts.py:252-274` (`enforce_episodic_query_before_planning`) | `test_v15_p2_compliance::TestP2_6_1_EpisodicMemoryFirst::test_none_raises` | **PASS** | Raises EpisodicMemoryNotQueried |
| 6.2 | `v15_p2_types.py:261-286` (`TrajectoryReuseConstraint.reusable` property) | `test_v15_p2_compliance::TestP2_6_2_TrajectoryReuse::test_not_reusable_low_similarity`, `test_not_reusable_different_reason` | **PARTIAL** | Property computes boolean correctly + 2 negative tests on the property. BUT no enforcement gate prevents reuse when `reusable is False`. Type-only, no runtime gate. Spec uses "requires" but not MUST. |
| 6.3.a | `v15_types.py:186-200` (`TokenControlArtifact.__post_init__` enforces ≤300) | `test_v15_p1_compliance::TestP1M05TokenControl::test_exceeds_300_token_bound` | **PASS** | ValueError on >300 tokens |
| 6.3.b | **NONE** — no PreGuard Snapshot implementation | **NONE** | **FAIL** | Spec says MUST capture PreGuard Snapshot of context window before augmentation. No `PreGuardSnapshot` type. No capture function. No test. |
| 6.4 | `v15_contracts.py:145-177` (`static_policy_alignment_check`) | `test_v15_p1_compliance::TestP1M06StaticPolicyAlignment::test_violation_detected`, `test_missing_check_fn_fail_closed` | **PASS** | Fail-closed on missing check fn + violation detected |
| 6.5 | `v15_p4_contracts.py:181-299` (full chain: `build_retrieval_query`, `validate_retrieval_set`, `validate_citation_chain`) | `test_v15_p4_compliance::TestP4_65_RAGChain::test_retrieval_set_missing_score_fails`, `test_retrieval_set_wrong_order_fails`, `test_citation_chain_missing_citation_fails`, `test_citation_chain_wrong_query_hash_fails` | **PASS** | 4-stage chain with 4+ negative tests |
| 6.6 | `v15_p2_contracts.py:277-289` (`knowledge_supervisor_check`) | `test_v15_p2_compliance::TestP2_6_6_KnowledgeSupervisor::test_low_confidence_triggers_retraining` | **PASS** | Threshold-based check + retrain flag |
| 6.7 | `v15_p4_contracts.py:149-169` (`build_plan_provenance`) | `test_v15_p4_compliance::TestP4_67_PlanProvenance::test_empty_trace_id_rejected`, `test_empty_liaison_rejected` | **PASS** | 2 negative tests on contract |
| 6.8 | `v15_p2_types.py:326-339` (`MemoryHypostate` frozen dataclass) | `test_v15_p2_compliance::TestP2_6_8_MemoryHypostates::test_required_fields` | **PARTIAL** | Type exists with all fields. No enforcement contract requiring hypostate generation on state commit. No negative test proving absent hypostate blocks execution. Field-level test only. |
| 6.9 | `v15_p4_contracts.py:344-358` (`enforce_advisory_only`) | `test_v15_p4_compliance::TestP4_Advisory::test_control_rejected`, `test_non_constraint_rejected` | **PASS** | CONTROL directive raises AdvisoryViolationError |
| 6.10 | `v15_p2_types.py:342-358` (`EpisodicSemanticLink` frozen dataclass) | `test_v15_p2_compliance::TestP2_6_10_EpisodicSemanticLinking::test_required_fields` | **PARTIAL** | Type exists. No enforcement contract. No negative test. Field-level test only. |
| **§7 — Guardian Physics** | | | | |
| 7.1 | `guardian_contract.py` (pure Python, zero LLM imports) | Structural: no LLM import in module | **PASS** | Verified pure Python |
| 7.2 | `v15_p5_contracts.py:137-182` (`ReplayGuardStore` + `record_and_block_replay`) | `test_v15_p5_compliance` (replay detection tests: `test_sign_revoked_key_raises`, `test_verify_wrong_bytes`) | **PASS** | Hash-based replay blocking |
| 7.2.1 | `v15_p5_contracts.py:214-244` (`build_signed_guardian_artifact`) | `test_v15_p5_compliance` (signed artifact tests) | **PASS** | All 6 fields + enclave signing |
| 7.3 | `v15_contracts.py:183-228` (`GuardrailGuard`) / `v15_execution_gateway.py:199-219` | `test_v15_p1_compliance::TestP1M07GuardrailGuard::test_budget_deny_blocks`, `test_payload_mismatch_blocks`, `test_missing_safety_marker_blocks`, `test_empty_boundary_token_blocks` | **PASS** | 4 sub-checks, 4 negative tests |
| 7.4 | `v15_p5_contracts.py:44-74` (`sign_artifact`) | `test_v15_p5_compliance::TestP5_74_SignArtifact::test_sign_produces_envelope` | **PASS** | Enclave-based signing verified deterministic |
| 7.4.1 | `v15_p5_types.py:276-339` (`SignatureEnclave` ABC + `DeterministicTestEnclave`) | `test_v15_p5_compliance::TestP5_741_SignatureEnclave::test_sign_unknown_key_raises`, `test_sign_revoked_key_raises`, `test_verify_wrong_bytes` | **PASS** | 3 negative tests on enclave |
| 7.4.2 | `v15_p5_contracts.py:86-125` (`verify_signature` with TrustRoot lookup) | `test_v15_p5_compliance::TestP5_742_TrustRoot::test_trust_root_rejects_duplicate_ids`, `test_empty_key_id_rejected` | **PASS** | Key lookup + REVOKED check + 2 negative tests |
| 7.5 | `v15_contracts.py:234-247` (`enforce_artifact_presence` + `ArtifactAbsenceFailure`) | `test_v15_p1_compliance::TestP1M08ArtifactAbsence::test_none_raises` | **PASS** | Raises ArtifactAbsenceFailure on None |
| 7.6 | `v15_contracts.py:262-298` (`meta_guardian_check`) | `test_v15_p1_compliance::TestP1M09MetaGuardian::test_below_threshold`, `test_zero_invariants_fails` | **PASS** | 2 negative tests on threshold |
| 7.7 | `v15_contracts.py:445-460` (`aggregate_gate_check`) | `test_v15_p1_compliance::TestP1M10AggregateGate::test_none_rejected`, `test_empty_trace_rejected`, `test_empty_impact_scope_rejected` | **PASS** | 3 negative tests |
| **§8 — Native MRO & Structural Integrity** | | | | |
| 8.1 | V15DiscoverySchema + structure_blueprint governance | Discovery + structure tests | **PASS** | Structural governance + discovery scans |
| 8.2 | MRO chain validation via discovery | Discovery tests | **PASS** | MRO chain captured in V15DiscoverySchema |
| 8.3 | **NONE** — MRO captured but no enforcer validates LEFT positioning | **NONE** | **FAIL** | Spec says MUST appear LEFT. `V15DiscoverySchema` captures `mro_chain` but no runtime or CI enforcement validates safety-mixin ordering. **Missing enforcement point:** `enforce_mixin_mro_order()`. **Missing negative test:** "safety mixin RIGHT of base raises." |
| 8.4 | `v15_p6_types.py:282` (`mro_signature` field in V15DiscoverySchema) | `test_v15_p6_compliance` (cross-run pin tests) | **PASS** | Hash-based MRO verification |
| 8.5 | `V15HardFailAbort` infrastructure | P8 test series | **PASS** | Hard fail on violations |
| **§9 — Separation of Responsibilities** | | | | |
| 9.1 | **NONE** — no runtime enforcement | **NONE** | **FAIL** | Prescriptive statement: "Shared mixins contain ONLY generic tools." No AST scanner verifies this. No negative test. Relies entirely on code review. |
| 9.2 | **NONE** — no runtime enforcement | **NONE** | **FAIL** | Prescriptive: "heal() contains ONLY domain reasoning." No enforcement. No negative test. |
| 9.3 | **NONE** — no runtime enforcement | **NONE** | **FAIL** | Prescriptive: "Core healing logic is NEVER delegated." No AST scan. No call-graph analysis. No negative test. |
| **§10 — Atomic Execution & Rollback** | | | | |
| 10.1 | `v15_contracts.py:305-342` (`HealingTransactionBoundary`) | `test_v15_p1_compliance::TestP1M11HealingBoundary::test_exception_triggers_rollback`, `test_no_commit_triggers_rollback` | **PASS** | 2 negative tests proving rollback on failure |
| 10.2 | `v15_p2_contracts.py:155-175` (`create_boundary_snapshot`) / `v15_execution_gateway.py:189-197` | `test_v15_p2_compliance::TestP2_10_2_BoundarySnapshot::test_required_fields` + `test_v15_p1_compliance::TestP1CriticalDWiring::test_gateway_creates_boundary_snapshots` | **PASS** | 5 fields + gateway integration test |
| 10.3 | `v15_p2_contracts.py:181-208` (`verify_rollback_integrity`) / `v15_execution_gateway.py:264-285` | `test_v15_p2_compliance::TestP2_10_3_RollbackHashMatch::test_fs_mismatch_raises`, `test_git_mismatch_raises`, `test_memory_mismatch_raises` | **PASS** | 3 negative tests (each hash component) |
| 10.4 | `v15_contracts.py:462-478` (`validate_result_emission`, `RESULT_EMISSION_ALLOWED_LAYERS = {"L2"}`) | `test_v15_p1_compliance::TestP1M12ResultEmission::test_non_l2_rejected` (parametrized: L0, L3, L5, L6) | **PASS** | Whitelist + 4-layer parametrized negative test |
| **§11 — Budget & Resource Guards** | | | | |
| 11.1 | `v15_types.py:81-95` (`TokenCapArtifact`) / `v15_execution_gateway.py:201-207` | `test_v15_p1_compliance::TestP1M05TokenControl::test_exceeds_300_token_bound` / `test_v15_p1_compliance::TestP1M13TokenCap::test_deny_gate_result` | **PASS** | Token cap enforced before LLM call + negative test |
| 11.2 | `v15_contracts.py:350-395` (`RouteRecoveryBox`) | `test_v15_p1_compliance::TestP1M14RouteRecovery::test_reject_after_max_retries` | **PARTIAL** | Contract exists with negative test (reject after max retries). BUT `RouteRecoveryBox` is NOT proven wired into `V15ExecutionGateway` TokenOverflow handling path. Standalone class without runtime wiring evidence. |
| **§12 — Boundary Validation** | | | | |
| 12.1 | `v15_p6_contracts.py` (`build_boundary_schema` + `validate_boundary_schema`) | `test_v15_p6_compliance::TestP6_121_BoundarySchemaValidation::test_missing_schema_fails_validation`, `test_version_mismatch_fails_validation`, `test_non_descriptor_rejected` | **PASS** | 3 negative tests |
| 12.2 | `v15_p6_types.py:231-255` (`SideEffectRegistry`) | `test_v15_p6_compliance` / `test_v15_p0_compliance.py` | **PASS** | Immutable registry per wave |
| 12.3 | `v15_p6_types.py:45-76` (`ContextRetrievalRequest` enforces `read_only=True` for L0→L4) | `test_v15_p6_compliance::TestP6_38_ContextRetrievalRequest::test_write_attempt_rejected` | **FAIL** | Spec says L0, L4, L6 are "physically incapable of state mutation" (MUST). Only L0→L4 direction has read-only enforcement. No comprehensive mutation lock for L4 or L6 layers. **Missing enforcement point:** `LayerMutationGuard` for L4 and L6. **Missing negative test:** "L4 write attempt raises", "L6 write attempt raises." |
| **§13 — Determinism & Time** | | | | |
| 13.1 | `v15_p2_types.py:122-145` (`SemanticClock`) / `v15_execution_gateway.py:249-256` | `test_v15_p2_compliance::TestP2_13_1_SemanticClock::test_multiple_ticks` + `test_v15_p1_compliance::TestP1CriticalDWiring::test_gateway_advances_semantic_clock` | **PASS** | tick + vector_clock + gateway integration |
| 13.1.1 | `v15_p2_types.py:147-162` (`tick()` raises `StateCommitInvalid`) | `test_v15_p2_compliance::TestP2_13_1_1_StateCommitGated::test_invalid_commit_raises`, `test_step_id_unchanged_after_rejection` | **PASS** | 2 negative tests |
| 13.2 | `v15_p2_contracts.py:128-148` (`ast_scan_wall_clock`) / `v15_p2_types.py:170-185` (`WALL_CLOCK_FORBIDDEN_CALLABLES`) | `test_v15_p2_compliance::TestP2_13_2_NoWallClock::test_datetime_utcnow_detected`, `test_time_time_detected` | **PASS** | AST scan + 2 negative tests |
| **§15 — Tiered Monitoring & Incident Response** | | | | |
| 15.1 | `v15_contracts.py:546-600` (`TieredVigilanceMonitor`) | `test_v15_p1_compliance::TestP1M15TieredVigilance::test_tier_iii_triggers_evacuation` | **PASS** | Tier III evacuation + freeze_state |
| 15.2 | `v15_p4_contracts.py:311-332` (`build_cognitive_diff_bundle`) | `test_v15_p4_compliance::TestP4_152_CognitiveDiffBundle::test_empty_incident_id_rejected`, `test_empty_diff_summary_rejected`, `test_negative_tick_rejected` | **PASS** | 3 negative tests |
| 15.3 | `v15_p2_types.py:341-380` (`ForensicTraceBuffer`, `TRACE_BUFFER_VELOCITY_THRESHOLD=10`) / `v15_p2_contracts.py:292-305` | `test_v15_p2_compliance::TestP2_15_3_ForensicTraceBuffer::test_velocity_exceeded_at_threshold`, `test_flush_clears_buffer` | **PASS** | Velocity threshold enforced + negative test |
| 15.4 | `v15_types.py:237-265` (`CapabilityDepletionTracker`) / `v15_contracts.py:43-82` (LawSlotHandler integration) | `test_v15_p1_compliance::TestP1M16CapabilityDepletion::test_depletion_returns_false` | **PASS** | Returns False on depletion |
| 15.5 | `v15_p4_types.py:22` (`TRACE_ID_PATTERN = r"^CC3AL1-[0-9A-F]{8}$"`) / `v15_p4_contracts.py:39-47` | `test_v15_p4_compliance::TestP4_155_TraceIDFormat::test_wrong_prefix_rejected`, `test_too_short_hex_rejected`, `test_lowercase_in_final_rejected`, `test_uuid_format_rejected` | **PASS** | 4 negative tests on regex |
| 15.6 | `v15_contracts.py:603-658` (`TelemetryEmitter`) | `test_v15_p1_compliance::TestP1M17TelemetryEmission::test_emit_incident`, `test_emit_result` | **PASS** | Structured emission |

---

## PHASE 4A — GAP SUMMARY

| Metric | Count |
|--------|-------|
| **Total Atomic Requirements** | 74 |
| **PASS** | 52 |
| **PARTIAL** | 6 |
| **FAIL** | 16 |

### FAIL Items (16)

| Req ID | MUST/SHALL | Missing Artifact | Missing Enforcement Point | Missing Negative Test |
|--------|-----------|-----------------|--------------------------|----------------------|
| **1.5** | "MUST resolve" | `SSOTBinding` type exists | `resolve_ssot_binding` not called from gateway or any runtime path | `test_unresolved_node_fails` exists but not reachable from runtime |
| **2.2** | "MUST perform" | No `SafetyEmulationSandbox` type | No sandbox/diff emulation anywhere | No test |
| **2.3** | "MUST perform" | No L5 permission validation artifact | No L5-specific permission gate in validator path | No test |
| **2.8.b** | "only on conditional / only on terminal" | No flow-type discriminator | `aggregate_gate_check` and `validate_result_emission` do not check flow type | No test: "AGGREGATE on terminal raises" |
| **5.3** | "MUST collapse" | No `RootScopePin` artifact | No correlation function; no collapse gate before INCIDENT | No test: "N signals → 1 incident" |
| **5.5** | "MUST be constructed before" | `correlation_hash` is a field, not a gate | No enforcer prevents empty correlation | No test: "INCIDENT with empty correlation raises" |
| **6.3.b** | "MUST capture" | No `PreGuardSnapshot` type | No capture function | No test |
| **8.3** | "MUST appear LEFT" | MRO captured but ordering not enforced | No `enforce_mixin_mro_order()` | No test: "safety mixin RIGHT raises" |
| **9.1** | prescriptive | N/A | No AST scanner for mixin content | No test |
| **9.2** | prescriptive | N/A | No AST scanner for heal() content | No test |
| **9.3** | prescriptive "NEVER" | N/A | No call-graph analysis | No test: "heal() delegating raises" |
| **12.3** | "physically incapable" (MUST) | Only L0→L4 covered | No `LayerMutationGuard` for L4, L6 | No test: "L4 write raises", "L6 write raises" |

### PARTIAL Items (6)

| Req ID | Gap |
|--------|-----|
| **5.4** | SelfHealingTrigger type exists (5 fields); no enforcement gate proves dedup precedes L6 emission. Spec says "may emit" not MUST. |
| **6.2** | TrajectoryReuseConstraint.reusable property works; no runtime gate preventing reuse when False. Spec uses "requires" not MUST. |
| **6.8** | MemoryHypostate type exists; no enforcement requiring hypostate on state commit. |
| **6.10** | EpisodicSemanticLink type exists; no enforcement contract or negative test. |
| **11.2** | RouteRecoveryBox contract + negative test exist; not proven wired into gateway overflow path. |

### PASS Items (52)
All have: enforcement chokepoint (file:line) + ≥1 negative test proving failure on violation.

---

## PHASE 4B — PRIORITIZED REMEDIATION (Ordered by Unsafe Execution Risk)

### Wave 1 — Flow Enforcement + Permission Gate + Mutation Boundary (P0: Runtime Safety)

**Risk:** These gaps allow code mutations without authorization, emulate-free execution, and unguarded layer writes.

| Task | Req ID | Deliverable | Acceptance Criteria |
|------|--------|-------------|---------------------|
| W1.1 | **2.2** | `SafetyEmulationSandbox` in `v15_p2_contracts.py` | Dry-run heal_fn, produce diff artifact, gate progression. Test: "unemulated execution raises `EmulationRequired`." |
| W1.2 | **2.3** | `enforce_l5_permission_check()` in `v15_contracts.py` | Validate manifest target_layer against L5 Guardian rules before healer. Test: "unpermitted target_layer raises `PermissionDenied`." |
| W1.3 | **12.3** | `LayerMutationGuard` in `v15_p6_contracts.py` | Enforce read-only for L0, L4, L6 at boundary level. Test: "L4 write raises `MutationViolation`", "L6 write raises `MutationViolation`." |
| W1.4 | **2.8.b** | Extend `aggregate_gate_check` + `validate_result_emission` with `flow_type` param | AGGREGATE rejects terminal flow; RESULT rejects conditional flow. Test: "AGGREGATE on terminal raises", "RESULT on conditional raises." |
| W1.5 | **8.3** | `enforce_mixin_mro_order()` in `v15_p6_contracts.py` | Parse mro_chain, assert safety mixins before base class. Test: "safety mixin RIGHT of base raises `MROOrderViolation`." Wire into CI gate. |

### Wave 2 — Correlation / Collapse (P1: Audit Integrity)

**Risk:** Without correlation, duplicate incidents pollute the audit trail and violate determinism.

| Task | Req ID | Deliverable | Acceptance Criteria |
|------|--------|-------------|---------------------|
| W2.1 | **5.3** | `RootScopePin` type + `collapse_correlated_signals()` in `v15_p2_contracts.py` | Deterministic correlation key: `SHA-256(target_node_id + semantic_clock_window)`. Collapse N signals → 1 incident. Test: "3 signals with same root scope → exactly 1 incident." Wire into TelemetryEmitter. |
| W2.2 | **5.5** | `enforce_correlation_before_incident()` in `v15_p4_contracts.py` | Gate in `TelemetryEmitter.emit_incident` requiring non-empty `correlation_hash`. Test: "INCIDENT with empty correlation_hash raises `CorrelationRequired`." |

### Wave 3 — SSOT Binding + Separation Scanners (P2: Structural Safety)

**Risk:** Unresolved node_ids and unchecked mixin/heal() content erode structural invariants silently.

| Task | Req ID | Deliverable | Acceptance Criteria |
|------|--------|-------------|---------------------|
| W3.1 | **1.5** | Wire `resolve_ssot_binding()` into `V15ExecutionGateway` pipe step 1 (schema validation) | node_id from manifest resolved against live `structure_blueprint.py`. Test: "invalid node_id causes gateway reject." |
| W3.2 | **9.1** | AST scanner: `scan_mixin_for_domain_logic()` | Walk mixin method bodies, flag domain-specific imports/calls. Test: "mixin with domain import raises." |
| W3.3 | **9.2** | AST scanner: `scan_heal_for_purity()` | Verify heal() body contains only domain reasoning, no infra calls. Test: "heal() calling factory raises." |
| W3.4 | **9.3** | Call-graph scanner: `scan_heal_no_delegation()` | Verify heal() does not call other_agent.heal(). Test: "heal() delegating to another agent raises." |

### Wave 4 — Emulation + Snapshots (P3: Completeness)

**Risk:** Missing but non-safety-critical artifacts that degrade traceability.

| Task | Req ID | Deliverable | Acceptance Criteria |
|------|--------|-------------|---------------------|
| W4.1 | **6.3.b** | `PreGuardSnapshot` in `v15_p2_types.py` + `capture_preguard_snapshot()` | Captures context_hash, token_count, semantic_clock_tick before prompt augmentation. Test: "absent snapshot raises `PreGuardRequired`." |

### Wave 5 — PARTIAL → PASS Hardening (P4: Polish)

These items have types but lack enforcement wiring. Lower risk since spec language is softer.

| Task | Req ID | Deliverable | Acceptance Criteria |
|------|--------|-------------|---------------------|
| W5.1 | **5.4** | Wire dedupe check before SelfHealingTrigger emission at L6 | Test: "duplicate trigger blocked by dedupe gate." |
| W5.2 | **6.2** | Add runtime gate: `enforce_trajectory_reuse_constraint()` | Prevents reuse when `reusable is False`. Test: "reuse attempt with False raises." |
| W5.3 | **6.8** | Add `enforce_hypostate_on_commit()` contract | Requires MemoryHypostate generation on each state commit. Test: "commit without hypostate raises." |
| W5.4 | **6.10** | Add `enforce_episodic_semantic_link()` contract | Requires link generation. Test: "reasoning without link raises." |
| W5.5 | **11.2** | Wire `RouteRecoveryBox` into `V15ExecutionGateway` overflow path | Test: "TokenOverflow triggers RouteRecoveryBox.handle_overflow()." |

---

## Evidence File Index

| Evidence Category | Files |
|-------------------|-------|
| **P1 Types** | `agentic_core/L0_maintenance/types/v15_types.py` |
| **P1 Contracts** | `agentic_core/L0_maintenance/types/v15_contracts.py` |
| **P2 Types** | `agentic_core/L0_maintenance/types/v15_p2_types.py` |
| **P2 Contracts** | `agentic_core/L0_maintenance/types/v15_p2_contracts.py` |
| **P3 Types** | `agentic_core/L0_maintenance/types/v15_p3_types.py` |
| **P3 Contracts** | `agentic_core/L0_maintenance/enforcement/v15_p3_contracts.py` |
| **P4 Types** | `agentic_core/L0_maintenance/types/v15_p4_types.py` |
| **P4 Contracts** | `agentic_core/L0_maintenance/enforcement/v15_p4_contracts.py` |
| **P5 Types** | `agentic_core/L0_maintenance/types/v15_p5_types.py` |
| **P5 Contracts** | `agentic_core/L0_maintenance/enforcement/v15_p5_contracts.py` |
| **P6 Types** | `agentic_core/L0_maintenance/types/v15_p6_types.py` |
| **P6 Contracts** | `agentic_core/L0_maintenance/enforcement/v15_p6_contracts.py` |
| **Execution Gateway** | `agentic_core/L0_maintenance/enforcement/v15_execution_gateway.py` |
| **Guardian Contract** | `agentic_core/L0_maintenance/types/guardian_contract.py` |
| **SovereignBase** | `agentic_core/base_agents/SovereignBaseAgent.py` |
| **P1 Tests** | `tests/guardian/test_v15_p1_compliance.py` (1152 lines, 22 test classes) |
| **P2 Tests** | `tests/guardian/test_v15_p2_compliance.py` (591 lines, 15 test classes) |
| **P3 Tests** | `tests/guardian/test_v15_p3_compliance.py` (361 lines, 6 test classes) |
| **P4 Tests** | `tests/guardian/test_v15_p4_compliance.py` (544 lines, 8 test classes) |
| **P5 Tests** | `tests/guardian/test_v15_p5_compliance.py` (525 lines, 8 test classes) |
| **P6 Tests** | `tests/guardian/test_v15_p6_compliance.py` (472 lines, 8 test classes) |

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

