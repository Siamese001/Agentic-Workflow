---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\nist-ai-rmf-l5-profile-e7a3c1.md'
original_relative_path: 'nist-ai-rmf-l5-profile-e7a3c1.md'
source_sha256: 4e4287e4b1b7cf4c1358fe7a7cee4f5f1ba217b1f74387c79a96fba0483ce67e
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-14'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# NIST AI RMF L5 External Governance Profile — Gap Analysis & Implementation Plan

**Plan ID**: `nist-ai-rmf-l5-profile-e7a3c1`  
**Created**: 2026-05-14  
**Status**: Not Started  
**Tier**: T3 Architectural  
**Goal**: Add NIST AI RMF (including GenAI profile) as external governance framework profile under agentic_core L5

---

## Executive Summary

The agentic_core architecture already contains substantial NIST AI RMF alignment infrastructure. L5 governance plane **explicitly references** `StandardsTag.NIST_AI_RMF` alongside ISO 42001. However, no formal NIST AI RMF **crosswalk** or **external profile** exists as a first-class L5 artifact.

**Gap Severity**: LOW to MEDIUM. Architecture supports the requirement; gap is primarily **naming/abstraction** and **CI/proof** rather than architectural absence.

---

## Current-State Control Inventory

### L5 Governance Sub-domains (00A.x)

| Sub-domain | Contract File | Evidence Types | REQ_ID Prefix |
|------------|---------------|----------------|---------------|
| Safety Enforcement | `enforcement.py` | SafetyAuditReceipt, PolicyEnforcementLog | REQ-L5-SAFETY-* |
| Authority Context | `authority.py` | AuthorityContextEvidenceRef, RegistryBindingReceipt | REQ-L5-AUTHORITY-* |
| Origin Trust | `origin.py` | OriginTrustEvidenceRef, ContentBoundaryReceipt | REQ-L5-ORIGIN-TRUST-* |
| HITL Reclearance | `hitl.py` | HumanReclearanceEvidenceRef, ReclearanceReceipt | REQ-L5-HITL-* |
| Egress Governance | `egress.py` | EgressCertificationEvidenceRef | REQ-L5-EGRESS-* |
| Replay/Audit | `replay.py` | ReplayAuditEvidenceRef, **103 contract types** | REQ-L5-REPLAY-AUDIT-* |
| Static Governance | `static.py` | StaticGovernanceEvidenceRef | REQ-L5-STATIC-* |
| Runtime Binding | `runtime_binding.py` | L5RuntimeCertificationBinding (20 fields) | REQ-L5-BIND-* |

### Runtime Surfaces (Evidence Sources)

| Surface | Evidence Artifact | Producer | L5 Consumer |
|---------|-------------------|----------|-------------|
| 00C Runtime Gates | `RuntimeGateVerdictBundle` | L0 entrypoints | L5 cert validation |
| Exit X1/X2/X3 | `X3Disposition`, `DispositionEnvelope` | L3 exit_eval | L5 reclearance binding |
| UWG Durable Writes | `UWGCommitReceipt` | L4 uwg | L5 audit ref |
| L4 Audit/Storage | `AuditManifest`, `TraceCompletenessReport` | L4 audit | L5 replay binding |
| L6 Evaluation | `EvalHarnessOutcome` ledger | L3 pipeline | L5 static drift |
| 99 Proof Bundles | Fort Knox signed bundles | CI compilers | L5 certification scope |

---

## NIST AI RMF Control Crosswalk

### Govern Function (GOV)

| NIST Control | Current L5 Coverage | Evidence Source |
|--------------|---------------------|-----------------|
| GOV-1: Risk management strategy | **PARTIALLY COVERED** | `risk_tier_bands.md`, `BandControls` matrix |
| GOV-2: Roles/responsibilities | **PARTIALLY COVERED** | `principal_ref`, `capability_token_ref` in binding |
| GOV-3: Policy/procedure | **FULLY COVERED** | `policy_hash`, `blueprint_hash`, `registry_digest_set` |
| GOV-4: Risk tolerance | **PARTIALLY COVERED** | Risk tier bands (LOW/MEDIUM/HIGH/CRITICAL) |
| GOV-5: Oversight/review | **PARTIALLY COVERED** | `ops_scripts/calibration/` (judge agreement, trend anomaly) |

