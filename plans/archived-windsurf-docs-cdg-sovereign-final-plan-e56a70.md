---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\cdg-sovereign-final-plan-e56a70.md'
original_relative_path: 'cdg-sovereign-final-plan-e56a70.md'
source_sha256: b58e5a4c1ae395ab2e472e0604d1325644062aba7343a0933fbcc971329a7193
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Critical Dissemination Guarantees — Full Sovereignty Implementation Plan

This plan remediates all 25 Critical Dissemination Guarantees to sovereign-grade enforcement, incorporating three rounds of audit findings to close every known bypass vector and achieve provable replay determinism.

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


## Sovereignty Violation Blocking Conditions (Policy, Not Documentation)

A phase is **FAIL** regardless of digest stability if ANY of these are true:
- Upward mutation across layers is possible
- Gateway bypass path exists (direct SDK import, subprocess, HTTP outside gateway)
- Embedding result influences routing/thresholds/safety
- Kill-switch (`EMBEDDING_ENABLED=false`) can be bypassed
- Negative control returns non-exit-0
- Multiple competing digests are emitted in a single run
- Replay mode allows un-transcripted nondeterminism

---

## Sovereignty Boundary Map

All guarantees must anchor to exactly one choke point:

| Choke Point | Authority |
|---|---|
| L0 Routing | Intent classification, trace assignment |
| L5 Safety | Validation, certification, re-clear |
| L2 UWG | Single mutation authority, tool allowlist |
| MetaLearning Stage 9 Commit Gate | Proposal activation |
| EmbeddingServiceFactory | Embedding governance, kill-switch |
| `digest_authority.py` | Single determinism emission point |

---

## Gap Classification

### ✅ Sovereign (5 — no change needed)
#16 No over-escalation · #17 Escalation signal determinism · #18 Single choke point · #20 Provider injectability · #24 Embedding startup integrity

### ⚠️ Needs Sovereign Hardening (8)
#1 Safety gates · #2 Safety fences · #4 Healed plan re-clear · #7 Tool allowlist · #10 Loop prevention · #14 Shared memory · #15 Ghost mutations · #19 Bounded re-entrancy

### ❌ Needs Sovereign Implementation (12)
#3 JIT context loading · #5 Error context preservation · #6 Sandbox isolation · #8 Task decomposition · #9 Knowledge protection · #11 Fresh data · #12 Replay key · #13 Injection neutralization · #21 Embedding C0-only · #22 Meta-learning proposal-only · #23 DPO bounding · #25 Negative control

---

## Phase 1 — Sovereign Safety Hardening
**Guarantees**: #1, #2, #4, #7
**Duration**: 

### Wave 1.1 — Single Determinism Authority Module
**NEW**: `agentic_core/determinism/digest_authority.py`
- Only module that computes canonical JSON (sorted keys, UTF-8, zero whitespace)
- Float rounding: 6 decimal places exactly
- Timestamps excluded unless captured in transcript
- Emits `W<n>-DETERMINISM-DIGEST: <sha256>` exactly once per run
- Second emission attempt raises `DuplicateDigestViolation`
- Input: `trace_id + plan_hash + policy_hash + transcript_hash + config_surface_hash`

### Wave 1.2 — L5 Hard Fence Binding (#1, #2)
**NEW**: `agentic_core/L5_safety/enforcement/sovereign_fence_validator_enforcer.py`
- L5 P1 `VALIDATE Proposal vs Policy` must call `validate()` — hard import, not optional
- Fence violation blocks before STAMP, emits deterministic reason code
- Raises `SovereignFenceViolation` (typed, no permissive mode)
- Digest contribution: fence_validation_result

### Wave 1.3 — Cryptographic Signature Invalidation (#4)
**NEW**: `agentic_core/L2_execution/healers/signature_invalidator.py`
- L2.3 healing strips previous signature, regenerates `policy_hash`
- Old signature reuse raises `StaleSignatureViolation`
- Forces full L5 re-clear loop before execution
- Digest contribution: new_policy_hash

### Wave 1.4 — UWG Tool Allowlist Enforcement (#7)
**MODIFY**: `agentic_core/L2_execution/UniversalWriteGateway.py`
- UWG validates `tool_name in allowed_tools[]` from InstructionPacket at entry
- Non-allowlist tool → immediate sandbox termination + audit emission + no partial writes
- Not a registry check — enforced inside UWG itself
- Digest contribution: tool_validation_transcript

