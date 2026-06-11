---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\chromadb-semantic-memory-layer-plan-578879.md'
original_relative_path: 'chromadb-semantic-memory-layer-plan-578879.md'
source_sha256: a020a8f24be9c5015b76babfd4fd872ba1d2d765fd1603d449379f1234ba9ca6
recovered_status: LOST_RECOVERED
last_commit: '20f413ffbf5'
last_commit_date: '2026-04-01 14:39:03 -0400'
created_date: '2026-03-27'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Production-Grade ChromaDB Semantic Memory Layer Plan

Design for a cohesive, multi-index semantic memory layer aligned to L0–L6 architecture and Library OS SSOT.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## A) SYSTEM OVERVIEW

ChromaDB serves as the **Sovereign Semantic Layer**, bridging the gap between design-time structure (Static ADG) and execution-time evidence (Runtime ADG). It provides the "fuzzy" reasoning capability that complements the "exact" truth of the core databases.

- **SQLite (Canonical Truth):** Authoritative source for structural relationships, dependency graphs, and historical logs.
- **Redis (Hot Cache):** High-throughput ephemeral storage for JIT context and session-scoped state.
- **ChromaDB (Semantic Layer):** High-dimensional vector space for similarity-based reasoning across disconnected artifact types.

### Integration Points:
- **L1 (C0 Retrieval):** ChromaDB acts as the primary provider for semantic search, feeding the retrieval-augmented cognition loop.
- **L3 Orchestration:** Supplies historical success/failure context to inform agent dispatch decisions.
- **L5 Governance:** Provides semantic policy lookup to detect intent-based violations that escape regex/AST guards.
- **L6 Observability:** Enables failure signature clustering and anomaly detection across high-volume traces.
- **Meta-Learning:** Indexes optimization proposals and DPO batches to accelerate policy improvement.

## B) ASCII ARCHITECTURE

```text
[ ARTIFACT EXTRACTION ] -> [ SYNTHETIC GEN ] -> [ EMBEDDING (BGE-M3) ] -> [ METADATA BINDING ] -> [ CHROMADB ]
          |                     |                      |                        |                  |
 (Library Archives)      (Librarian Summary)    (Semantic Encoding)      (Identity Stamping)   (Persistent Local)
          |                     |                      |                        |                  |
  +-------v-------+     +-------v-------+      +-------v-------+        +-------v-------+  +-------v-------+
  |  AST Parsing  |     | Responsibility|      | 1024-dim      |        | SSOT object_id|  | 10 collections|
  |  ADG Exports  |     | Invariant Map |      | Dense Vectors |        | Layer Labels  |  | Multi-Index   |
  |  Git History  |     | Failure Modes |      | Local Inference|        | Policy Tags   |  | Persistent    |
  +---------------+     +---------------+      +---------------+        +---------------+  +---------------+
          ^                     ^                      ^                        ^                  |
          |                     |                      |                        |                  |
 [ RETRIEVAL (L1) ] <------- [ RERANKING (LightGBM) ] <------- [ FUSION QUERY ] <------------------+
```

## C) COLLECTION DESIGN

### 1. `repo_code_chunks`
- **Purpose:** Semantic search across raw function/class implementations.
- **Embedding:** BGE-M3 (Dense).
- **Metadata:** `object_id`, `file_path`, `layer`, `entity_type`, `line_start`, `line_end`.
- **Use Case:** "How is the UWG implemented?"

### 2. `repo_symbols`
- **Purpose:** High-level reasoning about symbol responsibilities.
- **Embedding:** Summarized docstrings + signatures.
- **Metadata:** `symbol_name`, `authority_role`, `downstream_deps`.
- **Use Case:** "Which symbol is responsible for path routing?"

### 3. `repo_arch_docs`
- **Purpose:** Architecture reasoning and requirement alignment.
- **Embedding:** Markdown sections with header hierarchy.
- **Metadata:** `doc_type`, `territory`, `last_modified`.
- **Use Case:** "What are the invariants for L5 safety?"

