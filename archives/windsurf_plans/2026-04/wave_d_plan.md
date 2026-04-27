# Wave D Implementation Plan

**Version**: 1.0 · **Status**: ACTIVE (D1 output — planning complete, no implementation yet)  
**Date**: 2026-04-16  
**Author**: Agentic-Workflow engineering  
**Binding predecessors**: `docs/reports/wave_c_closeout.md`, `docs/reports/wave_c_gap_map.md`, `docs/reports/wave_c_freeze_gates.md`, `docs/requirements/wave_c_handoff_contract.md` v2.0  
**Entry precondition**: Wave C COMPLETE — all 11 freeze gates PASS (see `docs/reports/wave_c_freeze_gates.md`)  
**Plan tier**: T3 — multi-phase, cross-layer, multi-module

---

## Wave Summary

| Wave | Phase IDs | Focus | Status | Success Criteria |
|------|-----------|-------|--------|------------------|
| **D1** | D1.1 | Wave D planning (this document) | **DONE** | Plan is implementation-ready; execution order explicit |
| **D2** | D2.1–D2.3 | WC-G05 / F12 — hybrid retrieval + parent-child + ADG expansion | TODO | `HybridSearchEngine.search()` serves BM25 + dense fusion; `expand_results_with_parent_child()` and `expand_results_with_adg()` production-ready; all 11 freeze gates still PASS |
| **D3** | D3.1–D3.2 | WC-G07 / F06 — confidence-score abstain planning | TODO | Query planner (or dedicated abstain planner) emits an abstain decision when confidence < floor; unit tests cover abstain path |
| **D4** | D4.1–D4.2 | WC-G08 / F17 — R5 fallback / abstain route | TODO | `PathRouter` (or successor) emits R5 outcome for low-confidence cases; routes to abstain or fallback collection |
| **D5** | D5.1–D5.2 | WC-G06 / F14 — LOW_NORMATIVE_COVERAGE consumer | TODO | A production caller reads the `LOW_NORMATIVE_COVERAGE` signal from `evidence_shaper` and triggers refine / retry / abstain via D3 + D4 |
| **D6** | D6.1 | WC-G03 / F02 — optional ingress-auth advisory source | OPTIONAL | If still desired: evaluate one ext_authority candidate with `dist@1 < 0.45` gate; otherwise formally close as "advisory backlog — declined" |
| **D7** | D7.1 | WC-G04 / F28 — write-governance advisory follow-up | TODO | Documentation-only: Lane C note or ADR capturing write-governance posture; no code change required |
| **D8** | D8.1–D8.3 | Wave D validation and closeout | TODO | All 11 freeze gates PASS; new D2–D5 behaviors covered by unit + integration tests; `docs/reports/wave_d_closeout.md` written |

**Token budget (per-wave)**:

| Wave | Band | Status |
|------|------|--------|
| D1 | LOW (~3k) | 🟢 |
| D2 | HIGH (~25k) | 🟡 (largest implementation slice; may need sub-wave decomposition at D2.x boundary) |
| D3 | MEDIUM (~10k) | 🟢 |
| D4 | MEDIUM (~10k) | 🟢 |
| D5 | MEDIUM (~12k) | 🟢 |
| D6 | LOW (~3k) | 🟢 |
| D7 | LOW (~4k) | 🟢 |
| D8 | MEDIUM (~10k) | 🟢 |

Token estimator (`tools/utils/planning/token_estimator.py`) was not run inline with this D1 output; the bands above are qualitative per the Wave C plan convention. Each D2–D7 phase SHOULD run the estimator at phase entry and revise its band before implementation begins.

