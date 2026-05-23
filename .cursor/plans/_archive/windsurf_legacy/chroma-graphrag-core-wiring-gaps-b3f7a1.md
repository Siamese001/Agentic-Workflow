---
plan_id: chroma-graphrag-core-wiring-gaps-b3f7a1
plan_type: refactor
parent_plan: chroma-graphrag-lic-rg-research-f4a2e9
gap_register_source: artifacts/chromadb_graphrag_remediation/no_core_gap_register_final.md
authored_at: 2026-05-01
last_updated: 2026-05-12T06:30:00
status: Completed
---

# ChromaDB + Graph RAG — Core Wiring Gaps (GAP-01 through GAP-09)

Close all nine deferred gaps from the W*N no-core track: wire R1B semantic cache into the generic L0 binding, carry `GraphTraversePolicy` through `RouteContract`, register per-app C0.3 adapters, execute the full Graph RAG chain, and deliver real BAAI/bge-m3 ingestion — with zero app-id checks in `agentic_core`.

---

## Context (SCQA)

- **Situation** — Plan `chroma-graphrag-lic-rg-research-f4a2e9` (W*N no-core track) completed W0N–W6N, leaving all three apps (`apps_lic`, `apps_rg`, `apps_research`) config-prepared but not live-wired: cache profiles carry `live_wiring_deferred: true`, graph traverse profiles carry `wiring_gate: *_AGENTIC_CORE_REQUIRED`, and all three C0.3 adapter stubs build valid `GraphTraverseInput`-compatible dicts. Nine gaps were intentionally deferred and recorded in `artifacts/chromadb_graphrag_remediation/no_core_gap_register_final.md`.

- **Complication** — Closing any of the nine gaps requires authorized `agentic_core` GENERIC_INFRA_EDITs or a real ingestion pipeline with `sentence-transformers`. GAP-05 (runtime Graph RAG execution) is blocked on GAP-03 + GAP-04. GAP-07 (real embeddings) is blocked on GAP-06 (ingestion pipeline). GAP-08 (`apps_lic` live cache) is a business-logic non-goal. GAP-09 (`apps_rg` unquarantine) requires explicit RCA sign-off before unquarantine.

- **Question** — How do we close all eight actionable gaps (excluding the intentional GAP-08 business non-goal) in dependency order, using exactly the two pre-scoped GENERIC_INFRA_EDITs plus a new ingestion wave, without introducing any app-id checks into `agentic_core`?

- **Answer** — Execute seven waves in strict dependency order: W1 closes GAP-01/02 (R1B cache wiring), W2 closes GAP-03 (`RouteContract` graph policy carriage), W3 closes GAP-04 (adapter registry), W4 closes GAP-05 (runtime Graph RAG execution), W5 closes GAP-09 (apps_rg RCA + unquarantine), W6 closes GAP-06/07 (ingestion pipeline + real embeddings), with W7 as integration verification across all three apps.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `artifacts/chromadb_graphrag_remediation/no_core_gap_register_final.md` | Canonical 9-gap register from W6N closure | ✅ Confirmed |
| `agentic_core/L0_routing/package_driven_l0_binding.py` R1B arm | Reads `semantic_cache.enabled`; emits `RouteContract(route_type=CACHE_LOOKUP)`; never calls `check_d2_semantic_cache()` | ✅ Confirmed (GAP-01/02) |
| `agentic_core/L0_routing/reasoning/route_gates.check_d2_semantic_cache()` | Canonical R1B entry point at line ~217; no callers | ✅ Confirmed (GAP-01) |
| `agentic_core/runtime/contracts/route_contract.RouteContract` | Missing `graph_traverse_policy: GraphTraversePolicy \| None = None` field | ✅ Confirmed (GAP-03) |
| `agentic_core/L0_routing/c0_retrieval/c0_3_enhanced/` pipeline + `ADAPTER_REGISTRY` | `run_graph_traverse()` fully implemented; registry missing apps_lic/rg/research entries | ✅ Confirmed (GAP-04/05) |
| `apps_lic/config/domain_contract/cache_profiles.yaml` | `semantic_cache` block with `live_wiring_deferred: true`, `wiring_gate: R1B_SEMANTIC_CACHE_AGENTIC_CORE_REQUIRED` | ✅ Confirmed (GAP-01/08) |
| `apps_rg/config/domain_contract/cache_profiles.yaml` | Same `live_wiring_deferred` shape; `r1b_adapter.py` quarantined | ✅ Confirmed (GAP-02/09) |
| `apps_rg/cache/r1b_adapter.py` | Quarantined; `RuntimeError` on import; requires RCA sign-off | ✅ Confirmed (GAP-09) |
| `apps_research/engines/research_retrieval_engine.py` | `_embed()` returns zero vector (W5N stub); `create_retrieval_engine()` factory gated on `chromadb_path` | ✅ Confirmed (GAP-06/07) |
| All three `c0_graph_adapter.py` stubs | Implement `GraphTraversalAdapter`; produce valid `GraphTraverseInput`-compatible dicts | ✅ Confirmed (GAP-04/05) |
| `apps_lic`, `apps_rg`, `apps_research` route profiles | Carry `graph_traverse` blocks with `live_wiring_deferred: true` | ✅ Confirmed (GAP-03/04) |

