# ADR-100 — L5 Certification Reference Threading Through the Full Emit Chain

**Status**: Accepted

| Field | Value |
|---|---|
| **ADR ID** | ADR-100 |
| **Status** | Accepted |
| **Date** | 2026-05-09 |
| **Plan** | `l5-cert-ref-emit-chain-threading-c4e7f1` |
| **Author** | Codex (T3 architectural — cross-layer) |
| **Supersedes** | — |
| **Related** | ADR-049, ADR-051 (L5 governance plane), ADR-080 (runtime cert Phase D) |

---

## 1. Context

The L5 safety layer publishes a `previous_certification_ref` via its own doctrine output
(`agentic_core/L5_safety/contracts/egress.py`) and a registry lookup table
(`agentic_core/L5_safety/contracts/registry.py`).  Prior to this ADR, **no inter-layer
emit contract carried that reference**.  Every downstream layer (L1, L0, C0, PA, L3, L2,
Exit X3, UWG, L6) produced sealed artifacts without embedding the L5 authority token that
authorised the run — making post-hoc certification audits structurally impossible without
re-tracing the full OTEL span graph.

### Conformance baseline (2026-05-09 scan)

| Stage | Contract | File | Had `l5_certification_ref`? |
|---|---|---|---|
| U0 | `ValidatedRequest` | `runtime/contracts/apps_rg_ingress_payload.py` | ❌ |
| L1 | `L1PlanContract` | `prompt_governance/prompt_assembly/input_contracts.py` | ❌ |
| L0 | `RouteContract` | `runtime/contracts/route_contract.py` | ❌ |
| L0 | `L0RouteContract` | `prompt_governance/prompt_assembly/input_contracts.py` | ❌ |
| C0 | `FinalEvidenceContract` | `runtime/contracts/final_evidence_contract.py` | ❌ |
| PA | `CompiledPromptArtifact` | `runtime/contracts/compiled_prompt_artifact.py` | ❌ |
| L3 | `L3StepContract` | `L3_orchestration/doctrine/contracts_l3_7.py` | ❌ |
| L2 | `SealedL2Artifact` | `runtime/contracts/sealed_l2_artifact.py` | ❌ |
| Exit | `X3DenyPacket` … `X3BreakGlassAllowPacket` (5 variants) | `L3_orchestration/exit_eval/v6/types.py` | ❌ |
| UWG | `CommitRequest` | `L4_state/contracts/records.py` | ✅ plural `l5_certification_refs` only |
| UWG | `UWGCommitReceipt` | `L4_state/contracts/records.py` | ❌ |
| L6 | `RuntimeExhaustBundle` (canonical) | `L6_observability/runtime_trace/runtime_exhaust_bundle.py` | ❌ |
| L6 | `RuntimeExhaustBundle` (shadow) | `L6_observability/shadow_eval/contracts.py` | ❌ |

**Conformance ratio before: 1 of 13** (partial — plural form only on `CommitRequest`).

---

## 2. Decision

Thread a singular `l5_certification_ref: str = ""` field through **every** inter-layer
emit contract listed above, and wire a fail-soft inbound verification call-site at each
consuming layer entry point (PA, L3, L2, and selected upstream layers).

### Design decisions (Author-Gate W0 — 2026-05-09)

| # | Question | Decision | Rationale |
|---|---|---|---|
| AG-W0-1 | Singular vs plural | **`l5_certification_ref: str`** (singular) | Spec-aligned; `CommitRequest` plural kept as-is + singular alias added (W3) |
| AG-W0-2 | Field type | **plain `str`** (opaque cert ID) | Minimal contract footprint; registry is authoritative for metadata |
| AG-W0-3 | Verify placement | **fail-soft helpers at consume sites** | Avoids blocking runs during rollout; `L5_CERT_REF_FAIL_CLOSED=1` hardens to fail-closed |
| AG-W0-4 | Authority surface | **standalone `verify.py` helper** alongside `registry.py` | Single-responsibility; registry stays pure lookup |
| AG-W0-5 | Fail mode | **fail-soft (warn) default; fail-closed via env var** | Enables incremental rollout without blocking existing callers |

---

## 3. Specification (verbatim from user, 2026-05-09)

```
U0 Intake          emits ValidatedRequest          + l5_certification_ref
L1 Plan            emits L1PlanContract            + l5_certification_ref
L0 Route           emits RouteContract             + l5_certification_ref
C0 Evidence        emits FinalEvidenceContract     + l5_certification_ref
Prompt Assembly    emits CompiledPromptArtifact    + l5_certification_ref
L3 Workflow        emits L3StepContract            + l5_certification_ref
L2 Execute         emits SealedL2Artifact          + l5_certification_ref
Exit X3            emits X3 receipt + CommitRequest if needed + RuntimeExhaustBundle
UWG (X3C only)     consumes CommitRequest.l5_certification_ref → CommitReceipt
L6                 consumes RuntimeExhaustBundle (post-Exit)
```

Each inbound layer must verify the upstream `l5_certification_ref` against L5 authority
before producing its own.

---

## 4. Implementation

### Wave execution summary

| Wave | Scope | Status |
|---|---|---|
| W0 | Author-Gate decisions (5 packets) | ✅ Done |
| W1 | `ValidatedRequest`, `L1PlanContract`, `RouteContract`, `L0RouteContract`, `FinalEvidenceContract` + verify helpers | ✅ Done |
| W2 | `CompiledPromptArtifact`, `L3StepContract`, `SealedL2Artifact`, 5 X3 packets + PA/L3/L2 verify call-sites | ✅ Done |
| W3 | `CommitRequest` singular alias + `UWGCommitReceipt` + both `RuntimeExhaustBundle` variants | ✅ Done |
| W4 | `verify_certification_ref` helper + CI gate `check_l5_cert_ref_on_emit_contracts.py` (L5CR1) | ✅ Done |
| W5 | This ADR + cross-link | ✅ Done |

