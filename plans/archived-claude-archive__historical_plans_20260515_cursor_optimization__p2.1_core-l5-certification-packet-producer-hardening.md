---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\p2.1_core-l5-certification-packet-producer-hardening.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\p2.1_core-l5-certification-packet-producer-hardening.md'
source_sha256: f39242aefcb12c403ea5949bfec79c6649ce84c55ed38d1d3d2c3e9f1d191415
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
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
author_gate_receipt_ref: "artifacts/governance/core_l5_producer_author_gate_receipt.json"
dod_exempt: false
---

# Core L5 Certification Packet Producer — Generic Governance Infrastructure

Generic `L5CertificationPacket` producer and `EgressCertificationReceipt` interface for all apps_* requiring governed-release certification. Provides shared `l5_governance_context_digest` across child certifiers without emitting GateVerdict, X3, or L4 durable commits.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETED
CURRENT_WAVE: W5
LAST_COMPLETED_WAVE: W5
LAST_UPDATED: 2026-05-14
CLOSEOUT_RECEIPT: artifacts/governance/core_l5_producer_w5_closeout_receipt.json

---

## Status Semantics

This producer emits **evidence certification status only**. Two values are valid:

| Status | Meaning |
|--------|---------|
| `L5_CERTIFIED` | All required child certifier results are present, applicable, and digest-consistent. All non-applicable categories carry a reason + deciding policy ref + deciding stage. **This means evidence certification only — it is NOT a live proceed/stop signal, NOT final release authority, NOT a GateVerdict, NOT an X3, and NOT UWG commit approval.** |
| `L5_NOT_CERTIFIED` | One or more required child certifier results are missing, malformed, digest-inconsistent, or flagged `NOT_APPLICABLE` without a valid reason/policy/stage triple. Also set when any child status is `UNKNOWN` (never treated as pass). |

**Status values that MUST NOT be emitted by this producer:**

| Forbidden Status | Reason |
|------------------|--------|
| `L5_PARTIAL` | Not a canonical value in `_status_enums.CertificationStatus`; not in the two-value vocabulary for this producer. |
| `L5_NOT_APPLICABLE` | Not a packet-level status; applicability is per child category only, not packet-level. |

**Downstream authority chain (immutable — L5 touches none of these):**
- `00C` decides live proceed/stop (emits `GateVerdict`).
- `Exit` decides final output commit (emits exactly one `X3`).
- `UWG` decides durable write admission.
- This producer does **none** of the above — it creates certification evidence only. `L5_CERTIFIED` from this producer does not route, retrieve, execute, or unblock any of the above.

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
**Current**: W5 (COMPLETED)

**Wave Manifest**:
- **W1** — Contract dataclasses: L5CertificationPacket, EgressCertificationReceipt, ChildCertifierReceipt | ~2.5K tokens | Checkpoint A | STATUS: ✅ DONE
- **W2** — L5PacketProducer implementation with governance context aggregation | ~3K tokens | Checkpoint B | STATUS: ✅ DONE
- **W3** — EgressCertifier interface and provider gateway integration contract | ~2.5K tokens | Checkpoint C | STATUS: ✅ DONE
- **W4** — Fail-closed validation and comprehensive unit tests | ~2.5K tokens | Checkpoint D | STATUS: ✅ DONE
- **W5** — CI gate registration, documentation, and core receipt | ~1.5K tokens | Checkpoint E | STATUS: ✅ DONE

**Pre-flight Baseline (W0)**:
- Verify no existing L5 certification producer in `agentic_core/L5_safety/`
- Confirm `agentic_core` boundary rules allow L5 additions
- Establish baseline contract directory structure
- **W0 Baseline Receipt**: `artifacts/governance/core_l5_producer_w0_baseline_receipt.json`

---

## Wave 1 — Contract Dataclasses

WAVE_ID: W1
WAVE_STATUS: ✅ DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
core_addition_author_gate_status: PASS
CHECKPOINT: A

**Authorization**: REQUIRED — All `agentic_core` additions require Author-Gate per constitutional rule §22 and `agentic_core/AGENTS.md`. Must emit `CoreAdditionAuthorGateReceipt` with verdict=PASS before any code changes.