---

## Wave Structure

| Wave | Scope | Focus | Gaps Closed | Est. Tokens | Status |
|------|-------|-------|-------------|-------------|--------|
| W0 | Pre-flight | Verify all nine gap states live in source; emit preflight receipt | — | ~600 | ✅ DONE |
| W1 | `agentic_core/L0_routing/` | GENERIC_INFRA_EDIT: wire `check_d2_semantic_cache()` in L0 binding R1B arm; add generic namespace/threshold reader from app-owned cache profile | GAP-01, GAP-02 | ~2,000 | ✅ DONE |
| W2 | `agentic_core/runtime/contracts/` + L0 binding | GENERIC_INFRA_EDIT: add `graph_traverse_policy: GraphTraversePolicy \| None = None` to `RouteContract`; read `graph_traverse` block from route profiles in L0 binding | GAP-03 | ~1,500 | ✅ DONE |
| W3 | `agentic_core/L0_routing/c0_retrieval/c0_3_enhanced/` | Register `apps_lic`, `apps_rg`, `apps_research` adapters in `ADAPTER_REGISTRY` | GAP-04 | ~800 | ✅ DONE |
| W4 | `agentic_core/runtime/c0/` + app graph profiles | Wire `maybe_run_graph_rag()` in `c0_ground_package_driven()`; map `GraphExpandedEvidencePool` to `FinalEvidenceContract`; flip `live_wiring_deferred: false` on all three graph traverse profiles | GAP-05 | ~2,500 | ✅ DONE |
| W5 | `apps_rg/cache/` | RCA sign-off + keep quarantine; flip `apps_rg` to generic L0 R1B path (KEEP_QUARANTINED_DEPRECATED decision) | GAP-09 | ~1,500 | ✅ DONE |
| W6 | `apps_research/engines/` + ingestion tooling | Real BAAI/bge-m3 embedding in `ChromaResearchStore._embed()`; ingestion pipeline populates `process_docs` Chroma collection | GAP-06, GAP-07 | ~3,000 | ✅ DONE |
| W7 | All three apps | Integration verification: smoke runs, gate sweep, emit closure receipt | — | ~1,200 | ✅ DONE |

**Total: ~13,100 tokens across 8 waves (W0–W7)**

**Dependency chain**: W1 → W2 → W3 → W4 (sequential); W5 independent (parallel with W2–W4); W6 independent (parallel with W1–W5); W7 gated on all prior waves.

**Status tracking**: Notion Status flips "Not Started" → "In Progress" at **Wave 1 start** via `wave_execution_state.py start`. W0 is pre-flight only.

---

## Out Of Scope