### Wave 1.5 — Gateway Bypass Scanner — AST-Based (#1 CI)
**NEW**: `ops_scripts/ci/gateway_bypass_scanner.py`
- AST-based scan (no regex): direct provider SDK imports, model string literals, embedding instantiation
- Disallows `subprocess`, `requests`, `httpx` outside gateway namespace
- Detects dynamic imports and indirect wrapper modules
- Violation → CI fail with file:line reference

---

## Phase 2 — Deterministic Resource & Context Management
**Guarantees**: #3, #5, #6, #10, #11
**Duration**: 

### Wave 2.1 — Deterministic Context Window Optimization (#3)
**NEW**: `agentic_core/L1_cognition/engines/deterministic_context_optimizer.py`
- No dynamic sampling; top-K capped and logged
- Deterministic ordering: sort by `(score_round6 DESC, content_hash ASC)` — stable tie-break
- Emits `context_hash_before` + `context_hash_after`; replay must reproduce same slice
- Includes seed_pack_hash in determinism digest

### Wave 2.2 — L4 Error Context Preservation (#5)
**NEW**: `agentic_core/L4_state/engines/error_context_preserver.py`
- L4 stores `content_hash` with `prev_hash` chaining (genesis anchor)
- Silent overwrite disallowed; all mutations versioned
- Compaction snapshots signed with checkpoint hash — no chain discontinuity
- Emits ExecutionTrace envelope for all context changes

### Wave 2.3 — UWG Sandbox Isolation with Replay Enforcement (#6)
**NEW**: `agentic_core/L2_execution/enforcement/sovereign_sandbox_isolation.py`
- No FS writes outside UWG; no network calls outside transcript
- `replay_mode` injected via SandboxEnvelope, enforced at UWG + network boundary + randomness + time
- Time and random sources replaced with deterministic stubs in replay mode
- Replay violations raise `ReplayNondeterminismViolation`

### Wave 2.4 — Deterministic Circuit-Break Proof (#10)
**NEW**: `agentic_core/L2_execution/enforcement/deterministic_loop_detector.py`
- Attaches to L2 PTC Execution; increments deterministic counter
- Only `TOOL_BUDGET_EXCEEDED` termination — no heuristic kills
- Digest contribution: loop_counter + termination_reason

### Wave 2.5 — Fresh Data Timestamp Validation (#11)
**NEW**: `agentic_core/L4_state/engines/fresh_data_validator.py`
- Configurable freshness windows from config surface hash
- Stale data raises `StaleDataViolation` before serving
- Freshness window values included in config surface hash (replay binding)

---

## Phase 3 — Knowledge Integrity & Memory Protection
**Guarantees**: #8, #9, #12, #13, #14, #15
**Duration**: 

### Wave 3.1 — Bounded Task Decomposition (#8)
**NEW**: `agentic_core/L3_orchestration/engines/bounded_task_decomposer.py`
- L3 enforces task size limits and blast radius caps before dispatch
- Tasks exceeding limits rejected with `TaskBlastRadiusViolation`
- Digest contribution: decomposition_decisions

### Wave 3.2 — Knowledge Hash Chaining with Compaction Support (#9)
**NEW**: `agentic_core/L4_state/enforcement/knowledge_integrity_guard.py`
- Requires `content_hash` + `prev_hash` for all L4 mutations
- Genesis hash anchors chain; compaction creates signed checkpoint snapshot
- Chain discontinuity raises `KnowledgeIntegrityViolation`
- Pruned nodes handled via checkpoint — no integrity loss

### Wave 3.3 — L6 Replay Key Computation with L4 Storage (#12)
**NEW**: `agentic_core/L6_observability/engines/replay_key_computer.py`
- Computed in L6, stored in L4; includes: tier selection, retry_count, thresholds (X=0.75, Y=0.40), embedding_pack_hash, embedding_model_version, ToolBudget caps, all threshold configs, config surface hash
- Any input change → replay key changes
- Digest contribution: replay_key itself

### Wave 3.4 — Assembly Stage Injection Neutralization (#13)
**NEW**: `agentic_core/prompt_governance/security/assembly_injection_neutralizer.py`
- Executes in Assembly Stage BEFORE payload finalization
- Explicit pattern detection list (AST-based, no regex)
- Canonical sanitized reconstruction; logs `injection_detected=True|False`
- Digest contribution: injection_detection_result

