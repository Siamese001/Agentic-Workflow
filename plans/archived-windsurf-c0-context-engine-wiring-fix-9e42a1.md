---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\c0-context-engine-wiring-fix-9e42a1.md'
original_relative_path: 'c0-context-engine-wiring-fix-9e42a1.md'
source_sha256: 25b28922aebc93742f095d6ff1a4703a59e00e0c6e28d480d8a87e01e9b6e84a
recovered_status: SURVIVED_IN_CURRENT
last_commit: '315fd11926d'
last_commit_date: '2026-05-06 06:26:53 -0400'
created_date: '2026-04-23'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# C0 Context Engine — Wiring Fast-Follow Fix

Status: Todo (plan authored 2026-04-23)
Owner: architecture
Tier: T3 (cross-layer — creates L0 dispatcher, touches L1/L3/L4/L_PG)
Plan SSOT: `.windsurf/plans/c0-context-engine-wiring-fix-9e42a1.md`
Companion plan: `.windsurf/plans/adg-wiring-ci-hardening-7a5d84.md` (the CI that will keep C0 wired)

## Problem Statement

Per ADG snapshot `adg_indexed_04222026_2106.sqlite`, six of the seven modules implementing the C0 Context Engine pipeline (`@c:/Git/Agentic-Workflow/docs/reference/03_L0_Routing/C0 - Retrieval/C0 Context Engine.md`) have fan-in=0 in production. `agentic_core/L1_cognition/utils/c0_context_retriever.py` is a trace-theater stub (74 `_emit_*` calls, zero retrieval logic). Three parallel rerankers exist, all orphan. The L0 seam test asserts 3 exports that do not exist. C0.3 "Knowledge Graph" stage has no implementation at all.

## Goal

Wire C0 end-to-end from an L0 ingress dispatcher through C0.1→C0.5 against real storage adapters, collapse duplicates, fix the seam test, honestly mark C0.3 as deferred, and regenerate the ADG to prove fan-in>0 on every stage. Result: the 8 wiring-CI gates that fail red on C0 today (J1, A1, E1, G2, D1, B4, I2, O) all pass.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| C0-W1 | C0-W1.1–C0-W1.3 | Preparatory: delete/rename trace stub, doc honesty, exports | 🟢 6k | CI plane unchanged for this wave | Todo | Trace-stub removed; C0 doc marks C0.3 deferred; seam-test exports added or test rewritten |
| C0-W2 | C0-W2.1–C0-W2.4 | L4 VectorStore adapter + preretrieval gate concrete policy | 🟢 10k | `vector_db` MCP ChromaDB client reusable from L4 | Todo | `ChromaDBVectorStore` importable from L4; unit-tested against fake and live cache; preretrieval gate concrete ACL + freshness rules defined |
| C0-W3 | C0-W3.1–C0-W3.5 | L0 dispatcher + C0.1→C0.2→C0.4→C0.5 wiring | 🟡 14k | C0-W2 merged; `senior_librarian_reranker` kept as canonical | Todo | `agentic_core/L0_routing/context/c0_dispatcher.py` composes prefilter→gate→hybrid recall→reranker→evidence contract; L5 safety adapter bound; L6 OTEL spans emitted at every stage |
| C0-W4 | C0-W4.1 | C0.3 Knowledge Graph — deferred capture | 🟢 2k | Explicitly out of scope — DEFERRED_SCOPE posted | Deferred | Notion row auto-created by post-hook; C0 doc updated to mark C0.3 as `status: unimplemented` in manifest |
| C0-W5 | C0-W5.1–C0-W5.3 | Collapse duplicates; archive shadow implementations | 🟢 8k | Role dedup gate D1 will enforce | Todo | `L1_cognition/reasoning/ml_decision_support/models/{c0_reranker,advanced_c0_reranker}.py` archived; `agentic_core/evaluation/retrieval/reranker.py` archived; `omni_context_engine.py` archived or repurposed; `hybrid_search_engine.py` merged with `hybrid_recall_stage.py` (pick one authority) |
| C0-W6 | C0-W6.1–C0-W6.3 | Verification: regenerate ADG, prove fan-in>0, run wiring gates | 🟢 6k | CI hardening plan (W1-W3) in place OR gate scripts runnable locally | Todo | `mcp1_adg_edge_fanin` returns ≥1 caller per stage; 8 wiring gates flip from RED→GREEN; integration test exercises full C0 path |

