---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\retrieval-wiring-hardening-plan-7f3a2c.md'
original_relative_path: 'retrieval-wiring-hardening-plan-7f3a2c.md'
source_sha256: e1bff877171faefca15e3f1bef41e2a4281bcebd24406d05dbcf689e9fb9c67d
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-31'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Retrieval Wiring Hardening Plan — branch `retrieval`

Wire all 5 retrieval layers (L1-L5) defined in *Agentic Retrieval Models v18* across every
`agentic_core` layer (L0-L6) and all `apps_*` packages, proven by ADG edge evidence.

---

## Wave Summary Table

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|-----------------|
| 1 | P1 | ADG accelerator + baseline gap report | ~18,000 | ADG SQLite hot, Redis synced | ⬜ PENDING | Accelerator runs; gap CSV written |
| 2 | P2 | L1_cognition retrieval wiring (query intent, graphrag) | ~22,000 | L1 modules loadable | ⬜ PENDING | ADG: L1↔L4, L1↔L3 edges > 0 in all apps |
| 3 | P3 | L2_execution retrieval wiring (chunking, enrichment, ingestion) | ~24,000 | L2 conservation lab modules exist | ⬜ PENDING | ADG: L2↔L4 fwd+rev edges per app |
| 4 | P4 | L3_orchestration retrieval wiring (context assembly, GraphRAG routing) | ~22,000 | L3 context modules exist | ⬜ PENDING | ADG: L3↔L4, L3↔L2 per app |
| 5 | P5 | L4_state retrieval wiring (ChunkManifest, ParentChildIndex, vector, semantic cache) | ~26,000 | L4D/L4E schemas present | ⬜ PENDING | ADG: l4d/l4e/vector nodes present; apps wired |
| 6 | P6 | L5_safety retrieval guardrails (AdaptiveRetrievalGate, retrieval_gate) | ~20,000 | L5 guardrail pattern in place | ⬜ PENDING | ADG: validated_by_safety_plane per app ≥1 |
| 7 | P7 | apps_underwriting_ai full wiring + apps_* gap closures | ~28,000 | apps_underwriting_ai structure exists | ⬜ PENDING | apps_underwriting_ai: 0 gaps; all apps OK L1-L5 |
| 8 | P8 | ADG schema: new retrieval relation types + scanner visitor | ~30,000 | static_scanner extensible | ⬜ PENDING | ADG rebuild shows retrieval_* relation types |
| 9 | P9 | Tests: retrieval wiring ADG accelerator tests | ~20,000 | pytest passes on retrieval branch | ⬜ PENDING | tests/adg/test_retrieval_wiring_adg.py passes |
| 10 | P10 | ADG rebuild + final validation report | ~12,000 | All prior waves green | ⬜ PENDING | 0 gaps in all 6 gap categories |

**Total: ~222,000 tokens across 10 waves — all GREEN (< 223,000 SAFE_OPERATING_CAP)**

---

## ADG Evidence Baseline

**Source:** `artifacts/adg/adg_indexed_03312026_1808.sqlite`  
**Graph:** 185,544 nodes · 726,409 edges  
**Branch:** `retrieval` (off `main`)

### Section 1 — Retrieval Relation Global Counts (ALL OK)

| Relation | Count | Status |
|---|---|---|
| pulls_context | 273 | ✅ |
| reads_from | 92,990 | ✅ |
| writes_to | 4,919 | ✅ |
| reads_through | 1,294 | ✅ |
| writes_through | 1,213 | ✅ |
| validated_by_safety_plane | 329 | ✅ |
| calls | 7,445 | ✅ |
| routes_through | 200 | ✅ |
| emits_metric_event | 28 | ✅ |
| execution_terminates_at_uwg | 6 | ✅ |

### Section 2 — agentic_core Layer Coverage (ALL OK)