### Wave 3.5 — Memory Collision Detection with Deadlock Ordering (#14)
**NEW**: `agentic_core/L4_state/engines/memory_collision_detector.py`
- Global lock acquisition order defined (deterministic hierarchy)
- Deadlock resolution: timeout policy + `MemoryDeadlockViolation`
- No livelock: bounded resolution within N cycles
- Digest contribution: collision_resolution_decisions

### Wave 3.6 — Ghost Mutation Detection (#15)
**NEW**: `agentic_core/L4_state/engines/ghost_mutation_detector.py`
- State reconciliation across layers detects hidden mutations
- Anomaly reporting with `GhostMutationViolation`
- Digest contribution: reconciliation_results

---

## Phase 4 — Sovereign Meta-Learning & Embedding Governance
**Guarantees**: #19, #21, #22, #23, #24, #25
**Duration**: 

### Wave 4.1 — Monotonic Re-Entrancy with L4 Persistence (#19)
**NEW**: `agentic_core/L2_execution/healers/monotonic_reentrancy_enforcer.py`
- `retry_count` persisted in L4 (survives restart); part of replay digest
- `assert new_retry_count == old_retry_count + 1` enforced in `_tier_escalate()`
- Immutable once incremented; multi-node coordination via L4 persistence
- `_tier_escalate()` has zero writes, zero recursion, zero state mutation

### Wave 4.2 — C0-Only Embedding with Indirect Leakage Prevention (#21)
**NEW**: `agentic_core/L4_state/enforcement/embedding_sovereignty_guard.py`
- `EmbeddingResult` cannot be passed to `route_healing_tier()`, L0 threshold tuner, or L5 safety classifier — enforced by static typing barrier
- L0 threshold tuner explicitly rejects `embedding_metadata` fields
- Replay key includes `embedding_pack_hash` + `embedding_model_version`
- CI scanner extended: embedding artifact influencing routing → CI fail

### Wave 4.3 — Dual-Injection Proposal-Only Gate (#22)
**NEW**: `system_learning/enforcement/dual_injection_proposal_gate.py`
- `if not (version_store and approval_gate): proposal_only = True` — cannot be overridden by caller
- Activation requires: dual injection + `ApprovalGate.decide()` + L5 re-clear
- Digest contribution: gate_decision

### Wave 4.4 — Bounded DPO Feedback (#23)
**MODIFY**: `agentic_core/L6_observability/engines/dpo_pair_generator.py`
- Clamp to `[0.1, 2.0]`; Δ ≤ ±0.1 per decision
- Deterministic sort by `(control_hash, candidate_hash)` — replay mismatch → fail
- Digest contribution: dpo_adjustment_decisions

### Wave 4.5 — Kill-Switch Hardening (#24)
**MODIFY**: `system_learning/engines/embedding_service_factory.py`
- Refuses instantiation if: ENV var missing OR integrity mismatch OR replay mode active and pack hash differs
- `EMBEDDING_ENABLED=false`: no memmap, no telemetry, returns disabled stub, replay deterministic
- Kill-switch overrides any config injection

### Wave 4.6 — Exit-0 Negative Control (#25)
**NEW**: `tests/governance/test_negative_control_exit0_tamper.py`
- Tamper via `W<n>_NEGCTRL_TAMPER=1` → `pytest.mark.xfail(strict=True)` → exit code 0
- Restore run must PASS
- Non-exit-0 tamper result is a sovereignty violation

---

## Phase 5 — Sovereign Integration & Validation
**Duration**: 

### Wave 5.1 — Execution Transcript Freezing
**NEW**: `agentic_core/L2_execution/enforcement/transcript_freezer.py`
- Freezes transcript before digest computation
- Prohibits further mutation after freeze
- Seals with final hash; late writes raise `TranscriptMutationViolation`

### Wave 5.2 — Layer Sovereignty Guard
**NEW**: `tests/governance/test_layer_sovereignty_guard.py`
- AST-based: L6 cannot mutate L2, L2 cannot mutate L5, L4 never executes
- Upward mutation detection via import graph analysis

### Wave 5.3 — Config Surface Hashing
**MODIFY**: `agentic_core/L0_routing/scripts/execution_context.py`
- Replay key includes: all threshold configs, X=0.75, Y=0.40, ToolBudget caps, freshness windows
- Silent config drift breaks determinism — config hash is mandatory replay input

### Wave 5.4 — Two-Run Digest Stability Proof
**NEW**: `tests/governance/test_two_run_digest_stability.py`
- Proves `W<n>-DETERMINISM-DIGEST` identical across independent runs
- Any digest difference → fail

