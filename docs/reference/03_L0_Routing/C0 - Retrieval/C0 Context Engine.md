│ 🔵 Ingress: L1_Plan + query_vec
                         ▼
==========================================================================================
[C0] CONTEXT ENGINE (Ref Desk)
==========================================================================================

  ┌─────────────────────────────────────────────┐       ┌────────────────────────────────┐
  │ [C0.1] PLAN: SCOPE & POLICY                 │       │ [ L4 STATE / DATA STORES ]     │
  │  ├─► Parse L1 Route Boundary                │       │                                │
  │  ├─► Apply Tenant / ACL Gate                │       │                                │
  │  └─► Enforce Freshness / Date Window        │       │                                │
  └──────────────────────┬──────────────────────┘       │                                │
                         │ (Validated Plan)             │                                │
                         ▼                              │                                │
  ┌─────────────────────────────────────────────┐       │   ┌──────────────────────────┐ │
  │ [C0.2] FETCH: HYBRID RECALL                 │       │   │                          │ │
  │  ├─► Dense Search: 🔵 query_vec vs doc_vec  │◄──────┼──►│ [DB] VECTOR INDEX (Dense)│ │
  │  ├─► Sparse Search: BM25 / Exact Term       │◄──────┼──►│ [DB] SPARSE INDEX (BM25) │ │
  │  └─► Fetch Candidate Raw Chunks 🟠          │◄──────┼──►│ [DB] RAW CHUNK STORE 🟠  │ │
  └──────────────────────┬──────────────────────┘       │   │                          │ │
                         │ (Candidate Heaps)            │   └──────────────────────────┘ │
                         ▼                              │                                │
  ┌─────────────────────────────────────────────┐       │   ┌──────────────────────────┐ │
  │ [C0.3] GRAPH: ENTITY TRAVERSAL              │       │   │ [DB] KNOWLEDGE GRAPH 🟢  │ │
  │  ├─► Extract Entities from 🔵 query         │       │   │ - Entity Nodes & Edges   │ │
  │  ├─► Traverse Network Paths (n-hops)        │◄──────┼──►│ - Subgraph Extraction    │ │
  │  └─► Yield Entity Rel. & Subgraph 🟢        │       │   │ - Ontology Schema        │ │
  └──────────────────────┬──────────────────────┘       │   └──────────────────────────┘ │
                         │ (Context + Subgraph)         └────────────────────────────────┘
                         ▼
  ┌─────────────────────────────────────────────┐
  │ [C0.4] SHAPE: CONSOLIDATION & SCORING       │
  │  ├─► Merge: Dense + Sparse + Graph Nodes    │
  │  ├─► Deduplicate Overlapping Spans          │
  │  ├─► Rerank: Reciprocal Rank / Cross-Encoder│
  │  └─► Prune: Drop below confidence threshold │
  └──────────────────────┬──────────────────────┘
                         │ (Refined Array)
                         ▼
  ┌─────────────────────────────────────────────┐
  │ [C0.5] CONTRACT: EVIDENCE BINDING           │
  │  ├─► Verify Span Integrity & Provenance     │
  │  ├─► Calculate Aggregate Support Score      │
  │  └─► Compile Citation Slip (Evidence Cont.) │
  └──────────────────────┬──────────────────────┘
                         │
=========================▼================================================================
                     [EVIDENCE CONTRACT PAYLOAD]
                         │
                         ├─► 🟠 Cited Raw Text Chunks
                         ├─► 🟢 Entity Subgraph/Triplets
                         ├─► 🔵 Query Intent Vector
                         │
                         ▼
                   [Dispatch to PA: PROMPT ASSEMBLY]