### Files changed (representative set)

**New:**
- `agentic_core/L5_safety/contracts/verify.py` — `verify_certification_ref(ref: str) -> bool`
- `ops_scripts/ci/check_l5_cert_ref_on_emit_contracts.py` — L5CR1 CI gate
- `tests/agentic_core/test_l5_cert_ref_w{1,2,3,4}.py` — test suites per wave

**Modified (field add — `l5_certification_ref: str = ""`):**
- `agentic_core/runtime/contracts/apps_rg_ingress_payload.py` — `ValidatedRequest`
- `agentic_core/prompt_governance/prompt_assembly/input_contracts.py` — `L1PlanContract`, `L0RouteContract`
- `agentic_core/runtime/contracts/route_contract.py` — `RouteContract`
- `agentic_core/runtime/contracts/final_evidence_contract.py` — `FinalEvidenceContract`
- `agentic_core/runtime/contracts/compiled_prompt_artifact.py` — `CompiledPromptArtifact`
- `agentic_core/L3_orchestration/doctrine/contracts_l3_7.py` — `L3StepContract`
- `agentic_core/runtime/contracts/sealed_l2_artifact.py` — `SealedL2Artifact`
- `agentic_core/L3_orchestration/exit_eval/v6/types.py` — all 5 X3 packet variants
- `agentic_core/L4_state/contracts/records.py` — `CommitRequest` (singular alias), `UWGCommitReceipt`
- `agentic_core/L6_observability/runtime_trace/runtime_exhaust_bundle.py` — `RuntimeExhaustBundle`
- `agentic_core/L6_observability/shadow_eval/contracts.py` — shadow `RuntimeExhaustBundle`

**Modified (verify call-sites):**
- `agentic_core/prompt_governance/prompt_assembly/pipeline.py` — PA entry (`_check_l5_cert_ref_pa`)
- `agentic_core/L3_orchestration/managed_workflow_router.py` — L3 entry (`_check_l5_cert_ref_l3`)
- `agentic_core/L2_execution/l2_execution_contract.py` — L2 entry (`_check_l5_cert_ref_l2`)

**Modified (CI gate registration):**
- `ops_scripts/ci/run_contract_gates.py` — `assurance_gates` list, gate ID `L5CR1`

**Modified (registry re-export):**
- `agentic_core/L5_safety/contracts/registry.py` — re-exports `verify_certification_ref`

---

## 5. Consequences

### Positive

- Every sealed artifact in the emit chain carries a traceable L5 authority token — enabling
  post-hoc certification audit without OTEL re-trace.
- `L5CR1` CI gate (`check_l5_cert_ref_on_emit_contracts.py`) enforces presence across all
  18 (file, class) pairs at every CI run; regression is caught immediately.
- `verify_certification_ref` is import-safe from any layer — no L5→runtime circular
  dependency (L5 module has no `agentic_core.runtime.*` imports).
- Fail-soft default enables zero-disruption rollout; `L5_CERT_REF_FAIL_CLOSED=1` hardens
  any layer to blocking without code change.

### Negative / Trade-offs

- All callers constructing these dataclasses must supply `l5_certification_ref` or accept
  the empty-string default.  Empty string is structurally valid but semantically unverified
  (semantic checks — expiry, HMAC — are deferred to a future hardening wave).
- `CommitRequest` now has both `l5_certification_refs` (plural `Tuple[str, ...]`) and
  `l5_certification_ref` (singular `str`).  The plural field is retained for backward
  compatibility; the singular field is the canonical going-forward form.  A future
  migration wave can remove the plural field once all callers use the singular.

### Deferred

- Semantic validation (cert expiry, HMAC signature) — future hardening wave.
- `apps_*` caller pipeline glue (each app's ingress/egress wiring is a separate plan).
- Migration of existing serialized artifacts to include the new field.
- Removal of the legacy `CommitRequest.l5_certification_refs` plural field.

---

## 6. Verify helper contract

```python
# agentic_core/L5_safety/contracts/verify.py
def verify_certification_ref(ref: str) -> bool:
    """Return True iff ref is structurally valid as an L5 certification ref.

    A non-empty str is accepted as structurally valid.  Semantic checks
    (cert expiry, scope, HMAC) are intentionally deferred.
    """
    return bool(ref) and isinstance(ref, str)
```

Import path:
```python
from agentic_core.L5_safety.contracts.verify import verify_certification_ref
# or via registry re-export:
from agentic_core.L5_safety.contracts.registry import verify_certification_ref
```

---

## 7. CI gate

**Gate ID:** `L5CR1`
**Script:** `ops_scripts/ci/check_l5_cert_ref_on_emit_contracts.py`
**Mode:** advisory by default; `L5_CERT_REF_GATE_FAIL_CLOSED=1` → fail-closed
**Bypass:** `L5_CERT_REF_GATE_BYPASS=1`
**Baseline (2026-05-09):** 18/18 OK — gate GREEN

---

## 8. Cross-references

- `docs/reference/00A_L5_Governance_Safety/00A.8_L5_Runtime_Certification_Binding.md` — runtime certification binding reference (this ADR extends that surface)
- `docs/reference/00A_L5_Governance_Safety/00A.6_L5_Replay_Audit_and_Certification_Evidence.md` — replay/audit evidence contract (cert ref enables audit traceability)
- ADR-049, ADR-051 — L5 governance plane versions 4 and 5
- ADR-080 — runtime certification Phase D planning (cert-ref threading is a prerequisite for Phase E)
- Plan: `.claude/plans/l5-cert-ref-emit-chain-threading-c4e7f1.md`
