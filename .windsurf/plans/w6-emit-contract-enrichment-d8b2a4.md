# Plan — W6 Emit-Contract Enrichment (10-Concern Umbrella)

**Slug:** `w6-emit-contract-enrichment-d8b2a4`
**Tier:** T3 (architectural — cross-layer contract enrichment touching every layer U0 → L1 → L0 → C0 → PA → L3 → L2 → Exit → UWG → L6)
**Status:** In Progress — W0 Done; W1 unblocked
**Created:** 2026-05-09
**Updated:** 2026-05-10 01:13 UTC-04 — W0 Author-Gate complete; all 12 decisions resolved
**Authoring mode:** plan only — no code changes in this session

**Depends on:** `.windsurf/plans/l5-cert-ref-emit-chain-threading-c4e7f1.md` (parent plan covering concern #2 L5 authority certification end-to-end). This umbrella plan **may not start** until the parent plan is `Status=Completed` in Notion Plans DB. Per user direction 2026-05-09 19:25 UTC-04, AG-W0-D1 is resolved as **(c) chain**: the narrow L5 plan executes first; this umbrella picks up the remaining 9 concerns.

This is the umbrella plan covering **9 of 10 concerns** from the gap analysis 2026-05-09 19:17 UTC-04. Concern #2 (L5 authority certification) is delivered by the parent plan — it is documented here for completeness only and does **not** consume waves/phases/tokens in this plan.

---

## 1. Target

Make every W6 inter-layer emit dataclass in `agentic_core/` carry the typed fields that the spec expects for every layer transition: identity quad, gate receipts, replay/determinism, observability, origin/data boundary, risk posture, capability/sandbox/egress allowlists, schema/hash/signature, and write/learning-firewall markers. **L5 authority cert ref is excluded — delivered by parent plan `l5-cert-ref-emit-chain-threading-c4e7f1`.**

The vocabulary already exists in `L4_state/contracts/records.py` and `L5_safety/contracts/`. This plan threads it through the 11 W6 emit contracts and adds inbound verify at each layer entry.

This plan is a planning artifact only. Implementation lands in scoped follow-up plans, and starts only after the parent plan reports `Status=Completed`.

---

## 2. Spec — 10 Concerns (verbatim from user 2026-05-09 19:17 UTC-04)

| # | Concern | Required fields |
|---|---|---|
| 1 | Identity | `request_id`, `run_id`, `tenant_id`, `trace_id` |
| 2 | L5 authority certification | policy, registry, capability, sandbox, egress, origin, replay/audit refs |
| 3 | Runtime gate receipts | proof required gates passed or failed |
| 4 | Replay / determinism | `replay_key`, snapshot refs, hashes |
| 5 | Observability / audit | OTEL span refs, audit refs |
| 6 | Origin / data boundary | user text = intent; retrieved/tool/model/human text = data unless certified |
| 7 | Risk / side-effect posture | read-only, external call, write intent, HITL required or not |
| 8 | Capability / sandbox / egress | what tools/models/files/network/output paths are allowed |
| 9 | Schema / hash / signature | proves packet shape and integrity |
| 10 | Write / learning firewall | `proposed_state_diff` only, UWG-only write, L6 future-run-only |

---

## 3. Validated Gap Matrix (from 2026-05-09 19:17 analysis)

Matrix dimensions: 10 concerns × 11 emit contracts. Severity ranked by missing-cell count × constitutional §23 layer multiplier. **Concern #2 row is shown for context only — closed by parent plan.**

| Severity | Concerns | Status here | Why |
|---|---|---|---|
| **Critical** | #2 L5 cert | **Out of scope — parent plan** | Delivered by `l5-cert-ref-emit-chain-threading-c4e7f1` |
| **Critical** | #8 capability/sandbox/egress | In scope (W3) | 11 contracts missing; affects L0/L2 |
| **High** | #5 OTEL/audit, #6 origin/airlock, #9 schema/signature | In scope (W5/W4/W6) | 7–11 contracts missing; tamper-evidence and airlock discipline gaps |
| **Medium** | #1 tenant_id, #3 gate receipts, #4 replay/determinism, #7 risk posture | In scope (W1/W7/W8) | 6–9 contracts missing; cross-cuts L3/L4 |
| **Low** | #10 write firewall | In scope (W9) | Enforced at gateway layer; contract-shape gap is documentation-grade |

---

## 4. The 11 Emit Contracts (in scope)

| # | Layer | Contract | File |
|---|---|---|---|
| 1 | U0 | `ValidatedRequest` | `agentic_core/runtime/contracts/apps_rg_ingress_payload.py` |
| 2 | L1 | `L1PlanContract` | `agentic_core/prompt_governance/prompt_assembly/input_contracts.py` |
| 3 | L0 (W6) | `RouteContract` | `agentic_core/runtime/contracts/route_contract.py` |
| 4 | L0 (PA-input) | `L0RouteContract` | `agentic_core/prompt_governance/prompt_assembly/input_contracts.py` |
| 5 | C0 | `FinalEvidenceContract` | `agentic_core/runtime/contracts/final_evidence_contract.py` |
| 6 | PA | `CompiledPromptArtifact` | `agentic_core/runtime/contracts/compiled_prompt_artifact.py` |
| 7 | L3 | `L3StepContract` (referenced; live shape lives in `l3_runtime_orchestration_receipt.py`) | `agentic_core/runtime/contracts/l3_runtime_orchestration_receipt.py` |
| 8 | L2 | `SealedL2Artifact` | `agentic_core/runtime/contracts/sealed_l2_artifact.py` |
| 9 | Exit | 5 X3 packet variants | `agentic_core/L3_orchestration/exit_eval/v6/types.py` |
| 10 | UWG | `CommitRequest`, `UWGCommitReceipt` | `agentic_core/L4_state/contracts/records.py` |
| 11 | L6 | `RuntimeExhaustBundle` (canonical + shadow variants) | `agentic_core/L6_observability/runtime_trace/runtime_exhaust_bundle.py` + `…/shadow_eval/contracts.py` |

---

## 5. Reference Vocabulary Sources (already in repo)

| Source | Provides |
|---|---|
| `agentic_core/L4_state/contracts/records.py` | `tenant_id`, `replay_key`, `audit_refs`, `gate_verdict_refs`, `sandbox_required`, `egress_policy_ref`, `allowed_networks`, `allowed_file_roots`, `policy_hash`, `blueprint_hash`, `schema_version`, `deterministic_digest`, `acl_tags`, `source_authority_class`, `data_class`, `hitl_reclearance_refs` |
| `agentic_core/L5_safety/contracts/egress.py` + `registry.py` | `L5Ref` base class, `PreviousCertificationRef`, doctrine output registry |
| `agentic_core/runtime/contracts/identity.py` | identity primitives (request_id/run_id/trace_id builders) |
| `agentic_core/runtime/contracts/lifecycle_trace_contract.py` | `replay_key`, OTEL span declarations, audit emit functions |
| `agentic_core/runtime/contracts/runtime_telemetry_decorators.py` | `emits_side_effect`, `appends_hash_chain`, `traces_execute` |
| `agentic_core/runtime/contracts/llm_gateway_contract.py` | controlled egress wrapper |

---

## 6. Cross-Cutting Design Questions (W0 Author-Gate decisions)

These decisions inform every later wave. They must be drained before W1 begins. **AG-W0-D1 is pre-resolved by user direction (chain order).** The parent plan's W0 may pre-resolve other questions; W0 here only drains the unresolved residue.

1. ~~**Umbrella vs split.**~~ **RESOLVED 2026-05-09 19:25 UTC-04 → chain.** Parent plan delivers concern #2 first; this umbrella delivers concerns #1, #3, #4, #5, #6, #7, #8, #9, #10 after.
2. **Field-shape convention.** Each new field as plain str ref vs structured dataclass? Should the convention be **per-concern uniform** or **whole-plan uniform**? **Likely pre-resolved by parent plan AG-W0-2** — adopt parent's choice for cross-plan consistency unless explicit reason to diverge.
3. **Singular vs plural reconciliation.** Are new ref fields singular or plural? **Likely pre-resolved by parent plan AG-W0-1** — adopt parent's choice for cross-plan consistency.
4. **Verify-call placement.** Constructor-time (each emit dataclass `__post_init__`) vs reader-time (each consume site) vs both? **Likely pre-resolved by parent plan AG-W0-3** — adopt parent's choice; the same 8 verify call-sites are reused.
5. **Authority registry surface.** Extend `L5_safety/contracts/registry.py` vs add `L5_safety/verify.py` helper. **Likely pre-resolved by parent plan AG-W0-4** — reuse the helper landed by W4 of parent plan.
6. **Tenant_id source.** Where does tenant_id originate — U0 ingress payload, L5 issuance, or app-domain config? Threading must converge on one origin. *Not addressed by parent plan — first wave-blocking decision here.*
7. **Origin/data-boundary tagging shape.** Is `EvidenceItem.source_authority_class` (slice of L4 vocabulary) sufficient, or does each prompt block / tool result carry a typed `Origin` enum (`USER_INTENT`, `RETRIEVED_DATA`, `TOOL_OUTPUT`, `MODEL_GENERATION`, `HUMAN_REVIEW_DATA`)? *Not addressed by parent plan.*
8. **Schema_version naming.** Existing: `contract_version` (W6 contracts), `schema_version` (L4 records), `L4_CONTRACT_SCHEMA_VERSION` constant. Standardize on one across all 11 contracts? *Not addressed by parent plan.*
9. **Signature kind.** HMAC (matches `L0RouteContract.hmac_sig`), Ed25519, or sigstore-style? Per-layer-issued or one chain signature across the whole emit chain? *Not addressed by parent plan.*
10. **Fail-mode at each verify gate.** Fail-closed vs fail-soft (logged) during rollout? **Likely pre-resolved by parent plan AG-W0-5** — adopt parent's choice for cross-plan consistency.
11. **Backward-compat strategy.** All new fields default-empty so existing callers compile, vs hard cutover with caller migration tracked per wave? *Not addressed by parent plan.*
12. **CI gate strategy.** One umbrella gate `check_w6_emit_contract_enrichment.py` that asserts all 9 concerns vs 9 separate gates (one per concern)? *Not addressed by parent plan.*

**Net W0 here:** at most 7 unresolved decisions (#6, #7, #8, #9, #11, #12 plus any that parent plan elects not to standardize). The other 5 inherit parent plan's answers via the refactor decision ledger lookup.

---

## 7. Wave Structure

**Note:** old W2 (concern #2 L5 cert ref) is removed — delivered by parent plan. Remaining waves renumbered W2 → W9 (was W3 → W10). Total wave count drops from 11 → 10.

| Wave | Phase IDs | Focus | Concern # | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|---|
| W0 | P0.1 — P0.2 | Author-Gate decisions on §6 (≤7 unresolved + 5 inherited from parent plan) | cross-cutting | ~4k | Parent plan W0 decisions readable via refactor decision ledger; AG-W0-D1 already resolved (chain order) | ✅ Done | All 12 decisions answered (D2–D5, D10 inherited; D6–D9, D11–D12 fresh AG); ledger rows captured |
| W1 | P1.1 — P1.2 | Concern #1 — `tenant_id` added to all 11 contracts; identity quad standardized | #1 | ~8k | D6=U0 ingress (app_id→tenant_id); D11=default-empty | Not Started | All 11 contracts carry full `(request_id, run_id, tenant_id, trace_id)`; +20 tests |
| W2 | P2.1 — P2.4 | Concern #8 — capability/sandbox/egress fields stamped on `RouteContract`, `CompiledPromptArtifact`, `SealedL2Artifact`, `CommitRequest`; verify against `CapabilityRegistryRecord` / `ToolCatalogRecord` | #8 | ~16k | D11=default-empty; D3=`__post_init__` verify | Not Started | 4 emit contracts carry sandbox/egress allowlists; verify rejects out-of-allowlist tool/model use; +25 tests |
| W3 | P3.1 — P3.3 | Concern #6 — origin/data boundary `Origin` enum tagging on `EvidenceItem`, `PromptBlock`, `SealedL2Artifact.generated_content` (wrap as `OriginTaggedContent`) | #6 | ~14k | D7=typed Origin enum + OriginTaggedContent; new `runtime/contracts/origin.py` | Not Started | Every text payload in the chain is origin-typed; airlock CI gate green; +20 tests |
| W4 | P4.1 — P4.2 | Concern #5 — `otel_span_refs` and `audit_refs` tuples added to all 11 contracts | #5 | ~10k | D11=default-empty tuples; OTEL bridge already exists | Not Started | All 11 contracts carry `otel_span_refs: Tuple[str, ...]` + `audit_refs: Tuple[str, ...]`; +15 tests |
| W5 | P5.1 — P5.2 | Concern #9 — `schema_version` field standardized across all 11 contracts; per-layer `signature` field (HMAC) | #9 | ~12k | D8=rename all to `schema_version`; D9=HMAC-SHA256 reusing `L0RouteContract.hmac_sig` pattern | Not Started | All 11 contracts carry `schema_version` + `signature`; signature verification helper added; +20 tests |
| W6 | P6.1 — P6.3 | Concerns #3 + #7 — typed `RuntimePosture` struct (`read_only`, `external_call`, `write_intent`, `hitl_required`); typed `GateVerdictRef` array on every emit; reuse existing `gate_verdict_refs` on `CommitRequest` | #3, #7 | ~16k | D11=default-empty; new `runtime/contracts/posture.py` | Not Started | All 11 contracts carry posture + verdict refs; +25 tests |
| W7 | P7.1 — P7.2 | Concern #4 — `replay_key`, `snapshot_refs`, `deterministic_digest` standardized across all 11 contracts (currently only on CommitRequest + L3 receipt) | #4 | ~10k | D11=default-empty; `lifecycle_trace_contract.py` source | Not Started | All 11 contracts carry `replay_key` + `snapshot_refs`; replay determinism CI gate green; +15 tests |
| W8 | P8.1 — P8.2 | Concern #10 — explicit `write_firewall_marker` (e.g. `is_uwg_write_authority: bool`, `is_future_run_only: bool`) on relevant contracts | #10 | ~6k | D11=default False; gateway already enforces | Not Started | `SealedL2Artifact`/`X3CommitRequestPacket`/`CommitRequest`/`RuntimeExhaustBundle` carry firewall markers; +10 tests |
| W9 | P9.1 — P9.4 | CI gates (9 per-concern) + ADR + docs cross-link + final integration test sweep | cross-cutting | ~14k | D12=9 separate gates; all earlier waves landed | Not Started | Up to 9 CI gates registered in `run_contract_gates.py`; ADR(s) authored at `docs/architecture/adr/`; reference docs cross-linked under `docs/reference/00A_L5_Governance_Safety/`; full `tests/_apps_contract/` + `tests/runtime/` + `tests/uwg/` sweeps green |

**Total est. tokens: ~110k** (down from ~164k after parent plan absorbs W2's ~52k). W0 complete. W1 is next. W2–W9 remain Not Started.

---

## 8. Phase-Level Summary

**Note:** old W2 phases P2.1–P2.6 are removed (delivered by parent plan). Remaining phases renumbered to keep wave→phase prefix alignment. Total phase count: 33 → 25.

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P0.1 | Author-Gate decisions — inherit from parent plan ledger (D2, D3, D4, D5, D10) | refactor decision ledger lookup | Must verify ledger entries exist; else escalate to fresh AG | ~2k | ✅ Done — D2=plain str, D3=`__post_init__`, D4=standalone helper, D5=fail-closed, D10=default-empty+plural retained |
| P0.2 | Author-Gate decisions D6–D9, D11–D12 (tenant_id origin, origin enum, schema naming, signature kind, back-compat, CI strategy) | none | D7 is the airlock-doctrine pivot; D11 affects rollout sequencing | ~2k | ✅ Done — D6=U0 ingress, D7=Origin enum, D8=schema_version, D9=HMAC-SHA256, D11=default-empty, D12=9 per-concern gates |
| P1.1 | Identity quad — `tenant_id` field add to 11 contracts | all 11 contract files | D6: tenant_id = app_id value at U0; default-empty on downstream contracts | ~4k | Not Started |
| P1.2 | Identity verify at every layer entry | 8 verify call-sites | Surrogate `app_id` field already exists; reconcile | ~4k | Not Started |
| P2.1 | Capability/sandbox/egress — `RouteContract` + `CompiledPromptArtifact` field add | 2 contracts | Tie to `ToolCatalogRecord` registry | ~4k | Blocked |
| P2.2 | Capability/sandbox/egress — `SealedL2Artifact` field add (capability_used + sandbox_class_used + egress_used) | 1 contract | Records actual use; verify at L2 dispatch | ~4k | Blocked |
| P2.3 | Capability/sandbox/egress — `CommitRequest` field add (already partial via `affected_state_surfaces`) | 1 contract | Reuse vs new field decision | ~4k | Blocked |
| P2.4 | Allowlist verify at L0 + L2 dispatch sites | 2 verify sites | High touch; existing dispatch must wrap | ~4k | Blocked |
| P3.1 | `Origin` enum + `OriginTaggedContent` wrapper class | new module under `runtime/contracts/origin.py` | W0 #7 decision fixes shape | ~5k | Blocked |
| P3.2 | Apply origin tagging to `EvidenceItem`, `PromptBlock`, `SealedL2Artifact.generated_content` | 3 contracts | Touch every text-payload field | ~5k | Blocked |
| P3.3 | Airlock verify at PA + L2 + Exit | 3 verify sites + new CI gate | Doctrine: user-text = intent only | ~4k | Blocked |
| P4.1 | `otel_span_refs` + `audit_refs` field add to 11 contracts | all 11 contract files | Mechanical; mostly plural tuples | ~5k | Blocked |
| P4.2 | OTEL bridge + audit emitter wires set the new fields at emit time | `otel_lifecycle_bridge.py`, audit emitters | Avoid double-emit | ~5k | Blocked |
| P5.1 | `schema_version` field standardization (rename `contract_version`/`assembly_version`/`route_version` → `schema_version`) | all 11 contracts | Migration of existing field name | ~6k | Blocked |
| P5.2 | `signature` field + HMAC helper | all 11 contracts + new helper | Reuse `L0RouteContract.hmac_sig` precedent | ~6k | Blocked |
| P6.1 | `RuntimePosture` typed struct definition | new module | Replaces ad-hoc bool flags | ~4k | Blocked |
| P6.2 | Apply `posture` field to L1/L0/C0/PA/L2/X3/L6 | 7 contracts | `L1PlanContract.risk_hint` migrates into struct | ~6k | Blocked |
| P6.3 | `GateVerdictRef` array standardization (already on CommitRequest) | 11 contracts | Reuse L4 audit-ledger shape | ~6k | Blocked |
| P7.1 | `replay_key` + `snapshot_refs` field add to 11 contracts | all 11 contracts + bridge to `lifecycle_trace_contract.py` | Existing `compilation_hash` retained or migrated | ~5k | Blocked |
| P7.2 | Replay determinism CI gate + integration test | new CI gate | Asserts replay_key uniqueness + snapshot ref non-empty | ~5k | Blocked |
| P8.1 | `write_firewall_marker` field + per-contract default | 4 contracts (L2/Exit/UWG/L6) | Boolean flags; codifies gateway invariants | ~3k | Blocked |
| P8.2 | Firewall verify at gateway entry | `durable_write_gateway.py` | Belt-and-braces — gateway already enforces | ~3k | Blocked |
| P9.1 | CI gates registration | `ops_scripts/ci/run_contract_gates.py` + 1–9 new gate files | W0 #12 decides count | ~4k | Blocked |
| P9.2 | ADR(s) authored | `docs/architecture/adr/ADR-NNN-w6-emit-contract-enrichment.md` (+ optional sub-ADRs) | Spec §2 verbatim | ~4k | Blocked |
| P9.3 | Reference doc cross-link | `docs/reference/00A_L5_Governance_Safety/`, `docs/reference/_primers/` | Multi-file edit | ~2k | Blocked |
| P9.4 | Final integration sweep | full test suites | Catch late regressions | ~4k | Blocked |

---

## 9. Files In Scope

### Contract dataclasses (11)

- `agentic_core/runtime/contracts/apps_rg_ingress_payload.py`
- `agentic_core/prompt_governance/prompt_assembly/input_contracts.py`
- `agentic_core/runtime/contracts/route_contract.py`
- `agentic_core/runtime/contracts/final_evidence_contract.py`
- `agentic_core/runtime/contracts/compiled_prompt_artifact.py`
- `agentic_core/runtime/contracts/l3_runtime_orchestration_receipt.py`
- `agentic_core/runtime/contracts/sealed_l2_artifact.py`
- `agentic_core/L3_orchestration/exit_eval/v6/types.py` (5 X3 packets)
- `agentic_core/L4_state/contracts/records.py` (`CommitRequest`, `UWGCommitReceipt`)
- `agentic_core/L6_observability/runtime_trace/runtime_exhaust_bundle.py`
- `agentic_core/L6_observability/shadow_eval/contracts.py`

### Verify call-sites (8 layer entries)

- `agentic_core/L0_routing/` (L1/L0/C0 entry)
- `agentic_core/L0_routing/c0_retrieval/` (C0 entry)
- `agentic_core/prompt_governance/prompt_assembly/` (PA entry)
- `agentic_core/L3_orchestration/managed_workflow_router.py` (L3 entry)
- `agentic_core/L2_execution/` (L2 entry)
- `agentic_core/L3_orchestration/exit_eval/v6/` (Exit entry)
- `agentic_core/L4_state/uwg/durable_write_gateway.py` (UWG entry)
- `agentic_core/L6_observability/runtime_trace/` (L6 entry)

### Authority/registry surfaces

- `agentic_core/L5_safety/contracts/registry.py` (extend per W0 #5)
- `agentic_core/L5_safety/contracts/egress.py` (existing `L5Ref` base class)
- New `agentic_core/L5_safety/verify.py` helper (TBD by W0)

### New typed primitives (TBD by W0)

- `agentic_core/runtime/contracts/origin.py` — `Origin` enum + `OriginTaggedContent` (W4)
- `agentic_core/runtime/contracts/posture.py` — `RuntimePosture` struct (W7)
- `agentic_core/runtime/contracts/signature.py` — HMAC helper (W6)

### CI / docs

- Up to 10 new gates in `ops_scripts/ci/` (W10 — W0 #12 decides count)
- `ops_scripts/ci/run_contract_gates.py` (register new gates)
- `docs/architecture/adr/ADR-NNN-w6-emit-contract-enrichment.md` (+ optional sub-ADRs per concern)
- `docs/reference/00A_L5_Governance_Safety/` cross-links

---

## 10. Non-Goals

- Implementing `apps_*` callers' use of the new fields (each app's pipeline glue is a separate plan per app).
- Migrating existing serialized artifacts under `artifacts/certification/` or `certification/agentic_core/` to include the new fields — backward-compat is read-side only.
- Changing existing L4 records schema (vocabulary borrowed, not modified).
- Adding runtime certification claims (Constitutional §32 — requires separate Author-Gate).
- Performance regression analysis (deferred until all waves land).
- Cross-process serialization wire format upgrades (separate plan).
- L5 doctrine output `previous_certification_ref` redesign — reused as-is.

---

## 11. Success Criteria

- 8 verify call-sites enforce the fields on inbound, with fail-mode determined in W0 (or inherited from parent plan).
- All 11 contracts in §4 carry the typed fields for the 9 concerns covered by this umbrella (concern #2 already delivered by parent plan).
- Up to 9 CI gates are green and registered (umbrella vs per-concern decided in W0 #12).
- Test count grows by ≥145 (≈18 per wave × 8 implementation waves; W0 + W9 are non-test waves) across `tests/_apps_contract/`, `tests/runtime/`, `tests/uwg/`, `tests/unit/`.
- Zero regressions in existing test suites.
- ADR authored and cross-linked from `docs/reference/00A_L5_Governance_Safety/`.
- Constitutional §22 graph-layer evidence checked on every wave's plan refresh.

---

## 12. Author-Gate Queue Seeds

**Note:** AG-W0-D1 is pre-resolved (chain order — see §1 Depends-on header). D2/D3/D4/D5/D10 likely inherit from parent plan ledger (verified in P0.1). Only D6, D7, D8, D9, D11, D12 are guaranteed-fresh decisions here.

```
AG_QUEUE_SEED: plan=w6-emit-contract-enrichment-d8b2a4 id=AG-W0-D6 depends_on= title=tenant_id origin U0 ingress vs L5 issuance vs app-domain config
AG_QUEUE_SEED: plan=w6-emit-contract-enrichment-d8b2a4 id=AG-W0-D7 depends_on= title=Origin tagging shape Origin enum vs source_authority_class string slice
AG_QUEUE_SEED: plan=w6-emit-contract-enrichment-d8b2a4 id=AG-W0-D8 depends_on= title=schema_version naming standardize across all 11 contracts (rename contract_version/assembly_version/route_version)
AG_QUEUE_SEED: plan=w6-emit-contract-enrichment-d8b2a4 id=AG-W0-D9 depends_on= title=Signature kind HMAC vs Ed25519 vs sigstore per-layer vs chain
AG_QUEUE_SEED: plan=w6-emit-contract-enrichment-d8b2a4 id=AG-W0-D11 depends_on= title=Backward-compat strategy default-empty fields vs hard cutover with caller migration
AG_QUEUE_SEED: plan=w6-emit-contract-enrichment-d8b2a4 id=AG-W0-D12 depends_on= title=CI gate strategy one umbrella gate vs nine per-concern gates
```

---

## 13. ADG_HOTSPOT_REPORT

Hotspot ranking restricted to the 11 emit-contract files plus their primary verify call-sites and the L4/L5 vocabulary sources. Layer multipliers per constitutional §23: L0/L5 ×2.0, L3/L4 ×1.75, L1/L2 ×1.0, L6 ×0.75.

| Rank | Node | Layer | Archetype | Surfaces Intersected | Reason |
|---|---|---|---|---|---|
| 1 | `agentic_core/L4_state/contracts/records.py` | L4 | `STATE_NODE` | Write, State, Security, Observability | Pivot — already carries 9 of the 10 concerns' vocabulary; donor for the cross-layer threading |
| 2 | `agentic_core/runtime/contracts/route_contract.py::RouteContract` | L0 | `CENTRAL_DEPENDENCY` | Execution, Security | High fan-in: every downstream layer reads RouteContract; missing fields block every layer's verify |
| 3 | `agentic_core/L5_safety/contracts/registry.py` | L5 | `SAFETY_GATEKEEPER` | Security, Observability | Authority registry — every verify path lands here; helper extension amplifies across 8 verify sites |
| 4 | `agentic_core/L3_orchestration/exit_eval/v6/types.py` (5 X3 packets) | L3 | `SAFETY_GATEKEEPER` | Security, Write, Observability | X3 packets are the gate to UWG; threading must preserve `X3CommitRequestPacket` → `CommitRequest` field carry-forward |
| 5 | `agentic_core/runtime/contracts/sealed_l2_artifact.py::SealedL2Artifact` | L2 | `STATE_NODE` | Execution, Write, Observability | Carries `proposed_state_diff` + `state_diff_authorized`; concerns #6, #7, #8, #10 all touch this contract |
| 6 | `agentic_core/runtime/contracts/final_evidence_contract.py::FinalEvidenceContract` | L0/C0 | `STATE_NODE` | State, Security | C0 evidence is the source-authority anchor for prompt assembly; concern #6 origin/airlock pivot |
| 7 | `agentic_core/runtime/contracts/compiled_prompt_artifact.py::CompiledPromptArtifact` | L1/PA | `ORCHESTRATOR` | Execution, Security | PA fans out to every L2 invocation; concerns #6, #8, #9 all touch prompt blocks |
| 8 | `agentic_core/L4_state/contracts/records.py::CommitRequest` | L4 | `STATE_NODE` | Write, State, Security | Already partial conformance; reconciliation pivot for plural vs singular and cross-concern field naming |
| 9 | `agentic_core/L6_observability/runtime_trace/runtime_exhaust_bundle.py::RuntimeExhaustBundle` | L6 | `OBSERVABILITY_TERMINAL` | Observability, State | Terminal contract; concerns #4, #5, #9, #10 all add fields here; shadow variant must stay parallel |
| 10 | `agentic_core/runtime/contracts/lifecycle_trace_contract.py` | L6 | `ORCHESTRATOR` | Observability | Replay_key + OTEL emit source; concerns #4 + #5 plumb their refs from this module |

---

## 14. ADG_GRAPH_LAYER_EVIDENCE

### Materialized views

- `mv_hotspot_centrality` — confirms `RouteContract`, `CommitRequest`, `L4_state/contracts/records.py` rank in the top quartile of inter-layer fan-in (driving §13 ranks 1–3).
- `mv_dependency_cone_risk` — sizes the blast radius of changing each contract dataclass. Each new field is a constructor-signature change; cone tells the wave's caller-update scope.
- `mv_chokepoint_bridges` — identifies whether the verify call-sites at each layer entry are chokepoints (high `betweenness_approx`); `durable_write_gateway.py` and `managed_workflow_router.py` expected to dominate.
- `mv_critical_path_blast_radius` — sizes the critical path from U0 emit through L6 consume; each concern's field thread runs end-to-end on this path.
- `mv_graph_chokepoint_bridges` — confirms `runtime/contracts/__init__.py` re-exports as the single import seam; reduces breakage scope.

### Semantic edges

- `flows_to` — trace each concern's data flow through the chain (e.g. `tenant_id` from U0 → L6; `replay_key` from L5 → CommitRequest → L6 exhaust).
- `reads_from` — find all reader sites of each contract dataclass (verify must precede each reader; concern #2 has 8 entries, others fewer).
- `resolves_callsite` — for each verify helper invocation, confirm the call resolves to the L5 registry helper (not a stub or shadow copy).
- `emits_side_effect` — surfaces L6/UWG write-eligibility paths; concern #10 firewall markers must align with these emit declarations.
- `controls_flow` — gate decisions at X3 packets and `durable_write_gateway`; concern #3 gate-receipts threading must preserve control-flow semantics.

### P-views

- `v_p0_*` — surface any P0 critical-layer-break violations introduced by adding L5 imports into `runtime/contracts/` (must avoid `runtime/` ⇒ `L5_safety/` cycles).
- `v_p1_*` — surface mis-layered receivers; verify helpers must live in L5, not in `runtime/contracts/`.
- `v_p2_*` — confirm no contract dataclass becomes dormant or duplicated by the field adds.
- `v_p3_*` — surface isolated experimental dataclasses that should be culled before adding new fields (esp. shadow `RuntimeExhaustBundle`).

### Notes

ADG snapshot `05052026_0722` returned zero `nodes_by_file` results for several small contract files (one-class modules below the symbol-extraction floor). A pre-W1 ADG re-ingest is mandated in §15. Existing module-level node `id=957` for `L4_state/contracts/records.py` confirms the L4 vocabulary source is graph-resident with full edge fan-out.

---

## 15. Pre-Wave Prerequisites

- **Parent plan `l5-cert-ref-emit-chain-threading-c4e7f1` reports `Status=Completed` in Notion Plans DB.** This is the hard gate. Cascade MUST verify via `API-query-data-source` before any wave starts.
- ADG re-ingest: `python tools/generate_full_adg.py` then `python tools/adg/adg_redis_ingest.py --check` to ensure all 11 contract dataclasses are indexed.
- W0 Author-Gate queue drained — at most 6 unresolved packets answered (D6, D7, D8, D9, D11, D12) and captured to refactor decision ledger.
- W0 ledger lookup confirms parent plan answered D2, D3, D4, D5, D10 — adopt those answers; only escalate to fresh AG if the parent plan ledger row is missing or contradicts intent.
- Constitutional §22 compliance verified on this plan via `ops_scripts/ci/check_graph_layer_evidence.py` (`ADG_GRAPH_LAYER_EVIDENCE` section is present).

---

## 16. Sequencing & Risk

- **Hard gate:** parent plan `l5-cert-ref-emit-chain-threading-c4e7f1` MUST be `Status=Completed` before W0 starts. The L5-cert-ref scaffolding (verify helper, registry surface, default fail-mode) is a load-bearing prerequisite for W2/W3/W4/W5 here.
- **W0 → W1 → W2 sequence is mandatory.** W1 (tenant_id) sets identity-quad shape; W2 (capability/sandbox/egress) consumes the L5 verify helper landed by parent plan; later waves layer on the W1+W2 base.
- **W2, W3, W4, W5 may parallelize** after W1 completes — concern #8 (capability), #6 (origin), #5 (OTEL), #9 (schema/signature) operate on disjoint field sets.
- **W6, W7 should run after W2+W5** because posture (#7) and replay_key (#4) reference capability and signature primitives.
- **W8, W9 last** — firewall markers and CI/ADR codify the prior waves.
- **Risk: contract version churn.** Every wave changes constructor signatures; callers across `apps_*`, `tests/_apps_contract/`, `tests/runtime/` need updating. W0 #11 fail-mode + default-empty strategy mitigates. **Parent plan will have already churned the same constructors once for L5 cert ref** — additive churn here.
- **Risk: import cycles.** `runtime/contracts/` cannot import from `L5_safety/` directly without inversion. **Parent plan W0 #5 already settled this** — reuse its helper placement.
- **Risk: serialization drift.** Existing JSON artifacts under `artifacts/`/`certification/` may fail schema-version checks if W5 standardizes naming. Non-goal §10 sets backward-compat to read-side only.
- **Risk: parent plan delay.** If parent plan is descoped or split mid-execution, this umbrella's wave numbering and AG inheritance assumptions break. Mitigation: re-validate via P0.1 ledger lookup before W1; treat any missing inherited decision as a fresh AG packet.

---

## 17. References

- Spec source: user request 2026-05-09 19:17 UTC-04.
- Validation report: prior turn (10-concern × 11-contract gap matrix).
- Parent plan (hard prerequisite): `.windsurf/plans/l5-cert-ref-emit-chain-threading-c4e7f1.md` — delivers concern #2 L5 authority cert ref end-to-end. Must be `Status=Completed` before this umbrella starts.
- Constitutional §22 — graph-layer evidence required for T2/T3 plans.
- Constitutional §23 — ADG canonical invariants, archetype + surface classification.
- Constitutional §30 — `DECISION_CAPTURED:` for refactor-class Author-Gate answers.
- Constitutional §35 — Author-Gate queue drain after wave/phase completion.
- Constitutional §36 — plan-Notion registration mandatory.
- ADRs pending under W9 (`P9.2`).

---

PLAN_CREATED: slug=w6-emit-contract-enrichment-d8b2a4 path=.windsurf/plans/w6-emit-contract-enrichment-d8b2a4.md status=not_started tier=T3 layer=cross-cutting
