---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\core-l5-certification-packet-producer-hardening.md'
original_relative_path: 'core-l5-certification-packet-producer-hardening.md'
source_sha256: 950c22795842d8669308c608f14413ceda8a6b9aeea77f7f4e95dd3d7a4aec4d
recovered_status: LOST_RECOVERED
last_commit: '56872a6db68'
last_commit_date: '2026-05-13 17:19:32 -0400'
created_date: '2026-05-13'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: core-l5-certification-packet-producer-hardening
plan_type: platform_core_change
touches_agentic_core: true
touches_governance_ci: true
touches_windsurf_rules: false
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: ""
dod_exempt: false
---

# Core L5 Certification Packet Producer — Generic Governance Infrastructure

Generic `L5CertificationPacket` producer and `EgressCertificationReceipt` interface for all apps_* requiring governed-release certification. Provides shared `l5_governance_context_digest` across child certifiers without emitting GateVerdict, X3, or L4 durable commits.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-05-13

---

## Context (SCQA)

- **Situation** — The L5 safety layer requires a standardized certification packet for governed releases. Multiple apps_* (including apps_rg) need L5 certification, but no generic producer exists in `agentic_core`. Each app currently would need to implement its own L5 packet construction, leading to duplication and inconsistency.

- **Complication** — L5 is a critical safety boundary: it must aggregate child certifier receipts, produce a shared governance context digest, and emit egress receipts around external provider calls. However, L5 must NOT emit GateVerdict. 00C Runtime Gates emit GateVerdict; layer owners act within their authority; Exit emits final X3. L5 must not write to L4 durable surfaces (UWG responsibility). The producer must be app-agnostic and fail-closed.

- **Question** — How do we build a generic L5 certification packet producer in `agentic_core` that serves all apps_* without hardcoding app-specific literals, while respecting the L5 safety boundary constraints?

- **Answer** — Implement a core L5 certification package with: (1) `L5CertificationPacket` dataclass with schema_version, producer, child_certifiers, governance_context_digest, and egress_receipts; (2) `EgressCertificationReceipt` dataclass for provider call attestation; (3) `L5PacketProducer` class with `produce_packet()` method; (4) `EgressCertifier` interface for provider gateway integration; (5) Comprehensive fail-closed validation; (6) App-agnostic contract definitions. All changes Author-Gated before implementation.

---

## Wave Overview

**Waves**: 5 total (W1–W5)
**Total Estimate**: ~12K tokens
**Current**: W0 (pre-flight)

**Wave Manifest**:
- **W1** — Contract dataclasses: L5CertificationPacket, EgressCertificationReceipt, ChildCertifierReceipt | ~2.5K tokens | Checkpoint A | STATUS: TODO
- **W2** — L5PacketProducer implementation with governance context aggregation | ~3K tokens | Checkpoint B | STATUS: TODO
- **W3** — EgressCertifier interface and provider gateway integration contract | ~2.5K tokens | Checkpoint C | STATUS: TODO
- **W4** — Fail-closed validation and comprehensive unit tests | ~2.5K tokens | Checkpoint D | STATUS: TODO
- **W5** — CI gate registration, documentation, and core receipt | ~1.5K tokens | Checkpoint E | STATUS: TODO

**Pre-flight Baseline (W0)**:
- Verify no existing L5 certification producer in `agentic_core/L5_safety/`
- Confirm `agentic_core` boundary rules allow L5 additions
- Establish baseline contract directory structure
- **W0 Baseline Receipt**: `artifacts/governance/core_l5_producer_w0_baseline_receipt.json`

---

## Wave 1 — Contract Dataclasses

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
core_addition_author_gate_status: PENDING
CHECKPOINT: A

**Authorization**: REQUIRED — All `agentic_core` additions require Author-Gate per constitutional rule §22 and `agentic_core/AGENTS.md`. Must emit `CoreAdditionAuthorGateReceipt` with verdict=PASS before any code changes.

