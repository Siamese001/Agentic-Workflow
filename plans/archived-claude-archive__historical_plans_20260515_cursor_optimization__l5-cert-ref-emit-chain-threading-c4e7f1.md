---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\l5-cert-ref-emit-chain-threading-c4e7f1.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\l5-cert-ref-emit-chain-threading-c4e7f1.md'
source_sha256: 4fb88f157e60fa9895b5b41193d3701d960f4a27884785057dd4ef85911350b1
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan — Thread `l5_certification_ref` Through The Full Emit Chain

**Slug:** `l5-cert-ref-emit-chain-threading-c4e7f1`
**Tier:** T3 (architectural — cross-layer contract change touching U0 → L1 → L0 → C0 → PA → L3 → L2 → Exit → UWG → L6)
**Status:** Completed (all waves W0–W6 done)
**Created:** 2026-05-09
**Authoring mode:** plan only — no code changes in this session

---

## 1. Target

Make every inter-layer emit contract in `agentic_core/` carry an L5 certification reference, and make every inbound layer verify it against the L5 authority registry before emitting its own contract. Bring the codebase into alignment with the spec captured in §2.

This plan is a planning artifact only. Implementation lands in a follow-up plan after Author-Gate review of singular-vs-plural shape and L5 verify-call placement.

---

## 2. Spec (verbatim from user)

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

Each inbound layer must verify the upstream `l5_certification_ref` against L5 authority before producing its own.

---

## 3. Current State (validated 2026-05-09 from grep of `agentic_core/`)

| Stage | Contract | File | L5 cert ref present? |
|---|---|---|---|
| U0 | `ValidatedRequest` | `agentic_core/runtime/contracts/apps_rg_ingress_payload.py:74` | ❌ |
| L1 | `L1PlanContract` | `agentic_core/prompt_governance/prompt_assembly/input_contracts.py:26` | ❌ |
| L0 | `RouteContract` / `L0RouteContract` | `agentic_core/runtime/contracts/route_contract.py:12` + `…/input_contracts.py:44` | ❌ |
| C0 | `FinalEvidenceContract` | `agentic_core/runtime/contracts/final_evidence_contract.py:24` | ❌ |
| PA | `CompiledPromptArtifact` | `agentic_core/runtime/contracts/compiled_prompt_artifact.py:22` | ❌ |
| L3 | `L3StepContract` | `agentic_core/runtime/contracts/l3_step_contract.py` | ❌ |
| L2 | `SealedL2Artifact` | `agentic_core/runtime/contracts/sealed_l2_artifact.py:13` | ❌ |
| Exit | `X3DenyPacket` / `X3CommitRequestPacket` / `X3AllowPacket` / `X3SafeAbstainPacket` / `X3BreakGlassAllowPacket` | `agentic_core/L3_orchestration/exit_eval/v6/types.py:171-260` | ❌ |
| UWG | `CommitRequest` | `agentic_core/L4_state/contracts/records.py:760` | ✅ `l5_certification_refs: Tuple[str, ...]` (plural, line 783) |
| UWG | `UWGCommitReceipt` | `agentic_core/L4_state/contracts/records.py:858` | ❌ |
| L6 | `RuntimeExhaustBundle` | `agentic_core/L6_observability/runtime_trace/runtime_exhaust_bundle.py:90` + shadow variant `…/shadow_eval/contracts.py:190` | ❌ |

**Conformance ratio: 1 of 11 contracts.** L5 already publishes `previous_certification_ref` via its own doctrine output (`agentic_core/L5_safety/contracts/egress.py:1431` + registry at `agentic_core/L5_safety/contracts/registry.py:1380`), but this is L5's internal output namespace; nothing threads it through the inter-layer emit chain.

---

## 4. Open Design Questions — **RESOLVED W0 2026-05-09**

| # | Question | Decision | Rationale |
|---|---|---|---|
| AG-W0-1 | Singular vs plural | **`l5_certification_ref: str`** (singular) | Spec-aligned; CommitRequest plural migration deferred to W3 |
| AG-W0-2 | Field type | **plain `str`** (opaque cert ID) | Registry is authoritative for metadata; minimal contract footprint |
| AG-W0-3 | Verify call placement | **`__post_init__`** on each emit dataclass | Fail-fast at emit boundary; invalid cert cannot propagate |
| AG-W0-4 | Authority registry surface | **standalone helper** `verify_certification_ref(ref: str) -> bool` alongside `registry.py` | Single-responsibility; registry stays pure lookup table |
| AG-W0-5 | Fail mode at verify gate | **fail-closed** — `ValueError` on missing/invalid cert ref | Hard L5 safety guarantee from day 1; all W1 callers must supply valid ref |