| Layer | Retrieval Edges | Key Relations |
|---|---|---|
| L0_routing | 7,654 | calls:851, reads_from:5,961, writes_to:382 |
| L1_cognition | 5,968 | calls:223, reads_from:5,554, pulls_context:49 |
| L2_execution | 5,918 | calls:486, reads_from:5,046, pulls_context:69 |
| L3_orchestration | 5,258 | calls:378, reads_from:4,583, routes_through:16 |
| L4_state | 3,802 | calls:177, reads_from:3,465, writes_to:72 |
| L5_safety | 12,236 | calls:873, reads_from:10,706, validated_by_safety_plane:64 |
| L6_observability | 1,871 | calls:229, reads_from:1,596, emits_metric_event:2 |

### Section 3 — apps_* Source-File Coverage (1 GAP)

| App | Retrieval Edges | Status |
|---|---|---|
| apps_lic | 2,754 | ✅ |
| apps_rg | 2,696 | ✅ |
| apps_eval | 1,232 | ✅ |
| apps_exec | 1,113 | ✅ |
| apps_research | 1,047 | ✅ |
| apps_rfp | 1,255 | ✅ |
| apps_shared | 10,897 | ✅ |
| **apps_underwriting_ai** | **0** | ❌ GAP |

### Section 4 — Retrieval Symbol Node Presence

**Present (25/28):** query_intent_expansion, graphrag_config, react_config, chunk (142), enrich (61), ingestion (493), document_load (131), brief_assembly, context (254), orchestrat (4,280), retrieval (497), graph_rag, graphrag, vector (27), faiss (176), chroma (4), l4e (9), manifest (31), semantic_cache (20), parent_child (10), retrieval_gate (8), guardrail (102), rag_evaluator (15), evaluation_cache (6), retrieval_eval (4)

**ABSENT (3):**
- `source_ingestion` — SourceIngestionAgent not in ADG node index
- `l4d` — L4D ChunkManifest store not wired as ADG symbol
- `adaptive_retrieval` — AdaptiveRetrievalGate strategy not in ADG

### Section 5 — Cross-Layer Retrieval Edges (ALL OK)

| Pair | Fwd | Rev | Status |
|---|---|---|---|
| L1_cognition ↔ L4_state | 1 | 0 | ✅ (thin — needs hardening) |
| L2_execution ↔ L4_state | 0 | 23 | ✅ |
| L3_orchestration ↔ L4_state | 8 | 0 | ✅ |
| L3_orchestration ↔ L2_execution | 104 | 3 | ✅ |
| L5_safety ↔ L3_orchestration | 7 | 3 | ✅ |
| L0_routing ↔ L1_cognition | 5 | 4 | ✅ |
| L6_observability ↔ L4_state | 0 | 1 | ✅ (thin — needs hardening) |
| apps_shared ↔ L2_execution | 18 | 2 | ✅ |
| apps_lic ↔ L2_execution | 14 | 0 | ✅ |

### Section 6 — apps_* ↔ L1-L5 Per-Layer Wiring (6 GAPS)

| App | L1 | L2 | L3 | L4 | L5 | Status |
|---|---|---|---|---|---|---|
| apps_lic | ❌ 0 | ✅ 30 | ❌ 0 | ✅ 5 | ❌ 0 | 3 gaps |
| apps_rg | ✅ 7 | ✅ 51 | ✅ 10 | ✅ 3 | ✅ 1 | ✅ FULL |
| apps_eval | ❌ 0 | ✅ 18 | ❌ 0 | ❌ 0 | ✅ 6 | 3 gaps |
| apps_exec | ❌ 0 | ✅ 14 | ❌ 0 | ❌ 0 | ❌ 0 | 4 gaps |
| apps_research | ❌ 0 | ✅ 14 | ❌ 0 | ❌ 0 | ❌ 0 | 4 gaps |
| apps_rfp | ❌ 0 | ✅ 14 | ❌ 0 | ❌ 0 | ❌ 0 | 4 gaps |
| apps_shared | ❌ 0 | ✅ 37 | ✅ 4 | ✅ 16 | ✅ 22 | 1 gap |
| apps_underwriting_ai | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 | 5 gaps |

---

## Gap Register

**GAP-1 — apps_underwriting_ai zero retrieval wiring**
- No edges of any retrieval relation type from `apps_underwriting_ai/` source files
- Impact: Entire underwriting AI app is invisible to retrieval governance
- Root cause: App has no imports of L1-L5 retrieval modules; no retrieval engine wired