**Total**: ~46k tokens, ~6 PRs, one per wave. GREEN bands throughout; only C0-W3 is YELLOW because dispatcher integration spans 4 layers.

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---:|---|
| C0-W1.1 | Delete trace-stub `c0_context_retriever.py` | `agentic_core/L1_cognition/utils/c0_context_retriever.py` (delete) | May break telemetry tests that assert these `_emit_*` fire at import time | 2k | Todo |
| C0-W1.2 | Update C0 architecture doc for honesty | `docs/reference/03_L0_Routing/C0 - Retrieval/C0 Context Engine.md` | Mark C0.3 as DEFERRED; note L0 dispatcher will live in `agentic_core/L0_routing/context/` | 2k | Todo |
| C0-W1.3 | Fix seam test exports | `agentic_core/__init__.py`, `tests/unit/agentic_core/L0_routing/seams/test_c0_context_retriever_adg.py` | Either add 3 real exports or rewrite test against dispatcher API — **prefer rewrite** against `C0Dispatcher` | 2k | Todo |
| C0-W2.1 | Add `VectorStore` protocol concrete | `agentic_core/L4_state/utils/retrieval/chromadb_vector_store.py` (new) | ChromaDB client lifecycle (reuse `vector_db` MCP infra, do not spawn new) | 4k | Todo |
| C0-W2.2 | Add sparse-index adapter | `agentic_core/L4_state/utils/retrieval/bm25_sparse_store.py` (new) or document as deferred | Likely defer if no existing BM25 store — capture via DEFERRED_SCOPE | 3k | Todo |
| C0-W2.3 | Concrete preretrieval gate policy | `agentic_core/knowledge/gates/preretrieval_gate.py` (wire) | Tenant/ACL/freshness policy shape must be approved — Author-Gate if ambiguous | 2k | Todo |
| C0-W2.4 | L4 retrieval safety gate binding | `agentic_core/L5_safety/enforcement/retrieval/retrieval_safety_gate.py` (wire) | Currently orphan; decide whether it sits at L5-pre or L5-post of recall | 1k | Todo |
| C0-W3.1 | Scaffold L0 context package | `agentic_core/L0_routing/context/__init__.py` (new), `agentic_core/L0_routing/context/boundary_contract.py` (new) | Must export symbols expected by updated seam test | 2k | Todo |
| C0-W3.2 | Implement `C0Dispatcher` | `agentic_core/L0_routing/context/c0_dispatcher.py` (new, ~200 LOC) | Compose: `RetrievalPrefilter` → `preretrieval_gate` → `HybridRecallStage` → `SeniorLibrarianReranker` → `EvidenceContractBuilder`; add OTEL spans per stage | 5k | Todo |
| C0-W3.3 | Bind L5 safety gate into dispatcher path | `c0_dispatcher.py` (edit) | L5 `retrieval_safety_gate` must intersect `flows_to` path — satisfies gate C2 + I1 | 2k | Todo |
| C0-W3.4 | Bind L6 observability emit per stage | `c0_dispatcher.py` (edit) | Every stage emits `emits_side_effect` → L6; satisfies gate O | 2k | Todo |
| C0-W3.5 | Integration test end-to-end | `tests/integration/agentic_core/L0_routing/test_c0_dispatcher_e2e.py` (new) | Fake L4 stores + real prefilter/gate/reranker/evidence; assert payload shape | 3k | Todo |
| C0-W4.1 | C0.3 Knowledge Graph — deferred capture | Plan entry only; Notion row auto-posted via post-hook | Explicit deferral with DEFERRED_SCOPE marker (see top of this plan) | 2k | Deferred |
| C0-W5.1 | Archive duplicate rerankers | Move to `archives/2026-04-c0-dedup/`: `L1_cognition/reasoning/ml_decision_support/models/c0_reranker.py`, `advanced_c0_reranker.py`, `evaluation/retrieval/reranker.py`, `utils/workflow_engines/reranker.py`, `utils/workflow_engines/completeness_reranker.py` | Preserve test parity; update any imports in archived tests or delete | 3k | Todo |
| C0-W5.2 | Archive `omni_context_engine.py` OR repurpose | Decision: if no unique value over `C0Dispatcher`, archive | May require Author-Gate — symbol names suggest it's broader than C0 | 2k | Todo |
| C0-W5.3 | Merge `hybrid_search_engine` ↔ `hybrid_recall_stage` | Pick `hybrid_recall_stage` as canonical (symbol export surface larger); archive `hybrid_search_engine.py` | Ensure tests migrate | 3k | Todo |
| C0-W6.1 | Full ADG regeneration | `python tools/generate_full_adg.py` | Wait for snapshot ≥ `04232026_xxxx` | 2k | Todo |
| C0-W6.2 | Prove fan-in>0 on all stages | ADG MCP calls: `adg_edge_fanin` on each of the 6 modules | Zero tolerance — if any stage still 0, wave fails | 2k | Todo |
| C0-W6.3 | Run wiring gates locally | `python ops_scripts/ci/check_canonical_pipeline_wiring.py && python ops_scripts/ci/check_orphan_module_ratchet.py && python ops_scripts/ci/check_trace_stub_modules.py && ...` | Gates from CI hardening plan must be merged first, OR run scripts ad hoc | 2k | Todo |