**Phases**:
- **W1.1** — Create `agentic_core/L5_safety/contracts/l5_certification_contracts.py` with base types | ~0.8K tokens | PHASE_STATUS: ✅ DONE | PHASE_COMPLETE: YES
- **W1.2** — Implement `L5CertificationPacket` dataclass inheriting from `L5Result` (defined in `agentic_core/L5_safety/contracts/_base.py`). `L5Result` already carries `certification_status`, `reason_codes`, and `evidence_refs` from `L5OutputBase`. Add the packet-specific fields on top. `__post_init__` restricts `certification_status` to `{"L5_CERTIFIED", "L5_NOT_CERTIFIED"}`. Use `final_evidence_contract.py` and `x3_disposition.py` only as reference examples for `__post_init__` validation discipline — not as the base-class model. | ~0.9K tokens | PHASE_STATUS: ✅ DONE | PHASE_COMPLETE: YES
- **W1.3** — Implement `EgressCertificationReceipt` dataclass with attestation fields | ~0.5K tokens | PHASE_STATUS: ✅ DONE | PHASE_COMPLETE: YES
- **W1.4** — Implement `ChildCertifierReceipt` dataclass with digest sharing | ~0.3K tokens | PHASE_STATUS: ✅ DONE | PHASE_COMPLETE: YES