---

## 5. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W0 | P0.1 | Author-Gate decisions on §4 questions (singular vs plural; type; verify placement; registry surface; fail-mode) | ~3k | Decisions captured via `DECISION_CAPTURED:` per §30 | ✅ Done | All 5 decisions answered; AG packets logged to refactor decision ledger |
| W1 | P1.1 — P1.3 | Add `l5_certification_ref` field to U0/L1/L0/C0 contracts; add inbound verify at L1, L0, C0 entry sites | ~12k | W0 decisions inform shape | ✅ Done | 4 contracts updated; `verify.py` helper created; `__post_init__` fail-closed on `ValidatedRequest`, `L1PlanContract`, `RouteContract`, `FinalEvidenceContract` |
| W2 | P2.1 — P2.3 | Add `l5_certification_ref` field to PA/L3/L2/X3 packets; add inbound verify at PA, L3, L2 entry sites | ~14k | W1 pattern reused | ✅ Done | `__post_init__` fail-closed on `CompiledPromptArtifact`, `SealedL2Artifact`, `L3RuntimeOrchestrationReceipt`, all 6 X3 packets; `l5_certification_ref` field added to `L3RuntimeOrchestrationReceipt` |
| W3 | P3.1 — P3.2 | Reconcile `CommitRequest.l5_certification_refs` (plural) with new singular convention; add field to `UWGCommitReceipt` and `RuntimeExhaustBundle` (both variants) | ~8k | Plural/singular decision from W0 final | ✅ Done | `__post_init__` fail-closed on `CommitRequest`, `UWGCommitReceipt`, `RuntimeExhaustBundle` (runtime_trace + shadow_eval); plural `l5_certification_refs` retained as-is; singular `l5_certification_ref` alias already present on `CommitRequest` |
| W4 | P4.1 — P4.2 | L5 authority registry verify helper; CI gate that asserts every W6 contract field-set contains `l5_certification_ref` | ~6k | Reuse `L5_safety/contracts/registry.py` per W0 decision | ✅ Done | `verify.py` helper created (W1); `check_l5_cert_ref_on_emit_contracts.py` existed with stale `L3StepContract` ref — corrected to `L3RuntimeOrchestrationReceipt`; gate runs 18/18 OK |
| W5 | P5.1 | Documentation + ADR + verify drift report | ~4k | All earlier waves landed | ✅ Done | `docs/architecture/adr/ADR-102-l5-cert-ref-emit-chain-threading.md` authored; implementation table of all 18 contracts; cross-links to `00A.8`, `00A.6`, `00A.2` L5 reference docs |
| W6 | P6.1 | Test regression pass — fix stale `_defaults_empty` tests from pre-W3 era; verify 86-test suite green | ~2k | W3 `__post_init__` enforce landed before test update | ✅ Done | 5 stale `_defaults_empty` tests in `test_l5_cert_ref_w3.py` updated to `_empty_raises` (with explicit `l5_certification_ref=""`); all 86 W1–W4 tests passing |

---