**Phases**:
- **W1.1** — Create `agentic_core/L5_safety/contracts/l5_certification_contracts.py` with base types | ~0.8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** — Implement `L5CertificationPacket` dataclass with full BaseContractEnvelope + spine contract fields | ~0.9K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.3** — Implement `EgressCertificationReceipt` dataclass with attestation fields | ~0.5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.4** — Implement `ChildCertifierReceipt` dataclass with digest sharing | ~0.3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**L5CertificationPacket Schema (W1.2)** — Full spine contract compliance:
```python
@dataclass(frozen=True)
class L5CertificationPacket:
    # BaseContractEnvelope fields
    schema_version: str = "1.0.0"
    producer: str = "agentic_core.L5_safety.certification.l5_packet_producer"
    packet_id: str  # UUID
    produced_at: str  # ISO8601 timestamp
    
    # Certified object identity
    certified_object_ref: str
    certified_object_digest: str
    
    # Governance context shared across all child certifiers
    l5_governance_context_digest: str  # 64-char SHA256
    
    # Policy and blueprint references
    policy_hash: str
    blueprint_hash: str
    registry_digest_set: tuple[str, ...]
    
    # Authority chain
    principal_chain: tuple[str, ...]
    capability_token_ref: str
    sandbox_envelope_ref: str
    origin_trust_manifest_ref: str
    
    # Certification evidence
    child_certifier_results: tuple[ChildCertifierReceipt, ...]
    child_certifier_count: int
    
    # Egress receipts around external provider calls
    egress_certification_receipt_refs: tuple[str, ...]
    egress_receipts: tuple[EgressCertificationReceipt, ...]
    
    # HITL and replay
    hitl_reclearance_receipt_ref: str | None
    replay_envelope_ref: str
    audit_manifest_ref: str
    
    # Governance references
    static_governance_refs: tuple[str, ...]
    runtime_binding_refs: tuple[str, ...]
    
    # Digest validation
    digest_equality_result: str  # "PASS" | "FAIL" | "UNKNOWN"
    
    # Certification status (advisory only — 00C Runtime Gates emit GateVerdict; Exit emits X3)
    certification_status: str  # "L5_NOT_CERTIFIED" | "L5_CERTIFICATION_READY"
    decisive_reason: str | None
    
    # Non-repudiation chain
    packet_digest: str  # SHA256 of canonical packet serialization
    prior_packet_digest: str | None  # Chain to previous packet for replay
```

**Required Child Certifier Categories (must be covered by child_certifier_results):**
- 00A.1 Safety Enforcement
- 00A.2 Authority Context + Registry Binding
- 00A.3 Origin Trust + Content Boundary
- 00A.4 HITL Reclearance (when applicable)
- 00A.5 Egress + Provider Governance (when applicable)
- 00A.6 Replay / Audit / Certification Evidence
- 00A.7 Static Governance + Structure Drift
- 00A.8 Runtime Certification Binding

**Rule:** Missing applicable child certifier result => L5_NOT_CERTIFIED with decisive_reason; L5 still does not emit GateVerdict or X3.

**Acceptance**:
- All three dataclasses exist with `frozen=True`
- `l5_governance_context_digest` is 64-char hex string
- `child_certifier_results` is tuple type (immutable)
- `egress_receipts` is tuple type (immutable)
- `certification_status` vocabulary is limited to two values
- Schema version follows semver

---

## Wave 2 — L5PacketProducer Implementation

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
core_addition_author_gate_status: PENDING
CHECKPOINT: B

**Authorization**: REQUIRED — Continues core addition work; requires Author-Gate PASS receipt.

**Phases**:
- **W2.1** — Create `L5PacketProducer` class with `__init__` configuration | ~0.8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** — Implement `produce_packet()` with child receipt aggregation | ~1.2K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.3** — Implement governance context digest computation | ~0.6K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.4** — Add fail-closed validation for malformed child receipts | ~0.4K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Producer Behavior**:
```python
class L5PacketProducer:
    def produce_packet(
        self,
        child_receipts: Sequence[ChildCertifierReceipt],
        egress_receipts: Sequence[EgressCertificationReceipt],
        prior_packet_digest: str | None = None,
    ) -> L5CertificationPacket:
        # Compute shared governance context digest
        context_digest = self._compute_governance_context_digest(child_receipts)
        
        # Validate all child receipts share this digest
        for receipt in child_receipts:
            if receipt.l5_governance_context_digest != context_digest:
                raise L5CertificationError(
                    f"Child certifier {receipt.certifier_id} digest mismatch"
                )
        
        # Produce packet with advisory status
        status = self._determine_certification_status(child_receipts, egress_receipts)
        
        # Compute packet digest
        packet = L5CertificationPacket(...)
        return packet
```

