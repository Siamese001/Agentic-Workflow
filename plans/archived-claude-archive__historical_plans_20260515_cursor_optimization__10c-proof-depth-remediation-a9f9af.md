---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\10c-proof-depth-remediation-a9f9af.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\10c-proof-depth-remediation-a9f9af.md'
source_sha256: 63b3f696104e3b9ad0ee99b469790668b559d6fb4c691b383ac7ed547d9ecc2c
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# 10C Proof-Depth Remediation Plan

> **Source overlay**: `C:\Users\amita\Documents\10c_requirement_proof_depth_certification_overlay.xlsx` (336 KB, 6 sheets, generated 2026-04-30 17:56 UTC)
> **Generator caveat (from overlay)**: "Generated from CSV ledger metadata only. It does not inspect source tests or proof bundle JSON files."
> **Decision rule (from overlay)**: "A row is not accepted unless actual proof depth meets or exceeds required proof depth."

**Status**: Draft / Author-Gate pending
**Tier**: T3
**Total estimated tokens**: ~38,000
**Created**: 2026-04-30
**Plan file**: `.windsurf/plans/10c-proof-depth-remediation-a9f9af.md`

---

## 1. The headline gap

| Metric | Count |
|---|---:|
| Total rows in 10C matrix | 200 |
| Prior-state ACCEPTED | 198 |
| **Recomputed SATISFIED** (proof depth meets requirement) | **117** ✅ |
| **Recomputed PARTIAL** (proof depth shortfall) | **83** ❌ |
| Downgraded from prior ACCEPTED | 83 |
| Runtime-claim allowed (post-recomputation) | 113 |

The matrix is **only 117/200 = 58.5% honestly accepted** under the proof-depth rules — not 198/200 as the unhardened ledger claimed. The 83-row gap is the work this plan addresses.

## 2. The gap is highly concentrated (only 3 distinct classes)

| Class | Count | Required depth | Actual depth | Blocking gap (verbatim from overlay) |
|---|---:|---|---|---|
| **G1: OTEL export missing** | **81** | `E7_REAL_OTEL_EXPORT` | `E4_NEGATIVE_CONTROL` | Ledger metadata shows test/proof bundle, but not real collector-backed OTEL export or span/counter correlation. |
| **G2: Semantic-cache composition** | **1** | `E5_COMPOSITION_PROOF` | `E4_NEGATIVE_CONTROL` | Semantic cache row needs proof beyond RouteContract: live query_vec vs cached vector, different surface forms, threshold pass/miss, freshness/policy/tenant compatibility, unsafe-reuse negatives, terminal RET/Exit receipts. |
| **G3: Provenance-chain composition** | **1** | `E5_COMPOSITION_PROOF` | `E4_NEGATIVE_CONTROL` | Requires composed production-component proof with provenance chain; ledger metadata only supports component/negative evidence. |

> **Insight**: 81 of 83 gaps (97.6%) are the SAME shortfall — the 81 OBSERVABILITY_RUNTIME REQs have unit-test-grade evidence but no real-collector-backed OTEL export proof. **One reusable harness fixes 97.6% of the gap.**

## 3. Owner-surface distribution (G1's 81 rows)

| Owner | Count | Sample REQ_IDs |
|---|---:|---|
| L6 observability | 8 | 128, 129, 130, 131, 132, 133, 134, 200 |
| C0 governance | 7 | 110, 111, 112, 113, 114, 115, 116 |
| L4/UWG | 7 | 122–126, 149, 152 |
| L2 execution | 6 | 091–094, 175, 197 |
| C7 capability | 6 | 155, 156, 158–161 |
| L5/gateway | 4 | 050–052, 055 |
| L5 exit control | 4 | 095, 097, 099, 172 |
| L1 cognition | 3 | 061, 070, 174 |
| HITL L5 | 3 | 100, 101, 176 |
| L0 routing | 2 | 075, 077 |
| L6 shadow eval | 2 | 104, 173 |
| L2/L5, L3 healing, architecture, knowledge/chunking, etc. | 31 | scattered |

By semantic-class surface: **58 of 81 land in "D. Governance / capability / replay / observability"** — concentration confirms the OTEL harness is the right unit of work.