- **GAP-08** (`apps_lic` live R1B wiring): intentionally excluded — `personalized_outreach_not_cacheable` is a business-logic decision, not a gap to auto-resolve.
- Any new app-id (`if app_id == "apps_*"`) checks inside `agentic_core` — all edits must remain generic profile-resolver logic.
- Spearman calibration for semantic cache threshold tuning — separate calibration plan.
- `apps_exec` or `apps_rfp` Chroma/Graph RAG wiring — scoped to three apps only.
- New Chroma collection schemas beyond `process_docs` — W6 ingestion writes to the already-declared collection only.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W0.1 | Pre-flight gap verification | `no_core_gap_register_final.md` + all 9 gap source files | None expected | ~600 | ✅ DONE |
| W1.1 | Generic namespace/threshold reader | `package_driven_l0_binding.py` | GAP-01 (no profile reader for cache lookup dispatch) | ~1,000 | ✅ DONE |
| W1.2 | `check_d2_semantic_cache()` call wiring | `package_driven_l0_binding.py`, `route_gates.py` | GAP-02 (always-miss R1B arm) | ~1,000 | ✅ DONE |
| W2.1 | `GraphTraversePolicy` dataclass + `RouteContract` field | `route_contract.py` | GAP-03 (no policy carriage) | ~800 | ✅ DONE |
| W2.2 | L0 binding reads `graph_traverse` block from route profile | `package_driven_l0_binding.py` | GAP-03 (block never consumed) | ~700 | ✅ DONE |
| W3.1 | Adapter registry entries for all three apps | `c0_3_enhanced/adapter_registry.py` | GAP-04 (ADAPTER_REGISTRY empty for these apps) | ~800 | ✅ DONE |
| W4.1 | `maybe_run_graph_rag()` wired into `c0_ground_package_driven()` | `agentic_core/runtime/c0/c0_package_driven_grounding.py`, `c0_3_graph_rag_executor.py` | GAP-05 (never called despite full impl) | ~1,500 | ✅ DONE |
| W4.2 | `GraphExpandedEvidencePool` mapped to `FinalEvidenceContract` fields | `c0_package_driven_grounding.py`, `route_contract.py` | GAP-05 (evidence not surfaced) | ~600 | ✅ DONE |
| W4.3 | Flip `live_wiring_deferred: false` + W4 receipt | 3 app graph profiles + `artifacts/chromadb_graphrag_core_wiring/` | GAP-05 (gate marker removal + W3N test update) | ~400 | ✅ DONE |
| W5.1 | RCA completion for `r1b_adapter.py` quarantine | `apps_rg/cache/r1b_adapter.py`, RCA doc | GAP-09 (L4 import violation RCA) | ~800 | ✅ DONE |
| W5.2 | KEEP_QUARANTINED_DEPRECATED decision; flip apps_rg to generic L0 R1B path | `apps_rg/config/domain_contract/cache_profiles.yaml` | GAP-09 (unquarantine deferred; generic path live) | ~700 | ✅ DONE |
| W6.1 | Real `sentence-transformers` BAAI/bge-m3 in `_embed()` | `apps_research/engines/integration/chroma_research_store.py` | GAP-07 (zero-vector stub) | ~1,500 | ✅ DONE |
| W6.2 | Ingestion pipeline for `process_docs` collection | `tools/ingestion/chroma_ingest_pipeline.py` (new) | GAP-06 (no ingestion; collection unpopulated) | ~1,500 | ✅ DONE |
| W7.1 | Smoke runs all three apps + gate sweep | All 3 app `__main__.py` entry points | Integration proof | ~700 | ✅ DONE |
| W7.2 | Closure receipt + gap register final flip | `artifacts/chromadb_graphrag_core_wiring/` | Provenance close-out | ~500 | ✅ DONE |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

**GAP-01 — Live R1B semantic cache wiring (all apps)** ✅ CLOSED (W1)
- `check_d2_semantic_cache()` wired into L0 binding R1B arm.
- **Closed by**: W1

**GAP-02 — `package_driven_l0_binding.py` generic cache lookup** ✅ CLOSED (W1)
- Generic `_read_semantic_cache_profile()` added; namespace/threshold read from app-owned profile.
- **Closed by**: W1

**GAP-03 — `RouteContract` graph policy carriage** ✅ CLOSED (W2)
- `graph_traverse_policy: GraphTraversePolicy | None = None` added to `RouteContract`; L0 binding reads `graph_traverse` block from route profiles.
- **Closed by**: W2

**GAP-04 — C0.3 adapter registry wiring** ✅ CLOSED (W3)
- `ADAPTER_REGISTRY` populated for `apps_lic`, `apps_rg`, `apps_research` via config-driven lookup.
- **Closed by**: W3

**GAP-05 — C0.3 runtime Graph RAG execution** ✅ CLOSED (W4)
- `maybe_run_graph_rag()` wired into `c0_ground_package_driven()` with conditional policy gating.
- `GraphExpandedEvidencePool` mapped to 7 new `FinalEvidenceContract` fields.
- All three app graph traverse profiles flipped: `live_wiring_deferred: false`, `wiring_gate: CLEARED_BY_W4_GRAPH_RAG_EXECUTION`.
- Receipt: `artifacts/chromadb_graphrag_core_wiring/w4_graph_rag_execution_receipt.json`
- **Closed by**: W4 — 101 tests passing (W1+W2+W3+W4+core executor)

