# HARDEN-MERGE Sovereign Architecture Integration Plan-5869af

This plan implements cryptographic sovereignty hardening and merges the L2 Architecture Gap Analysis with the Full Zero-Loss Widescreen Architecture to create a deterministically replayable, sovereignty-enforced four-bucket L2 structure.

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

The HARDEN-MERGE phase will cryptographically seal all four L2 buckets (Pre-commit, Validation, Execution, Healing) with deterministic replay, universal write gateway enforcement, and healing sovereignty choke points. This creates a zero-loss architecture where every component is cryptographically verifiable and deterministically replayable.

## Current State Analysis

**Existing Cryptographic Infrastructure:**
- ✅ InstructionPacket and SandboxEnvelope already implemented with HMAC-SHA256
- ✅ HealingTierRouter exists as single choke point
- ✅ EmbeddingServiceFactory with kill-switch and integrity checks
- ✅ Comprehensive test suite in tests/governance/

**Missing Sovereignty Components:**
- ❌ No sovereign_hardening test directory for acceptance
- ❌ Universal Write Gateway not fully implemented
- ❌ Missing determinism digest emission
- ❌ L0 authority hardening incomplete
- ❌ Meta-learning safety gates need enforcement

## Implementation Plan by Phases

### Phase 1: Cryptographic Contract Layer Hardening
**Scope:** Strengthen existing cryptographic foundations

**Wave 1.1: Canonical JSON Serializer Enhancement**
- Verify InstructionPacket and SandboxEnvelope canonicalization
- Add strict UTF-8 encoding validation
- Implement zero whitespace drift enforcement
- Add invariant tests for serialization determinism

**Wave 1.2: Signature Verification Enforcement**
- Ensure L2 entry verifies signatures before ANY side-effect
- Add fail-closed rejection mechanisms
- Create comprehensive signature boundary tests
- Verify constant-time comparison implementations

**Wave 1.3: Contract Integration**
- Integrate InstructionPacket with L0 routing authority
- Ensure SandboxEnvelope verification at tool execution boundary
- Add cryptographic audit trails

### Phase 2: Universal Write Gateway Implementation
**Scope:** Implement single mutation authority

**Wave 2.1: Gateway Core Implementation**
- Create agentic_core/L2_execution/UniversalWriteGateway.py
- Intercept ALL non-gateway FS/DB/vector writes
- Implement replay_mode flag for simulation
- Add comprehensive write interception tests

**Wave 2.2: Runtime Enforcement**
- Integrate gateway with existing tool execution
- Add write permission validation
- Implement mutation ledger for audit trails
- Ensure backward compatibility with existing agents

**Wave 2.3: Determinism Enforcement**
- Block network calls in replay_mode
- Add timestamp capture for nondeterministic inputs
- Implement deterministic fallback mechanisms

### Phase 3: Escalation Choke Point Sovereignty
**Scope:** Harden healing tier selection

**Wave 3.1: Allowlist Freezing**
- Convert TIERING_ALLOWLIST to frozenset (no runtime mutation)
- Add HEALER_ESCALATION_ALLOWLIST enforcement
- Prohibit direct model/provider calls outside seam
- Create choke point bypass prevention tests

**Wave 3.2: FailureSignal Construction**
- Ensure FailureSignal built from EscalationContext ONLY
- Add invariant test for raw notes prohibition
- Implement deterministic escalation context parsing
- Add audit logging for escalation decisions

**Wave 3.3: HealingProviderInvoker Seam**
- Implement injectable HealingProviderInvoker protocol
- Add FakeInvoker for tests (no network)
- Ensure DefaultHealingProviderInvoker for production
- Create provider invocation audit trails

### Phase 4: Embedding Governance Enforcement
**Scope:** Strengthen embedding service sovereignty

**Wave 4.1: Kill-Switch Enforcement**
- Verify EMBEDDING_ENABLED environment variable handling
- Add _DisabledEmbeddingService fallback
- Implement fork guard with (pid, ctime) identity
- Add cross-process usage prevention

**Wave 4.2: Integrity and Determinism**
- Enforce SHA-256 integrity check at startup
- Implement BLAS thread locking (OMP/MKL single-thread)
- Add eps=1e-12 normalization guard
- Enforce score rounding to 6 decimals
- Implement deterministic tie-break (-score, content_hash ASC)

**Wave 4.3: C0 Informational Guard**
- Prevent embedding results from mutating routing/safety/execution
- Add informational-only output validation
- Create embedding governance invariant tests

### Phase 5: L0 Authority Hardening
**Scope:** Strengthen routing authority and policy enforcement

**Wave 5.1: Deterministic Ruleset Election**
- Implement precedence order for ruleset selection
- Add tool inventory arbitration with budget forecast
- Create policy_hash stamping into InstructionPacket
- Ensure L6 anomaly signals feed but don't mutate without validation

**Wave 5.2: Policy Hash Correlation**
- Add mandatory policy_hash to all routing decisions
- Implement signature verification with policy validation
- Create policy change detection and escalation
- Add policy audit trails

**Wave 5.3: L0-L5 Integration**
- Strengthen L0↔L5 communication protocols
- Add unified policy enforcement across layers
- Implement policy escalation and remediation workflows

### Phase 6: Meta-Learning Safety Gates
**Scope:** Enforce meta-learning proposal-only default