## 6. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P0.1 | Author-Gate decisions | none (planning packet only) | 5 design questions; need to drain queue before W1 | ~3k | ✅ Done |
| P1.1 | U0 + L1 emit field add | `apps_rg_ingress_payload.py`, `runtime/contracts/l1_plan_contract.py` | `l5_certification_ref` already present; added `__post_init__` fail-closed on `ValidatedRequest` + `L1PlanContract` | ~5k | ✅ Done |
| P1.2 | L0 emit field add (both `RouteContract` shapes) | `runtime/contracts/route_contract.py` | `l5_certification_ref` already present; added `__post_init__` fail-closed on `RouteContract`; `prompt_governance/input_contracts.py` L0RouteContract is permissive adapter — skip per design | ~3k | ✅ Done |
| P1.3 | C0 emit field add + verify at L1/L0/C0 entry | `runtime/contracts/final_evidence_contract.py`, `L5_safety/contracts/verify.py` (new) | `__post_init__` fail-closed on `FinalEvidenceContract`; `verify.py` standalone helper created; `registry.py` re-exports from `verify.py` | ~4k | ✅ Done |
| P2.1 | PA + L3 emit field add | `runtime/contracts/compiled_prompt_artifact.py`, `runtime/contracts/l3_runtime_orchestration_receipt.py` | `l5_certification_ref` already on PA; added field + verify to `L3RuntimeOrchestrationReceipt` (extends existing `__post_init__`); `l3_step_contract.py` does not exist — correct file is `l3_runtime_orchestration_receipt.py` | ~4k | ✅ Done |
| P2.2 | L2 + X3 packet field add | `runtime/contracts/sealed_l2_artifact.py`, `L3_orchestration/exit_eval/v6/types.py` (6 packet variants) | `l5_certification_ref` already present on all; added `__post_init__` fail-closed on `SealedL2Artifact` + all 6 X3 packets (Deny/Escalate/CommitRequest/Allow/SafeAbstain/BreakGlass) | ~6k | ✅ Done |
| P2.3 | PA/L3/L2 verify at entry | `runtime/contracts/compiled_prompt_artifact.py` + all emit dataclasses | Verify is at emit boundary via `__post_init__` on each dataclass — no separate entrypoint call-sites needed; pattern consistent with W1 | ~4k | ✅ Done |
| P3.1 | UWG receipt + L6 bundle field add | `L4_state/contracts/records.py` (`UWGCommitReceipt`), `L6_observability/runtime_trace/runtime_exhaust_bundle.py`, `L6_observability/shadow_eval/contracts.py` | `l5_certification_ref` already present on all three; added `__post_init__` fail-closed on `UWGCommitReceipt` + both `RuntimeExhaustBundle` variants | ~4k | ✅ Done |
| P3.2 | Plural/singular reconciliation | `L4_state/contracts/records.py` only | `CommitRequest` already had singular `l5_certification_ref` alias (line 784); `__post_init__` verify added on singular alias; plural tuple retained for backward compat; no shim needed | ~4k | ✅ Done |
| P4.1 | L5 authority verify helper | `L5_safety/contracts/verify.py` (created in W1), `L5_safety/contracts/registry.py` (re-export) | Standalone helper created with no runtime imports; registry re-exports; circular-import-safe | ~3k | ✅ Done (landed in W1) |
| P4.2 | CI gate for emit-contract field presence | `ops_scripts/ci/check_l5_cert_ref_on_emit_contracts.py` | Already existed with stale `L3StepContract` entry; corrected to `L3RuntimeOrchestrationReceipt`; gate verified 18/18 OK; registered in `run_contract_gates.py` as L5CR1 advisory | ~3k | ✅ Done |
| P5.1 | ADR + cross-link docs | `docs/architecture/adr/ADR-102-l5-cert-ref-emit-chain-threading.md` | ADR-102 authored with SCQA, decision, implementation table of 18 contracts, alternatives, rollback; cross-links to `00A.6`, `00A.8`, `00A.2` | ~4k | ✅ Done |
| P6.1 | Test regression pass | `tests/agentic_core/test_l5_cert_ref_w3.py` | 5 stale `_defaults_empty` tests expected empty construction to succeed; W3 `__post_init__` makes empty raise; updated to `_empty_raises` with explicit `l5_certification_ref=""`; 86/86 green | ~2k | ✅ Done |

---

## 7. Files In Scope

### Contract dataclasses (11)

- `agentic_core/runtime/contracts/apps_rg_ingress_payload.py` — `ValidatedRequest`
- `agentic_core/prompt_governance/prompt_assembly/input_contracts.py` — `L1PlanContract`, `L0RouteContract`
- `agentic_core/runtime/contracts/route_contract.py` — `RouteContract`
- `agentic_core/runtime/contracts/final_evidence_contract.py` — `FinalEvidenceContract`
- `agentic_core/runtime/contracts/compiled_prompt_artifact.py` — `CompiledPromptArtifact`
- `agentic_core/runtime/contracts/l3_step_contract.py` — `L3StepContract`
- `agentic_core/runtime/contracts/sealed_l2_artifact.py` — `SealedL2Artifact`
- `agentic_core/L3_orchestration/exit_eval/v6/types.py` — 5 X3 packet variants
- `agentic_core/L4_state/contracts/records.py` — `CommitRequest` (already partial), `UWGCommitReceipt`
- `agentic_core/L6_observability/runtime_trace/runtime_exhaust_bundle.py` — `RuntimeExhaustBundle`
- `agentic_core/L6_observability/shadow_eval/contracts.py` — shadow `RuntimeExhaustBundle`

### Verify call-sites (entry points to each layer — exact placement W0-decided)