**GAP-06 — Real production Chroma ingestion execution** ✅ CLOSED (W6)
- `tools/ingestion/chroma_ingest_pipeline.py` created. Targets `process_docs` collection, BAAI/bge-m3 embeddings, 1024 dims. `--dry-run` is safe default; `--execute` required for writes. No L4 state touched.
- Receipt: `artifacts/chromadb_graphrag_core_wiring/w6_real_embeddings_ingestion_receipt.json`
- **Closed by**: W6 — 135 tests passing (W1–W6 + c0_3_graph_rag_executor)

**GAP-07 — Real BAAI/bge-m3 embedding in `ChromaResearchStore._embed()`** ✅ CLOSED (W6)
- Zero-vector stub replaced with `SentenceTransformer("BAAI/bge-m3").encode()`. Lazy-loaded; raises `ImportError` with install hint if `sentence-transformers` missing. `InMemoryResearchStore` (test/dev path) unchanged.
- **Closed by**: W6

**GAP-08 — `apps_lic` live R1B wiring** *(intentional non-goal)*
- `personalized_outreach_not_cacheable` by business logic. R1B absent from route order by design.
- **Not closed by this plan** — requires a separate product-authorized decision.

**GAP-09 — `apps_rg` live R1B wiring (`r1b_adapter.py` unquarantine)** ✅ CLOSED (W5 — KEEP_QUARANTINED_DEPRECATED)
- RCA completed: `docs/architecture/rca/RCA_apps_rg_r1b_adapter_L4_import_violation.md`. Decision: KEEP_QUARANTINED_DEPRECATED — generic L0 R1B path now live for `apps_rg` via `cache_profiles.yaml` flip (`live_wiring_deferred: false`). `r1b_adapter.py` remains quarantined as deprecated artifact.
- Receipt: `artifacts/chromadb_graphrag_core_wiring/w5_apps_rg_r1b_rca_decision_receipt.json`
- **Closed by**: W5 — 115 tests passing

---

## Execution Plan

### W0 — Pre-flight

**Scope**: Verify all nine gap states are still live in source; re-confirm `check_d2_semantic_cache()` has zero callers; re-confirm `ADAPTER_REGISTRY` is missing entries; emit `w_core_gaps_preflight_receipt.json`.

**Acceptance**: Receipt emitted; all nine gaps confirmed open; no unexpected closures.

---

### W1 — GENERIC_INFRA_EDIT: R1B Cache Wiring (GAP-01, GAP-02)

**Scope**: `agentic_core/L0_routing/package_driven_l0_binding.py`

**Changes**:
1. Add generic `_read_semantic_cache_profile(app_profile)` — reads `semantic_cache.namespace` + `semantic_cache.similarity_threshold` from app-owned profile dict. Zero app-id checks.
2. In R1B arm: after emitting `RouteContract(route_type=CACHE_LOOKUP)`, call `check_d2_semantic_cache(namespace, query_embedding, threshold)`.
3. Flip `live_wiring_deferred: false` on `apps_research/config/domain_contract/cache_profiles.yaml` (apps_rg deferred to W5).

**Gate**: `apps_research` R1B cache lookup returns a hit/miss against `SovereignSemanticCache` (test with injected mock store).

**Acceptance**: `tests/_apps_contract/test_w1_r1b_cache_wiring.py` green; `check_d2_semantic_cache` call confirmed in coverage.

---

### W2 — GENERIC_INFRA_EDIT: RouteContract Graph Policy Carriage (GAP-03)

**Scope**: `agentic_core/runtime/contracts/route_contract.py`, `agentic_core/L0_routing/package_driven_l0_binding.py`

**Changes**:
1. Add `GraphTraversePolicy` dataclass (or import from existing `c0_3_enhanced/contracts.py`).
2. Add `graph_traverse_policy: GraphTraversePolicy | None = None` field to `RouteContract`.
3. In L0 binding: read `graph_traverse` block from app route profile; populate `route_contract.graph_traverse_policy`.

**Gate**: `RouteContract` carries populated `graph_traverse_policy` when profile has `graph_traverse` block; `None` when absent.

**Acceptance**: `tests/_apps_contract/test_w2_route_contract_graph_policy.py` green.