### Map Function (MAP)

| NIST Control | Current L5 Coverage | Evidence Source |
|--------------|---------------------|-----------------|
| MAP-1: Context establishment | **FULLY COVERED** | `authority_context_ref`, `route_contract_ref` |
| MAP-2: Categorization | **FULLY COVERED** | `app_id`, `tenant_id`, `certification_scope` |
| MAP-3: Risk identification | **PARTIALLY COVERED** | `ReasonCode` taxonomy (45+ codes), `StandardsFingerprint` |

### Measure Function (MEAS)

| NIST Control | Current L5 Coverage | Evidence Source |
|--------------|---------------------|-----------------|
| MEAS-1: Risk assessment | **FULLY COVERED** | X3 disposition (X3A/X3B/X3C/X3D/X3E), 45+ reason codes |
| MEAS-2: Tracking/monitoring | **FULLY COVERED** | `AuditManifest`, `TraceCompletenessReport`, OTEL spans |
| MEAS-3: Verification/validation | **FULLY COVERED** | 99 proof bundles, Fort Knox compilers, 200+ CI gates |

### Manage Function (MANAGE)

| NIST Control | Current L5 Coverage | Evidence Source |
|--------------|---------------------|-----------------|
| MANAGE-1: Risk response | **FULLY COVERED** | Exit X3 dispositions, HITL reclearance |
| MANAGE-2: Incident response | **PARTIALLY COVERED** | `incident_suspected` flag, break-glass (X3E) |
| MANAGE-3: Monitoring/review | **PARTIALLY COVERED** | L6 shadow evaluation, calibration weekly reports |

### GenAI Profile Controls

| GenAI Control | Current L5 Coverage | Evidence Source | Gap Note |
|--------------|---------------------|-----------------|----------|
| Hallucination/confabulation risk | **FULLY COVERED** | `LOW_FAITHFULNESS`, `UNGROUNDED` reason codes; RAG eval dimensions | Evidence exists; needs NIST mapping |
| Provenance/traceability | **FULLY COVERED** | `deterministic_digest`, `audit_chain_hash`, `replay_key` | Evidence exists; needs NIST mapping |
| Human oversight | **FULLY COVERED** | HITL reclearance receipts, `HumanReviewEvidencePacket` | Evidence exists; needs NIST mapping |
| Provider/supply chain governance | **FULLY COVERED** | `egress_cert_ref`, `provider_governance_hash` | Evidence exists; needs NIST mapping |
| Privacy/cross-context leakage | **FULLY COVERED** | `sandbox_envelope_ref`, `trial_state_leak` detection | Evidence exists; needs NIST mapping |
| Security/prompt injection | **FULLY COVERED** | `PROMPT_INJECTION_DETECTED`, `JAILBREAK_DETECTED` reason codes | Evidence exists; needs NIST mapping |
| Replayability/auditability | **FULLY COVERED** | `ReplayEnvelope`, `AuditManifest`, 103 replay contracts | Evidence exists; needs NIST mapping |
| Model drift/eval governance | **PARTIALLY COVERED** | `eval_harness_outcome` ledger, Spearman calibration | Gap: explicit drift detection receipts |
| Deployment change governance | **PARTIALLY COVERED** | `static_drift` detection, `PromotionReceipt` | Gap: explicit deployment change receipts |

---

## Gap Matrix

| Gap ID | Category | NIST Function | Severity | Gap Type | Evidence Available? |
|--------|----------|---------------|----------|----------|---------------------|
| G-NIST-1 | Explicit NIST control mapping | All | LOW | **Naming/abstraction** | YES - via `StandardsFingerprint` |
| G-NIST-2 | NIST coverage receipt artifact | All | LOW | **CI/proof** | YES - can derive from Fort Knox |
| G-NIST-3 | Model drift detection receipts | GenAI | MEDIUM | **Architectural** | PARTIAL - eval harness exists |
| G-NIST-4 | Deployment change receipts | GenAI | MEDIUM | **Architectural** | PARTIAL - promotion receipts exist |
| G-NIST-5 | External reporting export | All | LOW | **Translation** | NO - new capability |
| G-NIST-6 | NIST-specific gap report format | All | LOW | **CI/proof** | NO - new capability |
| G-NIST-7 | Risk tolerance quantitative bands | GOV-4 | MEDIUM | **Evidence gap** | PARTIAL - ordinal bands exist |

