---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\chromadb-bge-retrieval-hardening-e9aa09.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\chromadb-bge-retrieval-hardening-e9aa09.md'
source_sha256: 84482b160610cf2b4a6e1911868f944f7747251eb7d505054e387b893954428d
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ChromaDB + BGE-M3 Retrieval Hardening

**Plan ID:** `chromadb-bge-retrieval-hardening-e9aa09`
**Tier:** T3 (architectural, cross-layer, >5 files, irreversible data moves)
**Created:** 2026-04-23
**ADG Snapshot:** `adg_indexed_04232026_1802.sqlite` (73,697 nodes / 541,204 edges — healthy sqlite+redis)
**Status:** DRAFT — awaiting Author-Gate on wave ordering before execution

---

## 1. Executive Summary

The repository runs **two parallel ChromaDB stores** with **inconsistent embedding metadata**, **stale ADG joinability**, **silent zero-vector fallbacks**, **skipped code entities**, and **no post-ingest validation in the orchestrator**. Retrieval quality is therefore a function of which store a consumer happens to query — not a property of the pipeline. This plan closes those gaps in five waves under a single canonical store (`data/cache/chromadb/`) with a unified metadata contract and deterministic BGE-M3 (1024-d, L2-normalised) embeddings.

## 2. Current State — Evidence

### 2.1 Two stores, split corpus (measured 2026-04-23)

| Collection | `artifacts/chromadb/` | `data/cache/chromadb/` |
|---|---:|---:|
| code_chunks / repo_code_chunks | 16,943 | 3,584 |
| symbols | — | 78,591 |
| docs | 9,816 | — |
| tests_guardrails / repo_tests_guardrails | 2,682 | 8,317 |
| process_docs | — | 7,667 |
| runtime_evidence / repo_runtime_evidence | 125 | 255 |
| incidents_rca / repo_incidents_rca | 212 | 190 |
| repo_evidence | — | 3,489 |
| ext_authority / ext_raw | — | 604 / 70 |
| traces / agentic_best_practices | 0 / 0 | — |
| repo_adg_graph | **ERROR (compactor)** | — |

- `tools/generate/ingestion/validate_collection.py:35` declares `data/cache/chromadb/` as **`CANONICAL_STORE`**.
- `tools/ingestion/ingest_code.py:449` writes to **`artifacts/chromadb/`**.
- `tools/ingestion/ingest_docs.py:341` writes to **`artifacts/chromadb/`**.
- `SovereignChromaClient(persist_dir=…)` default is **`data/cache/chromadb/`**.
- No ADR reconciles these. ADR-018 declares ChromaDB canonical but does not specify the path.

### 2.2 Embedding-path defects

| Location | Defect |
|---|---|
| `tools/ingestion/ingest_code.py:326-327,376-377` | Metadata stamps `"embedding_model": "fallback_hash_384"` but `SovereignChromaClient.embed_texts` always uses BGE-M3 1024-d when `EMBEDDING_ENABLED=true`. Provenance is wrong. |
| `tools/ingestion/ingest_docs.py:298-304` | `_generate_bge_m3_embeddings` silently falls back to **all-zero vectors** on any exception. Zero vectors corrupt cosine similarity (every query returns arbitrary top-K). |
| `tools/ingestion/ingest_docs.py:237,249,260` | Default `embedding_provider="openai"` with dim=1536. Mixed with BGE 1024 → HNSW dim-mismatch if collection reused. |
| `tools/ingestion/ingest_code.py:567` | Hardcoded `stats["vector_dimensions"] = 384` in report — contradicts actual 1024-d store. |
| `agentic_core/L4_state/utils/client/chroma_client.py:54-57` | Collection metadata sets only `hnsw:space=cosine`; no `embedding_model`, no `embedding_dim`. Validator warns but does not fail. |
| `ingest_code.py` → BM25 populated; `ingest_docs.py` / traces / rca / runtime → no sparse index. Hybrid retrieval degraded for 5 of 7 collections. |