**Critical path**: D2 can proceed in parallel with D3. D4 depends on D3 (abstain primitive). D5 depends on D3 + D4. D6 and D7 are independent advisories. D8 runs last.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files / modules) | Pain Points | Est. Tokens | Status |
|----------|-------|-------------------------|-------------|-------------|--------|
| D1.1 | Wave D plan authorship | `.windsurf/plans/wave_d_plan.md` | None | LOW | DONE |
| D2.1 | BM25 lexical backend for `HybridSearchEngine` | `agentic_core/L3_orchestration/reasoning/engines/hybrid_search_engine.py`; `agentic_core/L4_state/utils/memory/bm25_store.py` | BM25 scoring normalization; score-fusion weights; must not change `query_router.py` | MEDIUM | TODO |
| D2.2 | `expand_results_with_parent_child()` | `hybrid_search_engine.py`; chunk-hierarchy metadata in `repo_evidence` | Parent-child linkage only present where `collapse_group` groups chunks — must handle missing parents | MEDIUM | TODO |
| D2.3 | `expand_results_with_adg()` | `hybrid_search_engine.py`; ADG client | ADG fan-in / fan-out lookups must tolerate cache-miss; bounded expansion depth | MEDIUM | TODO |
| D3.1 | Confidence-score abstain primitive | `agentic_core/L1_cognition/reasoning/query_planner.py` or new `agentic_core/L1_cognition/reasoning/abstain_planner.py` | Threshold selection; must not regress existing planner tests | MEDIUM | TODO |
| D3.2 | Abstain unit tests | `tests/unit/L1_cognition/reasoning/test_abstain_planner.py` | Must cover "abstain fires" and "abstain suppressed" paths | LOW | TODO |
| D4.1 | R5 fallback / abstain path in `PathRouter` | `agentic_core/L0_routing/reasoning/path_router.py`; `RoutingOutcomeStatus` enum | Must extend enum without breaking existing `Path.{A,B,C,D}` routes | MEDIUM | TODO |
| D4.2 | R5 routing tests | `tests/unit/L0_routing/reasoning/test_path_router.py` | Ensure RoutingContractError paths still behave; cover new R5 telemetry | LOW | TODO |
| D5.1 | `LOW_NORMATIVE_COVERAGE` consumer module | new module in `agentic_core/L3_orchestration/reasoning/` (e.g. `coverage_signal_consumer.py`); reads signal from `evidence_shaper` (no edits to shaper) | Must treat `evidence_shaper.py` as read-only; signal wiring via call-site instrumentation only | MEDIUM | TODO |
| D5.2 | End-to-end integration: shaper signal → consumer → D3/D4 | `tests/integration/` | Coordinating D3 + D4 + D5 across layers | MEDIUM | TODO |
| D6.1 | F02 advisory — evaluate one candidate | `tools/generate/ingestion/ingest_ext_authority.py` (ONLY if gate passes) | `dist@1 < 0.45` hard gate; otherwise no change | LOW | TODO / OPTIONAL |
| D7.1 | F28 write-governance advisory note | `docs/architecture/write_governance_note.md` (new); ingestion entry in `ingest_repo_evidence.py` | Lane C only; no code change | LOW | TODO |
| D8.1 | Full freeze-gate re-run | `tools/debug/probe_wave_d_freeze_gates.py` (or reuse `probe_wave_c_freeze_gates.py`); `docs/reports/wave_d_freeze_gates.md` | All 11 gates must remain PASS | MEDIUM | TODO |
| D8.2 | Wave D scoped test run | `pytest tests/unit/L0_routing tests/unit/L1_cognition tests/unit/L3_orchestration tests/integration -q` | Must exercise D2–D5 changes | MEDIUM | TODO |
| D8.3 | Wave D closeout report | `docs/reports/wave_d_closeout.md` | Final verdict on all D backlog items | LOW | TODO |

---

## 1. Wave D Objective

Implement the IMPL_GAPs deferred by Wave C into production code so the retrieval and routing pipeline delivers the behaviors promised by the B7 external target-state baseline and the Wave C internal architecture documents (TS-20 spec + F25-int ADR). Close the Wave C gap register without reopening any Wave B or Wave C decision.

**Explicit non-goals**:
- No retrieval redesign beyond the four IMPL_GAPs (F06, F12, F14, F17)
- No ingestion or source-authority changes beyond the optional F02 advisory and the F28 Lane C note
- No topology, routing-table, metadata-contract, or normative-filter changes
- No Wave E work or any work unlisted in §3

---

## 2. Frozen Invariants Inherited from Waves B + C

All items below are **non-negotiable through Wave D**. Any proposed deviation requires a new Author-Gate decision packet citing a concrete blocker.