## Dependency With CI Hardening Plan

This plan can proceed in **either** of two orders:

1. **Strict safety-first**: merge CI hardening plan W1–W2 first (gates J1, A1, E1 live) → watch C0 fail red on every PR → then fix via this plan → gates flip to green.
2. **Parallel**: start C0 fix plan immediately; CI hardening runs in parallel; they meet at C0-W6.3 where gates verify the fix.

Option 1 is the more rigorous demonstration (the CI catches the bug live, you fix it, the CI verifies). Option 2 is faster time-to-healthy-C0. Either works.

## ADG_HOTSPOT_REPORT — Target Modules

| Module | ADG id | Layer | Current fan-in | Archetype | Surface | Action |
|---|---:|---|---:|---|---|---|
| `agentic_core/L1_cognition/utils/c0_context_retriever.py` | 259 | L1 | 0 | ORPHAN (trace-stub) | None | **Delete** (C0-W1.1) |
| `agentic_core/L3_orchestration/reasoning/engines/omni_context_engine.py` | 553 | L3 | 0 | ORPHAN | None | **Archive or repurpose** (C0-W5.2) |
| `agentic_core/knowledge/retrieval/hybrid_recall_stage.py` | 1829 | L_PG | 0 | C0.2 CENTRAL_DEPENDENCY (future) | State | **Keep; wire via C0Dispatcher** |
| `agentic_core/knowledge/retrieval/retrieval_plan.py` | 1832 | L_PG | 0 | C0.1 SAFETY_GATEKEEPER | Security | **Keep; wire via C0Dispatcher** |
| `agentic_core/knowledge/retrieval/senior_librarian_reranker.py` | 1833 | L_PG | 0 | C0.4 CENTRAL_DEPENDENCY | None | **Keep as canonical reranker** |
| `agentic_core/knowledge/retrieval/evidence_contract_builder.py` | 1828 | L_PG | 0 | C0.5 STATE_NODE | State | **Keep; wire via C0Dispatcher** |
| `agentic_core/knowledge/gates/preretrieval_gate.py` | 1797 | L_PG | 0 | C0.1 SAFETY_GATEKEEPER | Security | **Keep; wire concrete ACL policy (C0-W2.3)** |
| `agentic_core/L3_orchestration/reasoning/engines/hybrid_search_engine.py` | (lookup) | L3 | 0 | ORPHAN (duplicate of 1829) | State | **Archive** (C0-W5.3) |
| `agentic_core/L1_cognition/reasoning/ml_decision_support/models/c0_reranker.py` | (lookup) | L1 | ? | ORPHAN (duplicate of 1833) | None | **Archive** (C0-W5.1) |
| `agentic_core/L1_cognition/reasoning/ml_decision_support/models/advanced_c0_reranker.py` | (lookup) | L1 | ? | ORPHAN (duplicate of 1833) | None | **Archive** (C0-W5.1) |

Post-wave-6 expectation: all kept modules have `fan_in ≥ 1`; all archived modules are gone from production import paths.

## ADG_GRAPH_LAYER_EVIDENCE

Views consulted during planning and verification:

- `mv_hotspot_centrality` — confirms none of the 7 C0 modules register centrality (all isolated)
- `mv_dependency_cone_risk` — shows zero downstream blast radius today; will grow once wired (expected)
- `v_p1_zero_caller_infra` — all 7 C0 modules currently appear here; post-fix they must **not** appear
- `v_p2_duplicated_adapters` — 3 reranker duplicates + 2 hybrid duplicates to be resolved in C0-W5

Semantic edges that must exist after C0-W3 completes:

- `imports`: L0 dispatcher → prefilter, gate, hybrid recall, reranker, evidence builder
- `flows_to`: dispatcher entry → C0.1 → C0.2 → C0.4 → C0.5 → evidence payload out
- `reads_from`: hybrid recall → L4 vector store + L4 sparse store
- `writes_to`: none at this layer (C0 is read-only retrieval; no writes through UWG expected)
- `emits_side_effect`: every stage → L6_observability OTEL span
- `controls_flow`: preretrieval gate → dispatcher (fail-closed on ACL reject)

## Gap Register

| Gap | Mitigation | Wave |
|---|---|---|
| Trace-stub deletion may break unknown telemetry consumer | Grep + ADG fan-in of `c0_context_retriever` first (already known = 0) | C0-W1.1 |
| No existing BM25 sparse store | Either wire a minimal BM25 against existing ChromaDB metadata, or DEFERRED_SCOPE and run recall with dense-only | C0-W2.2 |
| `omni_context_engine.py` may have broader scope than C0 | Author-Gate before archiving — needs 1-hour read-through | C0-W5.2 |
| L5 `retrieval_safety_gate` placement (pre-recall vs post-recall) ambiguous | Author-Gate decision during C0-W3.3 | C0-W3.3 |
| Tests that `importorskip("agentic_core")` masking missing exports | Rewriting seam test against dispatcher API closes the mask | C0-W1.3 |

## Rollback Checkpoints

- After C0-W1: one commit; rollback = `git revert`. Trace stub restoration possible from git history.
- After C0-W2: new modules only, no deletions; rollback = `git revert` of the VectorStore adapter.
- After C0-W3: dispatcher added but downstream consumers (PA prompt assembly) unchanged; rollback = remove `agentic_core/L0_routing/context/` directory. Zero callers outside this package until PA is wired in a later phase.
- After C0-W5: archive moves only; reversible via `git mv`.
- After C0-W6: verification only, no code changes.

## Token Budget Per Wave

| Wave | Estimate | Band |
|---|---:|:---:|
| C0-W1 | 6k | 🟢 GREEN |
| C0-W2 | 10k | 🟢 GREEN |
| C0-W3 | 14k | 🟡 YELLOW (cross-layer integration) |
| C0-W4 | 2k | 🟢 GREEN (deferred capture only) |
| C0-W5 | 8k | 🟢 GREEN |
| C0-W6 | 6k | 🟢 GREEN |

Grand total: **46k tokens across 6 PRs**. All waves well under 32k per-wave ceiling.

## Exit Criteria

Plan is DONE when:

1. `mcp1_adg_edge_fanin(module_id, "imports")` returns ≥1 caller for **every** of the following: `hybrid_recall_stage.py`, `retrieval_plan.py`, `senior_librarian_reranker.py`, `evidence_contract_builder.py`, `preretrieval_gate.py`.
2. `agentic_core/L1_cognition/utils/c0_context_retriever.py` no longer exists.
3. `v_p1_zero_caller_infra` no longer contains any of the 5 C0 stage modules above.
4. `v_p2_duplicated_adapters` no longer contains the 3 reranker cluster or 2 hybrid cluster.
5. Wiring CI gates J1, A1, E1, G2, D1, B4, I2, O all flip from RED to GREEN on main.
6. Integration test `tests/integration/agentic_core/L0_routing/test_c0_dispatcher_e2e.py` passes.
7. C0 architecture doc marks C0.3 honestly as `status: unimplemented` with a reference to the DEFERRED_SCOPE Notion row.
8. Memory entity `ProceduralPattern:C0DispatcherWiringPattern` written (how to compose L0 retrieval stages + L5 gate + L6 emit).
9. ADR `ADR-NNN-c0-context-engine-wiring.md` written and posted to Notion ADR Registry.

## Open Decisions (Author-Gate candidates, not yet opened)

| # | Decision | Trigger wave |
|---|---|---|
| D1 | Keep `senior_librarian_reranker` vs `advanced_c0_reranker` as canonical | C0-W5.1 |
| D2 | L5 retrieval safety gate — pre-recall or post-recall? | C0-W3.3 |
| D3 | `omni_context_engine.py` — archive or repurpose as C0Dispatcher base class? | C0-W5.2 |
| D4 | BM25 sparse adapter — build minimal or defer? | C0-W2.2 |
| D5 | Preretrieval ACL policy shape — tenant-only, freshness-only, or both? | C0-W2.3 |

Each decision will be scored per `author-gate-enforcement.md` and surfaced via `ask_user_question` when its wave begins.