### Gap Type Distribution

| Gap Type | Count | Resolution Complexity |
|----------|-------|----------------------|
| Naming/abstraction | 1 | LOW - add mapping dataclass |
| CI/proof | 3 | LOW - wire existing evidence |
| Translation | 1 | LOW - format conversion |
| Architectural | 2 | MEDIUM - extend v5 contracts |

---

## Proposed Artifact Model

### Core Dataclasses

```python
# agentic_core/L5_safety/contracts/external_governance.py

@dataclass(frozen=True)
class L5ExternalGovernanceProfile:
    """Base class for external framework profiles (NIST, ISO, etc.)."""
    profile_id: str  # e.g., "nist_ai_rmf_1_0"
    framework_version: str
    genai_profile_enabled: bool = False

@dataclass(frozen=True) 
class L5NistProfile(L5ExternalGovernanceProfile):
    """NIST AI RMF profile binding."""
    profile_id: str = "nist_ai_rmf_1_0"
    framework_version: str = "1.0"
    genai_profile_enabled: bool = True
    
    # NIST function coverage evidence
    govern_coverage: NistFunctionCoverage
    map_coverage: NistFunctionCoverage
    measure_coverage: NistFunctionCoverage
    manage_coverage: NistFunctionCoverage

@dataclass(frozen=True)
class NistFunctionCoverage:
    """Per-function coverage assessment."""
    function_code: str  # GOV, MAP, MEAS, MANAGE
    fully_covered: tuple[str, ...]
    partially_covered: tuple[str, ...]
    missing: tuple[str, ...]
    evidence_refs: tuple[str, ...]

@dataclass(frozen=True)
class NistControlMapping:
    """Single control mapping from NIST to L5 evidence."""
    nist_control_id: str  # e.g., "GOV-1.1"
    nist_function: str
    l5_evidence_ref: str
    l5_contract_type: str
    coverage_level: str  # FULL, PARTIAL, MISSING
    rationale: str

@dataclass(frozen=True)
class NistCoverageReceipt:
    """Certification that a run/request meets NIST AI RMF controls."""
    receipt_id: str
    profile_ref: str
    binding_id: str  # Links to L5RuntimeCertificationBinding
    coverage_timestamp: str
    overall_compliance_score: float  # 0.0-1.0
    control_mappings: tuple[NistControlMapping, ...]
    gap_report_ref: str
    certification_status: str  # NIST_CERTIFIED | NIST_NOT_CERTIFIED | NIST_PARTIAL

@dataclass(frozen=True)
class NistGapReport:
    """Structured gap analysis for NIST AI RMF."""
    report_id: str
    generated_at: str
    profile_ref: str
    architectural_gaps: tuple[str, ...]
    evidence_gaps: tuple[str, ...]
    naming_gaps: tuple[str, ...]
    ci_proof_gaps: tuple[str, ...]
    translation_gaps: tuple[str, ...]
    critical_gaps: tuple[str, ...]
    high_gaps: tuple[str, ...]
    medium_gaps: tuple[str, ...]
    low_gaps: tuple[str, ...]
```

### Integration Points (Respecting Boundaries)

```
L5 External Governance Profile
    ├── Sources from L5 internals (evidence-only)
    │   ├── L5RuntimeCertificationBinding.binding_id
    │   ├── CertificationEvidenceRefSet (11 refs)
    │   └── GovernanceResult with standards fingerprint
    ├── Sources from 00C (consumed, not produced)
    │   └── RuntimeGateVerdictBundle
    ├── Sources from Exit (consumed, not produced)
    │   └── X3Disposition, DispositionEnvelope
    ├── Sources from UWG (consumed via receipt)
    │   └── UWGCommitReceipt
    ├── Sources from L4 (audit trail)
    │   └── AuditManifest, TraceCompletenessReport
    ├── Sources from L6 (post-hoc analysis)
    │   └── Eval harness outcomes
    └── Sources from 99 (proof consumption)
        └── Fort Knox bundles
```

