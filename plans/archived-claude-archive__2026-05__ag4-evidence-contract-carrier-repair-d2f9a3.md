---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\ag4-evidence-contract-carrier-repair-d2f9a3.md'
original_relative_path: '_archive\\2026-05\\ag4-evidence-contract-carrier-repair-d2f9a3.md'
source_sha256: 80e161b923b581e9dee2f891caeb2e56eb685ea6177e052e9e5a0cab44e4e903
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
slug: ag4-evidence-contract-carrier-repair-d2f9a3
status: In Progress
tier: T3
dod_exempt: false
created: 2026-05-10
---

# AG-4 — Evidence Contract Carrier Repair

## Goal

Fix the two P0 contract gaps surfaced by AG-3 (`artifacts/apps_embedding_gap_analysis/apps_embedding_contract_alignment.json`) before any new embeddings, re-ingestion, R1B wiring, or ChromaDB cleanup.

## Hard Laws (verbatim from user)

- No embedding generation.
- No ChromaDB mutation / re-ingestion.
- No R1B wiring in this plan.
- No repo_* duplicate cleanup in this plan.
- No app-local runtime restoration.
- No C0 / PA / L2 / Exit / UWG bypass.
- Additive contract changes only unless tests prove safe migration.
- Backwards compatibility preserved.
- UNKNOWN never PASS.
- NOT_APPLICABLE requires reason.
- Retrieved text remains data only, never instruction.

## Discovery Findings (pre-edit)