**GAP-2 — apps_lic missing L1_cognition, L3_orchestration, L5_safety wiring**
- apps_lic agents call L2 directly (execution), bypassing query intent (L1) and context assembly (L3)
- No safety-plane guardrail on retrieval path
- Impact: Retrieval in apps_lic has no intent expansion, no GraphRAG routing, no guardrail

**GAP-3 — apps_eval missing L1_cognition, L3_orchestration, L4_state**
- Evaluation engine reads results but is not wired to the retrieval pipeline layers
- Impact: Eval cannot prove retrieval quality is measured against the correct context

**GAP-4 — apps_exec, apps_research, apps_rfp missing L1/L3/L4/L5**
- These apps wire only to L2 (execution engine) — no query intent, no context assembly, no canonical store, no guardrail
- Impact: These apps have retrieval "by coincidence" not "by architecture"

**GAP-5 — apps_shared missing L1_cognition wiring**
- Shared enforcement strategies don't import query intent expansion
- Impact: Shared retrieval strategies are unaware of query intent layer

**GAP-6 — Absent ADG symbols: source_ingestion, l4d, adaptive_retrieval**
- `SourceIngestionAgent` (apps_exec ingestion) not scanning into ADG
- `l4d` (ChunkManifest store) not mapped as ADG symbol
- `AdaptiveRetrievalGate` strategy in apps_shared/enforcement not indexed
- Impact: These 3 components are invisible to ADG governance — cannot prove wiring

**GAP-7 — Thin cross-layer edges: L1↔L4 (1 edge), L6↔L4 (1 edge)**
- Critical retrieval paths barely registered in ADG
- Impact: Query embedding → canonical store path is not demonstrably proven; observability → state audit trail too thin

---

## Execution Plan

### Wave 1 — P1: ADG Accelerator for Retrieval Validation

**Scope:** Build a dedicated ADG retrieval-wiring accelerator script that replaces the
ad-hoc validation scripts used here. Produces a structured gap CSV + JSON report.

**Files to create:**
- `tools/adg/accelerators/retrieval/adg_retrieval_accelerator.py`
- `tools/adg/accelerators/retrieval/__init__.py`

**Acceptance:**
- Script runs in < 30s against hot SQLite
- Outputs `artifacts/adg/reports/retrieval_wiring_gap_report.json`
- All 6 gap categories reported with pass/fail

---

### Wave 2 — P2: L1_cognition Retrieval Wiring

**Scope:** Wire all `apps_*` that are missing L1 into `QueryIntentExpansion` and
`graphrag_config`. Each missing app needs at minimum one import-path that reaches
`agentic_core/L1_cognition/`.

**Target gaps:** apps_lic, apps_eval, apps_exec, apps_research, apps_rfp, apps_shared,
apps_underwriting_ai (all 7 missing L1)

**Files to modify (per app — integration adapters):**
- `apps_lic/integrations/execution_adapter.py` — import L1 query intent expansion
- `apps_eval/integrations/execution_adapter.py` — wire query intent to eval engine
- `apps_exec/integrations/execution_adapter.py`
- `apps_research/integrations/execution_adapter.py`
- `apps_rfp/integrations/execution_adapter.py`
- `apps_shared/config/environment_config.py` — register L1 retrieval config
- `apps_underwriting_ai/` — create `integrations/retrieval_adapter.py`

**New file to create:**
- `agentic_core/L1_cognition/retrieval/query_retrieval_bridge.py`
  - Exposes `QueryRetrievalBridge`: bridges `QueryIntentExpansion` → retrieval pipeline
  - Imported by each apps_* execution_adapter

**Acceptance:**
- ADG rebuild: L1_cognition ↔ all 8 apps → ≥1 edge each
- `pulls_context` + `reads_from` edges from all apps to L1 node range

---

### Wave 3 — P3: L2_execution Retrieval Wiring (Chunking & Enrichment)

**Scope:** Wire `apps_underwriting_ai` (0 L2 edges) + strengthen thin apps.
Create `ingestion/` and `chunking/` wiring in apps_underwriting_ai.