**L5CertificationPacket Schema (W1.2)** — Full spine contract compliance:
```python
@dataclass(frozen=True, slots=True)
class L5CertificationPacket(L5Result):  # L5Result from agentic_core/L5_safety/contracts/_base.py
    # L5Result already provides: certification_status, reason_codes, evidence_refs
    # L5OutputBase (via L5Result) already provides: run_id, trace_id, emitted_at_utc, digest_sha256
    # output_kind ClassVar is inherited as "result"
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
    
    # certification_status is inherited from L5Result.
    # MUST be exactly one of: "L5_CERTIFIED" | "L5_NOT_CERTIFIED"
    # MUST NOT be: "L5_PARTIAL" | "L5_NOT_APPLICABLE" (or any other value)
    # L5_CERTIFIED = evidence certification only; NOT live proceed/stop, NOT GateVerdict, NOT X3.
    # certification_status: str  <- inherited; __post_init__ restricts to two-value set
    decisive_reason: str | None  # REQUIRED when certification_status == "L5_NOT_CERTIFIED"
    
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

**Child Applicability Semantics:**

Each category carries an `applicability` field with one of three values:
- `REQUIRED` — result must be present and digest-consistent or the packet is `L5_NOT_CERTIFIED`.
- `NOT_APPLICABLE` — category does not apply to this run. **Must** include a non-empty `not_applicable_reason`, a `deciding_policy_ref` (pointer to the policy that granted exemption), and a `deciding_stage` (the layer/gate that made the determination). Missing any of the three fails closed to `L5_NOT_CERTIFIED`.
- `OPTIONAL` — present if the category ran; absence does not fail the packet.

The `ChildCertifierReceipt` dataclass must carry: `certifier_id`, `category_id`, `applicability`, `not_applicable_reason`, `deciding_policy_ref`, `deciding_stage`, `child_status`, `l5_governance_context_digest`, `child_digest`.

**Rule:** Missing applicable child certifier result → `L5_NOT_CERTIFIED` with `decisive_reason`; `UNKNOWN` child status → `L5_NOT_CERTIFIED` (never treated as pass); `NOT_APPLICABLE` without full reason/policy/stage triple → `L5_NOT_CERTIFIED`; L5 still does not emit GateVerdict or X3.

**Acceptance**:
- All three dataclasses exist with `frozen=True`
- `l5_governance_context_digest` is 64-char hex string
- `child_certifier_results` is tuple type (immutable)
- `egress_receipts` is tuple type (immutable)
- `certification_status` vocabulary is exactly `{"L5_CERTIFIED", "L5_NOT_CERTIFIED"}` — `__post_init__` raises `ValueError` on any other value
- `NOT_APPLICABLE` child applicability requires non-empty `not_applicable_reason` + `deciding_policy_ref` + `deciding_stage` or `__post_init__` raises `ValueError`
- Schema version follows semver

---

## Wave 2 — L5PacketProducer Implementation

WAVE_ID: W2
WAVE_STATUS: ✅ DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
core_addition_author_gate_status: PASS
CHECKPOINT: B

**Authorization**: REQUIRED — Continues core addition work; requires Author-Gate PASS receipt.

**Phases**:
- **W2.1** — Create `L5PacketProducer` class with `__init__` configuration | ~0.8K tokens | PHASE_STATUS: ✅ DONE | PHASE_COMPLETE: YES
- **W2.2** — Implement `produce_packet()` with child receipt aggregation | ~1.2K tokens | PHASE_STATUS: ✅ DONE | PHASE_COMPLETE: YES
- **W2.3** — Implement governance context digest computation | ~0.6K tokens | PHASE_STATUS: ✅ DONE | PHASE_COMPLETE: YES
- **W2.4** — Add fail-closed validation for malformed child receipts | ~0.4K tokens | PHASE_STATUS: ✅ DONE | PHASE_COMPLETE: YES

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
- Evidence certification status only — `certification_status` is one of `{"L5_CERTIFIED", "L5_NOT_CERTIFIED"}`. `L5_CERTIFIED` means evidence certification only, not live release authority. `L5_PARTIAL` and `L5_NOT_APPLICABLE` are never emitted as packet-level status.
- `UNKNOWN` child status always fails closed to `L5_NOT_CERTIFIED`
- `NOT_APPLICABLE` child applicability requires full reason/policy/stage triple or fails closed

---

## Wave 3 — EgressCertifier Interface

WAVE_ID: W3
WAVE_STATUS: ✅ DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
core_addition_author_gate_status: PASS
CHECKPOINT: C

**Authorization**: REQUIRED — Core addition work; requires Author-Gate PASS receipt.

**Phases**:
- **W3.1** — Create `EgressCertifier` abstract base class / protocol | ~0.8K tokens | PHASE_STATUS: ✅ DONE | PHASE_COMPLETE: YES
- **W3.2** — Define `certify_egress()` method signature with call attestation | ~0.6K tokens | PHASE_STATUS: ✅ DONE | PHASE_COMPLETE: YES
- **W3.3** — Create `ProviderGatewayEgressCertifier` reference implementation | ~0.8K tokens | PHASE_STATUS: ✅ DONE | PHASE_COMPLETE: YES
- **W3.4** — Add provider call metadata capture fields | ~0.3K tokens | PHASE_STATUS: ✅ DONE | PHASE_COMPLETE: YES

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
    response_digest: str  # SHA256 of redacted canonical response — computed AFTER PII/secret redaction pass; raw text never stored
    redaction_policy_ref: str  # Pointer to the redaction policy applied before hashing
    
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
- Response digest is computed **after** a PII/secret redaction pass; `redaction_policy_ref` is non-empty and points to the applied policy
- `EgressCertifier.certify_egress()` must not accept a raw response string — it accepts a pre-redacted blob or a structured response with a separate `redaction_receipt_ref`
- Unit test `test_response_digest_computed_after_redaction` asserts that a synthetic response containing a PII marker (e.g. `REDACT_ME_SECRET`) is not present in the serialised `EgressCertificationReceipt`

---

## Wave 4 — Fail-Closed Validation and Tests

WAVE_ID: W4
WAVE_STATUS: ✅ DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
core_addition_author_gate_status: N/A
CHECKPOINT: D

**Authorization**: NOT_REQUIRED — No shared surface modifications; tests only.

**Phases**:
- **W4.1** — Comprehensive unit tests for L5CertificationPacket | ~0.7K tokens | PHASE_STATUS: ✅ DONE | PHASE_COMPLETE: YES
- **W4.2** — Comprehensive unit tests for L5PacketProducer | ~0.9K tokens | PHASE_STATUS: ✅ DONE | PHASE_COMPLETE: YES
- **W4.3** — Comprehensive unit tests for EgressCertifier implementations | ~0.6K tokens | PHASE_STATUS: ✅ DONE | PHASE_COMPLETE: YES
- **W4.4** — App-agnostic boundary tests (no apps_rg literals) | ~0.3K tokens | PHASE_STATUS: ✅ DONE | PHASE_COMPLETE: YES

**Test File**: `tests/unit/agentic_core/L5_safety/test_l5_packet_producer.py`

**Key Test Cases**:
1. `test_produce_packet_returns_frozen_dataclass` — immutability
2. `test_governance_context_digest_consistent_across_children` — digest sharing
3. `test_digest_mismatch_raises_l5_certification_error` — fail-closed
4. `test_certification_status_valid_complete_input_yields_l5_certified` — valid all-pass input (all REQUIRED children present, digest-consistent, authority-safe) yields `L5_CERTIFIED`
5. `test_prior_packet_digest_chains_correctly` — non-repudiation chain
6. `test_egress_receipts_included_in_packet` — egress attestation
7. `test_no_apps_rg_literals_in_l5_producer` — boundary scan
8. `test_no_gate_verdict_emission` — L5 boundary respected
9. `test_no_x3_commit_emission` — L5 boundary respected
10. `test_no_l4_write` — L5 boundary respected
11. `test_l5_packet_matches_spine_contract_required_fields` — spine contract compliance
12. `test_l5_certified_is_evidence_only` — asserts that when `produce_packet()` returns `L5_CERTIFIED`, the packet carries no `GateVerdict`, no `X3`, no L4-write token, and `is_evidence_only()` returns `True` (inherited from `L5OutputBase`)
13. `test_l5_partial_never_emitted` — asserts `"L5_PARTIAL"` is not present in the producer's emitted `certification_status` and cannot be returned by `produce_packet()`
14. `test_l5_not_applicable_not_emitted_as_packet_status` — asserts packet-level `certification_status` is never `"L5_NOT_APPLICABLE"`; `__post_init__` raises on invalid vocab
15. `test_missing_required_child_returns_l5_not_certified` — dropping one `REQUIRED` child from an otherwise-complete set yields `L5_NOT_CERTIFIED` with non-empty `decisive_reason`
16. `test_unknown_child_status_fails_closed` — a child with `child_status="UNKNOWN"` yields `L5_NOT_CERTIFIED`, not `L5_CERTIFIED`
17. `test_not_applicable_without_reason_fails_closed` — `NOT_APPLICABLE` child with empty `not_applicable_reason` raises `L5CertificationError`
18. `test_not_applicable_without_policy_ref_fails_closed` — `NOT_APPLICABLE` child with empty `deciding_policy_ref` raises `L5CertificationError`
19. `test_response_digest_computed_after_redaction` — synthetic egress receipt containing `REDACT_ME_SECRET` literal: asserts that string is absent from all serialised receipt fields
20. `test_no_authority_widening` — producer output `principal_chain`/`capability_token_ref`/`sandbox_envelope_ref` must be a subset of (or equal to) the union of child receipt authority fields; adding a provider/model/tool capability not declared in any child receipt raises `L5AuthorityWideningError`

**Acceptance**:
- 35+ unit tests pass (20 named above + 15 additional structural/boundary cases), 0 failures
- 100% line coverage on producer logic
- Zero apps_rg literals in `agentic_core/L5_safety/`
- `check_agentic_core_app_agnostic.py` passes
- `"L5_PARTIAL"` and `"L5_NOT_APPLICABLE"` appear in no assertion with `== certification_status` unless in a negative/forbidden assertion
- `"L5_CERTIFIED"` MAY appear as the expected pass value in positive assertions (e.g. `assert packet.certification_status == "L5_CERTIFIED"`) but must be accompanied by an assertion that `packet.is_evidence_only() is True`
- `test_no_authority_widening` and `test_response_digest_computed_after_redaction` both pass

---

## Wave 5 — CI Gate Registration and Documentation

WAVE_ID: W5
WAVE_STATUS: ✅ DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
core_addition_author_gate_status: N/A
CHECKPOINT: E

**Authorization**: NOT_REQUIRED — CI registration only.

**Phases**:
- **W5.1** — Register L5 safety tests in CI pipeline | ~0.3K tokens | PHASE_STATUS: ✅ DONE | PHASE_COMPLETE: YES
- **W5.2** — Capture final core closeout receipt and verify initial Author-Gate receipt was captured before W1 | ~0.4K tokens | PHASE_STATUS: ✅ DONE | PHASE_COMPLETE: YES
- **W5.3** — Final boundary verification and documentation | ~0.5K tokens | PHASE_STATUS: ✅ DONE | PHASE_COMPLETE: YES
- **W5.4** — Core receipt capture and plan closeout | ~0.3K tokens | PHASE_STATUS: ✅ DONE | PHASE_COMPLETE: YES

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

7. **L5-native base class** — `L5CertificationPacket` must subclass `L5Result` from `agentic_core/L5_safety/contracts/_base.py` (which itself subclasses `L5OutputBase`). All contract types must be immutable (`frozen=True, slots=True`). Use `final_evidence_contract.py` and `x3_disposition.py` from `agentic_core/runtime/contracts/` only as `__post_init__` validation discipline examples — not as the base-class model. No `BaseContractEnvelope` class exists in this repo.

8. **Symbolic provider refs** — Use `"provider_family/model_tier"` refs, not hardcoded `"openai/gpt-4o"` literals.

9. **No authority widening** — `L5PacketProducer` must not introduce provider, model, tool, sandbox, or capability authority not already present in child receipts or governed input refs. Detected by `test_no_authority_widening`; raises `L5AuthorityWideningError` at runtime.

10. **Egress redaction before digest** — `response_digest` in `EgressCertificationReceipt` is computed after the redaction pass. Raw PII or secret-like material must not appear in any serialised field of the receipt. Enforced by `test_response_digest_computed_after_redaction`.

11. **Two-value certification vocabulary** — `certification_status` on `L5CertificationPacket` must be one of `{"L5_CERTIFIED", "L5_NOT_CERTIFIED"}` (both canonical values in `agentic_core/L5_safety/contracts/_status_enums.CertificationStatus`). The `__post_init__` method raises `ValueError` on any other value. `L5_PARTIAL` and `L5_NOT_APPLICABLE` are forbidden at the packet level. `L5_CERTIFIED` means evidence certification only — it is not a live release signal, not a GateVerdict, not an X3, and does not authorize UWG writes.

12. **No provider SDK from L5** — `agentic_core/L5_safety/` must contain no imports of `openai`, `anthropic`, `boto3`, `httpx`, or any external SDK. Egress certifiers receive pre-formed call metadata; they do not make calls.

---

## Files and Paths

| File | Wave | Change Type | Description |
|------|------|-------------|-------------|
| `agentic_core/L5_safety/certification/__init__.py` | W1 | Create | Package init, exports |
| `agentic_core/L5_safety/certification/l5_packet_producer.py` | W1-W2 | Create | Main producer class |
| `agentic_core/L5_safety/certification/egress_certifier.py` | W3 | Create | Egress certifier interface |
| `agentic_core/L5_safety/contracts/l5_certification_contracts.py` | W1 | Create | Dataclass contracts |
| `agentic_core/L5_safety/contracts/__init__.py` | W1 | Create | Contracts exports |
| `agentic_core/L5_safety/exceptions.py` | W2 | Create | `L5CertificationError`, `L5AuthorityWideningError` |
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

**GAP-4: No Authority Widening Guard**
- Without an explicit check, producer could silently combine child authorities in a way that exceeds any individual child's grant
- Resolution: `produce_packet()` computes union of child authority refs and raises `L5AuthorityWideningError` if output claims exceed that union

**GAP-5: Egress Redaction Proof**
- No existing contract attests that the response digest is post-redaction
- Resolution: `EgressCertificationReceipt.redaction_policy_ref` is mandatory; certifier interface accepts pre-redacted response blob + receipt, never raw response

---

## Definition of Done

| DoD ID | Criterion | Verification |
|--------|-----------|--------------|
| DoD-1 | `L5CertificationPacket`, `EgressCertificationReceipt`, `ChildCertifierReceipt` dataclasses exist with frozen=True | Import test passes |
| DoD-2 | `L5PacketProducer` class exists with `produce_packet()` method | Unit test passes |
| DoD-3 | `EgressCertifier` interface exists with `certify_egress()` method | Unit test passes |
| DoD-4 | 35+ unit tests pass (including all 20 named cases in W4), 0 failures, 100% producer coverage | `pytest tests/unit/agentic_core/L5_safety/ -v` |
| DoD-5 | Zero apps_rg literals in `agentic_core/L5_safety/` | `rg "apps_rg" agentic_core/L5_safety/` returns empty |
| DoD-6 | L5 does not emit GateVerdict, X3, or write L4; does not emit `L5_PARTIAL` or `L5_NOT_APPLICABLE` as packet status; `L5_CERTIFIED` is emitted as evidence-only with `is_evidence_only() == True` | Boundary tests pass including `test_l5_certified_is_evidence_only`, `test_l5_partial_never_emitted`, `test_l5_not_applicable_not_emitted_as_packet_status` |
| DoD-10 | No authority widening — `L5PacketProducer` adds no provider/model/tool/sandbox authority not declared in child receipts | `test_no_authority_widening` passes |
| DoD-11 | Egress response digest computed after redaction — raw PII absent from serialised receipt | `test_response_digest_computed_after_redaction` passes |
| DoD-12 | `L5AuthorityWideningError` exists in `exceptions.py` and is raised on widening attempts | Import test + `test_no_authority_widening` |
| DoD-13 | `NOT_APPLICABLE` child applicability requires `not_applicable_reason` + `deciding_policy_ref` + `deciding_stage`; missing any fails closed | `test_not_applicable_without_reason_fails_closed` + `test_not_applicable_without_policy_ref_fails_closed` pass |
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
- `agentic_core/L5_safety/contracts/_base.py` — **L5-native base hierarchy**: `L5OutputBase` → `L5Packet` / `L5Result` / `L5Receipt` / `L5Report`. `L5CertificationPacket` must subclass `L5Result`.
- `agentic_core/L5_safety/contracts/_status_enums.py` — canonical `CertificationStatus` StrEnum; `L5_CERTIFIED` and `L5_NOT_CERTIFIED` are the two values used by this producer.
- `agentic_core/runtime/contracts/final_evidence_contract.py` — reference example only: `__post_init__` validation discipline, `NOT_APPLICABLE` requires non-empty reason.
- `agentic_core/runtime/contracts/x3_disposition.py` — reference example only: frozen-dataclass `__post_init__` pattern.