### 2.3 ADG joinability defects

| Location | Defect |
|---|---|
| `tools/ingestion/ingest_code.py:455` | Hardcoded `adg_db_path = "artifacts/adg/adg_indexed_04062026_1246.sqlite"`. Current snapshot is `04232026_1802` — 17+ days old. All stored `adg_node_id` values are stale. |
| `ADGNodeResolver._load` | Keys by `(basename, tail)` — ambiguous when two modules share file basename + symbol name. No fallback to `resolved_path` full match. |
| `ingest_docs`, `ingest_tests`, `ingest_traces` | No ADG node linkage at all. Cross-index joins from docs → code graph impossible. |

### 2.4 Coverage holes

| Source | Covered | Skipped |
|---|---|---|
| `ingest_code.py:213,223,229` | Classes with ≥1 method; functions with ≥1 arg | **Zero-arg functions, argless async, classes with no methods** — discards ~10-15 % of ADG nodes including most validators and guard modules. |
| `pipeline.py:66` | `--source-dir agentic_core` only | `apps_rg`, `apps_lic`, `apps_eval`, `apps_exec`, `apps_research`, `apps_rfp`, `apps_shared`, `apps_underwriting_ai`, `system_learning`, `infrastructure`, `tools`, `ops_scripts` — all excluded from code ingest. |
| `ingest_docs.py` | `docs/` markdown | Does not ingest `AGENTS.md`, `.windsurf/rules/*`, `.windsurf/plans/*`, `.windsurf/skills/*`, ADR bodies under `docs/architecture/adr/` get ingested but without ADR-specific metadata extraction. |
| `traces` collection | Empty | `data/corpus/healing_contexts_corpus.jsonl` is the declared source but the collection is `0` — ingest never succeeded or was wiped. |
| `repo_adg_graph` | Corrupt | Compactor error on `count()` — not recoverable via `delete_collection` without forcing WAL clean. |

### 2.5 Schema drift

`ingest_code` metadata: `{file_path, module, layer, entity_type, name, line_start, line_end, type, args, docstring, methods, adg_node_id, embedding_model, ingested_at, parent_id, chunk_context}`

`ingest_docs` metadata: `{doc_id, doc_type, layer, file_path, created_date, category, section, subsection, chunk_type}`

`tools/generate/ingestion/*` required keys (from validator): `{artifact_type, file_path, layer, canonical_digest, entity_type, ...}`

No overlap on `canonical_digest`, `artifact_type`, `embedding_model`, `embedding_dim`. Cross-collection queries cannot filter by these.

### 2.6 Ingestion-orchestrator defects

- `tools/ingestion/pipeline.py` orchestrates only the **older** 7 scripts; the **newer** 11 scripts under `tools/generate/ingestion/` (curated agent docs, ext authority, symbols, code_chunks, arch_docs, repo_evidence, …) have no orchestrator.
- No post-ingest validate step; `validate_collection.py` is never invoked by `pipeline.py`.
- `ingest_docs.py:365-370` chunk IDs include a per-loop index, so **re-ingest duplicates every chunk** rather than upserts.
- `SOURCE_ENV_DEFAULTS` sets `EMBEDDING_DEVICE=cuda` unconditionally — silent failure on CPU-only hosts.

### 2.7 Retrieval-time consumers (blast radius)

Consumers that read ChromaDB (ADG fan-in sample; non-exhaustive):

| Consumer | Layer | Impact of split-brain |
|---|---|---|
| `agentic_core/L1_cognition/reasoning/semantic_retriever.py` | L1 | Unknown which store it queries; coverage gaps = missed context. |
| `agentic_core/L3_orchestration/engines/hybrid_search_engine.py` | L3 | Dense+BM25 fusion — BM25 missing for 5/7 collections. |
| `agentic_core/L4_state/cache/gptcache_client.py` | L4 | GPTCache backend; uses ChromaDB for semantic cache (ADR-018). |
| `apps_rg/engines/achievement_prioritizer_engine.py`, etc. | L_APPS | Per-app retrieval. |

