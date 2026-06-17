# ADR-084 — W6 Emit-Contract Enrichment

**Status**: Accepted  
**Date**: 2026-05-09  
**Plan**: `.claude/plans/w6-emit-contract-enrichment-d8b2a4.md` (W0–W9)  
**Supersedes**: None  
**Related**: ADR-043 (L1PlanContract v2), ADR-049 (L5 v4 governance), ADR-083 (apps_rg PA boundary)

---

## 1. Context

The agentic pipeline emits 11 typed dataclass contracts across layers U0 → L6.
Prior to this ADR each contract carried only the fields required by its originating wave.
Cross-cutting concerns — identity propagation, gate receipts, replay/determinism,
observability linkage, integrity signatures, risk posture, write firewall — were handled
inconsistently or were absent on several contracts, making full-pipeline audit difficult.

---

## 2. Decision

Enrich all 11 emit contracts with a standardised field set covering 9 cross-cutting concerns.
All new fields are **default-empty or default-safe** to avoid breaking existing callers.

### 11 Target Contracts

| Contract | Module | Layer |
|---|---|---|
| `ValidatedRequest` | `agentic_core.runtime.contracts.apps_rg_ingress_payload` | U0 |
| `L1PlanContract` | `agentic_core.runtime.contracts.l1_plan_contract` | L1 |
| `RouteContract` | `agentic_core.runtime.contracts.route_contract` | L0 |
| `FinalEvidenceContract` | `agentic_core.runtime.contracts.final_evidence_contract` | C0 |
| `CompiledPromptArtifact` | `agentic_core.runtime.contracts.compiled_prompt_artifact` | PA |
| `SealedL2Artifact` | `agentic_core.runtime.contracts.sealed_l2_artifact` | L2 |
| `X3Disposition` | `agentic_core.runtime.contracts.x3_disposition` | Exit |
| `L3RuntimeOrchestrationReceipt` | `agentic_core.runtime.contracts.l3_runtime_orchestration_receipt` | L3 |
| `RuntimeExhaustBundle` | `agentic_core.L6_observability.runtime_trace.runtime_exhaust_bundle` | L6 |
| `CommitRequest` | `agentic_core.L4_state.contracts.records` | L4/UWG |
| `LifecycleTraceContract` | `agentic_core.runtime.contracts.lifecycle_trace_contract` | Cross |

### 9 Concerns Addressed

| # | Concern | Fields Added | Notes |
|---|---|---|---|
| C1 | Identity quad | `tenant_id`, `app_id` | `request_id`/`run_id`/trace already present |
| C2 | L5 cert ref | `l5_certification_ref` | `__post_init__` verify; fail-closed per AG-W0-5 |
| C3 | Gate receipts | `gate_verdict_refs: tuple[str, ...]` | default empty |
| C4 | Replay/determinism | `replay_key: str`, `snapshot_refs: tuple[str, ...]` | default empty; `CommitRequest` already had `replay_key` |
| C5 | Observability | `otel_span_refs: tuple[str, ...]`, `audit_refs: tuple[str, ...]` | default empty |
| C7 | Risk posture | `posture: RuntimePosture` | per-contract default sentinel |
| C9 | Schema/signature | `schema_version: str`, `signature: str` | default empty |
| C10 | Write firewall | `is_uwg_write_authority: bool`, `is_future_run_only: bool` | default False; 4 contracts only |
| —  | RuntimePosture | `POSTURE_READ_ONLY`, `POSTURE_GENERATION`, `POSTURE_WRITE_INTENT`, `POSTURE_HITL_REQUIRED`, `POSTURE_RETRIEVAL` | canonical sentinels in `posture.py` |

> **Concern #2 (L5 cert ref wiring)** was delivered by plan `l5-cert-ref-emit-chain-threading-c4e7f1`; this plan closes the one remaining gap (`X3Disposition`).  
> **Concern #8 (capability/sandbox/egress)** was delivered by `apps-rg-runtime-wiring-completion-d4e8a1`.  
> **Concern #6** was intentionally out of scope.

### Write-Firewall Contracts (C10)

Only 4 contracts are write-eligible and receive `is_uwg_write_authority` / `is_future_run_only`:

| Contract | Role |
|---|---|
| `SealedL2Artifact` | L2 may hand off to UWG |
| `X3Disposition` | Exit gate to UWG |
| `CommitRequest` | Canonical UWG authority holder |
| `RuntimeExhaustBundle` | L6 observability terminal — no write authority by convention |

### Identity Field Variants

- **`trace_id`**: used by U0/L1/L0/C0/PA/L2/Exit contracts
- **`trace_root`**: used by `L3RuntimeOrchestrationReceipt` and `CommitRequest` (pre-existing; not changed)
- **`bundle_id`**: used by `RuntimeExhaustBundle` (aggregator — no per-request identity fields by design)

---

## 3. Consequences

### Positive

- Full-pipeline audit now possible by inspecting a single standardised field set across all contracts
- Gate receipts (`gate_verdict_refs`) allow provenance tracing to individual enforcement decisions
- Replay keys + snapshot refs enable deterministic re-execution of any pipeline run
- Write firewall markers make write-eligibility explicit in the contract schema rather than implicit in gateway code
- `l5_certification_ref` on all 11 contracts closes the audit chain from L5 through to L6

### Negative / Mitigated

- Field count per contract increased by ~8 fields; mitigated by default-safe values so callers are never broken
- `X3Disposition.__post_init__` now enforces `l5_certification_ref`; existing callers must supply `cert-test-ok` (test sentinel) or a valid ref

---

## 4. CI Gate

**W6ECE1** — `ops_scripts/ci/check_w6_emit_contract_enrichment.py`

Structural field scan (dataclass introspection) across all 11 contracts. Checks all 9 concerns.  
Advisory by default; fail-closed via `W6_EMIT_CONTRACT_GATE_FAIL_CLOSED=1`.  
Bypass: `W6_EMIT_CONTRACT_GATE_BYPASS=1`.

---

## 5. Test Coverage

| Wave | Test File | Count |
|---|---|---|
| W1 | `tests/unit/runtime_contracts/test_w1_identity_quad.py` | — |
| W3 | `tests/unit/runtime_contracts/test_w3_gate_verdict_refs.py` | — |
| W4 | `tests/unit/runtime_contracts/test_w4_observability_audit_refs.py` | — |
| W5 | `tests/unit/runtime_contracts/test_w5_schema_version_signature.py` | — |
| W6 | `tests/unit/runtime_contracts/test_w6_posture.py` | — |
| W7 | `tests/unit/runtime_contracts/test_w7_replay_determinism.py` | 60 |
| W8 | `tests/unit/runtime_contracts/test_w8_write_firewall.py` | 28 |

Total runtime_contracts suite: **221 passing** (P9.4 final sweep).

---

## 6. References

- Plan: `.claude/plans/w6-emit-contract-enrichment-d8b2a4.md`
- Gate: `ops_scripts/ci/check_w6_emit_contract_enrichment.py`
- Posture module: `agentic_core/runtime/contracts/posture.py`
- L5 verify: `agentic_core/L5_safety/contracts/verify.py`
- Reference doc: `docs/reference/00A_L5_Governance_Safety/00A.6_L5_Replay_Audit_and_Certification_Evidence.md`