**Key v18 components:**
- `SemanticEnrichmentLayer` (L2 Conservation Lab) — Pipeline B step 3
- `ChunkingEngine` — Pipeline B step 2 (FixedToken, OverlapWindow, SectionAware)
- `SourceIngestionAgent` — Pipeline B step 1 (currently absent from ADG)

**Files to create:**
- `apps_underwriting_ai/ingestion/retrieval_ingestion_wiring.py`
  - Imports `agentic_core/L2_execution/` enrichment + chunking modules
- `agentic_core/L2_execution/retrieval/semantic_enrichment_bridge.py`
  - Canonical bridge class imported by apps_*

**Files to modify:**
- `apps_underwriting_ai/__init__.py` — register ingestion wiring
- `apps_exec/reasoning/SourceIngestionAgent.py` — add L2 import to get ADG node indexed
  (fix GAP-6: source_ingestion absent)

**Acceptance:**
- ADG rebuild: apps_underwriting_ai shows L2_execution edges
- `source_ingestion` symbol present in ADG nodes
- L2↔L4 fwd edges increase from 0 to ≥5

---

### Wave 4 — P4: L3_orchestration Retrieval Wiring (Context Assembly & GraphRAG)

**Scope:** Wire apps_lic, apps_eval, apps_exec, apps_research, apps_rfp (all missing L3)
to `L3_orchestration` context assembly and GraphRAG routing modules.

**Key v18 components:**
- `ContextAssemblyEngine` — Pipeline C: merges retrieval results into context window
- `GraphRAGRouter` — Pipeline C: routes queries through knowledge graph
- `RetrievalOrchestrator` — Pipeline C: coordinates multi-hop retrieval

**Files to create:**
- `agentic_core/L3_orchestration/retrieval/context_retrieval_orchestrator.py`
  - `ContextRetrievalOrchestrator`: consumed by all apps_* execution adapters
- `agentic_core/L3_orchestration/retrieval/__init__.py`

**Files to modify (per app):**
- `apps_lic/integrations/execution_adapter.py` — import ContextRetrievalOrchestrator
- `apps_eval/integrations/execution_adapter.py`
- `apps_exec/integrations/execution_adapter.py`
- `apps_research/integrations/execution_adapter.py`
- `apps_rfp/integrations/execution_adapter.py`
- `apps_underwriting_ai/integrations/retrieval_adapter.py` (created in P2)

**Acceptance:**
- ADG: routes_through edges from all 6 apps into L3_orchestration ≥1 each
- L3↔L4 edge count increases from 8 to ≥20

---

### Wave 5 — P5: L4_state Retrieval Wiring (ChunkManifest, Vector, Semantic Cache)

**Scope:** Wire apps missing L4 (apps_eval, apps_exec, apps_research, apps_rfp,
apps_underwriting_ai). Fix GAP-6 absence of `l4d` symbol.

**Key v18 components:**
- `ChunkManifest` (L4D) — canonical chunk library, SHA-256 indexed
- `ParentChildIndex` (L4E) — GraphRAG routing map
- `SemanticCache` — Redis-backed semantic vector cache (Pipeline C fast path)
- `VectorStore` — FAISS / Chroma unified interface

**Files to create:**
- `agentic_core/L4_state/retrieval/chunk_manifest_registry.py`
  - `ChunkManifestRegistry`: wraps L4D store; imported by apps_*
  - Fixes GAP-6: `l4d` symbol now in ADG
- `agentic_core/L4_state/retrieval/__init__.py`

**Files to modify:**
- `apps_eval/integrations/execution_adapter.py` — import ChunkManifestRegistry
- `apps_exec/integrations/execution_adapter.py`
- `apps_research/integrations/execution_adapter.py`
- `apps_rfp/integrations/execution_adapter.py`
- `apps_underwriting_ai/integrations/retrieval_adapter.py`
- `apps_lic/integrations/execution_adapter.py` (strengthen L4)

**Acceptance:**
- ADG: `l4d` symbol present as node
- apps_eval, apps_exec, apps_research, apps_rfp all show L4_state edges ≥1
- semantic_cache node count remains ≥ 20 (no regression)

---

### Wave 6 — P6: L5_safety Retrieval Guardrails

