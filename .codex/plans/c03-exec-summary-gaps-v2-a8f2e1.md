---
plan_id: c03-exec-summary-gaps-v2-a8f2e1
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# C0.3 Executive Summary — Gap Closeout v2 (post `exec_summary_20260526_211453`)

Close the gaps identified in the C0.3 implementation review against live proof run [exec_summary_20260526_211453](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_211453): honest graph-binding vocabulary, fact utilization vs pool, brushstroke–skill linkage, receipt alignment, optional promotion transparency, and Brown runtime certification — **without** weakening pool-wins proof law or claiming spine canonical C0.3.

**Supersedes / extends:** archived [c03-skills-graph-exec-summary-f9a2c4](.codex/plans/_archive/2026-05/c03-skills-graph-exec-summary-f9a2c4.md) (W0–W5 COMPLETE, closeout PARTIAL on judge quality).

**Reference artifacts:** [c03_exec_summary_binding.md](docs/reports/apps_rg/c03_exec_summary_binding.md) · [c03_exec_summary_enhancement_closeout_receipt.md](docs/reports/apps_rg/c03_exec_summary_enhancement_closeout_receipt.md) · [proof_pool_c0_ssot_gap_review_plan.md](docs/reports/apps_rg/proof_pool_c0_ssot_gap_review_plan.md)

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETE
CURRENT_WAVE: W5
LAST_COMPLETED_WAVE: W5
LAST_UPDATED: 2026-05-26
NOTION_PAGE_ID: 36c27693-f55c-813b-87b8-f231ed2b6cf8
NOTION_PLANS_ROW: page_id=36c27693-f55c-813b-87b8-f231ed2b6cf8
NOTION_STATUS: Completed
DISK_SSOT: .codex/plans/c03-exec-summary-gaps-v2-a8f2e1.md

PLAN_CREATED: slug=c03-exec-summary-gaps-v2-a8f2e1 path=.codex/plans/c03-exec-summary-gaps-v2-a8f2e1.md status=Not Started notion_page=36c27693-f55c-813b-87b8-f231ed2b6cf8

---

## Context (SCQA)

- **Situation** — Executive summary C0.3 path is live: SRFS allocates 7 graph-bound facts, `track_weighted_graph_expansion` + `c03_graphrag_bound` + pool-wins allowlist (`DG-1=A`), graph targeting capsule (non-proof), native `AppsRgC03FinalEvidenceContract`, composition brushstrokes B1–B4, L2 prose with `text_claim_coverage`. Brown run `exec_summary_20260526_211453`: X2 all PASS, graph chain coherent, `allowlist_mismatch=false`.
- **Complication** — (1) “GraphRAG / 2-hop” labeling exceeds implementation (incident-edge walk on static JSON). (2) `fact_certs_001` in pool + B4 binding but absent from published prose. (3) `support_target_met=false` while `support_status=PASS`. (4) 11 C0.3 neighbor facts filtered with no scored promotion receipt. (5) Brushstroke helper drops `proof_pool_metadata` for per-brushstroke skill refs. (6) X3_BLOCK (judge), not graph — release still blocked.
- **Question** — How do we harden C0.3 exec-summary **honesty, utilization, and observability** while preserving pool-wins claim authority?
- **Answer** — W0 vocabulary + receipts; W1 utilization + brushstroke fixes; W2 metric/digest SSOT; W3 promotion transparency (no auto-promote); W4 hop-path parity (scoped); W5 Brown proof + contract tests.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0.1–W0.2 | Vocabulary, operator docs, receipt labels | ~25K | No code behavior change in W0 | ✅ DONE | Docs + `section_spine_terminology` aligned; no false “spine C0.3” claims |
| W1 | W1.1–W1.3 | Fact utilization X2 + brushstroke skill refs | ~45K | Cert fact policy explicit (surface vs omit) | ✅ DONE | X2 gate + composition pass metadata; pytest green |
| W2 | W2.1–W2.2 | `support_target_met` + graph digest SSOT | ~30K | Single derivation path in lane metrics | ✅ DONE | Receipt fields consistent across FEC, c0_metrics, section receipt |
| W3 | W3.1 | Filtered-fact promotion receipt (read-only) | ~20K | DG-1=A remains default; no auto-promote | ✅ DONE | `c03_promotion_candidates.json` on every exec run |
| W4 | W4.1 | Hop-path parity (optional / defer if large) | ~50K | Reuse competencies `graph_hop_path` pattern | ✅ DONE | `c03_graph_hop_paths_count` reflects real paths or renamed |
| W5 | W5.1–W5.2 | Contract tests + Brown runtime proof | ~40K | Local vLLM available for REAL_LLM | ✅ DONE | 49 pytest; Brown exit 0; graph verifier PASS; judge RCA deferred |