- L1 entry: prompt_governance / managed_workflow planning sites
- L0 entry: routing dispatch in `agentic_core/L0_routing/`
- C0 entry: `agentic_core/L0_routing/c0_retrieval/` evidence assembly
- PA entry: `agentic_core/prompt_governance/prompt_assembly/`
- L3 entry: `agentic_core/L3_orchestration/managed_workflow_router.py`
- L2 entry: `agentic_core/L2_execution/` dispatch
- Exit entry: `agentic_core/L3_orchestration/exit_eval/v6/`
- UWG entry: `agentic_core/L4_state/uwg/durable_write_gateway.py`

### L5 authority surface

- `agentic_core/L5_safety/contracts/registry.py` (existing `previous_certification_ref` registration)
- `agentic_core/L5_safety/contracts/egress.py` (existing `PreviousCertificationRef(L5Ref)`)
- New helper file (path TBD by W0)

### CI / docs

- `ops_scripts/ci/check_l5_cert_ref_on_emit_contracts.py` (new)
- `ops_scripts/ci/run_contract_gates.py` (register new gate)
- `docs/architecture/adr/ADR-<NNN>-l5-cert-ref-emit-chain.md` (new)

---

## 8. Non-Goals

- Implementing `apps_*` callers' use of the new field (each app's pipeline glue is a separate plan).
- Migrating existing serialized artifacts under `artifacts/certification/` or `certification/agentic_core/` to include the new field — backward-compat is read-side only.
- Changing the L5 doctrine output `previous_certification_ref` itself.
- Adding runtime certification claims (Constitutional §32 — requires its own Author-Gate).
- Wiring L5 ref into `runtime_exhaust_bundle` shadow eval analytics paths beyond the dataclass field add.

---

## 9. Success Criteria

- All 11 contracts in §7 carry an L5 cert ref field (singular or plural per W0 decision).
- 8 verify call-sites in `agentic_core/` enforce the field on inbound, with fail-mode determined in W0.
- New CI gate `check_l5_cert_ref_on_emit_contracts.py` is green and registered.
- Test count grows by ≥40 (≈5 per layer × 8 layers) covering present, missing, malformed, and registry-mismatch ref cases.
- Zero regressions in `tests/_apps_contract/`, `tests/runtime/`, `tests/uwg/`.
- ADR authored, committed, and cross-linked from `docs/reference/00A_L5_Governance_Safety/`.

---

## 10. Author-Gate Queue Seeds

```
AG_QUEUE_SEED: plan=l5-cert-ref-emit-chain-threading-c4e7f1 id=AG-W0-1 depends_on= title=Singular l5_certification_ref vs plural l5_certification_refs (reconcile with existing CommitRequest field)
AG_QUEUE_SEED: plan=l5-cert-ref-emit-chain-threading-c4e7f1 id=AG-W0-2 depends_on=AG-W0-1 title=Field type — plain str id vs structured L5CertificationRef dataclass
AG_QUEUE_SEED: plan=l5-cert-ref-emit-chain-threading-c4e7f1 id=AG-W0-3 depends_on=AG-W0-1 title=Verify on emit (constructor) vs verify on consume (reader) vs both
AG_QUEUE_SEED: plan=l5-cert-ref-emit-chain-threading-c4e7f1 id=AG-W0-4 depends_on=AG-W0-2 title=Authority registry surface — extend existing L5 registry vs new verify helper
AG_QUEUE_SEED: plan=l5-cert-ref-emit-chain-threading-c4e7f1 id=AG-W0-5 depends_on=AG-W0-3 title=Fail-mode at each gate — fail-closed vs fail-soft during rollout
```

---

## 11. ADG_HOTSPOT_REPORT

Hotspot ranking restricted to the 11 emit-contract files plus their primary verify call-sites. Layer multipliers per constitutional §23: L0/L5 ×2.0, L3/L4 ×1.75, L1/L2 ×1.0, L6 ×0.75.