### 2a. Collection topology (frozen since B3)

| Collection | Lanes | `invalid_for_normative_use` |
|------------|-------|-----------------------------|
| `ext_authority` | A, B | `False` |
| `repo_evidence` | C, D | `True` |
| `ext_raw` | E | `True` |

No collection renames, splits, merges, or deletions. No new collections.

### 2b. Metadata contract (frozen at B5R)

14 required fields on every chunk of every collection:

`source_collection`, `source_band`, `authority_tier`, `normative_scope`, `invalid_for_normative_use`, `source_type`, `topic_bucket`, `doc_family`, `source_url`, `heading_path`, `collapse_group`, `title`, `chunk_index`, `canonical_digest`

### 2c. Frozen routing (`query_router.py` — DO NOT MODIFY)

```
policy          → ext_authority
best_practice   → ext_authority
tool_contracts  → ext_authority
architecture    → repo_evidence (prefilter: source_band=repo_canonical)
code            → code_chunks
```

Architecture-domain prefilter `{"source_band": "repo_canonical"}` remains frozen.

### 2d. Frozen normative filter (`evidence_shaper.py` — DO NOT MODIFY)

`allowed_collections` default = `ext_authority`. Wave D may READ from this module but MUST NOT modify its logic, thresholds, or filter behavior. The `LOW_NORMATIVE_COVERAGE` signal is consumed by D5 from its existing emission point.

### 2e. Frozen eval harness (`retrieval_eval_curated.py` — DO NOT MODIFY)

Wave D may add new targeted unit/integration tests but MUST NOT modify the curated eval set, thresholds, or gate definitions.

### 2f. F25 adjudication (final — NOT REOPENED in Wave D)

- F25-ext: ADEQUATE advisory in `ext_authority` (running_agents.md Author-Gate section). Do not add sources.
- F25-int: internal architecture captured in `docs/architecture/healing_dispatch_routing_adr.md` (repo_evidence Lane C). Wave D MAY implement `healing_tier_router.py` and `healing_tier_dispatcher.py` per the ADR tier contract — but the ADR itself and its Lane C placement are frozen.

### 2g. TS-20 disposition (final — NOT REOPENED in Wave D)

Normative requirements spec lives in `repo_evidence` Lane C only. Wave D MAY add new requirement entries to `docs/requirements/` but MUST NOT add a TS-20 source to `ext_authority`.

### 2h. B7-closed ext_authority topics (NO NEW SOURCES)

TS-03, TS-04, TS-07, TS-09, TS-19 are ADEQUATE at B7. No new `ext_authority` source for any of these topics.

### 2i. ext_raw contents (frozen since B3)

70 chunks. No new scrapes. No promotions from `ext_raw` to `ext_authority` without full re-ingestion.

---

## 3. Ordered Execution Slices

### Slice D2 — F12 Hybrid Retrieval + Parent-Child + ADG Expansion (WC-G05)

**Goal**: Provide a production BM25 lexical backend that fuses with dense retrieval inside `HybridSearchEngine.search()`, and production `expand_results_with_parent_child()` + `expand_results_with_adg()` helpers.

**Phase decomposition**:
- **D2.1** BM25 lexical backend — wire `bm25_store.py` into `HybridSearchEngine.search()`; implement score-fusion (RRF or weighted normalization); maintain the existing engine signature so callers are unaffected
- **D2.2** `expand_results_with_parent_child()` — lift top-N results to their collapse-group parents; tolerate missing parents
- **D2.3** `expand_results_with_adg()` — augment top-N with ADG fan-in / fan-out nodes; bounded depth ≤ 2; cache-miss tolerant

**Scope files (in-scope for edits)**:
- `agentic_core/L3_orchestration/reasoning/engines/hybrid_search_engine.py`
- `agentic_core/L4_state/utils/memory/bm25_store.py`
- Possibly `agentic_core/adg/client/` query helpers (read-only calls into existing ADG client)

**Scope files (read-only, MUST NOT edit)**:
- `agentic_core/L3_orchestration/reasoning/engines/query_router.py`
- `agentic_core/L3_orchestration/reasoning/engines/evidence_shaper.py`
- `tools/eval/retrieval_eval_curated.py`