**Acceptance**:
- `L5PacketProducer` class exists in `agentic_core/L5_safety/certification/l5_packet_producer.py`
- `produce_packet()` returns frozen `L5CertificationPacket`
- Governance context digest is consistent across all child receipts
- Digest mismatch raises `L5CertificationError` (fail-closed)
- Advisory status only — never "L5_CERTIFIED" (00C Runtime Gates emit GateVerdict; Exit emits final X3)

---

## Wave 3 — EgressCertifier Interface

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
core_addition_author_gate_status: PENDING
CHECKPOINT: C

**Authorization**: REQUIRED — Core addition work; requires Author-Gate PASS receipt.

**Phases**:
- **W3.1** — Create `EgressCertifier` abstract base class / protocol | ~0.8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** — Define `certify_egress()` method signature with call attestation | ~0.6K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.3** — Create `ProviderGatewayEgressCertifier` reference implementation | ~0.8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.4** — Add provider call metadata capture fields | ~0.3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**EgressCertificationReceipt Schema**:
```python
@dataclass(frozen=True)
class EgressCertificationReceipt:
    receipt_id: str  # UUID
    certifier_id: str  # "egress_certifier"
    produced_at: str  # ISO8601 timestamp
    
    # Call attestation
    provider_ref: str  # symbolic registry ref, e.g., "provider_family/model_tier" or "provider_ref://<registry-key>"
    call_purpose_ref: str  # Semantic purpose ref, e.g., "call_purpose_ref://<semantic-purpose>"
    request_digest: str  # SHA256 of canonical request
    response_digest: str  # SHA256 of canonical response (excl PII)
    
    # L5 governance context
    l5_governance_context_digest: str  # Must match packet digest
    
    # Status
    egress_status: str  # "EGRESS_SUCCEEDED" | "EGRESS_FAILED" | "EGRESS_UNKNOWN"
    
    # Non-repudiation
    receipt_digest: str  # SHA256 of canonical serialization
```

**Acceptance**:
- `EgressCertifier` interface exists in `agentic_core/L5_safety/certification/egress_certifier.py`
- `certify_egress()` returns `EgressCertificationReceipt`
- Provider refs are symbolic, not hardcoded model IDs
- Call purpose is a semantic ref (e.g., "call_purpose_ref://<semantic-purpose>"), not a raw prompt and not app-specific
- Response digest excludes PII (hashed after redaction)

---

## Wave 4 — Fail-Closed Validation and Tests

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
core_addition_author_gate_status: N/A
CHECKPOINT: D

**Authorization**: NOT_REQUIRED — No shared surface modifications; tests only.

**Phases**:
- **W4.1** — Comprehensive unit tests for L5CertificationPacket | ~0.7K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.2** — Comprehensive unit tests for L5PacketProducer | ~0.9K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.3** — Comprehensive unit tests for EgressCertifier implementations | ~0.6K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.4** — App-agnostic boundary tests (no apps_rg literals) | ~0.3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Test File**: `tests/unit/agentic_core/L5_safety/test_l5_packet_producer.py`

**Key Test Cases**:
1. `test_produce_packet_returns_frozen_dataclass` — immutability
2. `test_governance_context_digest_consistent_across_children` — digest sharing
3. `test_digest_mismatch_raises_l5_certification_error` — fail-closed
4. `test_certification_status_advisory_only_not_certified` — never claims certified
5. `test_prior_packet_digest_chains_correctly` — non-repudiation chain
6. `test_egress_receipts_included_in_packet` — egress attestation
7. `test_no_apps_rg_literals_in_l5_producer` — boundary scan
8. `test_no_gate_verdict_emission` — L5 boundary respected
9. `test_no_x3_commit_emission` — L5 boundary respected
10. `test_no_l4_write` — L5 boundary respected
11. `test_l5_packet_matches_spine_contract_required_fields` — spine contract compliance

**Acceptance**:
- 25+ unit tests pass, 0 failures
- 100% line coverage on producer logic
- Zero apps_rg literals in `agentic_core/L5_safety/`
- `check_agentic_core_app_agnostic.py` passes

---

## Wave 5 — CI Gate Registration and Documentation

WAVE_ID: W5
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
core_addition_author_gate_status: N/A
CHECKPOINT: E

**Authorization**: NOT_REQUIRED — CI registration only.