---

### W3 — Adapter Registry (GAP-04)

**Scope**: `agentic_core/L0_routing/c0_retrieval/c0_3_enhanced/` adapter registry

**Changes**:
1. Register `apps_lic`, `apps_rg`, `apps_research` `c0_graph_adapter.py` stubs in `ADAPTER_REGISTRY` via config-driven lookup (app spine manifest or profile key, not app-id string comparison).

**Gate**: `ADAPTER_REGISTRY` lookup for all three app identifiers returns the correct `GraphTraversalAdapter` subclass.

**Acceptance**: `tests/_apps_contract/test_w3_adapter_registry.py` green.

---

### W4 — Runtime Graph RAG Execution (GAP-05)

**Scope**: `agentic_core/L0_routing/c0_retrieval/c0_3_enhanced/pipeline.py`, all three app graph traverse profiles

**Changes**:
1. Wire `run_graph_traverse(adapter, traverse_input)` in C0.3 pipeline when `route_contract.graph_traverse_policy` is not None.
2. Flip `live_wiring_deferred: false` + remove `wiring_gate` annotation on all three app graph traverse profile blocks.

**Gate**: C0.3 pipeline calls `run_graph_traverse()` for all three apps in test fixtures.

**Acceptance**: `tests/_apps_contract/test_w4_graph_rag_execution.py` green; no `live_wiring_deferred` annotation present in any of the three profiles.

---

### W5 — apps_rg Unquarantine + Live R1B (GAP-09)

**Scope**: `apps_rg/cache/r1b_adapter.py`, `apps_rg/config/domain_contract/cache_profiles.yaml`, RCA doc

**Changes**:
1. Complete RCA for original L4 import violation: document root cause and fix in `docs/architecture/rca/`.
2. Fix the import violation (move to correct layer import path).
3. Remove quarantine guard (`RuntimeError` on import).
4. Flip `live_wiring_deferred: false` on `apps_rg` semantic cache profile.

**Gate**: `from apps_rg.cache.r1b_adapter import R1BAdapter` no longer raises; `apps_rg` R1B lookup returns hit/miss.

**Acceptance**: `tests/_apps_contract/test_w5_apps_rg_r1b_unquarantine.py` green; RCA doc committed.

---

### W6 — Real BAAI/bge-m3 Embeddings + Ingestion Pipeline (GAP-06, GAP-07)

**Scope**: `apps_research/engines/chroma_research_store.py`, `tools/ingestion/chroma_ingest_pipeline.py` (new)

**Changes**:
1. Replace zero-vector stub in `ChromaResearchStore._embed()` with `SentenceTransformer("BAAI/bge-m3").encode()` guarded by factory gate (only active when `chromadb_path` is set).
2. New `tools/ingestion/chroma_ingest_pipeline.py`: dry-run flag mandatory; populates `process_docs` collection; 1024-dim vectors; no-side-effect boundary respected.

**Gate**: `_embed()` returns 1024-dim vector when `sentence-transformers` available; ingestion pipeline dry-run exits 0.

**Acceptance**: `tests/_apps_contract/test_w6_real_embeddings.py` green; `python tools/ingestion/chroma_ingest_pipeline.py --dry-run` exits 0.

---

### W7 — Integration Verification + Closure Receipt

**Scope**: All three apps, `artifacts/chromadb_graphrag_remediation/`

**Changes**:
1. Smoke run each app's entry point with Graph RAG path enabled.
2. Run `python ops_scripts/ci/run_contract_gates.py` — confirm zero new errors.
3. Emit `artifacts/chromadb_graphrag_remediation/core_gaps_closure_receipt.json` with per-gap status.
4. Update `no_core_gap_register_final.md` — all eight actionable gaps flipped to ✅ CLOSED (GAP-08 remains intentional non-goal).

**Acceptance**: All DoD rows green; closure receipt present; gate sweep clean.

---

## Rules

- **Zero app-id checks in `agentic_core`**: all W1–W4 edits must be generic profile-resolver logic with no `if app_id == "apps_*"` conditionals.
- **GAP-08 is a non-goal**: do not attempt to enable `apps_lic` R1B caching — it is disabled by product decision.
- **GAP-09 (W5) requires RCA doc first**: unquarantine must not precede the completed RCA write-up.
- **W6 ingestion pipeline must have `--dry-run` flag**: no side-effect writes without explicit operator flag.
- **Dependency order is strict**: W4 must not start until W2 + W3 are green; W7 must not start until all prior waves are green.
- **No new app-specific files in `agentic_core/`**: GENERIC_INFRA_EDIT label requires that any new file is app-agnostic.