**Validation strategy**:
- Unit tests under `tests/unit/L3_orchestration/reasoning/engines/` for each new public function
- `probe_wave_d_hybrid_retrieval.py` against `repo_evidence` exercising a smoke query and asserting parent-child + ADG expansion fields present on the result
- Re-run `tools/eval/audit_wave_b_target_state.py` (read-only) to confirm G9 does not regress (target: still ≥ 75%)

**Non-regression gates**:
- G1–G11 all still PASS after D2 (no collection edits; should be trivially stable — verify via `probe_wave_c_freeze_gates.py`)
- No new bare `except Exception` introduced
- No subprocess without timeout
- No PowerShell

**Dependencies**: independent — may run in parallel with D3.

---

### Slice D3 — F06 Confidence-Score Abstain Planning (WC-G07)

**Goal**: Add a confidence-score-aware abstain branch to the planner so low-confidence queries emit an abstain decision instead of a fabricated response.

**Phase decomposition**:
- **D3.1** Abstain primitive — either extend `agentic_core/L1_cognition/reasoning/query_planner.py` with an `abstain()` branch, OR create `agentic_core/L1_cognition/reasoning/abstain_planner.py` and dispatch from the planner entrypoint. Decide at D3.1 entry via a small Author-Gate packet (both options are architecturally valid; dedicated planner gives cleaner separation, extension reuses existing planner plumbing).
- **D3.2** Abstain unit tests — cover `abstain fires when confidence < floor`, `abstain suppressed when evidence is strong`, and `abstain signal propagates to caller in expected shape`

**Scope files (in-scope)**:
- `agentic_core/L1_cognition/reasoning/query_planner.py` OR new `abstain_planner.py` (decision at D3.1)
- `tests/unit/L1_cognition/reasoning/test_abstain_planner.py` (new)

**Validation strategy**:
- Scoped pytest: `pytest tests/unit/L1_cognition/reasoning/ -q`
- Normative requirements spec (`docs/requirements/normative_requirements_spec.md`) entries for AGEN-0106 / AGEN-0108 as the acceptance behavior specification
- The abstain decision MUST be serializable (dict with at least `{"decision": "abstain", "reason": <str>, "confidence": <float>}`) so D5 can consume it

**Non-regression gates**:
- All 11 freeze gates still PASS (no collection edits)
- Existing planner test suite still passes

**Dependencies**: independent; blocks D4.

---

### Slice D4 — F17 R5 Fallback / Abstain Route (WC-G08)

**Goal**: Add an R5 outcome to `PathRouter` that dispatches to the D3 abstain primitive OR to a fallback collection when routing confidence is below the floor.

**Phase decomposition**:
- **D4.1** R5 path implementation — extend `RoutingOutcomeStatus` with `R5_FALLBACK_OR_ABSTAIN`; add confidence-floor trigger in `PathRouter.select_path()`; dispatch to D3 abstain primitive when the trigger fires; emit R5 telemetry
- **D4.2** R5 unit tests — cover `R5 fires for low-confidence input`, `R5 suppressed for high-confidence input`, `R5 integrates with existing Path.A–D semantics`, `RoutingContractError still raised for contract violations`

**Scope files (in-scope)**:
- `agentic_core/L0_routing/reasoning/path_router.py`
- `agentic_core/L0_routing/reasoning/escalation_router.py` (if the R5 path reuses escalation telemetry)
- `tests/unit/L0_routing/reasoning/test_path_router.py`

**Validation strategy**:
- Scoped pytest: `pytest tests/unit/L0_routing/reasoning/ -q`
- Confirm R5 telemetry shows up in `otel_mcp` spans (optional live trace via `mcp7_otel_spans_by_agent`)

**Non-regression gates**:
- All existing `RoutingOutcomeStatus.ROUTE_SUCCEEDED` paths unchanged
- No change to `query_router.py` domain mappings (which live in a different module)
- 11 freeze gates still PASS

**Dependencies**: D3 must be merged before D4.1 can integrate against the abstain primitive. D4.1 may be drafted in parallel and integrated once D3 lands.

