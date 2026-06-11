---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\harden-merge-lockdown-implementation-plan-5869af.md'
original_relative_path: 'harden-merge-lockdown-implementation-plan-5869af.md'
source_sha256: a301f065ce1636da7956bccb58f65bc0c3a330f058a6af9a2a6f69b464b15803
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# HARDEN-MERGE-LOCKDOWN Sovereign Hardening Implementation Plan-5869af

This plan implements runtime sovereignty enforcement, bypass-proof architecture, and deterministic replay validation to achieve 100% convergence with the HARDEN-MERGE-LOCKDOWN requirements.

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

The HARDEN-MERGE-LOCKDOWN phase will implement fail-closed runtime enforcement across all L2 boundaries, create comprehensive bypass detection via AST scanning, and establish deterministic replay validation with negative control testing. This transforms the existing cryptographic foundations into a fully sovereignty-enforced architecture.

## Current State Analysis

**Existing Sovereignty Infrastructure:**
- ✅ InstructionPacket and SandboxEnvelope with HMAC-SHA256 verification
- ✅ HealingTierRouter as single escalation choke point
- ✅ EmbeddingServiceFactory with kill-switch and integrity checks
- ✅ ExecutionGateway with budget enforcement and trace building
- ✅ Extensive governance test suite (60+ tests)
- ✅ Static invariant scanners (write_gateway_enforcer, powershell_ban)

**Critical Gaps for LOCKDOWN:**
- ❌ No sovereign_hardening test directory for unified acceptance
- ❌ Missing UniversalWriteGateway runtime implementation
- ❌ No L2 side-effect boundary guard with fail-closed signature verification
- ❌ Missing HARDEN-MERGE-LOCKDOWN-DETERMINISM-DIGEST emission
- ❌ No W_HARDEN_NEGCTRL_TAMPER negative control mechanism
- ❌ Incomplete bypass detection (provider SDK, unsigned ingress)
- ❌ Missing L0 election determinism and replay key binding

## Implementation Plan by Phases

### Phase 1: L2 Side-Effect Boundary (Fail-Closed Runtime Guard)
**Scope:** Implement mandatory signature verification at L2 entry point

**Wave 1.1: L2 Entry Guard Implementation**
- Add signature verification as first executable line in ExecutionGateway.execute_with_trace()
- Verify SandboxEnvelope signature BEFORE any logging, state operations, or tool selection
- Create dedicated SignatureBoundaryError exception for fail-closed behavior
- Ensure zero side-effects on signature verification failure

**Wave 1.2: Side-Effect Prevention Tests**
- Create tests proving no logging occurs when signature invalid
- Verify no file IO, network calls, or state mutations on verification failure
- Add timing tests to ensure immediate failure without side-effects
- Create negative control tests for invalid signature scenarios

### Phase 2: Universal Write Gateway (Runtime Enforcement)
**Scope:** Implement real write gateway with comprehensive bypass detection

**Wave 2.1: Gateway Core Implementation**
- Create agentic_core/L2_execution/UniversalWriteGateway.py
- Implement MutationRecord ledger for audit trails
- Add replay_mode flag that simulates diffs and blocks network calls
- Create write permission validation system

**Wave 2.2: Tool Integration**
- Integrate gateway with all tool execution paths
- Add guarded write adapters for FS/DB/vector operations
- Implement gateway bypass detection and prevention
- Ensure backward compatibility with existing tools

**Wave 2.3: Enforcement Tests**
- Test direct write attempts outside gateway raise exceptions
- Verify replay_mode blocks network calls and returns simulated results
- Add mutation ledger validation tests
- Create gateway permission boundary tests

### Phase 3: Healing Sovereignty Choke Point (Bypass-Proof)
**Scope:** Harden healing tier selection against all bypass attempts

**Wave 3.1: Allowlist Freezing**
- Convert TIERING_ALLOWLIST to frozenset (no runtime mutation)
- Add runtime guards against allowlist modification
- Implement frozenset integrity validation
- Create allowlist bypass prevention tests

**Wave 3.2: Provider SDK Bypass Prevention**
- Prohibit direct provider invocation outside HealingProviderInvoker seam
- Add AST scanner detection for direct provider SDK imports
- Implement runtime guard against direct model calls
- Create provider bypass prevention tests

**Wave 3.3: Escalation Context Enforcement**
- Ensure FailureSignal built ONLY from EscalationContext
- Add invariant test preventing raw notes in escalation
- Implement deterministic escalation context parsing
- Create escalation integrity tests

### Phase 4: System Invariant Scanner (AST/CI Enforcement)
**Scope:** Comprehensive bypass detection with deterministic output