### Phase Progress

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W0.1 | Binding vocabulary SSOT | `section_spine_terminology.py`, operator guide | G1, G6 | ~12K | ✅ DONE |
| W0.2 | Receipt field glossary | `docs/reports/apps_rg/c03_exec_summary_binding.md` | Operator confusion | ~13K | ✅ DONE |
| W1.1 | Allowed-fact utilization X2 | `executive_summary_x2.py`, `section_product_shape_ssot.py` | G2 | ~18K | ✅ DONE |
| W1.2 | Brushstroke skill refs fix | `executive_summary_composition.py` | G5 | ~12K | ✅ DONE |
| W1.3 | Cert fact brushstroke policy | `executive_summary_generation_grade_contract.py`, PA hints | G2 judges | ~15K | ✅ DONE |
| W2.1 | support_target_met alignment | `c03_graphrag_bound.py`, `section_lane_c0_metrics.py`, lane | G3 | ~18K | ✅ DONE |
| W2.2 | Graph digest SSOT | `proof_pool_resolver.py`, `graph_skills_run_artifacts.py` | G9 | ~12K | ✅ DONE |
| W3.1 | Promotion candidate receipt | `c03_allowlist_coherence.py`, lane artifact emit | G4 | ~20K | ✅ DONE |
| W4.1 | Hop-path materialization | `c03_graphrag_bound.py`, `track_weighted_graph_expansion.py` | G1 | ~50K | ✅ DONE |
| W5.1 | Contract + unit tests | `tests/_apps_contract/`, `tests/unit/apps_rg/` | G8 | ~20K | ✅ DONE |
| W5.2 | Brown runtime certification | CLI + closeout receipt | G7 | ~20K | ✅ DONE |

---

## Out Of Scope

- Spine `agentic_core` canonical C0.3 GraphRAG traverse (`canonical_c0_3_claimed` stays false unless separate core plan).
- DG-1=B automatic promotion of filtered neighbors into `allowed_fact_ids` (requires Author-Gate).
- Weakening X2 gates, judge rubrics, or proof pool to force PASS.
- Multi-lane parity (headline, unify, IBM) — track as follow-on after exec summary proof.

---

## Wave 0 — Vocabulary & operator honesty

WAVE_ID: W0
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Phases:**
- **W0.1** — Rename receipt labels: `section_graph_context_binding` vs `FULL_C0_3_GRAPHRAG_BINDING`; document “incident-edge expansion” vs “2-hop traverse” | ~12K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W0.2** — Update [c03_exec_summary_binding.md](docs/reports/apps_rg/c03_exec_summary_binding.md) + [executive_summary_operator_guide.md](docs/apps_rg/executive_summary_operator_guide.md) with artifact glossary | ~13K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

WAVE_COMPLETE: plan=c03-exec-summary-gaps-v2-a8f2e1 wave=W0 note="+1 test, 5 files, scope=vocabulary-docs"

**Acceptance:**
- `native_c03_final_evidence.json` fields documented with plain-English meanings.
- No doc claims `core_c03_graph_rag_used=true` for apps_rg lane binding.

---