## 4. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| **W1** | W1.1–W1.3 | Build single OTEL collector-backed proof harness | 12,000 | OTEL infrastructure already exists in `agentic_core/runtime/.../otel_emitter.py` and `agentic_core/L6_observability/`; harness binds to existing emitters + adds collector receipt verification | Todo | Harness produces a tamper-checked bundle (OTEL run digest + collector receipt SHA + span list) for any REQ supplying its expected `otel_span_ref`; tests pass for 5 sample REQs spanning 5 different owners |
| **W2** | W2.1–W2.2 | Build 2 composition-proof harnesses for G2 + G3 | 6,000 | G2 (REQ-077 semantic cache) and G3 (REQ-128 L6 composition) each need a one-off proof script that chains live components | Todo | Each composition harness emits a bundle with `proof_classification=COMPOSITION_PROOF`, provenance chain documented, replay-deterministic |
| **W3** | W3.1–W3.5 | Apply W1 harness to 81 G1 REQs; bind upgraded bundles | 14,000 | Sweep across 5 owner clusters (L6/L4/L2/C7/L5 = ~31; C0 = 7; remaining scattered = 12; misc = 7); each cluster is its own bind PR | Todo | All 81 G1 REQs get upgraded `proof_bundles/10c-req-NNN.json` with `actual_proof_depth=E7_REAL_OTEL_EXPORT`; CSV `proof_depth_status` flips to `SATISFIED`; merkle root regenerated |
| **W4** | W4.1–W4.2 | Validate + recompute matrix + final attestation | 4,000 | All previous waves green | Todo | Re-run overlay generator: prior-PARTIAL count drops from 83 → ≤2 (only G2/G3 remaining if those didn't bind); new merkle root committed to `artifacts/requirements/10c_pilot_merkle_root.json`; INVENTORY.md updated |
| **W5** | W5.1 | Update `harden_10c_ledger.py` + regenerate CSV matrix | 2,000 | The CSV at `docs/reports/design/10c_reconciliation/10c_semantic_requirement_ledger.csv` is regenerated from ledger | Todo | CSV's `evidence_status`, `final_acceptance_status`, `acceptance_caveat` columns reflect post-remediation state for all 200 rows |

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| W1.1 | Design `tools/proof/otel_collector_proof.py` harness | new file ~250 LOC; reads `otel_span_expected` from ledger; runs target test under in-memory OTEL exporter; validates expected spans land; SHA-256 over canonical span dump | OTel collector-vs-in-memory: rule says E7=collector-backed, in-memory may need separate tier (E7-in-mem) | 4,000 | Todo |
| W1.2 | Wire collector-backed mode (E7 strict) | docker-compose otel-collector or in-process pipeline; receipt format = JSON with collector ack | Real collector adds CI runtime cost | 5,000 | Todo |
| W1.3 | Tests for harness on 5 sample REQs (one per owner cluster) | `tests/unit/tools/proof/test_otel_collector_proof.py` | Snapshot stability | 3,000 | Todo |
| W2.1 | `tools/proof/composition_proof_semantic_cache.py` for REQ-077 | covers live query_vec → cached vector → threshold → receipt | Determinism on FP comparison | 3,000 | Todo |
| W2.2 | `tools/proof/composition_proof_provenance_chain.py` for REQ-128 | composed component chain with provenance | Provenance schema | 3,000 | Todo |
| W3.1 | Bind L6 observability cluster (8 REQs: 128–134, 200) | `artifacts/requirements/proof_bundles/10c-req-{128..134,200}.json` regenerated with E7 evidence | REQ-128 also touched by W2.2 (overlap — coordinate sequence) | 2,500 | Todo |
| W3.2 | Bind L4/UWG cluster (7 REQs: 122–126, 149, 152) + L2/C7 (12 REQs) | bundle regen | UWG-specific span shapes | 3,500 | Todo |
| W3.3 | Bind L5 cluster (4 gateway + 4 exit control + 3 HITL = 11 REQs) | bundle regen | L5 has multiple sub-surfaces | 3,000 | Todo |
| W3.4 | Bind C0/C7 governance cluster (7 + 6 = 13 REQs) | bundle regen | governance vs capability span semantics | 2,500 | Todo |
| W3.5 | Bind remaining scattered REQs (~30 across 12 owners) | bundle regen | per-owner one-offs; lowest density | 2,500 | Todo |
| W4.1 | Recompute merkle root + write attestation | `artifacts/requirements/10c_pilot_merkle_root.{json,md}` regen | Atomic with W3 closure | 2,000 | Todo |
| W4.2 | Re-run overlay generator + verify | regenerate xlsx (or replicate the generator); verify PARTIAL count ≤2 | Generator may not be in this repo | 2,000 | Todo |
| W5.1 | Patch `tools/requirements/harden_10c_ledger.py` + regenerate CSV | `docs/reports/design/10c_reconciliation/10c_semantic_requirement_ledger.csv` updated | Need to extend ledger schema with `actual_proof_depth` column | 2,000 | Todo |

## 6. ADG_HOTSPOT_REPORT

This plan is evidence-binding work, not structural refactoring — the hotspot ranking is light:

| Rank | File / Area | Layer | Fan-in | Archetype | Surface | Why on plan |
|---:|---|---|---:|---|---|---|
| 1 | `tools/proof/otel_collector_proof.py` (NEW) | L_TOOLS | 0 (new) | ORCHESTRATOR | Observability | Harness consumed by 81 REQs |
| 2 | `agentic_core/runtime/.../otel_emitter.py` | L_PG / L6 | high | CENTRAL_DEPENDENCY | Observability | Existing OTel emit surface that the harness wraps |
| 3 | `agentic_core/L6_observability/*` | L6 | mid | STATE_NODE | Observability | Owners of 8 G1 REQs |
| 4 | `tools/requirements/harden_10c_ledger.py` | L_TOOLS | mid | ORCHESTRATOR | State | Computes the CSV matrix; needs schema extension for `actual_proof_depth` |
| 5 | `artifacts/requirements/proof_bundles/*` | L_DATA | n/a | STATE_NODE | State | 81 bundles regenerated |

Layer multipliers (per `adg-canonical-invariants.md` §6):
- L6 observability x0.75 → 60.75 weight (8 × 0.75 × 10 fan-in factor)
- L_TOOLS x1.0 → harness creation is mid-priority structural work
- No L0/L5 ×2.0 hotspots fired (this is observability-tier work, not safety/routing)

**Net**: light hotspot profile. Single new tool drives 97.6% of remediation. No safety-plane disruption.

## 7. ADG_GRAPH_LAYER_EVIDENCE

Materialized views consulted (per constitutional §22):

1. **`mv_graph_reverse_dependency_hotspots`** — confirmed `agentic_core/runtime/.../otel_emitter.py` is high-fan-in (sound foundation for harness to wrap)
2. **`mv_hotspot_centrality`** — no L0/L5 hotspots in the 81 G1 REQs' owner files; confirms the work is observability-tier
3. **`mv_dependency_cone_risk`** — REQ-077 (L0 routing semantic cache) sits in a 7-deep cone via SemanticCacheManager → R1B threshold → cache_proof; W2.1 harness must respect this depth

Semantic edges:
- `emits_side_effect` (L6 observability → OTEL collectors) — the verification target
- `flows_to` (L1/L2/L3/L4/L5 → L6 via OTEL) — the spans to verify

P-views cross-referenced:
- `v_p2_duplicated_adapters` — none of the 81 G1 REQs land in P2 dedup territory; clean

## 8. Anti-cheat invariants (must not violate during execution)

1. **No fabricated runtime evidence** — same as the 2 pedagogical stubs: bundles upgraded by W3 must claim ONLY what was actually proven by the W1 harness run. If a REQ's owner test doesn't actually emit the expected span, mark `proof_depth_status=PARTIAL` and document the residual gap, do not claim E7.
2. **Replay determinism** — every upgraded bundle MUST include a `replay_digest` over canonical span dump; two runs of the harness on the same code MUST yield the same digest.
3. **Collector receipts are real** — the harness must include the collector's actual ack/receipt (or in-memory exporter's deterministic span dump SHA), not a synthesized claim.
4. **Merkle root regeneration is non-optional** — every bundle change requires recomputation; the existing `f6aa5c8b…ef4f0` root MUST update.
5. **Honest classification of residuals** — if W2 cannot fully prove G2 (semantic cache) or G3 (provenance chain) within scope, leave them as `ACCEPTED_WITH_CAVEAT` like REQ-011 / REQ-162. Do not falsely claim composition proof.

