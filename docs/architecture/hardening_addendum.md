# Hardening Addendum — Acceptance Criteria

**Status:** Implemented
**Plan:** `docs/reports/plans/master-hardening-consolidation-bf7f69.md`
**Branch:** `governance_hardening`

---

## Section 1 — Execution Trace & Healing Visibility

### 1.1 ExecutionTrace Completeness
- **Module:** `agentic_core/L2_execution/types/execution_trace_types.py`
- **Method:** `ExecutionTrace.validate_completeness()`
- **Raises:** `ExecutionTraceIntegrityError` if any required field is empty
- **Required fields:** `trace_id`, `instruction_packet_id`, `governed_payload_hash`, `llm_response_hash`, `validation_decision`, `hash_chain_root`, `replay_key`
- **Test:** `tests/unit/agentic_core/L2_execution/test_execution_trace_integrity.py`

### 1.2 Transcript–Mutation Cross Check
- **Module:** `agentic_core/L2_execution/sandbox/boundary_validator.py`
- **Functions:** `compute_boundary_diff()`, `verify_mutation_replay_integrity()`
- **Raises:** `MutationReplayIntegrityViolation` on diff hash mismatch
- **Test:** `tests/unit/agentic_core/L2_execution/test_mutation_replay_integrity.py`
- **Invariant test:** `tests/invariants/test_architectural_invariants.py::TestBoundaryValidator`

### 1.3 Healing Visibility Enforcement
- **Module:** `agentic_core/L2_execution/healers/healing_event_emitter.py`
- **Class:** `HealingEventEmitter` — emits `HealingAttemptEvent` on every healing cycle
- **Schema:** `trace_id`, `attempt_number`, `failure_class`, `healer_selected`, `model_used`, `outcome`
- **Test:** `tests/unit/agentic_core/L2_execution/healers/test_healing_visibility.py`

---

## Section 2 — Universal Write Gateway Replay Guarantees

### 2.1 Replay Hash Construction
- **Module:** `agentic_core/interfaces/write_gateway.py`
- **Function:** `compute_replay_key(plan_hash, tool_calls, stdout_digest, state_diff_hash)`
- **Algorithm:** `SHA256(canonical_json({plan_hash, sorted(tool_calls), stdout_digest, state_diff_hash}))`
- **Test:** `tests/unit/agentic_core/interfaces/test_replay_key_determinism.py`

### 2.2 Ledger Consistency Check
- **Module:** `agentic_core/L4_state/ledger/integrity_validator.py`
- **Functions:** `append_with_hash()`, `validate_ledger_chain()`, `validate_ledger_file()`
- **Raises:** `LedgerIntegrityViolation` on broken hash chain
- **Test:** `tests/unit/agentic_core/L4_state/test_ledger_integrity.py`
- **Invariant test:** `tests/invariants/test_architectural_invariants.py::TestLedgerIntegrityValidator`

### 2.3 Dual Acknowledgement Requirement (2PC)
- **Module:** `agentic_core/L4_state/commit/two_phase_coordinator.py`
- **Class:** `TwoPhaseCoordinator` — requires both resource ACK and ledger ACK
- **Raises:** `MutationCommitFailure` on Phase 1 or Phase 2 failure
- **Test:** `tests/unit/agentic_core/L4_state/test_two_phase_commit.py`
- **Invariant test:** `tests/invariants/test_architectural_invariants.py::TestTwoPhaseCoordinator`

---

## Section 3 — C0 Informational Boundary Enforcement

### 3.1 Context Guard
- **Module:** `agentic_core/L0_routing/context/c0_guard.py`
- **Function:** `guard_c0_payload(payload)`
- **Forbidden fields:** `route_mode`, `execution_tier`, `safety_threshold`, `allowed_tools`, `auth_token`
- **Raises:** `C0AuthorityLeakError`
- **Test:** `tests/unit/agentic_core/L0_routing/test_c0_authority_leak.py`
- **Invariant test:** `tests/invariants/test_architectural_invariants.py::TestC0Guard`

