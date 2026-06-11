---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\sovereignty-complete-prompt-taxonomy-implementation-edfc91.md'
original_relative_path: 'sovereignty-complete-prompt-taxonomy-implementation-edfc91.md'
source_sha256: 075ffc772544661be87f27b1307919a3a7a1fd12e335c518ead47655427ae7c2
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Sovereignty-Complete Prompt Taxonomy Implementation Plan

This plan merges the Zero-Loss Prompt Taxonomy gaps with cryptographic sovereignty hardening requirements to achieve a truly mathematically-sealed governance architecture.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Executive Summary

The original prompt taxonomy implementation plan identified critical gaps but lacked cryptographic boundary enforcement, determinism invariants, and sovereignty-hardened execution guarantees. This merged plan incorporates hardening requirements to achieve Zero-Loss compliance through cryptographic contracts, replay-verified determinism, and capability-bound execution tokens.

## Critical Integration Requirements

### Phase 0: Sovereignty Preconditions (Week 0)

**Priority: CRITICAL - Must precede all other phases**

#### 0.1 Cryptographic Boundary Enforcement
**Files to Create/Modify:**
- `agentic_core/L2_execution/types/instruction_packet_types.py` - ENHANCE
- `agentic_core/L2_execution/types/sandbox_envelope_types.py` - ENHANCE
- `agentic_core/L2_execution/enforcement/boundary_validator.py` - NEW
- `tests/governance/test_cryptographic_boundaries.py` - NEW

**Hardened Requirements:**
- Every L0→L2 transfer MUST canonicalize JSON (alphabetical keys, UTF-8, no whitespace variance)
- HMAC-SHA256 sign InstructionPacket at L0, validate at L2 entry
- Fail-closed on signature mismatch
- Bind trace_id + policy_hash immutably in packet metadata

#### 0.2 Embedding Integrity Sovereignty
**Files to Create/Modify:**
- `agentic_core/L2_execution/embeddings/embedding_service_factory.py` - NEW
- `agentic_core/L2_execution/embeddings/integrity_validator.py` - NEW
- `data/embeddings/matrix_manifest.yaml` - NEW
- `tests/governance/test_embedding_integrity.py` - NEW

**Hardened Requirements:**
- Enforce SINGLETON EmbeddingServiceFactory
- Verify sha256(embeddings.f32) == manifest.matrix_hash at startup
- Lock BLAS determinism
- Enforce max_k <= 20, cutoff >= 0.5
- System boot abort on integrity mismatch

#### 0.3 Replay-Verified Determinism Engine
**Files to Create/Modify:**
- `agentic_core/L2_execution/determinism/replay_engine.py` - NEW
- `agentic_core/L2_execution/determinism/digest_calculator.py` - NEW
- `agentic_core/L2_execution/determinism/nondeterminism_guard.py` - NEW
- `tests/governance/test_replay_determinism.py` - NEW

**Critical Fixes Required:**
- Remove timestamp and run_id from digest calculation
- Digest must include only: sorted artifact hash + artifact count + structural config hashes
- Print deterministic digest once per run
- Two identical runs required before PASS

### Phase 1: L5 Safety & Airlock Cryptographic Hardening (Weeks 1-2)

#### 1.1 L5 Safety Integration with Compliance Stamping
**Files to Create/Modify:**
- `agentic_core/L5_safety/core/safety_evaluator.py` - NEW
- `agentic_core/L5_safety/core/compliance_stamper.py` - NEW
- `agentic_core/L5_safety/adapters/llamaguard_adapter.py` - NEW
- `agentic_core/L0_routing/seams/elevator_shaft_seam.py` - MODIFY

**Enhanced Requirements:**
- Deterministic risk tier mapping: `risk_tier = deterministic_map(intent_signature, policy_hash)`
- L5 emits: compliance_hash, policy_version, certified_timestamp, signed_safety_stamp
- Assembly MUST reject payloads without L5 stamp
- All modify_diff plans MUST re-clear L5