### Wave 5.5 — Sovereignty Violation Matrix (Documentation)
**NEW**: `docs/governance/sovereignty_violation_matrix.md`
- Maps each of 25 guarantees to: enforcement boundary, failure mode, deterministic artifact, CI coverage, replay binding surface

---

## Complete File Manifest

### New Files (32)
```
agentic_core/determinism/digest_authority.py
agentic_core/L1_cognition/engines/deterministic_context_optimizer.py
agentic_core/L2_execution/enforcement/deterministic_loop_detector.py
agentic_core/L2_execution/enforcement/sovereign_sandbox_isolation.py
agentic_core/L2_execution/enforcement/transcript_freezer.py
agentic_core/L2_execution/healers/monotonic_reentrancy_enforcer.py
agentic_core/L2_execution/healers/signature_invalidator.py
agentic_core/L3_orchestration/engines/bounded_task_decomposer.py
agentic_core/L4_state/enforcement/embedding_sovereignty_guard.py
agentic_core/L4_state/enforcement/knowledge_integrity_guard.py
agentic_core/L4_state/engines/error_context_preserver.py
agentic_core/L4_state/engines/fresh_data_validator.py
agentic_core/L4_state/engines/ghost_mutation_detector.py
agentic_core/L4_state/engines/memory_collision_detector.py
agentic_core/L5_safety/enforcement/sovereign_fence_validator_enforcer.py
agentic_core/L6_observability/engines/replay_key_computer.py
agentic_core/prompt_governance/security/assembly_injection_neutralizer.py
system_learning/enforcement/dual_injection_proposal_gate.py
system_learning/engines/enhanced_embedding_integrity.py
ops_scripts/ci/gateway_bypass_scanner.py
tests/governance/test_negative_control_exit0_tamper.py
tests/governance/test_layer_sovereignty_guard.py
tests/governance/test_two_run_digest_stability.py
docs/governance/sovereignty_violation_matrix.md
```

### Modified Files (8)
```
agentic_core/L2_execution/UniversalWriteGateway.py          (UWG tool allowlist)
agentic_core/L2_execution/healers/healing_tier_router.py    (monotonic enforcement)
agentic_core/L2_execution/determinism.py                    (delegate to digest_authority)
agentic_core/L6_observability/engines/dpo_pair_generator.py (DPO bounding)
agentic_core/L0_routing/scripts/execution_context.py        (config surface hash)
system_learning/pipelines/meta_learning_pipeline.py         (dual injection)
system_learning/engines/embedding_service_factory.py        (kill-switch hardening)
agentic_core/L5_safety/enforcement/activation_gate.py       (hard binding)
```

---

## Compliance Readiness Checklist

Before declaring 100% sovereign compliance:
- [ ] All 25 guarantees mapped in sovereignty_violation_matrix.md
- [ ] `W<n>-DETERMINISM-DIGEST` printed exactly once per run (DuplicateDigestViolation enforced)
- [ ] Two-run digest stability test passing
- [ ] Negative control exit-0 verified
- [ ] Gateway bypass scanner active — zero violations in CI
- [ ] Layer sovereignty guard passing
- [ ] Replay mode blocks all nondeterminism (time, random, network)
- [ ] Transcript frozen before digest computation
- [ ] Config surface hash in every replay key
- [ ] `retry_count` persisted in L4 and immutable post-increment
- [ ] Embedding result statically blocked from routing path
- [ ] Dual-injection gate cannot be overridden by caller
- [ ] Knowledge hash chain anchored to genesis with compaction snapshots
- [ ] Deadlock ordering rules defined and enforced

---

## Timeline

| Phase | Focus | Duration |
|---|---|---|
| 1 | Sovereign Safety Hardening |  |
| 2 | Deterministic Resource & Context |  |
| 3 | Knowledge Integrity & Memory |  |
| 4 | Meta-Learning & Embedding |  |
| 5 | Integration & Validation |  |
| **Total** | | **** |

---

## Risk Assessment

| Area | Status |
|---|---|
| Choke-point binding | Sovereign |
| Fail-closed design | Sovereign |
| Deterministic tiering | Sovereign |
| Embedding governance | Sovereign (indirect leakage closed) |
| Replay enforcement | Sovereign (boundary-sealed) |
| Meta-learning containment | Sovereign |
| Gateway bypass protection | Sovereign (AST-based, dynamic imports covered) |
| Layer sovereignty | Sovereign (restart/distributed handled via L4) |
| Determinism canonicalization | Sovereign (single authority module) |
| Hash chain integrity | Sovereign (compaction snapshots) |

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

