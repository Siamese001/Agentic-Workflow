# ADR-102: Thread `l5_certification_ref` Through the Full Agentic Emit Chain

**Status**: ACCEPTED
**Date**: 2026-05-09
**Phase**: l5-cert-ref-emit-chain-threading-c4e7f1 W0–W4
**Deciders**: Codex + user Author-Gate (W0 packet, 2026-05-09)
**ADG Snapshot**: `artifacts/adg/adg_indexed_<ts>.sqlite` (structural; cross-layer contract change)

---

## Context (SCQA)

- **Situation** — Every inter-layer emit contract in `agentic_core/` passes data across an architectural boundary (U0 → L1 → L0 → C0 → PA → L3 → L2 → Exit → UWG → L6). The L5 authority layer (`L5_safety/`) holds a registry of certified refs (`registry.py`, `egress.py`) but no mechanism forces each boundary-crossing contract to carry a reference back to that certification. The field `l5_certification_ref` had been added opportunistically to several dataclasses (e.g. `CommitRequest`, X3 packets) but was absent or unverified on others.

- **Complication** — Without a uniform field and a fail-closed verify at each emit site, L5 governance is advisory rather than enforced: a contract can cross a layer boundary without any L5 lineage. The W3/W4 Fort Knox certification pipeline (`compile_requirement_signoff.py`) treats L5 evidence as a hard prerequisite. A missing ref on any inter-layer contract creates a silent gap in the certification chain.

- **Question** — How do we make L5 certification evidence mandatory and verifiable at every inter-layer contract emit boundary across the full agentic pipeline?

- **Answer** — Add a singular `l5_certification_ref: str = ""` field (defaulting to empty for backward compat) to every emit-contract dataclass, and enforce its presence at emit time via `__post_init__` using a standalone `verify_certification_ref` helper. A CI gate asserts field presence statically.

---

## Decision

Thread `l5_certification_ref: str = ""` through all 18 canonical inter-layer emit-contract dataclasses in `agentic_core/`, verify it fail-closed at each emit boundary via `__post_init__`, and enforce presence with CI gate `L5CR1` (`ops_scripts/ci/check_l5_cert_ref_on_emit_contracts.py`).

---

## Consequences

### Positive
- Every inter-layer contract carry an L5 lineage pointer — the certification chain is no longer advisory.
- `__post_init__` fail-closed verify catches missing refs at instantiation time, not at downstream consumers.
- CI gate L5CR1 prevents regression: new contracts added to the emit chain without `l5_certification_ref` fail the gate.
- Consistent singular field name across all 18 contracts simplifies downstream tooling and audit scans.

### Negative
- All 18 dataclass constructors now require a non-empty `l5_certification_ref` — existing callers that omit the field will raise `ValueError` at runtime (intentional fail-closed; callers must be updated).
- `CommitRequest` retains the legacy plural `l5_certification_refs: Tuple[str, ...]` for backward compat with serialized artifacts; the new singular alias is the enforced field.

### Neutral
- `verify_certification_ref` is a thin helper in `L5_safety/contracts/verify.py` (no heavy registry lookup at instantiation); full registry validation is deferred to the runtime certification path.
- `L1PlanContract` and `L0RouteContract` in `prompt_governance/prompt_assembly/input_contracts.py` carry the field but are permissive input adapters (no `__post_init__` enforcement) — they are included in the L5CR1 field-presence scan but not the fail-closed verify.

---

## Alternatives Considered

| Option | Pros | Cons | Why rejected |
|---|---|---|---|
| Plural `l5_certification_refs: Tuple[str, ...]` on all contracts | Matches existing `CommitRequest` shape; multi-ref chain possible | Harder to scan/verify; breaks existing singular callers; W0 AG decision rejected | Rejected by W0 Author-Gate packet |
| Optional `l5_certification_ref: str \| None` | Cleaner "absent" vs "empty" semantic | None-check adds branching; empty string is sufficient sentinel for advisory mode | Rejected by W0 Author-Gate packet |
| Central verify call-site per layer (not `__post_init__`) | Single verify point per layer | Requires modifications to every layer dispatcher; contracts remain unguarded if dispatcher bypassed | `__post_init__` is simpler and guards the contract at the point of construction regardless of caller |
| No enforcement (field-only) | Zero caller breakage | Provides no fail-closed guarantee; CI gate alone is insufficient for runtime safety | Rejected — goal is fail-closed, not advisory |