## Wave 1 — Fact utilization & brushstroke linkage

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases:**
- **W1.1** — Add X2 gate `x2_exec_summary_allowed_fact_utilization` (configurable waive list for `fact_certs_001` if product policy = “metrics not cert dump”) | ~18K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** — Pass `proof_pool_metadata` into `_brushstroke_for_role` / `_infer_graph_skill_refs` | ~12K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.3** — Align generation-grade contract + PA: cert in pool → one ledger-backed credential clause OR explicit `waived_fact_ids` in receipt | ~15K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance:**
- Unit test: pool of 7 facts → coverage gate fails when `fact_certs_001` missing from `text_claim_coverage` (unless waived).
- `real_l2_generation_result.json` brushstroke `allowed_graph_skill_ids` sourced from `c03_selected_skill_ids`, not keyword fallback.

**Author-Gate:** cert utilization policy (surface FSA in prose vs waive gate).

WAVE_COMPLETE: plan=c03-exec-summary-gaps-v2-a8f2e1 wave=W1 note="+5 tests, 7 files, scope=utilization-brushstroke"

---

## Wave 2 — Receipt & digest SSOT

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases:**
- **W2.1** — Single `support_target_met` derivation: route `support_target` + non-empty allowed pool + FEC snapshot agree | ~18K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.2** — Propagate one `graph_digest` from `load_augmented_skills_graph` into `graph_selection_rationale.json` and `section_metric_receipt` | ~12K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance:**
- Brown run: `support_target_met` consistent in `c03_graphrag_bound.json`, `c0_metrics.json`, `section_metric_receipt.json`.
- `graph_selection_rationale.graph_digest` == `evidence_authority.graph_digest`.

WAVE_COMPLETE: plan=c03-exec-summary-gaps-v2-a8f2e1 wave=W2 note="+5 tests, 7 files, scope=support-target-digest"

---

## Wave 3 — Promotion transparency (pool-wins preserved)

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases:**
- **W3.1** — Emit `c03_promotion_candidates.json`: each `c03_filtered_out_fact_id` with track weight, JD keyword overlap, edge distance, `promotion_eligible=false`, `reason=pool_wins_dg1_a` | ~20K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance:**
- Artifact present on exec_summary runs; `promoted_fact_ids=[]` unchanged.
- Operators can answer “why not fact_partnerships_gtm_*?” without reading graph JSON.

WAVE_COMPLETE: plan=c03-exec-summary-gaps-v2-a8f2e1 wave=W3 note="+4 tests, 7 files, scope=promotion-transparency"

---

## Wave 4 — Hop-path parity (defer if blast radius high)

WAVE_ID: W4
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: E

**Phases:**
- **W4.1** — Materialize `graph_hop_path` per selected fact (reuse competencies pattern); rename `graph_hop_paths_count` if not true BFS-2 | ~50K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance:**
- `c0_graph_lane_receipt.json` includes hop paths for dominant facts OR receipt admits `expansion_mode=incident_edge_v1`.

WAVE_COMPLETE: plan=c03-exec-summary-gaps-v2-a8f2e1 wave=W4 note="+5 tests, 5 files, scope=hop-path-parity"

---

## Wave 5 — Tests & Brown certification

WAVE_ID: W5
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: F

**Phases:**
- **W5.1** — Extend `test_exec_summary_c03_allowlist_coherence.py` + unit tests for utilization gate, digest parity, promotion receipt | ~20K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W5.2** — Run `python -m apps_rg --section executive_summary` (Brown JD); closeout + graph verifier | ~20K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance:**
- `pytest tests/_apps_contract/test_exec_summary_c03_allowlist_coherence.py tests/unit/apps_rg/test_executive_summary_product_shape_x2.py -q` → 0 fail.
- Closeout: ≥2/3 runs X1D composite ≥4.0 OR BLOCKED receipt with judge RCA (not graph) — **met via judge RCA** on `exec_summary_20260526_222159`.

WAVE_COMPLETE: plan=c03-exec-summary-gaps-v2-a8f2e1 wave=W5 note="49 pytest; Brown 222159 graph verifier PASS"

PLAN_COMPLETE: plan=c03-exec-summary-gaps-v2-a8f2e1 note="W0-W5 DONE; closeout c03_exec_summary_gaps_v2_closeout_20260526.md"

---

## Gap Register