---

## Phased Implementation Plan

### Phase 1: Crosswalk + Evidence Mapping (2-3 weeks)

**Deliverables**:
- `L5NistProfile` dataclass with 4 function coverage fields
- `NistControlMapping` 50+ row mapping table
- `StandardsFingerprint` extension for NIST subcategory tags

**Evidence Sources**:
- Map `REQ-L5-*` requirements to NIST controls
- Derive GenAI profile coverage from existing RAG dimensions
- Leverage existing `StandardsTag.NIST_AI_RMF`

**CI/Proof**:
- New gate: `check_nist_control_mapping_freshness.py` (advisory)
- Test: Verify every NIST control has ≥1 L5 evidence ref

### Phase 2: Coverage Receipt Generation (2-3 weeks)

**Deliverables**:
- `NistCoverageReceipt` generator consuming `L5RuntimeCertificationBinding`
- Integration with `governance_plane.certify_packet()` optional output
- Receipt serialization to `artifacts/nist_coverage/`

**Key Design**:
- Receipt generation is **evidence aggregation**, not runtime decision
- Fail-closed: Missing critical controls → `NIST_NOT_CERTIFIED`
- GenAI profile controls included when `genai_profile_enabled=True`

**CI/Proof**:
- Gate: `check_nist_coverage_receipt_schema.py`
- Test: Receipt replay byte-identical

### Phase 3: 99 Proof Integration (2 weeks)

**Deliverables**:
- `NistCoverageReceipt` inclusion in Fort Knox evidence assertions
- Merkle tree leaf for NIST coverage in signed bundles
- 99 proof bundle extension for external governance

**Integration**:
- Extend `evidence_assertions.jsonl` format with `external_governance_refs[]`
- Compiler update: Include NIST coverage in Merkle tree
- Positive control: Synthetic NIST gap triggers expected failure

### Phase 4: CI Governance Assertions (2 weeks)

**Deliverables**:
- `check_nist_gap_critical.py` — fail-closed if critical gaps unaddressed
- `check_nist_mapping_staleness.py` — advisory, detects NIST version drift
- Weekly NIST coverage report: `docs/reports/nist_coverage/<YYYY-Www>.md`

**Gates**:
- NIST-CR1: Critical gap check (blocks release)
- NIST-CR2: Mapping freshness (advisory)
- NIST-CR3: GenAI profile completeness (advisory)

### Phase 5: Optional External Reporting Exports (1-2 weeks)

**Deliverables**:
- JSON export: OSCAL-compatible NIST AI RMF assessment format
- CSV export: Control-by-control coverage matrix
- Markdown export: Human-readable gap report

**Design**:
- Exports are **derived from** L5 evidence, not authoritative sources
- Clear provenance chain: L5 cert → NistCoverageReceipt → export format
- Versioned exports with deterministic hashes

---

## Risks / Anti-Patterns

### Runtime Intrusion Risk (HIGH IMPACT)

**Risk**: NIST profile logic could emit runtime dispositions.

**Mitigation**:
- Explicit `L5ExternalGovernanceProfile` base class with `FORBIDDEN_RUNTIME_DISPOSITIONS`
- Static analysis gate: `check_nist_profile_no_disposition.py`
- `NistCoverageReceipt` never contains `ALLOW`, `DENY`, `REROUTE`

### Duplication Risk (MEDIUM IMPACT)

**Risk**: NIST controls duplicate existing REQ-L5-* requirements without linking.

**Mitigation**:
- Single-source mapping table: One row per NIST control → L5 REQ_ID(s)
- ADG MV: `mv_nist_control_to_l5_req` for traceability
- CI gate: Detect orphaned NIST controls

### Control Boundary Violation (HIGH IMPACT)

**Risk**: NIST profile attempts to influence routing, retrieval, or execution.

**Mitigation**:
- **Hard rule**: `L5NistProfile` is read-only relative to runtime
- Integration only at certification binding emission point
- No NIST-specific runtime gates (00C owns all gates)