**Phases**:
- **W5.1** — Register L5 safety tests in CI pipeline | ~0.3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.2** — Capture final core closeout receipt and verify initial Author-Gate receipt was captured before W1 | ~0.4K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.3** — Final boundary verification and documentation | ~0.5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.4** — Core receipt capture and plan closeout | ~0.3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Author-Gate Receipt Discipline:**
- **W0.1** — Capture `CoreAdditionAuthorGateReceipt` before W1 code changes (initial authorization)
- **W5.2** — Capture final core closeout receipt and verify initial Author-Gate receipt exists

**Core Addition Author-Gate Receipt (captured at W0.1 and verified at W5.2)**:
```json
{
  "receipt_type": "CoreAdditionAuthorGateReceipt",
  "receipt_version": "1.0",
  "plan_id": "core-l5-certification-packet-producer-hardening",
  "verdict": "PASS",
  "author_gate_decision_id": "<decision_id_from_pipeline>",
  "core_files_added": [
    "agentic_core/L5_safety/certification/__init__.py",
    "agentic_core/L5_safety/certification/l5_packet_producer.py",
    "agentic_core/L5_safety/certification/egress_certifier.py",
    "agentic_core/L5_safety/contracts/l5_certification_contracts.py"
  ],
  "apps_literals_found": [],
  "boundary_verdict": "CLEAN",
  "emits_gate_verdict": false,
  "emits_x3": false,
  "writes_l4": false,
  "timestamp": "2026-05-13T...",
  "digest": "sha256:..."
}
```

**Acceptance**:
- `CoreAdditionAuthorGateReceipt` exists with verdict=PASS
- `ops_scripts/ci/run_contract_gates.py` includes L5 safety tests
- All boundary verifications pass
- Plan marked complete with W5 receipt

---

## Hard Constraints

**Invariants (Never Violate):**

1. **No apps_rg literals** — `agentic_core/L5_safety/` must contain zero references to apps_rg, resume, CV, or company-specific terms.

2. **L5 does not emit GateVerdict** — Only 00C Runtime Gates emit `GateVerdict`. L5 produces certification evidence only.

3. **L5 does not emit X3** — Exit layer owns X3C commit protocol. L5 must not emit X3 directly.

4. **L5 does not write L4** — UWG owns all L4 durable writes. L5 produces in-memory packets only.

5. **Child certifiers share one governance context digest** — All `ChildCertifierReceipt.l5_governance_context_digest` values must match. Mismatch = fail-closed error.

6. **Egress receipts are attestation-only** — They certify that a call occurred, not that the result was correct or safe.

7. **Frozen dataclasses only** — All contract types must be immutable (`frozen=True`).

8. **Symbolic provider refs** — Use `"provider_family/model_tier"` refs, not hardcoded `"openai/gpt-4o"` literals.

---

## Files and Paths

| File | Wave | Change Type | Description |
|------|------|-------------|-------------|
| `agentic_core/L5_safety/certification/__init__.py` | W1 | Create | Package init, exports |
| `agentic_core/L5_safety/certification/l5_packet_producer.py` | W1-W2 | Create | Main producer class |
| `agentic_core/L5_safety/certification/egress_certifier.py` | W3 | Create | Egress certifier interface |
| `agentic_core/L5_safety/contracts/l5_certification_contracts.py` | W1 | Create | Dataclass contracts |
| `agentic_core/L5_safety/contracts/__init__.py` | W1 | Create | Contracts exports |
| `agentic_core/L5_safety/exceptions.py` | W2 | Create | `L5CertificationError` |
| `tests/unit/agentic_core/L5_safety/__init__.py` | W4 | Create | Test package |
| `tests/unit/agentic_core/L5_safety/test_l5_packet_producer.py` | W4 | Create | Producer tests |
| `tests/unit/agentic_core/L5_safety/test_egress_certifier.py` | W4 | Create | Egress tests |
| `tests/unit/agentic_core/L5_safety/test_l5_contracts.py` | W4 | Create | Contract tests |
| `tests/unit/agentic_core/L5_safety/test_boundary.py` | W4 | Create | App-agnostic verification |
| `ops_scripts/ci/run_contract_gates.py` | W5 | Modify | Register L5 tests |
| `artifacts/governance/core_l5_producer_author_gate_receipt.json` | W5 | Create | Author-Gate receipt |

**Total new files**: 11
**Modified files**: 1
**Tests**: 25+ unit tests

---

## Downstream Integration Reference Only — Not Implemented By This Core Plan

**This section is illustrative. No apps_rg files are modified by this core plan.**