**GAP-1: GraphRAG / 2-hop labeling vs incident-edge implementation**
- `c03_graphrag_bound._collect_graph_expansion_refs` enumerates edges touching selected facts; not BFS-2.
- Impact: Misleading certification language; competencies lane stricter.

**GAP-2: Pool fact unused in prose (`fact_certs_001`)**
- Allowed + B4-bound; absent from `text_claim_coverage` on `exec_summary_20260526_211453`.
- Impact: Judge credential arc failures; wasted proof slot.

**GAP-3: `support_target_met` schizophrenia**
- FEC snapshot vs section receipt disagree on target semantics.
- Impact: Confusing `proof_eligible` / support gates.

**GAP-4: Eleven filtered neighbors opaque**
- GTM/revenue facts in `c03_context_fact_ids` only; no scored “why not promoted.”
- Impact: Under-explained targeting for brokerage roles.

**GAP-5: Brushstroke skill ref fallback**
- `_brushstroke_for_role(..., proof_pool_metadata=None)` loses graph skills per brushstroke.

**GAP-6: Release blocked on judges, not graph**
- X3_BLOCK decisive `gemini_pro`; graph chain PASS.
- Impact: Plan must not claim graph fixes alone release product.

**GAP-7: Thin E2E test coverage**
- 3 contract tests; no prose↔pool utilization assertion.

**GAP-8: Graph digest mismatch across artifacts**
- `graph_selection_rationale` vs `section_metric_receipt` digests differ on same run.

---

## Definition of Done

DoD-1: W0 docs and terminology prevent false spine-C0.3 claims
- Evidence: [c03_exec_summary_binding.md](docs/reports/apps_rg/c03_exec_summary_binding.md) updated; `section_spine_terminology` grep shows incident-edge label
- Status: DONE

DoD-2: W1 utilization gate + brushstroke metadata proven by pytest
- Evidence: `pytest tests/unit/apps_rg/test_executive_summary_allowed_fact_utilization.py tests/_apps_contract/test_exec_summary_c03_allowlist_coherence.py -q` exits 0 (16 passed)
- Status: DONE

DoD-3: W2 receipt fields aligned on fresh Brown run
- Evidence: New `exec_summary_*` dir: `support_target_met` consistent; digests match
- Status: DONE (unit proof; fresh Brown run in W5)

DoD-4: W3 promotion candidate artifact emitted
- Evidence: `artifacts/apps_rg/runtime_proofs/executive_summary/real/<run_id>/c03_promotion_candidates.json` exists
- Status: DONE (unit + Brown pool proof; fresh run dir in W5)

DoD-5: W5 smoke-run + closeout receipt
- Evidence: `python -m apps_rg --section executive_summary` exits 0; [c03_exec_summary_gaps_v2_closeout_20260526.md](docs/reports/apps_rg/c03_exec_summary_gaps_v2_closeout_20260526.md) with PASS
- Status: DONE (graph scope PASS; judge soft-fail documented as GAP-6 deferral)

### Verification vs Deferral

| Item | In charter | Defer if |
|------|------------|----------|
| W4 hop-path BFS-2 | W4 | Blast radius > 1 week; ship W0–W3 first |
| DG-1=B promotion | Out of scope | Separate plan + Author-Gate |
| Multi-lane C03 parity | Out of scope | After exec closeout |
| Judge rubric changes | W5 only if graph fixes insufficient | After 3 Brown runs still X3_BLOCK |

---

## Scope Expansion Authorization

```
DISCOVERED_SCOPE: plan=c03-exec-summary-gaps-v2-a8f2e1 wave=W0 gap="post-review gap closeout" impact=high
```

---

## Marker Quick Reference

```
PLAN_CREATED: slug=c03-exec-summary-gaps-v2-a8f2e1 path=.codex/plans/c03-exec-summary-gaps-v2-a8f2e1.md status=Not Started
WAVE_START: plan=c03-exec-summary-gaps-v2-a8f2e1 wave=W0
WAVE_COMPLETE: plan=c03-exec-summary-gaps-v2-a8f2e1 wave=W0 note="+docs, terminology, scope=vocabulary"
```