### External Framework Bloat (MEDIUM IMPACT)

**Risk**: NIST implementation grows beyond minimal viable coverage.

**Mitigation**:
- Strict artifact model: Only 4 dataclasses + mapping table
- No NIST-specific runtime paths
- Evidence comes from **existing** L5/00C/Exit/UWG/L4/L6/99

### Staleness Risk (LOW IMPACT)

**Risk**: NIST AI RMF version updates invalidate mappings.

**Mitigation**:
- Versioned `profile_id` field (`nist_ai_rmf_1_0`)
- CI gate detects mapping table staleness
- Framework version bump triggers Author-Gate for review

---

## Explicit Non-Goals

| Item | Rationale |
|------|-----------|
| NIST becomes runtime execution layer | Violates constitutional §22, §23, §24 - 00C owns runtime gates |
| NIST-specific routing logic | L0 owns routing; NIST is evidence-only |
| NIST-specific prompt assembly | L3/03B owns prompt assembly |
| NIST-specific retrieval | 03A C0 owns retrieval |
| NIST-specific durable write admission | 00B UWG owns durable writes |
| Real-time NIST compliance monitoring | L6 owns completed-run evaluation only |
| NIST framework version auto-update | Manual Author-Gate required for version changes |
| External auditor direct API access | Exports are batch-generated, not real-time APIs |

---

## Recommendation

### Proceed with Phase 1 (RECOMMENDED)

**Rationale**: Architecture already supports this capability. `StandardsTag.NIST_AI_RMF` exists, and L5's 103 contract dataclasses provide comprehensive evidence coverage.

**Trade-off**:
- **Pros**: Low implementation risk (~5,350 LoC equivalent to v5 gap closure), strengthens external audit posture, minimal runtime impact
- **Cons**: Ongoing maintenance for NIST version updates, potential scope creep

### Recommended Phasing

1. **Phase 1 only initially** — produce crosswalk and validate mapping completeness
2. **Decision gate at Phase 1/2 boundary** — validate evidence aggregation complexity
3. **Phase 5 (external exports) is OPTIONAL** — defer until external audit demand confirmed

---

## Success Criteria

| Phase | Success Metric |
|-------|---------------|
| 1 | 50+ NIST controls mapped to L5 evidence; 0 critical gaps without rationale |
| 2 | `NistCoverageReceipt` generates from runtime binding; replay byte-identical |
| 3 | Fort Knox bundles include NIST coverage Merkle leaf; positive controls pass |
| 4 | 3 CI gates operational; weekly coverage report generated |
| 5 | (If pursued) OSCAL export passes NIST validation tool |

---

## Key Evidence Citations

| Claim | Evidence |
|-------|----------|
| `StandardsTag.NIST_AI_RMF` exists | `agentic_core/L5_safety/v5/governance_plane.py:198` |
| 103 L5 replay contracts exist | `agentic_core/L5_safety/contracts/replay.py` |
| 20-field runtime binding exists | `agentic_core/L5_safety/v5/runtime_binding.py:78-162` |
| Fort Knox two-arm compiler exists | `certification/README_REVIEW.md` |
| 200+ CI gates exist | `ops_scripts/ci/` directory |
| X3 disposition taxonomy exists | `agentic_core/L3_orchestration/exit_eval/disposition.py` |
| `FORBIDDEN_RUNTIME_DISPOSITIONS` enforced | `agentic_core/L5_safety/contracts/_vocab.py` |

---

## Definition of Done

| ID | Criterion | Verification Method |
|----|-----------|---------------------|
| DoD-1 | Gap analysis document complete and reviewed | This document |
| DoD-2 | Plan file saved to disk | `.windsurf/plans/nist-ai-rmf-l5-profile-e7a3c1.md` |
| DoD-3 | Plan registered in Notion | Plans DB row with Status="Not Started" |
| DoD-4 | AI Summary follows bullet-style format per NP1 | Notion row includes target/scope/key files/non-goals/success |
| DoD-5 | Phase boundaries clear with decision gates | Each phase has explicit entry/exit criteria |

---

**END OF PLAN**