## 3. ADG_GRAPH_LAYER_EVIDENCE

> Constitutional §22 requires materialized-view and semantic-edge evidence for T3 refactoring plans.

### 3.1 Materialized-view hotspot citations

- **`mv_graph_reverse_dependency_hotspots`** — ranks `SovereignChromaClient`, `bge_runtime`, `semantic_retriever`, `hybrid_search_engine` by fan-in. Expect `chroma_client` in top-50 (L4 infra consumed by L1/L3/L_APPS).
- **`mv_hotspot_centrality`** — betweenness for ingestion bridge modules (`_embedding_factory_bridge.py`, `contextual_chunk_builder.py`).
- **`mv_dependency_cone_risk`** — cone risk from `ingest_code.py` / `ingest_docs.py` scripts into consumers; confirms that fixing the ingest pipeline alone avoids touching most call sites.

### 3.2 Semantic edges used

- `imports` — to enumerate consumers of `SovereignChromaClient` and `bge_runtime`.
- `reads_from` / `writes_to` — ChromaDB persist_dir write sites (ingest scripts) and read sites (retrieval engines).
- `flows_to` — document → chunk → embedding → collection.add.

### 3.3 P-view cross-references

- **`v_p0_apps_direct_infra`** — does any `apps_*` file import `chromadb.PersistentClient` directly (bypassing `SovereignChromaClient`)? To be confirmed in Wave 0.
- **`v_p1_mis_layered_infra`** — `tools/ingestion/*.py` importing from `agentic_core.L4_state.utils.client.chroma_client` is OK (tool → L4 utility). Flag any tool importing L1/L2/L3 reasoning modules.
- **`v_p2_duplicated_adapters`** — the `_embedding_factory_bridge.py` in `tools/ingestion/` vs. `agentic_core/embeddings/embedding_factory.py`. Candidate consolidation.

### 3.4 Surface intersection

- **Execution surface:** ingest scripts invoke `SentenceTransformer.encode` (L_EMBED) and `PersistentClient.add` (L4). Silent zero-fallback (§2.2) = swallowed execution failure.
- **State surface:** split-brain persist_dir = two canonical stores = silent state inconsistency.
- **Observability surface:** embedding_model metadata lies → forensics broken.

## 4. ADG_HOTSPOT_REPORT

| Rank | Node / File | Layer | Archetype | Fan-in | Violations (surface) | Impact |
|---|---|---|---|---:|---|---:|
| 1 | `agentic_core/L4_state/utils/client/chroma_client.py` | L4 | STATE_NODE | high (all ingest + retrieval paths) | State (split-brain), Observability (weak metadata) | **P1** — ×1.75 layer |
| 2 | `agentic_core/embeddings/bge_runtime.py` | L4_EMBED (infra) | CENTRAL_DEPENDENCY | high | Execution (device fallback OK); no known defect | P3 |
| 3 | `tools/ingestion/ingest_code.py` | L_TOOLS | ORCHESTRATOR | low | Execution (stale ADG), Observability (lying metadata) | **P1** |
| 4 | `tools/ingestion/ingest_docs.py` | L_TOOLS | ORCHESTRATOR | low | Execution (silent zero fallback), State (wrong store) | **P0** — zero-vector corruption |
| 5 | `tools/ingestion/pipeline.py` | L_TOOLS | ORCHESTRATOR | low | State (ignores newer ingestion set) | P2 |
| 6 | `tools/generate/ingestion/*` (11 files) | L_TOOLS | ORCHESTRATOR | low | No orchestrator → unknown liveness | P2 |

## 5. Gap Register