### 4. `repo_adg_graph`
- **Purpose:** Graph-aware semantic retrieval (converting edges to text).
- **Embedding:** Edge descriptions (e.g., "Module A calls Symbol B").
- **Metadata:** `edge_type`, `src_node`, `dst_node`, `confidence`.
- **Use Case:** "What is the blast radius of changing the cache loader?"

### 5. `repo_tests_guardrails`
- **Purpose:** Test intelligence and coverage analysis.
- **Embedding:** Test descriptions + failure messages.
- **Metadata:** `test_links`, `invariant_family`, `coverage_type`.
- **Use Case:** "Which tests cover the replay determinism guard?"

### 6. `repo_runtime_evidence`
- **Purpose:** Contextual debugging from historical traces.
- **Embedding:** Trace logs + state snapshots.
- **Metadata:** `run_id`, `path_mode`, `mutates_state`.
- **Use Case:** "Find traces where a policy violation occurred in L2."

### 7. `repo_policies_invariants`
- **Purpose:** Intent-based governance.
- **Embedding:** Policy descriptions + Rationale.
- **Metadata:** `policy_id`, `requires_human_review`, `authority_role`.
- **Use Case:** "Which policy governs cross-repo data imports?"

### 8. `repo_git_history`
- **Purpose:** Change impact and temporal reasoning.
- **Embedding:** Commit messages + diff summaries.
- **Metadata:** `commit_hash`, `author`, `files_changed`.
- **Use Case:** "How has the L0 routing logic changed in the last month?"

### 9. `repo_incidents_rca`
- **Purpose:** Failure prevention and root cause intelligence.
- **Embedding:** RCA documents + resolution steps.
- **Metadata:** `status`, `incident_date`, `impact_severity`.
- **Use Case:** "Have we seen this timeout error before?"

### 10. `repo_prompt_taxonomy`
- **Purpose:** Prompt engineering optimization.
- **Embedding:** Prompt templates + slot descriptions.
- **Metadata:** `prompt_id`, `layer`, `d0_injections`.
- **Use Case:** "Find templates used for agentic capability validation."

## D) CANONICAL OBJECT MODEL

**Unified `object_id` Strategy:**
- Format: `URN:<domain>:<layer>:<artifact_type>:<hash>`
- Example: `URN:code:L2:function:8f2a1b...`
- **Linkage Support:**
  - `ADG::Symbol::` names map to `repo_symbols` IDs.
  - `file_path:line` maps to `repo_code_chunks`.
  - `run_id` links `repo_runtime_evidence` to `repo_incidents_rca`.

## E) INGESTION PIPELINE DESIGN

### Stage 1: Artifact Extraction
- **Code:** Parallel AST extraction using `tools/ingestion/ingest_code.py`.
- **ADG:** Export SQLite `nodes` and `edges` tables to structured JSON.
- **Runtime:** Fetch traces from `data/corpus/` and L6 logs.

### Stage 2: Synthetic Artifact Generation
- Generate **Responsibility Statements** for every L0-L6 module.
- Map **Failure Modes** to specific symbols based on L6 historical logs.
- Produce **Change Impact Summaries** by comparing Git diffs with ADG edges.

### Stage 3: Embedding Generation
- **Model:** Local BGE-M3 (FlagEmbedding) for dense/sparse fusion support.
- **Chunking:** Semantic chunking for docs (header-based); AST-aware chunking for code.

### Stage 4: Metadata Binding
- Bind `layer`, `subsystem`, and `authority_role` using `agentic_core/adg/schema.py` mapping.
- Inject `upstream_dependencies` from ADG SQLite before insertion.

### Stage 5: Storage
- Persistent local storage in `artifacts/chromadb/`.
- Full rebuild initially; incremental logic using `canonical_digest` matching.

## F) METADATA SCHEMA (DETAILED)