## 9. Dependencies & Sequencing

```
W1 (harness)  ─────────────┐
                           ▼
                       W3 (sweep) ──► W4 (recompute) ──► W5 (CSV regen)
                           ▲
W2 (composition) ──────────┘
```

W1 must finish before W3 can start. W2 can run in parallel with W1 (independent harnesses). W4 and W5 are sequential to W3.

## 10. Out of scope for this plan

- The `artifacts/runtime/requirements_proof/` consolidation (deferred 2026-04-30 in the SSOT folder consolidation; 104 hardcoded refs)
- Re-running the OVERLAY GENERATOR itself — the user's xlsx was generated externally; we don't have that script in-repo. W4.2 might require either (a) reverse-engineering the generator from the xlsx structure or (b) producing our own gap-analysis script that reads the post-remediation ledger and verifies all PARTIAL → SATISFIED transitions
- Non-10C requirement universes (the 150-REQ Step 1 baseline at `docs/reference/contracts/enforcement/`)
- Migrating any existing tests; this plan ONLY adds new evidence/harness, does not modify existing tests' behavior

## 11. Open questions (Author-Gate items embedded in the plan)

1. **W1.2 — collector mode**: Real collector (`docker-compose otel-collector`) vs in-memory (`opentelemetry.sdk.trace.export.InMemorySpanExporter`)? In-memory is faster + CI-friendly but is technically E6.5_INTEGRATED_RUNTIME, not strict E7_REAL_OTEL_EXPORT. The overlay rule reads "Collector-backed observability export is proven" — strict reading requires a real collector. **Author-Gate when W1.2 starts.**
2. **W3 PR granularity**: 5 cluster-PRs (per phase 3.1–3.5) or 1 mega-PR with 81 bundle updates? Cluster gives reviewability; mega-PR ships faster. **Author-Gate when W3 starts.**
3. **W2.1 + W2.2 — fail-safe for unprovable composition**: If REQ-077 or REQ-128 cannot be proven cleanly (e.g., production semantic cache requires real persistence), do we accept ACCEPTED_WITH_CAVEAT like the pedagogical stubs, or block the plan until W4 cannot close? **Author-Gate when W2 starts.**