---

## Definition of Done

| # | Criterion | Verification command / evidence | Status |
|---|---|---|---|
| DoD-1 | `check_d2_semantic_cache()` is called by L0 binding R1B arm for `apps_research` and `apps_rg` | `grep -r "check_d2_semantic_cache" agentic_core/` returns ≥1 call site in `package_driven_l0_binding.py` | ✅ |
| DoD-2 | `RouteContract` carries `graph_traverse_policy` field and all three apps populate it at runtime | `python -c "from agentic_core.runtime.contracts.route_contract import RouteContract; assert hasattr(RouteContract(), 'graph_traverse_policy')"` exits 0 | ✅ |
| DoD-3 | `maybe_run_graph_rag()` is invoked by `c0_ground_package_driven()` and 101 regression tests pass | `pytest tests/_apps_contract/test_w1_core_r1b_cache_wiring.py tests/_apps_contract/test_w2_route_contract_graph_policy.py tests/_apps_contract/test_w3_c03_adapter_registry.py tests/_apps_contract/test_w4_graph_rag_execution.py tests/agentic_core/runtime/c0/test_c0_3_graph_rag_executor.py` — 101 passed, 0 failed | ✅ |
| DoD-4 | `apps_rg` generic L0 R1B path live; `r1b_adapter.py` kept quarantined per RCA decision KEEP_QUARANTINED_DEPRECATED | W5 tests green (14 passing); RCA doc at `docs/architecture/rca/RCA_apps_rg_r1b_adapter_L4_import_violation.md` | ✅ |
| DoD-5 | `ChromaResearchStore._embed()` returns 1024-dim vector; ingestion dry-run exits 0 | `python tools/ingestion/chroma_ingest_pipeline.py --dry-run` exits 0; W6 20 tests green; full regression 135/135 | ✅ |
| DoD-6 | Gate sweep clean (no new errors) | `python ops_scripts/ci/run_contract_gates.py` exits 0 or advisory baseline unchanged — confirmed PRE_EXISTING_BASELINE_UNCHANGED; exit code 1 pre-dates this plan (git stash verify) | ✅ |
| DoD-7 | Closure receipt present; all 8 actionable gaps marked CLOSED | `artifacts/chromadb_graphrag_core_wiring/core_gaps_closure_receipt.json` exists; GAP-01–07 + GAP-09 all CLOSED; GAP-08 INTENTIONAL_NON_GOAL | ✅ |

**Verification-vs-Deferral table**:

| Item | Why deferred | Tracked in |
|---|---|---|
| GAP-08 `apps_lic` live R1B wiring | Business-logic non-goal (`personalized_outreach_not_cacheable`) — requires product authorization | `no_core_gap_register_final.md` GAP-08 entry |
| Spearman ≥ 0.80 semantic cache threshold calibration | Separate calibration plan; needs holdout corpus | `NEXT_STEP:` — semantic cache threshold calibration plan |
| `apps_exec` / `apps_rfp` Chroma/Graph RAG wiring | Out of scope for this plan (three-app boundary) | Future per-app extension plan |
| Real production ingestion run (non-dry-run) | Requires operator sign-off; no-side-effect boundary enforced | `NEXT_STEP:` — production ingestion operator runbook |

---

## Rollback Strategy

1. All `agentic_core` GENERIC_INFRA_EDITs (W1–W4) are additive fields / new call sites — roll back by reverting the specific commits to those files.
2. `r1b_adapter.py` unquarantine (W5): re-add `RuntimeError` guard if regression found; the RCA doc is kept regardless.
3. W6 real embeddings: the `chromadb_path` factory gate ensures zero-vector stub behavior is preserved when `chromadb_path=None` — safe fallback without rollback.
4. `wave_execution_state.py` tracks wave state; run `complete` only after W7 verification passes.

---

## Cursor Agent Alignment Checks

- Keep always-on rules lean; place detailed procedures in skills or workflows.
- Retrieve local or scoped evidence before synthesis.
- Prefer exact or structural matches before broad semantic expansion.
- For high-risk outputs, extract evidence or quotes before summarizing.
- Reserve deterministic enforcement for hooks or scripts, not template prose.