#### 1.2 Airlock Integrity with Cryptographic Handshake
**Files to Create/Modify:**
- `agentic_core/L0_routing/core/airlock_validator.py` - NEW
- `agentic_core/L0_routing/core/trace_binder.py` - NEW
- `agentic_core/L0_routing/core/cryptographic_handshake.py` - NEW
- `agentic_core/L0_routing/engines/path_router.py` - MODIFY

**Enhanced Requirements:**
- Cryptographic handshake preventing U0 bypass attempts
- Trace ID binding with immutable policy hashes
- State locking for race condition prevention
- InstructionPacket fields are read-only beyond L0

### Phase 2: L2 Execution Pipeline with Capability Tokens (Weeks 3-4)

#### 2.1 L2 Validator with Replay Guard
**Files to Create/Modify:**
- `agentic_core/L2_execution/validator/preflight_validator.py` - NEW
- `agentic_core/L2_execution/validator/replay_guard.py` - NEW
- `agentic_core/L2_execution/validator/contract_checker.py` - NEW
- `agentic_core/L2_execution/types/capability_token_types.py` - ENHANCE

**Enhanced Requirements:**
- ReplayGuard monkeypatches network stack and datetime/random
- Fail if nondeterministic source invoked outside transcript
- Pre-flight simulation with InstructionPacket signature validation
- Boundary snapshot generation for healing rollback

#### 2.2 L2 Executor with Capability-Bound Tokens
**Files to Create/Modify:**
- `agentic_core/L2_execution/executor/singular_mutation_point.py` - NEW
- `agentic_core/L2_execution/executor/capability_enforcer.py` - NEW
- `agentic_core/L2_execution/healer/rollback_engine.py` - NEW
- `agentic_core/L2_execution/core/execution_orchestrator.py` - NEW

**Enhanced Requirements:**
- Capability tokens bound to execution trace + policy hash + determinism digest
- Environment-injected authority secret (not hardcoded)
- Token signature includes: execution trace ID, policy version hash, determinism artifact hash
- Singular mutation point for all durable writes

### Phase 3: Comprehensive Prompt Type Coverage (Weeks 5-6)

#### 3.1 System & Instructional Prompts with Constitution Enforcement
**Files to Create/Modify:**
- `agentic_core/prompt_governance/types/system_prompts.py` - NEW
- `agentic_core/prompt_governance/types/instructional_prompts.py` - NEW
- `agentic_core/prompt_governance/core/constitution_enforcer.py` - NEW
- `data/prompt_governance/system/constitutions.yaml` - NEW

**Enhanced Requirements:**
- System prompt loading with cryptographic constitution validation
- Instructional prompts with capability-bound injection
- Mixin hydrator with signature verification
- All prompt libraries signed with repository keys

#### 3.2 Dependency & Context Prompts with JIT Validation
**Files to Create/Modify:**
- `agentic_core/prompt_governance/types/dependency_prompts.py` - NEW
- `agentic_core/prompt_governance/core/context_loader.py` - NEW
- `agentic_core/prompt_governance/core/citation_validator.py` - NEW
- `agentic_core/L0_routing/seams/elevator_shaft_seam.py` - ENHANCE

**Enhanced Requirements:**
- C0 informational-only invariant enforced
- JIT context loading with cryptographic metadata validation
- Citation validator with integrity verification
- Embedding retrieval never influences routing or risk tier

### Phase 4: Advanced Governance with Meta-Learning Containment (Weeks 7-8)

#### 4.1 Policy Enforcement with CI Fail-Closed Scanning
**Files to Create/Modify:**
- `agentic_core/L5_safety/core/policy_enforcer.py` - NEW
- `agentic_core/L5_safety/core/compliance_checker.py` - NEW
- `.github/workflows/sovereignty-hardening.yml` - ENHANCE
- `ops_scripts/ci/ast_scanner.py` - NEW

**CI Enforcement Requirements:**
- Fail build on provider SDK import outside gateway
- Fail build on model literal outside registry
- Fail build on embedding instantiation outside factory
- Fail build on unsigned InstructionPacket ingress

#### 4.2 Meta-Learning with Proposal-Only Default
**Files to Create/Modify:**
- `system_learning/pipelines/meta_learning_pipeline.py` - ENHANCE
- `system_learning/enforcement/dual_injection_proposal_gate.py` - ENHANCE
- `system_learning/enforcement/oscillation_detector.py` - NEW
- `system_learning/enforcement/cooldown_enforcer.py` - NEW

