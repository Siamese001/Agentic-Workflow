==============================================================================================================================
[00C] 🗂️ INDEX MATERIALIZATION + RUNTIME HANDOFF
     Scope: Deep drill-down into vectors, metadata, sparse rails, and lineage storage/retrieval.
     Purpose: Connect embedding output to C0 grounded retrieval and prompt assembly.
==============================================================================================================================

                                   [ 📥 INPUT FROM 00B PIPELINE ]
                        chunk_id | vector | schema_version | metadata_ptr
                                                 │
                                                 ▼
==============================================================================================================================
                                     DUAL STORAGE PATTERN
==============================================================================================================================

             ┌───────────────────────────────────┴───────────────────────────────────┐
             ▼                                                                       ▼
╭───────────────────────────────────────╮                 ╭──────────────────────────────────────────────────╮
│ 🧮 C1. VECTOR STORE                    │                 │ 🏛️ C2. CANONICAL METADATA STORE                 │
│ (The Fast Math Shelf)                 │                 │ (The Durable Truth Shelf)                        │
│                                       │                 │                                                  │
│ ├─ Engines: ChromaDB, pgvector, FAISS │                 │ ├─ ChunkManifest: raw text, enriched json, hash  │
│ ├─ Primary: UUID -> fact_vec          │                 │ ├─ ParentChild  : graph edges, parent/child ids  │
│ └─ Sidecar: UUID -> metadata refs     │                 │ ├─ Access Ctrl  : ACL, tenant, freshness, schema │
╰────────────────────┬──────────────────╯                 │ ├─ Search Surfs : sparse terms, lexical maps     │
                     │                                    │ └─ Anchors      : provenance, citations, sections│
                     │                                    ╰──────────────────────────┬───────────────────────╯
                     └───────────────► [ nearest-neighbor ids ] ◄────────────────────┘
                                                 │
                                                 │ [ publish ]
                                                 ▼
╭────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ 🌐 C3. PUBLISHED RETRIEVAL SURFACES                                                                         │
│  [🧠 Dense: vector sim]   [🔎 Sparse: exact/lexical]   [🔗 Lineage: graph]   [🧾 Canonical: raw truth]      │
╰────────────────────────────────────────────────┬───────────────────────────────────────────────────────────╯
                                                 │
                                                 ▼
==============================================================================================================================
                                      QUERY-TIME HANDOFF
==============================================================================================================================

                                         [ 🏃‍♂️ RUNTIME ASK ]
                                     (From L1 Plan + L0 Route)
                                                 │
                                                 ▼
╭────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ 🧭 C4. C0 RETRIEVAL PLAN                                                                                    │
│ ├─ Binds : source scope, ACL, freshness, tenant, retrieval mode                                            │
│ └─ Rule  : Strictly retrieval authority ONLY (No routing, no execution)                                    │
╰────────────────────────────────────────────────┬───────────────────────────────────────────────────────────╯
                                                 │ [ Search Params ]
                                                 ▼
╭────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ 🎣 C5. EVIDENCE FETCH                                                                                       │
│ ├─ Dense Recall  : query_vec vs fact_vec / raw_text_vector / contextual_text_vector                        │
│ ├─ Sparse Recall : exact term / schema / code match                                                        │
│ ├─ Graph Hydrate : parent-child lineage expansion                                                          │
│ └─ Meta Fetch    : ACL / provenance / version / freshness verification                                     │
╰────────────────────────────────────────────────┬───────────────────────────────────────────────────────────╯
                                                 │ [ Raw Candidates ]
                                                 ▼
╭────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ 💎 C6. EVIDENCE SHAPING                                                                                     │
│ ├─ Pipeline : dedupe ──► rerank ──► contradiction retain ──► citation preservation                         │
│ ├─ Metrics  : support scoring, coverage analysis                                                           │
│ └─ Outputs  : verified chunks, cited spans, coverage/gaps                                                  │
╰────────────────────────────────────────────────┬───────────────────────────────────────────────────────────╯
                                                 │ [ Verified Context ]
                                                 ▼
╭────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ 📦 C7. PROMPT ASSEMBLY HANDOFF                                                                              │
│ ├─ Generate : PromptEnvelope (verified context + assigned task + system blocks)                            │
│ ├─ Bind     : strict citation anchors + replay metadata                                                    │
│ └─ Dispatch : Send Bounded Packet ──► [ 🛠️ L2 BACK ROOMS ]                                                │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

==============================================================================================================================
                              LIVE RUNTIME BGE EMBEDDING PATH  (repaired 2025)
==============================================================================================================================

C8. SHARED SYNCHRONOUS BGE RUNTIME HELPER
──────────────────────────────────────────
Module  : agentic_core/embeddings/bge_runtime.py
Model   : BAAI/bge-m3  (1024-dim, L2-normalised, CPU)
Pattern : Process-level singleton — one SentenceTransformer load per OS process, thread-safe (double-checked lock)

                          [ query string ]
                                │
                                ▼
                  ┌─────────────────────────────┐
                  │  bge_runtime._get_model()    │
                  │  (lazy load, lock-guarded)   │
                  │  Raises BGEInstallError if   │
                  │  sentence-transformers absent │
                  └──────────────┬──────────────┘
                                 │ singleton reuse after first call
                                 ▼
                  ┌─────────────────────────────┐
                  │  bge_embed_query(text)       │
                  │  model.encode([text],        │
                  │    normalize_embeddings=True │
                  │    convert_to_numpy=True)    │
                  │  Raises RuntimeError on      │
                  │  BGE_DIM_MISMATCH (loud)     │
                  └──────────────┬──────────────┘
                                 │ list[float], len=1024
                    ┌────────────┴────────────┐
                    ▼                         ▼
       SemanticRetriever            HybridSearchEngine
       (L1 cognition)               (L3 orchestration)
       _query_collection()          _generate_query_embedding()
       direct import                catches BGEInstallError +
       of bge_embed_query           ImportError → returns None
                    └────────────┬────────────┘
                                 ▼
                     TitaniumRAGPipeline
                     (L3 orchestration)
                     delegates to HybridSearchEngine
                     via get_global_hybrid_engine()

WHAT WAS INTENTIONALLY NOT CHANGED:
- Async embedding factory  : agentic_core/embeddings/embedding_factory.py
  Still owns the async + sovereignty allowlist path used by ingestion scripts.
  bge_runtime is a separate sync-only runtime surface.
- Ingestion scripts        : ingest_code_chunks.py / ingest_symbols.py
  Continue using SentenceTransformer directly with device="cuda" for batch work.
- Sovereignty redesign     : EmbeddingSovereignAgent allowlist not extended.
  Runtime sync path currently bypasses allowlist by design (Prompt 5 governance item).

BENCHMARK (CPU, local dev, 2025):
  Cold model load : ~4 200 ms
  Warm query avg  : ~29 ms / call   (10 queries, BAAI/bge-m3, 1024-dim)
  Singleton check : True — SR and HSE share identical model object

==============================================================================================================================
[ DRILL-DOWN RELATION ]
[00A] End-to-end implementation bridge
  │
  ├──> [00B] Token -> vector internals (tokenizer -> weights -> forward pass -> pooling -> normalization)
  │
  └──> [00C] Index materialization + runtime handoff (This Document)
               vector store -> canonical metadata -> C0 fetch -> prompt assembly

[ BOTTOM LINE ]
00A = whole implementation flow. 00B = model internals. 00C = storage & runtime handoff.
==============================================================================================================================