---

### Slice D5 — F14 `LOW_NORMATIVE_COVERAGE` Consumer (WC-G06)

**Goal**: Add a consumer that reads the `LOW_NORMATIVE_COVERAGE` signal emitted by `evidence_shaper.py` and triggers refine / retry / abstain via the D3 + D4 primitives.

**Phase decomposition**:
- **D5.1** Consumer module — new `agentic_core/L3_orchestration/reasoning/coverage_signal_consumer.py`; subscribes to the shaper output (via the existing API surface; no shaper edits); decides among refine / retry / abstain based on coverage score and attempt count
- **D5.2** End-to-end integration test — given a low-coverage shaper output, the consumer must route through D3/D4 and surface an abstain outcome; given an adequate-coverage output, the consumer must pass through unchanged

**Scope files (in-scope)**:
- new `agentic_core/L3_orchestration/reasoning/coverage_signal_consumer.py`
- `tests/integration/test_coverage_signal_consumer_e2e.py` (new)

**Scope files (read-only, MUST NOT edit)**:
- `agentic_core/L3_orchestration/reasoning/engines/evidence_shaper.py`

**Validation strategy**:
- Unit tests for the consumer in isolation
- Integration test wiring shaper → consumer → D3/D4
- `probe_wave_d_coverage_consumer.py` smoke run against `repo_evidence` demonstrating the end-to-end flow

**Non-regression gates**:
- `evidence_shaper.py` byte-unchanged (verify via `git diff --stat` before D8)
- Existing shaper unit tests all pass
- 11 freeze gates still PASS

**Dependencies**: D3 + D4 must be merged first.

---

### Slice D6 — F02 Optional Advisory Source (WC-G03)

**Goal**: Only execute if re-evaluation is desired. Otherwise, formally close WC-G03 as "declined — advisory backlog".

**Phase decomposition**:
- **D6.1** F02 candidate evaluation — identify one candidate (e.g. OpenAI platform auth docs); dry-run embed + query; accept only if `dist@1 < 0.45`; otherwise skip and mark "declined"

**Scope files (in-scope)**:
- `tools/generate/ingestion/ingest_ext_authority.py` (ONLY if gate passes)
- `docs/reports/wave_d_f02_advisory_outcome.md` (new; captures decision either way)

**Validation strategy** (if gate passes):
- Rebuild `ext_authority` only
- Re-run G1, G2, G3 on new chunks
- Re-run G9 audit — must stay ≥ 75%

**Non-regression gates**:
- `repo_evidence` and `ext_raw` untouched
- All 11 gates PASS

**Dependencies**: none; may run any time before D8.

---

### Slice D7 — F28 Write-Governance Advisory Follow-up (WC-G04)

**Goal**: Documentation-only. Add a Lane C advisory note describing the current write-governance posture; no implementation change.

**Phase decomposition**:
- **D7.1** Draft `docs/architecture/write_governance_note.md`; add to `REPO_CANONICAL_SOURCES` in `ingest_repo_evidence.py`; rebuild `repo_evidence` only; verify G4 / G5 / G6 on new chunks

**Scope files (in-scope)**:
- new `docs/architecture/write_governance_note.md`
- `tools/generate/ingestion/ingest_repo_evidence.py` (single entry)

**Validation strategy**:
- Rebuild `repo_evidence` only
- Re-run G4 / G5 / G6

**Non-regression gates**:
- `ext_authority` and `ext_raw` untouched
- 11 gates PASS

**Dependencies**: none; may run any time before D8.

---

### Slice D8 — Wave D Validation and Closeout

**Goal**: Prove D2–D7 changes did not regress any frozen invariant; produce final closeout.

**Phase decomposition**:
- **D8.1** Full freeze-gate re-run — all 11 Wave B freeze gates against the post-D7 collection state; write `docs/reports/wave_d_freeze_gates.md`
- **D8.2** Scoped test run — `pytest tests/unit/L0_routing tests/unit/L1_cognition tests/unit/L3_orchestration tests/integration -q` must pass with 0 failures, 0 skips (per constitutional §1)
- **D8.3** Wave D closeout report — `docs/reports/wave_d_closeout.md` records what Wave D did, what it deliberately skipped, and the final verdict