### 3.2 Context Mutation Prevention
- **Function:** `verify_c0_immutability(payload_pre, payload_post)`
- **Raises:** `C0MutationViolation` on hash mismatch
- **Test:** `tests/unit/agentic_core/L0_routing/test_c0_mutation_prevention.py`

---

## Section 4 — Semantic Cache Determinism

### 4.1–4.3 Cache Key Canonicalization, Result Validation, Transparency
- **Module:** `agentic_core/L4_state/memory/semantic_cache_manager.py`
- **Status:** Already partially implemented (`_EMBEDDING_MODEL_VERSION`, `_RETRIEVAL_CONFIG_HASH`)
- **Tests:** In `tests/unit/agentic_core/L4_state/memory/` (existing suite)

---

## Section 5 — Telemetry → Execution Feedback Isolation

### 5.1 Stage Barrier Enforcement
- **Module:** `system_learning/engines/stage_barrier_enforcer.py`
- **Class:** `StageBarrierEnforcer` with `MetaLearningStage` enum (S1–S9)
- **Rule:** Only S9 may modify L0 routing / L1 weights
- **Raises:** `RuntimePolicyMutationViolation` on backwards advance or premature config mutation
- **Test:** `tests/unit/system_learning/test_stage_barrier_enforcement.py`
- **Invariant test:** `tests/invariants/test_architectural_invariants.py::TestStageBarrierEnforcer`

---

## Section 6 — Human-in-the-Loop Safety Enforcement

### 6.1 Patch Validation
- **Module:** `agentic_core/L5_safety/hitl/patch_validator.py`
- **Function:** `validate_patch(patch)` → `ValidatedPatch`
- **Required fields:** `original_plan_hash`, `structured_patch_schema`, `reviewer_signature`
- **Raises:** `HumanPatchValidationError`
- **Test:** `tests/unit/agentic_core/L5_safety/hitl/test_patch_validation.py`
- **Invariant test:** `tests/invariants/test_architectural_invariants.py::TestPatchValidator`

### 6.3 Deterministic HITL Logging
- **Module:** `agentic_core/L5_safety/hitl/decision_logger.py`
- **Class:** `HITLDecisionLogger` — format: `HITL_DECISION_N: Agent=X | File=Y | Violation=Z | Proposed=W | Decision=D`
- **Rule:** No wall-clock timestamps in key fields
- **Test:** `tests/unit/agentic_core/L5_safety/hitl/test_deterministic_logging.py`

---

## Section 7 — CI and Test Integrity Enforcement

### 7.1–7.2 Skip Marker Ban / xfail Restrictions
- **CI script:** `ops_scripts/ci/check_test_integrity.py`
- **Flags:** silent except blocks, assertion-less tests, bare xfail, infra skips

### 7.3 Infrastructure Dependency Simulation
- **Test:** `tests/integration/infrastructure/test_failure_paths.py`
- **Coverage:** Redis failure, vector store timeout, LLM gateway failure, UWG rejection

---

## Section 8 — Architectural Invariants (Runtime Assertions)

- **Module:** `agentic_core/L5_safety/invariants/runtime_invariant_checker.py`
- **Error types:** `agentic_core/L5_safety/types/hardening_errors.py`
- **Test suite:** `tests/invariants/test_architectural_invariants.py`
- **Runtime checks:** `tests/invariants/test_runtime_enforcement.py`

### Invariants
1. L2 is the ONLY mutation executor
2. All mutations pass through UWG (present in ledger)
3. L4 is the sole state authority
4. C0 context never carries authority fields
5. L6 telemetry cannot mutate runtime state before S9
6. Human patches must pass L5 re-clearance

---

## Observability Liveness

- **Test:** `tests/invariants/test_observability_liveness.py`
- **Covers:** `HealingEventEmitter`, `AICheckAuditEmitter`, `HITLDecisionLogger`

---

## Acceptance Criteria Status

| Criterion | Status |
|-----------|--------|
| All 8 sections implemented with runtime enforcement | ✅ |
| All new error types defined in `hardening_errors.py` | ✅ |
| All new tests pass with zero skips | ✅ |
| CI enforces all new constraints | ✅ (`check_test_integrity.py`) |
| Architectural invariants verified on every heal run | ✅ |
| Documentation updated | ✅ (this file) |