## 12. Definition of done

This plan is COMPLETE when ALL of the following hold:

- [ ] `tools/proof/otel_collector_proof.py` exists and produces deterministic bundles (W1)
- [ ] G2 + G3 composition harnesses exist and produce bundles for REQ-077 and REQ-128 (W2)
- [ ] All 81 G1 REQ bundles in `artifacts/requirements/proof_bundles/` show `actual_proof_depth=E7_REAL_OTEL_EXPORT` (or honest `ACCEPTED_WITH_CAVEAT` for any unprovable subset) (W3)
- [ ] New merkle root committed to `artifacts/requirements/10c_pilot_merkle_root.json` (W4)
- [ ] CSV at `docs/reports/design/10c_reconciliation/10c_semantic_requirement_ledger.csv` shows `evidence_status=PROOF_PRESENT` and `acceptance_caveat=""` for the 81 upgraded rows (W5)
- [ ] Re-running the overlay generator (or our equivalent) shows `Generated PARTIAL ≤ 2` (only G2/G3 if not closed)
- [ ] `INVENTORY.md` references this plan as the source-of-record for the upgrade
- [ ] No anti-cheat invariant from §8 violated (every claim cryptographically backed)

## 13. Provenance

- Overlay file: `C:\Users\amita\Documents\10c_requirement_proof_depth_certification_overlay.xlsx`
- Overlay generated: 2026-04-30 17:56:38 UTC
- Source ledger CSV: `docs/reports/design/10c_reconciliation/10c_semantic_requirement_ledger.csv`
- Plan author: Cascade
- Plan created at git HEAD: `5ef982ea14`
- Author-Gate decisions referenced: 2026-04-30 (refactor_scope, finish_two_items + single_ssot_home_retire_satellites)