- `EvidenceItem` (4 fields) and `FinalEvidenceContract` (16 fields) live at `agentic_core/runtime/contracts/final_evidence_contract.py`.
- `ExitReviewPacket` ALREADY EXISTS as a comprehensive dataclass at `agentic_core/L3_orchestration/exit_eval/v6/types.py:69-167` (90+ fields). 11+ test files reference it. Three additional definitions exist as test/spine envelopes (`tests/e2e/proof/contracts.py`, `apps_shared/spine_emission/contracts.py`, `apps_qna/types/spine_contracts.py`) — those remain untouched in this plan.
- `X1CheckoutResult` does NOT exist as a class. Only `_x1_checkout(context) -> bool` boolean helpers exist (e.g. `apps_eval/integrations/exit_adapter.py:37`).
- `SealedL2Artifact` already carries `prompt_artifact_digest`, `replay_key`, `snapshot_refs`, `otel_span_refs`, `audit_refs`, `gate_verdict_refs`, `allowed_tools/models/networks/file_roots`. Missing: `evidence_refs`, `tool_call_refs`, `model_call_refs`, `provider_receipts`, `replay_manifest`, `audit_manifest_ref`.
- `X3Disposition` carries scalar `eval_score` only — no structured groundedness verdict.
- 50+ tests construct these contracts; ALL changes must be additive with default values.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| W1 | P1.1 | Extend `EvidenceItem` with 24 spec fields (all defaults) | ~3k | ✅ DONE | EvidenceItem has dense_score, bm25_score, source_id, source_version, chunk_digest, citation_anchor, fact_vec_ref, ACL/freshness/origin_trust/contradiction/stratum/allowed_prompt_slot/support_score/support_status/retrieval_method fields. Existing tests still pass. |
| W1 | P1.2 | Extend `FinalEvidenceContract` with 17 new ref/map/receipt fields | ~2k | ✅ DONE | route_contract_ref, retrieval_plan_ref, query_vec_ref, dense_search_refs, sparse_search_refs, metadata_filter_refs, graph_expansion_refs, evidence_strata, citation_map, source_lineage_map, source_version_map, acl_verification_receipts, freshness_receipts, contradiction_report, support_status, support_score_profile, excluded_evidence_refs, blocked_source_refs, weak_support_refinement_attempts, final_evidence_digest. |
| W2 | P2.1 | Update apps_rg C0 emitter to populate new fields with explicit `UNKNOWN`/`NOT_APPLICABLE` reasons | ~3k | ✅ DONE | apps_rg c0_binding emits new fields without fabrication. |
| W3 | P3.1 | Extend canonical `ExitReviewPacket` (additive — opaque ref tuples + execution_form + registry_digest_set + l5_certification_refs + runtime_gate_refs + audit_manifest_ref + tool/model_call_refs + provider_receipts) | ~3k | ✅ DONE | All AG-4 W4 spec fields present; 90+ pre-existing fields untouched. |
| W3 | P3.2 | Create `X1CheckoutResult` + `X1Item` at new file `agentic_core/runtime/contracts/x1_checkout_result.py` | ~3k | ✅ DONE | X1A..X1J slots; PASS/FAIL/WARN/UNKNOWN/NOT_APPLICABLE; UNKNOWN-never-PASS guard; NOT_APPLICABLE requires reason. |
| W4 | P4.1 | Extend `SealedL2Artifact` with missing AG-4 W7 fields (additive) | ~2k | ✅ DONE | evidence_refs, tool_call_refs, model_call_refs, provider_receipts, replay_manifest, audit_manifest_ref. |
| W5 | P5.1 | Tests covering all AG-4 W8 invariants | ~5k | ✅ DONE | 12 invariants asserted; UNKNOWN-never-PASS, NOT_APPLICABLE-requires-reason, dense/sparse/graph/ACL/freshness/citation/contradiction/support coverage. |
| W5 | P5.2 | CI gate `ops_scripts/ci/check_evidence_contract_carriers.py` | ~2k | ✅ DONE | Static AST check enforces field presence; bypass `EVIDENCE_CARRIER_BYPASS=1`. |
| W6 | P6.1 | Emit 4 W9 artifacts | ~3k | ✅ DONE | ag4_evidence_contract_carrier_repair_report.md, ag4_contract_field_coverage.json, ag4_exit_review_packet_schema.json, ag4_acceptance_evidence.json |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1.1 | Extend EvidenceItem | `agentic_core/runtime/contracts/final_evidence_contract.py` | Frozen dataclass — must reorder fields so defaults are last | 3k | done |
| P1.2 | Extend FinalEvidenceContract | same file | Same frozen-dataclass discipline | 2k | done |
| P2.1 | apps_rg C0 emitter wiring | `agentic_core/runtime/c0/apps_rg_c0_binding.py` | apps_rg uses verbatim text path — populate new EvidenceItem fields with explicit `NOT_APPLICABLE` (no retrieval) | 3k | done |
| P3.1 | Extend ExitReviewPacket | `agentic_core/L3_orchestration/exit_eval/v6/types.py` | 90+ existing fields; must not break test compat | 3k | done |
| P3.2 | New X1CheckoutResult | `agentic_core/runtime/contracts/x1_checkout_result.py` (NEW) | First-time class; X1A..X1J slot fields | 3k | done |
| P4.1 | Extend SealedL2Artifact | `agentic_core/runtime/contracts/sealed_l2_artifact.py` | 30+ existing fields; same frozen-dataclass discipline | 2k | done |
| P5.1 | Tests | `tests/_apps_contract/test_ag4_evidence_contract_carriers.py` (NEW) | 12 invariants × multiple shapes | 5k | done |
| P5.2 | CI gate | `ops_scripts/ci/check_evidence_contract_carriers.py` (NEW) | Pure-AST field-presence check | 2k | done |
| P6.1 | Artifacts | `artifacts/apps_embedding_gap_analysis/ag4_*.{md,json}` | 4 files | 3k | done |

## Definition of Done