| ID | Gap | Severity | Wave |
|---|---|:---:|:---:|
| G1 | Silent zero-vector embedding fallback in `ingest_docs.py` | **P0** | W1 |
| G2 | Split-brain persist_dir (`artifacts/chromadb` vs `data/cache/chromadb`) | **P1** | W1 |
| G3 | Lying `embedding_model` / `vector_dimensions` metadata in `ingest_code` | **P1** | W1 |
| G4 | Stale hardcoded ADG snapshot path | **P1** | W1 |
| G5 | `repo_adg_graph` collection corrupt | P2 | W1 |
| G6 | No unified metadata contract across collections | **P1** | W2 |
| G7 | Re-ingest produces duplicates (chunk-ID instability) | **P1** | W2 |
| G8 | No post-ingest validation in orchestrator | P2 | W2 |
| G9 | Coverage hole: `apps_*`, `system_learning`, `infrastructure`, `tools`, `ops_scripts` uningested | P2 | W3 |
| G10 | Coverage hole: zero-arg functions / argless async / methodless classes skipped | P3 | W3 |
| G11 | `traces` and `agentic_best_practices` empty | P2 | W3 |
| G12 | BM25 parity — only `code_chunks` has sparse index | P2 | W4 |
| G13 | No query-time reranker / hybrid fusion at retrieval boundary | P2 | W4 |
| G14 | BGE-M3 multi-vector (sparse + ColBERT) unused | P3 | W5 |
| G15 | Two parallel ingestion systems (`tools/ingestion` vs `tools/generate/ingestion`) | **P1** | W5 |
| G16 | `ADGNodeResolver` ambiguous on duplicate basenames | P3 | W5 |

## 6. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|:---:|---|
| **W0** | W0.1 | Pre-flight: freeze canonical store, snapshot both stores, emit read-only evidence | 🟢 4k | ADG healthy; disk has free space for tar snapshot | TODO | Both stores snapshotted to `artifacts/chromadb_backup_<ts>/`; canonical path ADR drafted |
| **W1 — STOP THE BLEED** | W1.1 W1.2 W1.3 W1.4 | Fix silent zero-fallback; enforce canonical persist_dir; correct embedding metadata; un-pin ADG snapshot | 🟡 18k | W0 complete; no consumer edits this wave | TODO | (a) zero-vector fallback raises `RuntimeError`; (b) all ingest scripts resolve persist_dir from single SSOT const; (c) metadata records `embedding_model`, `embedding_dim`, `embedding_provider`; (d) `adg_db_path` resolved at runtime from `artifacts/adg/adg_indexed_*.sqlite` newest match |
| **W2 — UNIFIED METADATA CONTRACT** | W2.1 W2.2 W2.3 | Define `ChunkMetadataV1` dataclass; retrofit code + docs + tests ingesters; add validate step to pipeline | 🟡 22k | W1 merged | TODO | Shared required keys `{artifact_type, source_path, canonical_digest, layer, embedding_model, embedding_dim, ingested_at, adg_node_id?}` enforced at add-time; `validate_collection.py` invoked per stage; duplicate-chunk re-ingest is upsert, not double-write |
| **W3 — COVERAGE EXPANSION** | W3.1 W3.2 W3.3 W3.4 | Ingest `apps_*` + `system_learning` + `tools`; re-enable traces; populate best-practices seed; remove entity-skip filters | 🟡 26k | W2 contract stable | TODO | `code_chunks` count within 90 % of live ADG symbol count; `traces` populated from healing corpus; `agentic_best_practices` populated or collection deleted; coverage_report.md produced |
| **W4 — HYBRID / BM25 PARITY** | W4.1 W4.2 | BM25 sidecar for all 7+ collections; add reranker hook at `hybrid_search_engine` boundary | 🟡 18k | W3 coverage stable | TODO | Every collection in canonical store has `data/cache/sparse/<name>.db`; retrieval end-to-end test passes at nDCG@10 ≥ baseline |
| **W5 — CONSOLIDATION & MULTI-VEC** | W5.1 W5.2 W5.3 | Merge `tools/ingestion` + `tools/generate/ingestion` into one orchestrator; archive duplicates; optional BGE-M3 sparse + ColBERT ingestion path | 🟡 20k | W1–W4 green | TODO | Single `tools/ingestion/pipeline.py` runs both legacy and new stages; duplicate scripts moved to `archives/`; ADR-018 updated; `repo_adg_graph` rebuilt or removed |