**Containment Requirements:**
- proposal_only=True hard default (no shortcut activation)
- Activation requires: version_store injected + approval_gate injected
- Minimum sample size before threshold shift
- Oscillation detection with auto-reject
- DPO clamped deltas

## Cryptographic Contract Specifications

### BOUNDARY INVARIANT
```
Every L0→L2 transfer MUST:
1. Canonicalize JSON (alphabetical key order, UTF-8, no whitespace variance)
2. HMAC-SHA256 sign InstructionPacket
3. Validate signature at L2 entry
4. Fail-closed on mismatch
```

### DETERMINISM INVARIANT
```
W<n>-DETERMINISM-DIGEST:
sha256(
    policy_hash +
    registry_hash +
    config_surface_hash +
    transcript_hash
)
Printed once per run.
Two identical runs required before PASS.
```

### CAPABILITY TOKEN INVARIANT
```
Token signature must include:
- execution trace ID
- policy version hash
- determinism artifact hash
Authority secret must be:
- environment-injected
- rotation-capable
- hashed into determinism artifact
- fail-closed if absent
```

## Escalation Governance Hardening

### Choke Point Enforcement
```
if check_id not in HEALER_ESCALATION_ALLOWLIST:
    emit FailureSignal
    DO NOT escalate

EscalationContext.from_result() is deterministic
FailureSignal built only from EscalationContext
Only route_healing_tier() selects model
```

### Blast Radius Limiter
```
ToolBudget constraints:
- Max tool calls per execution
- Max parallel branches
- Rate limit enforcement per trace
- Budget exhaustion auto-terminate
```

## Testing Strategy

### Cryptographic Tests
- InstructionPacket signature validation
- SandboxEnvelope boundary enforcement
- Capability token binding and verification
- Deterministic digest calculation

### Sovereignty Tests
- Airlock integrity with cryptographic handshake
- Embedding integrity verification at startup
- Replay strictness with nondeterminism guard
- CI fail-closed scanning enforcement

### Meta-Learning Containment Tests
- Proposal-only default enforcement
- Dual injection requirement validation
- Oscillation detection and auto-reject
- Cooldown window enforcement

## Success Metrics

### Cryptographic Metrics
- 100% signature verification on all L2 ingress
- 0% unsigned packet acceptance
- Complete deterministic digest consistency
- Full capability token binding coverage

### Sovereignty Metrics
- 100% airlock integrity enforcement
- Complete embedding integrity verification
- Full replay strictness compliance
- All CI sovereignty scans passing

### Governance Metrics
- 100% policy enforcement compliance
- Complete meta-learning containment
- Full escalation choke point enforcement
- Zero bypass attempts successful

## Risk Mitigation

### Cryptographic Risks
- **Key Management**: Environment-injected secrets with rotation capability
- **Signature Overhead**: Optimized verification with caching
- **Canonicalization**: Single shared serializer to prevent variance

### Sovereignty Risks
- **Performance Impact**: Parallel validation and caching
- **Complexity**: Incremental rollout with comprehensive testing
- **Integration**: Maintain backward compatibility during transition

### Meta-Learning Risks
- **Over-Restriction**: Risk-based tiered enforcement
- **Compliance Gaps**: Continuous audit and monitoring
- **Change Management**: Phased rollout with rollback capability

## Conclusion

This sovereignty-complete implementation plan merges the Zero-Loss Prompt Taxonomy with cryptographic hardening requirements to achieve true mathematical determinism and governance enforcement. The plan addresses all critical gaps including cryptographic boundary enforcement, replay-verified determinism, capability-bound execution tokens, and meta-learning containment.

The phased approach ensures manageable implementation while maintaining system stability and achieving the highest standards of security, compliance, and architectural sovereignty. Successful implementation will result in a cryptographically-sealed, mathematically-provable prompt governance architecture that meets Zero-Loss compliance requirements.

**Final Verdict: Conceptually Strong + Cryptographically Complete = Sovereignty-Ready**

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