**Scope files (in-scope)**:
- `docs/reports/wave_d_freeze_gates.md` (new)
- `docs/reports/wave_d_closeout.md` (new)
- `tools/debug/probe_wave_d_*.py` (temporary probes — delete after closeout)

**Validation strategy**: same pattern as C4.1 (reuse canonical audit module imports; do not overwrite B7 or Wave C canonical artifacts)

**Non-regression gates**: all 11 freeze gates PASS; no skipped tests; no subprocess without timeout; no new bare `except Exception`; no imports from `archives/`

**Dependencies**: all of D2–D7 must be merged.

---

## 4. Files / Modules In-Scope per Slice (Summary Matrix)

| Slice | Production files (edit) | Test files (new / edit) | Read-only (MUST NOT edit) |
|-------|-------------------------|--------------------------|---------------------------|
| D2 | `hybrid_search_engine.py`, `bm25_store.py` | `tests/unit/L3_orchestration/reasoning/engines/test_hybrid_search_engine.py` | `query_router.py`, `evidence_shaper.py`, `retrieval_eval_curated.py` |
| D3 | `query_planner.py` OR new `abstain_planner.py` | `tests/unit/L1_cognition/reasoning/test_abstain_planner.py` | `evidence_shaper.py`, `retrieval_eval_curated.py` |
| D4 | `path_router.py`, optionally `escalation_router.py` | `tests/unit/L0_routing/reasoning/test_path_router.py` | `query_router.py` |
| D5 | new `coverage_signal_consumer.py` | `tests/integration/test_coverage_signal_consumer_e2e.py` | `evidence_shaper.py` |
| D6 | `ingest_ext_authority.py` (ONLY if gate passes) | — | `ingest_repo_evidence.py` |
| D7 | `ingest_repo_evidence.py` + new `docs/architecture/write_governance_note.md` | — | `ingest_ext_authority.py` |
| D8 | `docs/reports/wave_d_freeze_gates.md`, `wave_d_closeout.md`, temp probes | all Wave D tests re-run | canonical B7 and Wave C artifacts |

---

## 5. Validation Strategy per Slice

| Slice | Unit | Integration | Freeze-gate re-run | Probe |
|-------|------|-------------|---------------------|-------|
| D2 | new engine tests | — | yes (post-D2) | `probe_wave_d_hybrid_retrieval.py` |
| D3 | new abstain tests | — | yes (trivially PASS — no collection edits) | — |
| D4 | new path-router tests | — | yes (trivially PASS) | optional otel span check |
| D5 | new consumer tests | new e2e test | yes (trivially PASS) | `probe_wave_d_coverage_consumer.py` |
| D6 | — | — | G1/G2/G3/G9 only (if gate passes) | F02 gate probe |
| D7 | — | — | G4/G5/G6 on new chunks | — |
| D8 | full Wave D scoped run | full Wave D e2e run | **full 11-gate re-run** | C4.1-style probe |

---

## 6. Non-Regression Gates (always-on through Wave D)

All gates below MUST remain true at every slice boundary. If any fails, Wave D is BLOCKED until remediated.

| Invariant | Check method | Owner |
|-----------|-------------|-------|
| G1–G3 (ext_authority metadata) | `tools/eval/audit_wave_b_target_state.py` after any ext_authority change | D6 only |
| G4–G6 (repo_evidence metadata) | ingestion dry-run + probe after any repo_evidence change | D7 only |
| G7–G8 (ext_raw metadata + dedup) | ext_raw untouched in Wave D | — |
| G9 ≥ 75% | G9 query suite after D6 (if executed) | D6 only; D2 must not degrade via any indirect path |
| G10, G11 contamination = 0 | target-state audit after any collection change | D6, D7 |
| Route purity (`query_router.py`) | `git diff --stat agentic_core/L3_orchestration/reasoning/engines/query_router.py` must show 0 lines changed | every slice |
| Normative filter (`evidence_shaper.py`) | same — 0 lines changed | every slice |
| Eval harness (`retrieval_eval_curated.py`) | same — 0 lines changed | every slice |
| F25 adjudication | `docs/architecture/healing_dispatch_routing_adr.md` content + ingestion entry unchanged | every slice |
| TS-20 disposition | `docs/requirements/normative_requirements_spec.md` source_band stays `repo_canonical` | every slice |
| Constitutional §1 — no test skips | `rg "pytest.mark.skip|@pytest.mark.xfail" tests/` returns 0 new entries | D3, D4, D5, D8 |
| Constitutional §14 — subprocess timeout | no new `subprocess.run(...)` without `timeout=` | D2–D7 |
| Constitutional §15 — precise exceptions | no new bare `except Exception` without guardian comment | D2–D7 |
| Archives isolation | `rg "from archives" agentic_core/ apps_*/` returns 0 | D2–D7 |