🟢 <8k · 🟡 8–30k · 🔴 >30k

## 7. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|:---:|
| W0.1 | Freeze + snapshot | New script `tools/retrieval/snapshot_stores.py`; ADR draft `docs/architecture/adr/ADR-024-chromadb-canonical-path.md` | disk I/O; compactor error on `repo_adg_graph` may block tar | 🟢 4k | TODO |
| W1.1 | Remove zero-vector fallback | `tools/ingestion/ingest_docs.py:298-304`; add regression test | Need to update any test that relied on soft-fail | 🟢 3k | TODO |
| W1.2 | Single persist_dir SSOT | New `agentic_core/L4_state/config/chroma_paths.py`; update `chroma_client.py`, `ingest_code.py`, `ingest_docs.py`, `ingest_traces.py`, `ingest_tests.py`, `ingest_runtime.py`, `ingest_history.py`, `ingest_adg.py` | 8 files, must not break existing consumers mid-wave → ship with alias | 🟡 6k | TODO |
| W1.3 | Truthful embedding metadata | `ingest_code.py`, `ingest_docs.py`, `chroma_client.py` | Must also stamp collection-level `embedding_model`/`embedding_dim` | 🟢 4k | TODO |
| W1.4 | Runtime ADG snapshot resolver | `tools/ingestion/ingest_code.py`, new `tools/ingestion/_adg_snapshot.py` helper | Snapshot changes during long ingest → pin at pipeline start | 🟢 5k | TODO |
| W2.1 | `ChunkMetadataV1` contract | `agentic_core/L4_state/utils/chunk_metadata.py` (new); dataclass + validator | Cross-layer decision; needs Author-Gate on placement (L4 utility vs `tools/ingestion/schema.py`) | 🟡 7k | TODO |
| W2.2 | Retrofit existing ingesters | `ingest_code.py`, `ingest_docs.py`, `ingest_tests.py`, `ingest_traces.py`, `ingest_runtime.py`, `ingest_history.py`, `ingest_adg.py` | 7 scripts; chunk-ID stability requires recompute → full re-ingest once | 🟡 10k | TODO |
| W2.3 | Pipeline validation step | `tools/ingestion/pipeline.py` (add post-stage `validate_collection`); CI smoke | Must surface dim/metadata-key failures as stage failures | 🟢 5k | TODO |
| W3.1 | Apps + shared ingest | Parameterise `ingest_code.py` for multi-root; update pipeline default roots | Token-heavy ingest run; execute once, keep idempotent | 🟡 6k | TODO |
| W3.2 | Traces re-ingest | `ingest_traces.py` + corpus check; maybe regenerate `healing_contexts_corpus.jsonl` | Corpus file may be missing rows | 🟡 5k | TODO |
| W3.3 | Best-practices corpus | `ingest_web_to_chroma_enhanced.py` + new seed list OR delete empty collection | Needs external URLs or deletion Author-Gate | 🟢 4k | TODO |
| W3.4 | Un-skip small entities | `ingest_code.py:213,223,229` | May multiply chunk count ~15 % — storage check | 🟢 3k | TODO |
| W3.5 | Coverage report | New `tools/retrieval/coverage_report.py` — joins ADG nodes ↔ ChromaDB IDs | Large join; progress bar mandatory (§16) | 🟡 8k | TODO |
| W4.1 | BM25 sidecars for all | Reuse `tools/generate/ingestion/build_sparse_index.py`; wire to pipeline | Paths differ between `tools/ingestion` and `tools/generate/ingestion`; reconcile | 🟡 10k | TODO |
| W4.2 | Reranker hook | `agentic_core/L3_orchestration/engines/hybrid_search_engine.py` — pluggable reranker | Must not regress latency; keep default = off | 🟡 8k | TODO |
| W5.1 | Unified orchestrator | Merge `tools/generate/ingestion/*` into `tools/ingestion/pipeline.py`; archive the other | Large diff; Author-Gate on archival strategy | 🟡 10k | TODO |
| W5.2 | ADG graph collection | Decide: rebuild `repo_adg_graph` from current sqlite OR remove it and rely on live ADG MCP | Author-Gate — rebuild vs remove | 🟢 4k | TODO |
| W5.3 | BGE-M3 multi-vector (optional) | `bge_runtime.py` extension for sparse + colbert pass; new `symbols_multi` collection | Storage ×3; opt-in via env | 🟡 6k | TODO |