**Wave 6.1: Proposal-Only Enforcement**
- Ensure MetaLearningPipeline.proposal_only=True by default
- Add explicit dual injection requirement for activation
- Implement VersionStore + ApprovalGate injection validation
- Create activation prevention tests

**Wave 6.2: Validation Pipeline**
- Implement ReplayValidator for change validation
- Add ShadowEvaluator for impact assessment
- Create OscillationDetector for stability
- Implement DampeningValidators for cooldown enforcement

**Wave 6.3: Bounded Change Enforcement**
- Clamp RLHF deltas to [0.1, 2.0] range
- Add Δ±0.1 per decision limits
- Ensure ChangePackage never directly mutates safety tiers
- Require L0 re-clear for safety tier changes

### Phase 7: Determinism Proof Implementation
**Scope:** Implement deterministic digest emission

**Wave 7.1: Digest Calculation**
- Implement HARDEN-MERGE-DETERMINISM-DIGEST emission
- Include registry hash, embedding pack hash, allowlist hash, routing ruleset hash
- Ensure exactly one digest per run
- Add digest validation tests

**Wave 7.2: Determinism Validation**
- Implement dual-run digest comparison
- Add reproducibility verification across environments
- Create deterministic build verification
- Add digest integrity checks

### Phase 8: Test Suite Creation
**Scope:** Create comprehensive sovereign hardening test suite

**Wave 8.1: Acceptance Test Structure**
- Create tests/sovereign_hardening/ directory
- Implement acceptance SSOT command: pytest tests/sovereign_hardening -q
- Add signature verification enforcement tests
- Create gateway block tests

**Wave 8.2: Negative Control Implementation**
- Implement W_HARDEN_NEGCTRL_TAMPER=1 tampering mechanism
- Add pytest XFAIL(strict=True) exit 0 behavior
- Create tampering detection and restoration tests
- Verify negative control exit-0 behavior

**Wave 8.3: Cross-Layer Validation**
- Add upward mutation prevention tests
- Create gateway bypass prevention tests
- Implement embedding mutation blocking tests
- Add architectural closure validation

## Detailed Implementation Specifications

### Universal Write Gateway Interface
```python
class UniversalWriteGateway:
    """Single mutation authority for all writes"""

    def __init__(self, replay_mode: bool = False):
        self.replay_mode = replay_mode
        self.write_permissions: Dict[str, bool] = {}
        self.mutation_ledger: List[MutationRecord] = []

    def check_write_permission(self, path: str, operation: str) -> bool:
        """Check if write operation is permitted"""

    def record_mutation(self, path: str, operation: str, data: Any) -> None:
        """Record mutation for audit trail"""

    def simulate_write(self, path: str, operation: str, data: Any) -> SimulationResult:
        """Simulate write without actual mutation in replay_mode"""
```

### Determinism Digest Calculation
```python
def calculate_determinism_digest() -> str:
    """Calculate SHA-256 digest of system state"""
    components = [
        get_registry_hash(),
        get_embedding_pack_hash(),
        get_allowlist_hash(),
        get_routing_ruleset_hash()
    ]
    combined = "".join(components).encode("utf-8")
    return hashlib.sha256(combined).hexdigest()
```

### Sovereign Hardening Test Structure
```
tests/sovereign_hardening/
├── __init__.py
├── test_signature_verification.py
├── test_write_gateway_enforcement.py
├── test_escalation_choke_point.py
├── test_embedding_governance.py
├── test_l0_authority.py
├── test_meta_learning_safety.py
├── test_determinism_digest.py
├── test_negative_control.py
└── conftest.py
```

## Acceptance Criteria

### Functional Requirements
- ✅ All cryptographic contracts verified before side-effects
- ✅ Universal Write Gateway blocks unauthorized writes
- ✅ Escalation cannot bypass healing choke point
- ✅ Embedding kill-switch and governance enforced
- ✅ Replay mode blocks nondeterminism
- ✅ No cross-layer upward mutation possible

### Test Requirements
- ✅ collected > 0 tests
- ✅ 0 failed tests
- ✅ 0 errors
- ✅ Determinism digest identical across runs
- ✅ Negative control exit-0 XFAIL behavior
- ✅ No critical sovereignty violations

### Evidence Requirements
- ✅ Single markdown evidence file: artifacts/windsurf/HARDEN-MERGE-EVIDENCE.md
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

## Next Phase Triggers

### If Converge % >= 94% and No Critical Violations
- Automatically emit next phase prompt for SYSTEM INVARIANT SCANNER & CI ENFORCEMENT

### If Converge % = 100%
- Emit next phase in hybrid format
- Do not repeat HARDEN-MERGE phase

This plan creates a cryptographically sovereign, deterministically replayable architecture that enforces strict boundaries between all four L2 buckets while maintaining backward compatibility and operational excellence.

## Gap Register

| Gap | Priority | Impact | Status |
|------|----------|--------|---------|
| [Gap 1] | High | Critical | Open |
| [Gap 2] | Medium | Moderate | In Progress |

---

## Execution Plan

1. **Phase 1**: Analysis and Planning
2. **Phase 2**: Implementation
3. **Phase 3**: Testing and Validation
4. **Phase 4**: Documentation and Cleanup

---