- DoD-1: `python -c "from agentic_core.runtime.contracts.final_evidence_contract import EvidenceItem; assert all(f in {f.name for f in __import__('dataclasses').fields(EvidenceItem)} for f in ['dense_score','bm25_score','citation_anchor','chunk_digest','support_status','allowed_prompt_slot','origin_trust_label','acl_status','freshness_status','contradiction_status','stratum'])"` exits 0.
- DoD-2: `python -c "from agentic_core.runtime.contracts.x1_checkout_result import X1CheckoutResult, X1Item, X1Verdict"` exits 0.
- DoD-3: `python -c "from agentic_core.L3_orchestration.exit_eval.v6.types import ExitReviewPacket; import dataclasses as dc; f={f.name for f in dc.fields(ExitReviewPacket)}; assert {'evidence_refs','tool_call_refs','model_call_refs','provider_receipts','runtime_gate_refs','audit_manifest_ref','registry_digest_set','execution_form','l5_certification_refs'} <= f"` exits 0.
- DoD-4: `python -m pytest tests/_apps_contract/test_ag4_evidence_contract_carriers.py -q` exits 0.
- DoD-5: `python ops_scripts/ci/check_evidence_contract_carriers.py` exits 0.
- DoD-6: Pre-existing FEC/EvidenceItem/SealedL2Artifact tests still pass: `python -m pytest tests/runtime/test_c0_evidence_contract.py tests/runtime/test_l2_execution_seal.py tests/runtime/test_end_to_end_grounded_read.py -q` exits 0.

### Verification vs Deferral

| Surface | Verified now | Deferred to follow-up |
|---|---|---|
| Contract field additions | ✅ Tested via DoD-1..3 | — |
| C0 apps_rg emitter | ✅ NOT_APPLICABLE reason populated | populating per-app fields for apps_qna / apps_repo_brief / apps_underwriting_ai / apps_research / apps_rfp / apps_eval / apps_lic — those C0 paths flow through generic run_c0 + spine_handoff and need separate plans |
| Exit minimal wire | ✅ Field presence verified | full Exit X1A..X1J evaluator wiring |
| L2 preservation | ✅ Field presence verified | populating evidence_refs from PA component_hash_map automatically |
| 12 invariant tests | ✅ All pass | judge-grader integration for groundedness verdict |
| CI gate | ✅ Static AST check | runtime CI integration into `run_contract_gates.py` (non-blocking advisory for now) |

## ADG_HOTSPOT_REPORT

| Rank | Node | Layer | Archetype | Surfaces | Fan-in | Multiplier | Impact |
|---|---|---|---|---|---|---|---|
| 1 | `agentic_core/runtime/contracts/final_evidence_contract.py` | L0/contracts | CENTRAL_DEPENDENCY | State + Observability | 50+ tests | 2.0 | very high |
| 2 | `agentic_core/L3_orchestration/exit_eval/v6/types.py::ExitReviewPacket` | L3 | SAFETY_GATEKEEPER | Execution + State + Security | 11+ tests | 1.75 | high |
| 3 | `agentic_core/runtime/contracts/sealed_l2_artifact.py` | L0/contracts | CENTRAL_DEPENDENCY | Execution + State | 12+ tests | 2.0 | high |

All edits are additive with default values — fan-in surface remains backward-compatible.

## ADG_GRAPH_LAYER_EVIDENCE

- MV `mv_hotspot_centrality`: `final_evidence_contract.py` ranks high — confirmed via 50+ test references in pre-flight scan.
- MV `mv_dependency_cone_risk`: extending FinalEvidenceContract additively is the lowest-risk shape per cone analysis.
- Semantic edges `flows_to`: FEC flows to PA → L2 → Exit → X3Disposition. New ref fields preserve this chain.
- P-view `v_p0_layer_breaks`: zero P0 layer breaks introduced (no upward dependencies).

ADG Provenance: backend=sqlite, snapshot=adg_indexed_05052026_0722.sqlite

PLAN_CREATED: slug=ag4-evidence-contract-carrier-repair-d2f9a3 path=.cursor/plans/ag4-evidence-contract-carrier-repair-d2f9a3.md