---

## Implementation Notes

### Contracts updated (W1–W3)

| Layer | File | Class | Wave |
|---|---|---|---|
| U0 | `agentic_core/runtime/contracts/apps_rg_ingress_payload.py` | `ValidatedRequest` | W1 |
| L1 | `agentic_core/runtime/contracts/l1_plan_contract.py` | `L1PlanContract` | W1 |
| L0 | `agentic_core/runtime/contracts/route_contract.py` | `RouteContract` | W1 |
| C0 | `agentic_core/runtime/contracts/final_evidence_contract.py` | `FinalEvidenceContract` | W1 |
| PA | `agentic_core/runtime/contracts/compiled_prompt_artifact.py` | `CompiledPromptArtifact` | W2 |
| L3 | `agentic_core/runtime/contracts/l3_runtime_orchestration_receipt.py` | `L3RuntimeOrchestrationReceipt` | W2 |
| L2 | `agentic_core/runtime/contracts/sealed_l2_artifact.py` | `SealedL2Artifact` | W2 |
| Exit | `agentic_core/L3_orchestration/exit_eval/v6/types.py` | `X3DenyPacket` | W2 |
| Exit | `agentic_core/L3_orchestration/exit_eval/v6/types.py` | `X3EscalatePacket` | W2 |
| Exit | `agentic_core/L3_orchestration/exit_eval/v6/types.py` | `X3CommitRequestPacket` | W2 |
| Exit | `agentic_core/L3_orchestration/exit_eval/v6/types.py` | `X3AllowPacket` | W2 |
| Exit | `agentic_core/L3_orchestration/exit_eval/v6/types.py` | `X3SafeAbstainPacket` | W2 |
| Exit | `agentic_core/L3_orchestration/exit_eval/v6/types.py` | `X3BreakGlassAllowPacket` | W2 |
| UWG | `agentic_core/L4_state/contracts/records.py` | `CommitRequest` | W3 |
| UWG | `agentic_core/L4_state/contracts/records.py` | `UWGCommitReceipt` | W3 |
| L6 | `agentic_core/L6_observability/runtime_trace/runtime_exhaust_bundle.py` | `RuntimeExhaustBundle` | W3 |
| L6 | `agentic_core/L6_observability/shadow_eval/contracts.py` | `RuntimeExhaustBundle` | W3 |

*Permissive adapters scanned but not fail-closed:* `L1PlanContract`, `L0RouteContract` (`prompt_governance/prompt_assembly/input_contracts.py`)

### Helper and registry

- `agentic_core/L5_safety/contracts/verify.py` — standalone `verify_certification_ref(ref: str) -> bool`; circular-import-safe; no runtime registry lookup at instantiation.
- `agentic_core/L5_safety/contracts/registry.py` — re-exports `verify_certification_ref` for callers that already import from registry.

### CI gate

- `ops_scripts/ci/check_l5_cert_ref_on_emit_contracts.py` — static AST scan over 18 (file, class) pairs; advisory by default; `L5_CERT_REF_GATE_FAIL_CLOSED=1` to enforce; `L5_CERT_REF_GATE_BYPASS=1` to skip.
- Registered in `ops_scripts/ci/run_contract_gates.py` as label `L5CR1 emit-contract l5_certification_ref field scan (advisory)`.
- Verified green: 18/18 OK (2026-05-09).

### Rollback path

Remove `__post_init__` methods from the 17 fail-closed dataclasses; the field itself is backward-compatible (defaults to `""`). CI gate reverts to advisory automatically.

---

## References

- Related ADRs: ADR-080 (runtime certification binding), ADR-050 (intelligence-ledger family), ADR-023 (HITL runtime HITL)
- Related plans: `.claude/plans/l5-cert-ref-emit-chain-threading-c4e7f1.md`
- L5 reference docs:
  - `docs/reference/00A_L5_Governance_Safety/00A.8_L5_Runtime_Certification_Binding.md`
  - `docs/reference/00A_L5_Governance_Safety/00A.6_L5_Replay_Audit_and_Certification_Evidence.md`
  - `docs/reference/00A_L5_Governance_Safety/00A.2_L5_Authority_Context_and_Registry_Binding.md`
- Constitutional rules: §8 (guardian exemptions), §22 (ADG graph-layer primary), §32 (Fort Knox certification integrity)