| Field | Type | Description |
|-------|------|-------------|
| `object_id` | string | Canonical URN identifier |
| `artifact_type` | string | code, doc, sym, edge, trace, policy |
| `layer` | string | L0 through L6 |
| `subsystem` | string | routing, cognition, execution, etc. |
| `authority_role` | string | Library OS role mapping |
| `file_path` | string | Repository relative path |
| `symbol_name` | string | Qualified Python symbol name |
| `edge_types` | string[] | List of ADG relations (for edges) |
| `path_mode` | string | A/B/C/D execution path |
| `mutates_state` | boolean| True if UWG write occurs |
| `canonical_digest` | string | SHA-256 of content for drift detection |

## G) ADG INTEGRATION

- **SQLite as Source:** Ingestion script queries `adg_indexed_*.sqlite`.
- **Graph to Embedding:** Converts triples `(src, relation, dst)` into natural language sentences for semantic indexing.
- **Blast Radius:** Retrieve symbols with similar implementation patterns + check ADG for structural dependencies.

## H) RUNTIME + FAILURE INTELLIGENCE

- **Failure Signatures:** Normalize traceback messages into generic patterns.
- **Clustering:** Use ChromaDB similarity to group related `repo_incidents_rca`.
- **Replay Linkage:** Store `replay_key` in metadata to allow instant debugging from a search result.

## I) RETRIEVAL STRATEGY

1. **Query Routing:** L1 Cognition determines which collections are relevant.
2. **Multi-Query Fusion:** Execute parallel searches across relevant indices.
3. **Reranking:** Apply **LightGBM** model trained on `EvalSpine` feedback.
4. **Fusion:** Reciprocal Rank Fusion (RRF) to combine semantic and structural scores.

## J) IMPLEMENTATION PLAN

### Wave 1: Core Knowledge (Baseline)
- **Files:** `tools/ingestion/ingest_core.py`, `agentic_core/L4_state/client/chroma_client.py`
- **Artifacts:** `repo_code_chunks`, `repo_symbols`, `repo_arch_docs`.
- **Success:** Agent can answer "What does the UWG do?" with source code citations.

### Wave 2: Structural & Test Intelligence
- **Files:** `tools/ingestion/ingest_adg.py`, `tools/ingestion/ingest_tests.py`
- **Artifacts:** `repo_adg_graph`, `repo_tests_guardrails`.
- **Success:** Agent can determine blast radius via semantic similarity.

### Wave 3: Execution & History
- **Files:** `tools/ingestion/ingest_runtime.py`, `tools/ingestion/ingest_history.py`
- **Artifacts:** `repo_runtime_evidence`, `repo_git_history`, `repo_incidents_rca`.
- **Success:** Agent clusters failures across 100+ execution traces.

## K) FILE DIFFS (PROPOSED)

### `agentic_core/L4_state/client/chroma_client.py`
```python
import chromadb
from FlagEmbedding import BGEM3FlagModel

class SovereignChromaClient:
    def __init__(self, persist_dir="artifacts/chromadb"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)
        
    def get_collection(self, name):
        return self.client.get_or_create_collection(name=name)
        
    def embed_texts(self, texts):
        return self.model.encode(texts)['dense_vecs'].tolist()
```

### `agentic_core/L1_cognition/engines/semantic_retriever.py`
```python
class SemanticRetriever:
    async def retrieve(self, query):
        # 1. Route to collections
        # 2. Get candidates
        # 3. Rerank with LightGBM
        pass
```

## L) RISKS + FAILURE MODES

- **Embedding Drift:** New BGE model versions require full re-index.
- **Stale Metadata:** ADG updates must trigger ChromaDB partial rebuilds.
- **Hallucination:** Mitigation via **GroundednessScorer** in L6.

## M) VALIDATION + METRICS

- **Retrieval Relevance (nDCG@5):** Measured against `evaluation_prompts.json`.
- **Groundedness:** Percentage of agent claims backed by semantic citations.
- **SSOT Alignment:** Zero mismatch between ChromaDB `layer` tag and ADG SQLite.

---
**Status:** IMPLEMENTATION READY  
**Author:** Cascade  
**Alignment:** Library OS SSOT / L0-L6 Architecture

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

