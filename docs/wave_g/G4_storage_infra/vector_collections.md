# G4 — Vector Collections

**ADG snapshot**: `artifacts/adg/adg_indexed_04172026_0611.sqlite` (04172026_0611).

ChromaDB-backed vector stores. Embedded local (SQLite registry + HNSW persist dirs); **not** a network egress (per G2b provider_inventory.md §P09).

## 1. Canonical store — `data/cache/chromadb/`

- **Registry**: `data/cache/chromadb/chroma.sqlite3` (188 KB)
- **HNSW persist directories**: 56 UUID-named subdirectories
- **Total footprint**: ~10.2 GB (out of 10.5 GB in `data/cache/`)
- **Env-overridable path**: `VECTOR_DB_CHROMA_PATH`

### 1.1 Registered collections (11)

Listed from SQLite `collections` table:

| Collection | Purpose (inferred from name) |
|---|---|
| `code_chunks` | code-chunk embeddings (largest; drives the 628 MB `data_level0.bin` observed) |
| `symbols` | symbol-level embeddings (function/class) |
| `repo_evidence` | repo-evidence bundles for eval |
| `runtime_evidence` | runtime trace evidence |
| `process_docs` | process documentation corpus |
| `ext_authority` | external authority docs |
| `ext_raw` | external raw corpus |
| `incidents_rca` | incident / RCA corpus |
| `tests_guardrails` | guardrail test corpus |
| `test_col` | test fixture collection |
| `dupe_col` | duplicate-detection fixture |

### 1.2 Owner / writer / reader modules

| Role | Modules |
|---|---|
| **Owner** | `tools/retrieval/vector_store.py` (Chroma client init); `tools/retrieval/vector_service.py` (service orchestration) |
| **Writers** | `tools/retrieval/vector_service.py::add_documents`; `tools/mcp/vector_db_server.py` (MCP write tool `add_documents`); `agentic_core/L4_state/utils/client/chroma_client.py` |
| **Readers** | `tools/retrieval/vector_service.py::query_collection` + `semantic_search`; `agentic_core/L1_cognition/reasoning/semantic_retriever.py`; `agentic_core/L3_orchestration/reasoning/engines/hybrid_search_engine.py`; `agentic_core/L4_state/reasoning/retrieval_layers.py`; `agentic_core/L4_state/utils/memory/in_memory_vector_cache.py`; `tools/diag/**`; `tools/debug/**` |

### 1.3 Lifecycle

- **Creation**: on first `get_or_create_collection()` call in `vector_store.py`.
- **Ingest**: `add_documents` via service / MCP. Embedding via `tools/retrieval/embedder.py` using `BAAI/bge-m3` (dim 1024).
- **Invalidation**: manual via `delete_collection` MCP tool.
- **Staleness**: not tracked. No auto-refresh when source corpus changes.
- **Retention**: indefinite. No auto-prune.

### 1.4 Pipelines

- **PIPE-VECTOR-RETRIEVAL** — primary reader (MCP tool surface + in-process).
- **PIPE-EMBEDDING** — writer via `add_documents` → embedder → HNSW insert.
- **PIPE-JUDGE-EVAL** — reader for evidence assembly via `evidence_assembler.py`.

## 2. Artefact / diagnostic store — `artifacts/chromadb/chroma.sqlite3`

- Footprint: 188 KB (registry only — no HNSW dirs observed alongside).
- Registered collections (2): `docs`, `traces`.
- **No live runtime writer**. Used by `tools/diag/**` and `tools/debug/**` for isolated experiments.
- **B7-G4-05**: consolidate or remove — vestigial registry without live persistence alongside it.

## 3. Sparse-vector cache — `data/cache/sparse/`

- Presence observed; size included in `data/cache/` aggregate (10.5 GB).
- Consumer: `agentic_core/L3_orchestration/reasoning/engines/hybrid_search_engine.py` (hybrid dense+sparse retrieval leg).
- Writer attribution not enumerated at G4 — deferred.

## 4. In-process vector cache

Module: `agentic_core/L4_state/utils/memory/in_memory_vector_cache.py`.

- Process-lifetime only (no disk persistence).
- Reader side-cache in front of ChromaDB to avoid round-trips for hot queries.
- Not catalogued as a persistent store — captured here for completeness.

## 5. Embedding model binding

- **Model**: `BAAI/bge-m3` (dim 1024 per `tools/retrieval/vector_config.py KNOWN_MODEL_DIMS`).
- **Runtime**: `sentence_transformers.SentenceTransformer` loaded once per process.
- **Offline by default**: `HF_HUB_OFFLINE=1` enforced via `.windsurf/mcp_config.json` vector_db env block.
- **Fetch gate**: `VECTOR_DB_ALLOW_MODEL_DOWNLOAD=0` (default). When `=1`, enables EGRESS-HF-HUB-01.
- **Cache**: HuggingFace model cache typically under `~/.cache/huggingface/` (operator-local, not in repo).

## 6. Search timeouts and budgets (from G2b)

Per `tools/retrieval/vector_config.py`:

| Knob | Default |
|---|---:|
| `VECTOR_DB_MODEL_LOAD_TIMEOUT` | 120 s |
| `VECTOR_DB_CHROMA_INIT_TIMEOUT` | 30 s |
| `VECTOR_DB_ENCODE_TIMEOUT` | 20 s |
| `VECTOR_DB_ENCODE_QUEUE_WAIT_TIMEOUT` | 20 s |
| `VECTOR_DB_QUERY_COLLECTION_TIMEOUT` | 40 s |
| `VECTOR_DB_SEARCH_PER_COLLECTION_TIMEOUT` | 20 s |
| `VECTOR_DB_SEARCH_GLOBAL_TIMEOUT` | 60 s |
| `VECTOR_DB_COUNT_CACHE_TTL` | 60 s |

All re-homed under G4b `config_knob_catalogue.yaml` (hand-off).

## 7. Write-sovereignty note

Per G2 `boundary_violations.md` L4 critical-write bucket, `retrieval_layers.py` (line 227) performs `persist_dir.mkdir` directly. This is the parent-directory creation step before Chroma's own HNSW write. It is outside the UWG envelope. If F09.01 (UWG sole-durable-write authority) applies to directory creation, this is a gap. **B7-G4-06**.

## 8. Summary

| Dimension | Value |
|---|---:|
| Persistent vector stores | 2 (canonical + artefact) |
| Collections in canonical | 11 |
| Collections in artefact | 2 |
| HNSW persist dirs (canonical) | 56 |
| Total vector footprint | ~10.2 GB |
| Embedding model | `BAAI/bge-m3` (1024 dim) |
| External egress | conditional (HF Hub when model download enabled) |
| Pipelines using vector stores | 3 (PIPE-VECTOR-RETRIEVAL, PIPE-EMBEDDING, PIPE-JUDGE-EVAL) |
| B7 candidates from this file | 2 (B7-G4-05 artefact consolidation, B7-G4-06 persist_dir direct write) |