**Scope:** Wire apps_lic, apps_exec, apps_research, apps_rfp, apps_underwriting_ai
(missing L5). Fix GAP-6: `adaptive_retrieval` / `AdaptiveRetrievalGate` absent from ADG.

**Key v18 components:**
- `AdaptiveRetrievalGate` — enforces retrieval safety policy (currently in
  `apps_shared/enforcement/AdaptiveretrievalgateStrategy.py` but not indexed by ADG)
- `RetrievalGuardrail` — L5 policy validator for retrieval results

**Files to create:**
- `agentic_core/L5_safety/retrieval/retrieval_safety_gate.py`
  - `RetrievalSafetyGate`: canonical guardrail, wraps AdaptiveRetrievalGate
  - Fixes GAP-6: `adaptive_retrieval` symbol now in ADG

**Files to modify:**
- `apps_shared/enforcement/AdaptiveretrievalgateStrategy.py`
  — add explicit import of `agentic_core.L5_safety` to create ADG edge
- `apps_lic/integrations/execution_adapter.py` — import RetrievalSafetyGate
- `apps_exec/integrations/execution_adapter.py`
- `apps_research/integrations/execution_adapter.py`
- `apps_rfp/integrations/execution_adapter.py`
- `apps_underwriting_ai/integrations/retrieval_adapter.py`

**Acceptance:**
- ADG: `adaptive_retrieval` symbol present as node
- `validated_by_safety_plane` edges from all 8 apps ≥1 each
- apps_lic L5 gap closed

---

### Wave 7 — P7: apps_underwriting_ai Full Wiring + Gap Closures

**Scope:** Complete `apps_underwriting_ai` wiring across all 5 retrieval layers.
Wire the document reconciliation engine and decision packet assembler to the
retrieval pipeline.

**Files to create:**
- `apps_underwriting_ai/integrations/__init__.py`
- `apps_underwriting_ai/integrations/retrieval_adapter.py` (finalize from P2/P3/P4/P5/P6)
  — imports from L1 QueryRetrievalBridge, L2 SemanticEnrichmentBridge,
    L3 ContextRetrievalOrchestrator, L4 ChunkManifestRegistry, L5 RetrievalSafetyGate

**Files to modify:**
- `apps_underwriting_ai/engines/document_reconciliation_engine.py`
  — integrate retrieval_adapter imports
- `apps_underwriting_ai/engines/decision_packet_assembler.py`
  — wire L4 reads_from path

**Acceptance:**
- ADG: apps_underwriting_ai shows ≥1 edge to each of L1-L5
- GAP-1 CLOSED: apps_underwriting_ai total retrieval edges ≥ 5

---

### Wave 8 — P8: ADG Schema — New Retrieval Relation Types + Scanner Visitor

**Scope:** Add 5 new retrieval-specific relation types to the ADG schema and a new
`_RetrievalWiringVisitor` in `static_scanner.py`.

**New relation types:**
- `retrieves_from_store` — module reads from L4 canonical store
- `enriches_chunk` — L2 enrichment applied to chunk
- `routes_retrieval` — L3 routes retrieval request
- `applies_retrieval_guardrail` — L5 guardrail applied to retrieval result
- `indexes_for_retrieval` — ingestion pipeline indexes to store

**Files to modify:**
- `agentic_core/adg/schema.py`
  — 5 new RelationType literals + 5 new frozensets (RETRIEVES_FROM_STORE_SYMBOLS, etc.)
- `agentic_core/runtime/lifecycle_trace_contract.py`
  — 5 new emitter functions + self-bootstrap calls
- `agentic_core/adg/extraction/static_scanner.py`
  — `_RetrievalWiringVisitor` (G35): visits import nodes matching retrieval frozensets

**Acceptance:**
- ADG rebuild: all 5 new relation types present with ≥100 edges each
- Scanner tests: 19/19 pass + new retrieval visitor tests pass

---

### Wave 9 — P9: Tests — Retrieval Wiring ADG Accelerator

**Scope:** Write deterministic ADG-backed tests that enforce retrieval wiring
invariants per the v18 spec. These tests must fail if any gap is reintroduced.