### apps_rg Wiring (Master Plan Phase 8) — Illustrative Only

This core plan enables downstream wiring in `apps-rg-master-governed-runtime-hardening.md` Phase 8:

```python
# apps_rg/runtime/bindings/l2_binding.py (illustrative — not modified by this plan)
from agentic_core.L5_safety.certification.l5_packet_producer import L5PacketProducer
from agentic_core.L5_safety.certification.egress_certifier import EgressCertifier

def produce_l5_packet(run_context: RunContext) -> L5CertificationPacket:
    producer = L5PacketProducer()
    
    # Collect child certifier receipts from U0/L1/L0/C0/PA/L2
    child_receipts = collect_child_receipts(run_context)
    
    # Collect egress receipts from ProviderGateway calls
    egress_receipts = collect_egress_receipts(run_context)
    
    return producer.produce_packet(
        child_receipts=child_receipts,
        egress_receipts=egress_receipts,
    )
```

### Other Apps

- `apps_qna`, `apps_lic`, `apps_research`, `apps_rfp`, `apps_exec`, `apps_underwriting_ai` can all use the same generic L5 producer.

---

## Gap Register

**GAP-1: No Generic L5 Producer Exists**
- Currently each app would need its own L5 packet implementation
- Leads to duplication and inconsistency
- Resolution: This plan creates generic producer

**GAP-2: Egress Receipts Around Provider Calls**
- No standardized attestation for external API calls
- Needed for audit trails without PII exposure
- Resolution: `EgressCertificationReceipt` interface

**GAP-3: Child Certifier Digest Sharing**
- Child certifiers may produce inconsistent digests
- Need validation that all share one governance context
- Resolution: Fail-closed digest comparison in `produce_packet()`

---

## Definition of Done

| DoD ID | Criterion | Verification |
|--------|-----------|--------------|
| DoD-1 | `L5CertificationPacket`, `EgressCertificationReceipt`, `ChildCertifierReceipt` dataclasses exist with frozen=True | Import test passes |
| DoD-2 | `L5PacketProducer` class exists with `produce_packet()` method | Unit test passes |
| DoD-3 | `EgressCertifier` interface exists with `certify_egress()` method | Unit test passes |
| DoD-4 | 25+ unit tests pass, 0 failures, 100% producer coverage | `pytest tests/unit/agentic_core/L5_safety/ -v` |
| DoD-5 | Zero apps_rg literals in `agentic_core/L5_safety/` | `rg "apps_rg" agentic_core/L5_safety/` returns empty |
| DoD-6 | L5 does not emit GateVerdict, X3, or write L4 | Boundary tests pass |
| DoD-7 | `CoreAdditionAuthorGateReceipt` exists with verdict=PASS | Receipt file exists with valid JSON |
| DoD-8 | CI gate registration complete | `run_contract_gates.py` includes L5 tests |
| DoD-9 | Smoke run of downstream apps_rg passes | `python -m apps_rg --dry-run` exits 0 |

### Verification-vs-Deferral

| Item | In plan? | Deferral reason |
|------|----------|-----------------|
| Downstream apps_rg L5 wiring | Not implemented | Belongs in Master Plan Phase 8 |
| ProviderGateway concrete implementation | Not implemented | Belongs in apps_rg L2 binding |
| Child certifier implementations | Not implemented | Each layer owns its certifier |
| L5 HITL reclearance | Not implemented | Deferred unless required |

---

## Scope Expansion Authorization

When scope is discovered during execution, follow the four-step discipline: DISCOVERED_SCOPE → AUTHORIZATION_DECISION → Plan updates → SCOPE_EXPANSION.

**Author-Gate Required Before**: Any file creation or modification under `agentic_core/`.

---

## Related Plans

| Plan | Relation |
|------|----------|
| apps-rg-master-governed-runtime-hardening.md | Downstream Phase 8 uses this producer |
| core-l6-g29-promotion-proof-hardening-d9e3b2.md | Related core-enabling work |
| apps-rg-l5-governance-gap-report-hardened-f8c2e1.md | Gap evidence reference (GAP-001) |

---

## References

- Constitutional §22: ADG graph layer primary for refactoring
- Constitutional §29: Closed-loop router evidence mandatory
- `agentic_core/AGENTS.md`: Core boundary rules
- `agentic_core-static.md`: Core principle — apps customize inputs, core enforces contracts