**Wave 4.1: Enhanced Scanner Implementation**
- Extend existing static invariants with comprehensive bypass detection
- Add scanner rules for:
  - Gateway bypass (direct open(), pathlib.write_text, os.remove outside approved modules)
  - Provider SDK bypass (openai, anthropic, google.generativeai, vertexai, litellm, requests/httpx)
  - Embedding bypass (EmbeddingServiceFactory outside factory entrypoint)
  - Unsigned ingress (tool execution without signature verification)
- Implement deterministic sorted findings output

**Wave 4.2: Allowlist Management**
- Create allowlist of approved modules for restricted operations
- Implement gateway + seam only allowlist enforcement
- Add allowlist integrity validation
- Create allowlist bypass prevention tests

**Wave 4.3: CI Integration**
- Integrate scanner into CI pipeline with failure on violations
- Add deterministic output validation
- Implement scanner performance optimization
- Create CI enforcement tests

### Phase 5: Embedding Governance (Replay Key Binding)
**Scope:** Ensure embedding metadata is included in replay determinism

**Wave 5.1: Replay Key Enhancement**
- Extend replay key to include embedding metadata:
  - embedding_model_version
  - seed_pack_hash/matrix_hash
  - top_k and cutoff values
  - BLAS/threading identity (threads=1 flags)
- Implement embedding metadata binding in replay calculation
- Add replay key integrity validation

**Wave 5.2: Negative Control Implementation**
- Implement W_HARDEN_NEGCTRL_TAMPER=1 environment variable
- Add embedding metadata perturbation mechanism
- Create XFAIL(strict=True) exit 0 behavior for tampered runs
- Add embedding tampering detection tests

**Wave 5.3: C0-Only Enforcement**
- Ensure embedding results cannot mutate routing/safety/execution tiers
- Add informational-only output validation
- Create embedding mutation prevention tests
- Implement embedding governance boundary tests

### Phase 6: L0 Election Determinism
**Scope:** Implement deterministic ruleset election and tool arbitration

**Wave 6.1: Deterministic Sorting**
- Implement deterministic sorting/tie-break rules for ruleset election
- Add tool arbitration with deterministic conflict resolution
- Ensure stable routing_ruleset_hash generation
- Create election determinism tests

**Wave 6.2: Hash Stability**
- Ensure routing_ruleset_hash is stable across runs
- Include routing hash in determinism digest
- Implement hash stability validation
- Create hash stability tests

**Wave 6.3: Proof of Determinism**
- Add tests running election twice with identical results
- Implement election result validation
- Create determinism proof tests
- Add election audit trail validation

### Phase 7: Determinism Digest (Complete Surface)
**Scope:** Implement comprehensive determinism digest emission

**Wave 7.1: Digest Composition**
- Extend digest to include all sovereignty hashes:
  - registry hash
  - tool inventory hash
  - healer registry hash
  - allowlists hash
  - routing ruleset hash
  - embedding pack hash + config surface hash
  - meta-learning config surface version hash
- Implement deterministic digest calculation

**Wave 7.2: Emission Protocol**
- Emit exactly one HARDEN-MERGE-LOCKDOWN-DETERMINISM-DIGEST per run
- Add digest emission validation
- Implement digest integrity checks
- Create digest emission tests

**Wave 7.3: Cross-Run Validation**
- Add tests for identical digest across runs
- Implement digest reproducibility validation
- Create cross-run determinism tests
- Add digest stability validation

### Phase 8: Meta-Learning Safety (Runtime Guards)
**Scope:** Enforce proposal-only default with dual injection requirements

**Wave 8.1: Runtime Enforcement**
- Enforce proposal_only=True default at runtime
- Implement dual injection requirement (VersionStore + ApprovalGate)
- Add fail-closed behavior when injections missing
- Create activation safety tests

**Wave 8.2: ChangePackage Guards**
- Prevent ChangePackage from mutating safety tiers without L0 re-clear
- Add safety tier mutation validation
- Implement L0 re-clear path enforcement
- Create mutation guard tests

**Wave 8.3: Validation Pipeline**
- Add runtime validation for meta-learning operations
- Implement ChangePackage integrity checks
- Create validation pipeline tests
- Add safety enforcement tests

### Phase 9: Test Suite Creation (Unified Acceptance)
**Scope:** Create comprehensive sovereign hardening test suite

**Wave 9.1: Test Structure**
- Create tests/sovereign_hardening/ directory
- Implement unified acceptance test structure
- Add conftest.py with shared fixtures
- Create test organization and categorization

**Wave 9.2: Acceptance Tests**
- Implement signature boundary tests
- Add write gateway enforcement tests
- Create invariant scanner tests
- Add healing choke point bypass tests
- Implement embedding replay key binding tests
- Add L0 election determinism tests
- Create determinism digest tests
- Implement negative control tests

**Wave 9.3: Integration Validation**
- Add end-to-end sovereignty tests
- Create cross-layer validation tests
- Implement architectural closure tests
- Add acceptance criteria validation

## Detailed Implementation Specifications