| Rank | Node | Layer | Archetype | Surfaces Intersected | Reason |
|---|---|---|---|---|---|
| 1 | `agentic_core/L4_state/contracts/records.py::CommitRequest` | L4 | `STATE_NODE` | Write, State, Security | Already carries plural `l5_certification_refs`; lone conformance point; reconciliation pivot |
| 2 | `agentic_core/L3_orchestration/exit_eval/v6/types.py::X3CommitRequestPacket` | L3 | `SAFETY_GATEKEEPER` | Security, Write, Observability | Sole authorized X3 disposition that produces a `CommitRequest` — must thread cert ref through the X3C → UWG handoff |
| 3 | `agentic_core/runtime/contracts/route_contract.py::RouteContract` | L0 | `CENTRAL_DEPENDENCY` | Execution, Security | High fan-in: every downstream layer reads RouteContract; missing cert ref blocks every layer's verify |
| 4 | `agentic_core/L5_safety/contracts/registry.py` | L5 | `SAFETY_GATEKEEPER` | Security, Observability | L5 authority registry — verify helper added here amplifies across all 8 verify call-sites |
| 5 | `agentic_core/runtime/contracts/sealed_l2_artifact.py::SealedL2Artifact` | L2 | `STATE_NODE` | Execution, Write, Observability | Carries `proposed_state_diff` with `state_diff_authorized` flag — cert ref binds authorization origin |
| 6 | `agentic_core/runtime/contracts/final_evidence_contract.py::FinalEvidenceContract` | L0/C0 | `STATE_NODE` | State, Security | C0 evidence is the authority anchor for prompt assembly — cert ref binds source-authority decisions |
| 7 | `agentic_core/runtime/contracts/compiled_prompt_artifact.py::CompiledPromptArtifact` | L1/PA | `ORCHESTRATOR` | Execution, Security | Prompt assembly fans out to every L2 invocation — cert ref propagation is high-multiplier |
| 8 | `agentic_core/L6_observability/runtime_trace/runtime_exhaust_bundle.py::RuntimeExhaustBundle` | L6 | `OBSERVABILITY_TERMINAL` | Observability, State | Post-Exit terminal; cert ref enables L6 promotion-eligibility audit per spec |

---

## 12. ADG_GRAPH_LAYER_EVIDENCE

### Materialized views

- `mv_hotspot_centrality` — to confirm `RouteContract` and `CommitRequest` rank in the top quartile of inter-layer fan-in (driving §11 ranks 3 and 1).
- `mv_dependency_cone_risk` — to size the blast radius of changing each contract dataclass (each new field is a constructor-signature change).
- `mv_chokepoint_bridges` — to identify whether the verify call-sites at each layer entry are chokepoints (high `betweenness_approx`) or distributed.

### Semantic edges

- `flows_to` — trace cert ref data flow from L5 registry → U0 emit → L1 verify → L1 emit → … → L6 consume. Confirms the spec's "every inbound verify" contract is satisfied.
- `reads_from` — find all reader sites of each contract dataclass (verify must precede each); 11 contracts × N readers.
- `resolves_callsite` — for each verify helper invocation, confirm the call resolves to the L5 registry helper (not a stub or shadow copy).

### P-views

- `v_p0_*` — surface any P0 critical-layer-break violations introduced by adding L5 imports into `runtime/contracts/` (must avoid `runtime/` ⇒ `L5_safety/` cycles).
- `v_p1_*` — surface mis-layered receivers; the verify helpers must live in L5, not in runtime/contracts.
- `v_p2_*` — confirm no contract dataclass becomes dormant or duplicated by the field add.

### Notes

ADG snapshot `05052026_0722` had zero `nodes_by_file` results for the small contract files (one-class modules likely below the symbol-extraction floor). The hotspot ranking in §11 falls back to L4_state/contracts/records.py module node (id=957) plus the structural classification in constitutional §23. A pre-W1 ADG re-ingest is in §13.

---

## 13. Pre-Wave Prerequisites

- ADG re-ingest: `python tools/generate_full_adg.py` then `python tools/adg/adg_redis_ingest.py --check` to ensure the contract dataclasses are indexed.
- W0 Author-Gate queue drained — all 5 packets answered and captured to refactor decision ledger.
- Constitutional §22 compliance verified on this plan via `ops_scripts/ci/check_graph_layer_evidence.py` (`ADG_GRAPH_LAYER_EVIDENCE` section is present).

---

## 14. References

- Spec source: user request 2026-05-09 19:10 UTC-04.
- Validation report: prior turn (validates 9 of 10 emit contracts lack the field).
- Constitutional §22 — graph-layer evidence required for T2/T3 plans.
- Constitutional §23 — ADG canonical invariants, archetype + surface classification.
- Constitutional §30 — `DECISION_CAPTURED:` for refactor-class Author-Gate answers.
- Constitutional §35 — Author-Gate queue drain after wave/phase completion.
- Constitutional §36 — plan-Notion registration mandatory.
- ADR pending under W5 (`P5.1`).

---

PLAN_CREATED: slug=l5-cert-ref-emit-chain-threading-c4e7f1 path=.windsurf/plans/l5-cert-ref-emit-chain-threading-c4e7f1.md status=not_started tier=T3 layer=cross-cutting