---

## 7. Out-of-Scope (Explicit, Forbidden in Wave D)

Any proposal to do any of the following requires a new Author-Gate decision packet citing a concrete blocker.

| Category | Forbidden action |
|----------|-----------------|
| Topology | Add, rename, split, or merge any ChromaDB collection |
| Metadata contract | Add, remove, or rename any of the 14 mandatory metadata fields |
| Routing | Modify `query_router.py` domain-to-collection mappings or prefilters |
| Shaping | Modify `evidence_shaper.py` normative filter, `allowed_collections`, or signal emission |
| Eval harness | Modify `retrieval_eval_curated.py` query set, thresholds, or gate definitions |
| F25 adjudication | Reopen F25-int as ext_authority target; add sources for retired F25 query; move the F25-int ADR out of Lane C |
| TS-20 disposition | Add TS-20 as an `ext_authority` source; move `normative_requirements_spec.md` out of Lane C |
| Closed B7 topics | Add ext_authority sources for TS-03, TS-04, TS-07, TS-09, TS-19 |
| ext_raw | Add any new ext_raw chunk; promote any ext_raw chunk to ext_authority |
| Cross-lane gap filling | Fill ext_authority gap with repo_evidence; fill repo_evidence gap with ext_authority |
| Retrieval redesign | Any retrieval-path change beyond the four explicit IMPL_GAPs (F06, F12, F14, F17) |
| Wave E scope | Any work unlisted in §3 |
| Anti-patterns | New bare `except Exception`, subprocess without timeout, PowerShell invocation, test skip, `except Exception: pass` |
| Agent deletion | Delete any `*Agent.py` file without the AGENT-DELETION-AUTHORIZED marker and 90-day deprecation |

---

## 8. Final Recommended Execution Order

The recommended order maximizes parallelism while honoring dependencies. Each slice ends with a mandatory gate check.

```
D1 (DONE) — this plan is written.
│
├── D2 (F12 hybrid retrieval) — parallel with D3
│   D2.1 BM25 backend
│   D2.2 parent-child expansion
│   D2.3 ADG expansion
│   └── gate: D2 unit tests + 11 freeze gates
│
├── D3 (F06 abstain planning) — parallel with D2
│   D3.1 abstain primitive (tiny Author-Gate at entry: extend query_planner vs new abstain_planner)
│   D3.2 abstain unit tests
│   └── gate: D3 unit tests + 11 freeze gates
│
├── D4 (F17 R5 fallback) — depends on D3 merge
│   D4.1 R5 path in PathRouter
│   D4.2 R5 unit tests
│   └── gate: D4 unit tests + 11 freeze gates
│
├── D5 (F14 coverage consumer) — depends on D3 + D4 merge
│   D5.1 consumer module
│   D5.2 e2e integration test
│   └── gate: D5 tests + 11 freeze gates + evidence_shaper.py byte-unchanged check
│
├── D6 (F02 optional advisory) — independent; may run any time before D8
│   D6.1 evaluate candidate; accept iff dist@1 < 0.45; otherwise close as "declined"
│   └── gate: if accepted, G1/G2/G3/G9 re-run
│
├── D7 (F28 write-governance advisory note) — independent; may run any time before D8
│   D7.1 Lane C advisory note + ingest
│   └── gate: G4/G5/G6 on new chunks
│
└── D8 (Wave D validation + closeout) — depends on ALL prior slices
    D8.1 full 11-gate re-run → wave_d_freeze_gates.md
    D8.2 scoped Wave D test run
    D8.3 closeout report → wave_d_closeout.md
    └── gate: Wave D COMPLETE verdict
```