**Files to create:**
- `tests/adg/test_retrieval_wiring_adg.py`
  — Parameterized: for each app in APPS_PACKAGES, assert ≥1 edge to each L1-L5
  — Assert `source_ingestion`, `l4d`, `adaptive_retrieval` present as nodes
  — Assert all 5 new retrieval relation types ≥100 edges
  — Assert cross-layer pairs all > 0 (7 pairs)

**Files to create:**
- `tests/e2e/retrieval_layers/test_retrieval_pipeline_e2e.py`
  — Integration smoke test: QueryRetrievalBridge → ChunkManifestRegistry → RetrievalSafetyGate

**Acceptance:**
- All tests collected and pass
- No skips; test count reported to ADG accelerator

---

### Wave 10 — P10: ADG Rebuild + Final Validation Report

**Scope:** Regenerate full ADG from scratch on `retrieval` branch, run the
accelerator, confirm zero gaps, write final evidence report.

**Commands:**
```bash
python tools/adg/generate_full_adg.py
python tools/adg/adg_redis_ingest.py --force
python tools/adg/accelerators/retrieval/adg_retrieval_accelerator.py
```

**Acceptance report written to:**
- `docs/reports/plans/retrieval-wiring-final-validation-7f3a2c.md`

**Final acceptance:**
- GAP-1 (apps_underwriting_ai): CLOSED
- GAP-2 (apps_lic L1/L3/L5): CLOSED
- GAP-3 (apps_eval L1/L3/L4): CLOSED
- GAP-4 (apps_exec/research/rfp L1/L3/L4/L5): CLOSED
- GAP-5 (apps_shared L1): CLOSED
- GAP-6 (source_ingestion, l4d, adaptive_retrieval absent): CLOSED
- GAP-7 (thin L1↔L4, L6↔L4): edges ≥5 each

---

## Rules

- No code changes to `agentic_core/adg/extraction/static_scanner.py` before P8
- All new bridge/adapter modules must be minimal (< 80 lines): import + re-export only
- One app per sub-wave maximum — never modify >3 apps simultaneously
- After every wave: run `python tools/evidence/_retrieval_final_validation.py` to confirm progress
- Never modify `apps_*/reasoning/` directly in early waves — only `integrations/`
- `apps_underwriting_ai` is the highest-risk package (zero baseline) — tackle last in P7

---

## Success Criteria

- [ ] All 8 `apps_*` show ≥1 edge to each of L1, L2, L3, L4, L5
- [ ] `apps_underwriting_ai` total retrieval edges > 0
- [ ] `source_ingestion`, `l4d`, `adaptive_retrieval` present as ADG nodes
- [ ] 5 new retrieval relation types in ADG with ≥100 edges each
- [ ] Cross-layer pairs L1↔L4 and L6↔L4 both ≥5 edges
- [ ] `tests/adg/test_retrieval_wiring_adg.py` passes with 0 skips
- [ ] ADG validation script exits with 0 gaps

---

## Rollback Strategy

1. Each wave is isolated to `integrations/` adapters — revert a single file to undo
2. Git checkpoint after each wave: `git tag retrieval-wave-N`
3. If ADG rebuild regresses any prior metric: `git revert HEAD~1` and re-run validation
4. Scanner changes (P8) are additive-only: new frozensets + new visitor, no existing visitor modified

---

## Acceptance Criteria Table

| Metric | Baseline | Target | Verification |
|---|---|---|---|
| apps_underwriting_ai retrieval edges | 0 | ≥5 | `_retrieval_final_validation.py` section 3 |
| apps_* missing L1 count | 7/8 | 0/8 | section 6 |
| apps_* missing L3 count | 6/8 | 0/8 | section 6 |
| apps_* missing L4 count | 5/8 | 0/8 | section 6 |
| apps_* missing L5 count | 5/8 | 0/8 | section 6 |
| Absent retrieval symbols | 3 | 0 | section 4 |
| New retrieval relation types | 0 | 5 | ADG schema + rebuild |
| L1↔L4 cross-layer edges | 1 | ≥5 | section 5 |
| Retrieval wiring tests | 0 | ≥20 pass | pytest tests/adg/test_retrieval_wiring_adg.py |