## 8. Success Criteria (system-wide)

- **Single canonical persist_dir** — no code path writes to any other ChromaDB directory (CI gate).
- **Embedding truthfulness** — every stored chunk has `embedding_model="BAAI/bge-m3"` and `embedding_dim=1024`; collection metadata matches; validator gate passes.
- **Zero silent corruption** — no zero-vector fallback; every embed failure raises.
- **ADG joinability ≥ 90 %** — `adg_node_id` resolved for ≥ 90 % of code chunks under the current ADG snapshot.
- **Coverage** — `code_chunks` count ≥ 0.9 × (ADG `Symbol` nodes in Python layers); `docs` covers `docs/`, `AGENTS.md`, `.windsurf/rules/`, ADRs.
- **Hybrid retrieval parity** — every primary collection has a BM25 sidecar.
- **Idempotent ingest** — re-running the pipeline does not duplicate chunks (validated via count diff ≤ 1 %).

## 9. Rollback / Checkpoint

- W0 snapshot (`artifacts/chromadb_backup_<ts>.tar`) is the baseline rollback for W1–W5.
- Each wave commits independently; roll back by `git revert` + restore snapshot for that wave's tables.
- No deletion of `artifacts/chromadb/` until W5 completes green and consumers are cut over (Author-Gate).

## 10. Out of Scope

- Replacing BGE-M3 with a larger model.
- Moving off ChromaDB (ADR-018 decision stands).
- Reranking model selection / training (W4.2 ships hook only).
- Online/streaming ingest (current: batch only).

## 11. Open Decisions Requiring Author-Gate

1. **`ChunkMetadataV1` placement** — L4 utility (`agentic_core/L4_state/utils/chunk_metadata.py`) vs `tools/ingestion/schema.py`. Default recommendation: L4 utility (consumed by both ingest and retrieval).
2. **`agentic_best_practices` empty collection** — repopulate (need seed URL list) vs delete collection.
3. **`repo_adg_graph` corrupt collection** — drop & rebuild from current ADG SQLite vs remove entirely (live ADG MCP is always-on).
4. **Archival strategy for duplicate ingest scripts** — move to `archives/` vs delete (constitutional §9 defaults to archival).

## 12. References

- `tools/ingestion/pipeline.py`, `tools/ingestion/ingest_*.py`
- `tools/generate/ingestion/*.py`, `tools/generate/ingestion/validate_collection.py`
- `agentic_core/L4_state/utils/client/chroma_client.py`
- `agentic_core/embeddings/bge_runtime.py`
- `docs/architecture/adr/ADR-018-chromadb-as-canonical-vector-store.md`
- ADG snapshot `artifacts/adg/adg_indexed_04232026_1802.sqlite`
- Constitutional §22 (graph-layer primary driver), §16 (progress bar), §24 (deferred scope capture)