**Critical path (minimum serial chain)**: D1 → D3 → D4 → D5 → D8.  
**Parallel opportunities**: D2 with D3; D6 and D7 any time before D8.

**Per-slice Author-Gate gates**:
- D3.1 entry: `extend query_planner` vs `new abstain_planner` — tiny Author-Gate packet (2 options, low-ambiguity)
- D6.1 entry: `accept F02 candidate` vs `decline` — auto-resolved by the `dist@1 < 0.45` gate; no Author-Gate unless gate is ambiguous (e.g. dist ≈ 0.45)
- D8.3 verdict: `Wave D COMPLETE` vs `BLOCKED by <gate>` — no Author-Gate; verdict is evidence-driven

---

## 9. Wave D Entry Criteria (verified at plan creation)

- [x] `wave_c_closeout.md` v1.0 — FINAL
- [x] `wave_c_freeze_gates.md` v1.0 — all 11 gates PASS
- [x] `wave_c_gap_map.md` — WC-G01/WC-G02 closed; WC-G03 skipped by design; WC-G04/WC-G05/WC-G06/WC-G07/WC-G08 recorded as Wave D scope
- [x] `wave_c_handoff_contract.md` v2.0 — frozen; Wave D inherits §4 route purity, §5 metadata contract, §7 external target-state baseline, §9 forbidden actions
- [x] This plan created — Wave D may begin with D2 or D3 (either first; parallel allowed)

---

## 10. Gap Register (Wave D entry state)

| Gap ID | Topic | Type | Wave D Slice | Status |
|--------|-------|------|--------------|--------|
| WC-G03 | F02 — ingress auth/quota/schema | ADVISORY | D6 (OPTIONAL) | Open — may be declined again |
| WC-G04 | F28 — UWG / write governance | ADVISORY | D7 | Open |
| WC-G05 | F12 — hybrid retrieval + expansion | IMPL_GAP | D2 | Open |
| WC-G06 | F14 — LOW_NORMATIVE_COVERAGE consumer | IMPL_GAP | D5 | Open |
| WC-G07 | F06 — abstain planning | IMPL_GAP | D3 | Open |
| WC-G08 | F17 — R5 fallback / abstain route | IMPL_GAP | D4 | Open |

At the end of Wave D (D8.3), every row above must be either **Closed**, **Closed-Declined** (D6 only), or **Deferred with documented Wave E scope note**.

---

## 11. Explicit Wave B + Wave C Decisions Inherited (NOT to be reopened)

1. **`ext_authority` defines target state.** Every external best-practice, policy, tool-contract, or architecture-pattern guidance comes from `ext_authority` only.
2. **`repo_evidence` defines current state.** Every query about what the current codebase does, how it is structured, and where it diverges from target state uses `repo_evidence` only.
3. **No cross-lane gap filling.** An external target-state gap is never closed by adding a `repo_evidence` document. An internal current-state gap is never closed by adding an `ext_authority` source.
4. **F25 adjudication is final.** F25-int is a `repo_evidence` Lane C topic; F25-ext is grounded advisory in `ext_authority`. Wave D may implement the F25-int tier contract but MUST NOT move the ADR, alter its Lane, or add ext_authority sources for the F25 family.
5. **TS-20 disposition is final.** Normative requirements spec is `repo_evidence` Lane C only.
6. **B7 closed topics stay closed.** TS-03, TS-04, TS-07, TS-09, TS-19 get no new ext_authority sources.
7. **C4.1 boundary-noise disposition is final.** TS-03 / TS-07 / TS-09 at dist~0.51 are compute-path noise; Wave D MUST NOT add ext_authority sources under the guise of "fixing" these boundary values. If the STRONG stability band is desired for these queries, the only permitted mechanism is new repo-internal implementation that legitimately changes the embedding corpus — not a policy change.

---

*Wave D plan frozen at D1. Updates require a new Author-Gate decision packet and a versioned revision (v1.1, v1.2, …).*