### L2 Entry Guard Implementation
```python
class ExecutionGateway:
    async def execute_with_trace(self, envelope: SandboxEnvelope, ...):
        # FAIL-CLOSED: Verify signature BEFORE ANY side-effects
        try:
            envelope.verify(get_current_secret())
        except SignatureVerificationError:
            # No logging, no state changes, immediate exit
            raise SignatureBoundaryError("Invalid envelope signature")

        # Only proceed if signature valid
        # ... rest of implementation
```

### Universal Write Gateway Interface
```python
class UniversalWriteGateway:
    def __init__(self, replay_mode: bool = False):
        self.replay_mode = replay_mode
        self.mutation_ledger: List[MutationRecord] = []

    def check_write_permission(self, path: str, operation: str) -> bool:
        """Check if write operation is permitted"""

    def record_mutation(self, path: str, operation: str, data: Any) -> None:
        """Record mutation for audit trail"""

    def simulate_write(self, path: str, operation: str, data: Any) -> SimulationResult:
        """Simulate write in replay_mode"""
```

### Determinism Digest Calculation
```python
def calculate_lockdown_determinism_digest() -> str:
    """Calculate comprehensive determinism digest"""
    components = [
        get_registry_hash(),
        get_tool_inventory_hash(),
        get_healer_registry_hash(),
        get_allowlists_hash(),
        get_routing_ruleset_hash(),
        get_embedding_pack_hash(),
        get_embedding_config_hash(),
        get_meta_learning_config_hash()
    ]
    combined = "".join(components).encode("utf-8")
    return hashlib.sha256(combined).hexdigest()
```

### Negative Control Implementation
```python
def get_embedding_config_with_tamper() -> dict:
    """Get embedding config with optional tampering"""
    config = get_embedding_config()
    if os.environ.get("W_HARDEN_NEGCTRL_TAMPER") == "1":
        config["top_k"] = 999  # Tamper with config
        config["cutoff"] = 0.999
    return config
```

## Test Structure
```
tests/sovereign_hardening/
├── __init__.py
├── conftest.py
├── test_signature_boundary.py
├── test_write_gateway_enforcement.py
├── test_invariant_scanner.py
├── test_healing_choke_point.py
├── test_embedding_replay_key.py
├── test_l0_election_determinism.py
├── test_determinism_digest.py
├── test_meta_learning_safety.py
└── test_negative_control.py
```

## Acceptance Criteria

### Functional Requirements
- ✅ L2 signature verification before any side-effects
- ✅ Universal Write Gateway blocks unauthorized writes
- ✅ Healing choke point bypass-proof enforcement
- ✅ System invariant scanner detects all bypass attempts
- ✅ Embedding governance with replay key binding
- ✅ L0 election determinism with stable hashes
- ✅ Complete determinism digest emission
- ✅ Meta-learning safety with runtime guards

### Test Requirements
- ✅ collected > 0 tests
- ✅ 0 failed tests
- ✅ 0 errors
- ✅ Determinism digest identical across runs
- ✅ Negative control XFAIL(strict=True) exit 0
- ✅ No critical sovereignty violations

### Evidence Requirements
- ✅ Single evidence file: artifacts/windsurf/HARDEN-MERGE-LOCKDOWN-EVIDENCE.md
- ✅ Exact transcript entry count
- ✅ Canonical wrapper commands only
- ✅ Single text block per entry
- ✅ OUT_FILE= and TYPED_FILE= as lines 1-2
- ✅ No helper scripts or PowerShell
- ✅ Absolute paths only

## Risk Mitigation

### Technical Risks
- **Backward Compatibility**: Incremental implementation with feature flags
- **Performance Impact**: Comprehensive benchmarking and optimization
- **Test Coverage**: Extensive test suite with negative controls

### Operational Risks
- **Deployment Disruption**: Parallel development with rollback capability
- **Configuration Drift**: Automated configuration validation
- **Monitoring**: Enhanced observability and alerting

## Success Metrics

### Convergence Targets
- **94% Convergence**: Acceptable for production deployment
- **100% Convergence**: Target for complete architectural alignment
- **0 Critical Violations**: Required for sovereignty integrity

### Quality Gates
- All acceptance tests passing
- Determinism digest stable across runs
- Negative controls functioning correctly
- No sovereignty violations detected
- Runtime enforcement active and effective

## Next Phase Triggers

### If Converge % >= 94% and No Critical Violations
- Auto-emit next phase prompt for "CI ENFORCEMENT INTEGRATION + PRE-COMMIT HOOKS"

### If Converge % = 100%
- Emit next phase in hybrid format
- Do not repeat HARDEN-MERGE-LOCKDOWN phase

This plan creates a bypass-proof, sovereignty-enforced architecture with comprehensive runtime guards, deterministic replay validation, and complete bypass detection via AST scanning and CI enforcement.

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

