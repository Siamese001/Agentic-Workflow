# AGENTIC RETRIEVAL & GENERATION PIPELINES: HARDENED TARGET STATE

+=========================================================================================================================================================================================+
|                                                                 PIPELINE B: INGESTION & INDEX BUILD (OFFLINE PRE-RUNTIME)                                                               |
+=========================================================================================================================================================================================+
| [ RAW SOURCES ] -> Portable Document Formats, Word Documents, Relational Databases, SharePoint, Web Fetch, Execution Telemetry, Incident Traces                                         |
|       |                                                                                                                                                                                 |
|       v                                                                                                                                                                                 |
| [ 1. INTAKE & MODALITY DETECT ] -> Route based on content type (The Intake Clerk)                                                                                                       |
|       +--> [ Text Extractor ] ---> Prose, event logs, flat text files                                                                                                                   |
|       \--> [ Visual Detector ] --> Tables, charts, diagrams, scanned pages, engineering illustration visuals                                                                            |
|       |                                                                                                                                                                                 |
|       v                                                                                                                                                                                 |
| [ 2. CANONICAL RAW UNIT ] -------> Establish the base immutable record (raw text, source identifier, parent identifier, visual modality flag)                                           |
|       |                                                                                                                                                                                 |
|       v                                                                                                                                                                                 |
| [ 3. LIFECYCLE & STATE SYNC ] ---> [ Operational Update Path: Dedupe Checksum -> Version Compare -> Tombstone Stale Data -> Preserve Graph Lineage -> Reindex ]                         |
|       |                                                                                                                                                                                 |
|       v                                                                                                                                                                                 |
| [ 4. CHUNKING POLICY ] ----------> [ Corpus Classifier: Route to specific chunking strategy. No generic defaults. ]                                                                     |
|       +--> Policy / Long Document   ==> Section-aware boundaries, parent-child hydrate markers, eval-tuned overlap                                                                      |
|       +--> Incident / Trace         ==> Event-boundary chunks, temporal adjacency metadata, strict no-paragraph splitting                                                               |
|       +--> Code / Configuration     ==> Symbol and block-aware extraction, file lineage, dependency metadata tags                                                                       |
|       \--> Visuals / Tables         ==> Page or element-aware units, multimodal flag assignment                                                                                         |
|       |                                                                                                                                                                                 |
|       v                                                                                                                                                                                 |
| [ 5. METADATA BINDING ] ---------> Bind Access Control Lists, tenant identifiers, confidentiality tiers, freshness bands, effective/expiry dates, embedding schema versions             |
|       |                            (CRITICAL: Metadata is bound here to enable strict pre-retrieval gating in Pipeline C)                                                               |
|       v                                                                                                                                                                                 |
| [ 6. DUAL-REPRESENTATION ] ------> [ CORE LOGIC: SEMANTIC ENRICHMENT & DUAL EMBEDDING ]                                                                                                 |
|       |                            Maintain canonical raw text integrity WHILE generating contextualized semantic overlays.                                                             |
|       +--> Raw Path:               [ Canonical Raw Text ]  ==> [ raw_text_vector ]                                                                                                      |
|       \--> Contextual Path:        [ Enricher / Reference Note ] ==> [ Title / Summary / Pattern Concepts ] ==> [ contextual_text_vector ]                                              |
|       |                                                                                                                                                                                 |
|       v                                                                                                                                                                                 |
|  [ MULTI-VECTOR MASTER ARCHIVES ]                                           [ METADATA & CANONICAL STORE: THE KNOWLEDGE SUBSTRATE ]                                                     |
|  Stores [Identifier : raw_text_vector] and [Identifier : contextual]        Relational Truth (Canonical Data, Telemetry, Lineage edges)                                                 |
|  ┌────────────────────────────┐ ┌────────────────────────────┐              ┌────────────────────────────┐ ┌────────────────────────────┐                                               |
|  │ 1. Dense Search Index      │ │ 2. Sparse Keyword Index    │              │ 1. Canonical Raw Chunk     │ │ 2. Parent-Child Index      │                                               |
|  ├────────────────────────────┤ ├────────────────────────────┤              ├────────────────────────────┤ ├────────────────────────────┤                                               |
|  │ Meaning match (Vectors)    │ │ Exact term/code match      │              │ Complete unaltered text    │ │ Graph routing & lineage    │                                               |
|  └────────────────────────────┘ └────────────────────────────┘              └────────────────────────────┘ └────────────────────────────┘                                               |
+=========================================================================================================================================================================================+

===========================================================================================================================================================================================
                                            PIPELINE C: INFERENCE / QUERY TIME (INTEGRATED CASCADING AGENT)                                                                                
===========================================================================================================================================================================================
[ RETRIEVAL STACK PRINCIPLE: Pre-filter strictly, cache intelligently via policy, retrieve via hybrid methods, rerank rigorously, and hydrate canonical truth. ]                           

[ START: INBOUND USER QUERY / TASK ] (Patron Ask)                                                                                                                                          
          |                                                                                                                                                                                
          v                                                                                                                                                                                
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 1. QUERY PRE-PROCESSING & NORMALIZATION (SHARED EXTERNAL PIPELINE)                                                                                                                      |
| 1. NORMALIZE:      Clean raw string to base units yielding [ normalized_query ].                                                                                                        |
| 2. ROUTE SIGNAL:   External lightweight model assesses intent/domain for policy routing yielding [ route_signal ].                                                                      |
| 3. QUERY VECTOR:   External Embedding API executes pooling for semantic representation yielding [ query_vec ].                                                                          |
| 4. OUTPUT:         Contextual packet split for distinct routing vs. retrieval duties.                                                                                                   |
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
          |                                                                                                                                                                                
          v                                                                                                                                                                                
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 2. PRE-RETRIEVAL GATE (FRONT DESK SECURITY)  [!! CRITICAL OVERRIDE !!]                                                                                                                  |
| Enforce filters BEFORE retrieval or cache lookup to prevent wasted recall operations and eliminate cross-scope contamination risks.                                                     |
| FILTERS APPLIED: Tenant | Access Control List | Region | Confidentiality Level | Effective/Expiry Dates | Freshness Band Requirements -> yields [ scope_metadata ]                      |
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
          |                                                                                                                                                                                
================================================================( FAST CACHE -> DEEP EXECUTION BOUNDARY )==================================================================================
| [ FRONT DESK DISPATCHER (AUTHORITY) ]                                                                                                                                                   |
| ROLE:   Retains routing authority based on explicit Cache Decision Policies, compute budgets, and hybrid retrieval thresholds. Retrieval never dictates execution.                      |
===========================================================================================================================================================================================

[ NORMALIZED_QUERY + ROUTE_SIGNAL + QUERY_VEC + SCOPE_METADATA ]                                                                                                                           
                         │                                    │                                                │                                                  │                          
                         ▼ (Cache Policy)                     ▼ (Hybrid Search + Rerank)                       ▼ (Text / Schemas)                                 ▼ (Text)                   
+==========+============================+============================================+=================================================+==================================================+
| EXEC TIER| 1. VERSION-AWARE CACHE     | 2. AGENTIC HYBRID RETRIEVAL                | 3. AGENTIC ACTION ESCALATION                    | 4. FALLBACK GENERATOR                            |
+==========+============================+============================================+=================================================+==================================================+
| ANALOGY  | Exact match on intent,     | Hybrid shelf search, Senior Librarian      | Escalate to an                                  | Answer directly                                  |
|          | version, ACL & freshness.  | reranks, Stack Runner fetches context.     | active specialist (Text only).                  | from internal reading matrix.                    |
+==========+============================+============================================+=================================================+==================================================+
| CORE EXECUTION INVARIANTS (HIGH SIGNAL)                                                                                                                                                 |
+==========+============================+============================================+=================================================+==================================================+
| LOGIC    | Multi-factor cache key     | Dense + Sparse Fusion -> Rerank            | Dynamic Tool Selection                          | Next-Token Prediction                            |
| RULES    | NO universal thresholds.   | Expand ONLY validated winners              | NO vectors processed                            | Internal mapped coordinates                      |
+==========+============================+============================================+=================================================+==================================================+
| CONTROL  | [ CACHE DECISION POLICY ]  | [ MULTI-STAGE RETRIEVAL FLOW ]             | [ ACTION CONTROL FLOW ]                         | [ FALLBACK CONTROL FLOW ]                        |
| FLOW     | EVAL: Exact Match on Key?  | EVAL: Hybrid Search & Validate Evidence    | EVAL: External Action Req?                      | EVAL: No matches/actions?                        |
|          | ├─ [HIT]  -> Return        | ├─ [Dense] & [Sparse] Recall Pass          | ├─ [HIT]  -> Execute & Return                   | ├─ [HIT]  -> Execute                             |
|          | └─ [MISS] -> To Ret. Tier─>| └─ [Merge/Dedup/Reciprocal Rank]           | └─ [MISS] -> Trigger Action Tier ──────────────>| └─ [FAIL] -> System Exception                    |
+==========+============================+============================================+=================================================+==================================================+
| INTERNAL | ┌────────────────────────┐ | ┌────────────────────────────────────────┐ | ┌───────────────────────────────────────────────┐ | ┌────────────────────────────────────────────────┐ |
| SEQUENCE | │ 1. [Catalog Keymaker]  │ | │ 1. [Hybrid Recall Stage]               │ | │ 1. [Heap] Orchestrator                        │ | │ 1. [Heap] Prompt Inject                        │ |
|          | │  ├─ Hash route_signal  │ | │  ├─ Dense: query_vec vs context        │ | │  ├─ Parse routing payload                     │ | │  ├─ Load persona rules                         │ |
|          | │  ├─ Bind Security ACL  │ | │  ├─ Sparse: Exact term/code match      │ | │  ├─ Determine required actions                │ | │  ├─ Bind raw text input                        │ |
|          | │  ├─ Bind Source Vers.  │ | │  └─ Merge/Dedup candidate list         │ | │  └─ Initialize execution state                │ | │  └─ Setup conversation hist.                   │ |
|          | └───────────┬────────────┘ | └───────────────────┬────────────────────┘ | └──────────────────────┬────────────────────────┘ | └───────────────────────┬────────────────────────┘ |
|          |             ▼              |                     ▼                      |                        ▼                        |                         ▼                          |
|          | ┌────────────────────────┐ | ┌────────────────────────────────────────┐ | ┌───────────────────────────────────────────────┐ | ┌────────────────────────────────────────────────┐ |
|          | │ 2. [Policy Evaluate]   │ | │ 2. [Rerank Stage]                      │ | │ 2. [Heap] Auth & Sandbox                      │ | │ 2. [Matrix] Context Assembly                   │ |
|          | │  ├─ Check freshness    │ | │  ├─ Senior Librarian evaluation        │ | │  ├─ Check policy rules                        │ | │  ├─ Assemble normalized query                  │ |
|          | │  ├─ Verify exact ACL   │ | │  ├─ Score support & coverage           │ | │  ├─ Mount isolated environment                │ | │  ├─ Inject baseline rules                      │ |
|          | │  └─ Yield if perfect   │ | │  └─ Prune low-signal nodes             │ | │  └─ Inject secure access keys                 │ | │  └─ Prepare generation window                  │ |
|          | └───────────┬────────────┘ | └───────────────────┬────────────────────┘ | └──────────────────────┬────────────────────────┘ | └───────────────────────┬────────────────────────┘ |
|          |             ▼              |                     ▼                      |                        ▼                        |                         ▼                          |
|          | ┌────────────────────────┐ | ┌────────────────────────────────────────┐ | ┌───────────────────────────────────────────────┐ | ┌────────────────────────────────────────────────┐ |
|          | │ 3. [Fast Terminal]     │ | │ 3. [Parent-Child Hydrate]              │ | │ 3. [Heap] Execution Telemetry                 │ | │ 3. [System] Output Handoff                     │ |
|          | │  ├─ Evict stale items  │ | │  ├─ Stack Runner fetches canonical     │ | │  ├─ Run script/interface sub-steps            │ | │  ├─ Log fallback trigger                       │ |
|          | │  ├─ Update access log  │ | │  ├─ Expand ONLY validated winners      │ | │  ├─ Evaluate return codes                     │ | │  ├─ Emit unanswerable warning                  │ |
|          | │  └─ Zero Generat. Cost │ | │  └─ Ensure visual flags routed to VLM  │ | │  └─ Capture standard out/error                │ | │  └─ Yield to Reading Room                      │ |
|          | └────────────────────────┘ | └───────────────────┬────────────────────┘ | └──────────────────────┬────────────────────────┘ | └───────────────────────┬────────────────────────┘ |
|          |                            |                     ▼                      |                        ▼                        |                         ▼                          |
|          |                            | ┌────────────────────────────────────────┐ | ┌───────────────────────────────────────────────┐ |                                                  |
|          |                            | │ 4. [Evidence Contract Builder]         │ | │ 4. [Store] State Handoff                      │ |                                                  |
|          |                            | │  ├─ Compile Citation Slip              │ | │  ├─ Write Canonical audit records             │ |                                                  |
|          |                            | │  ├─ Verify provenance & support status │ | │  ├─ Compile standard out payload              │ |                                                  |
|          |                            | │  └─ Yield precise context packet       │ | │  └─ Yield data to Reading Room                │ |                                                  |
|          |                            | └───────────────────┬────────────────────┘ | └──────────────────────┬────────────────────────┘ |                                                  |
|          |                            |                     ▼                      |                        ▼                        |                                                  |
+==========+============================+============================================+=================================================+==================================================+
| DOWNSTRM | TERMINAL PATH              | DOWNSTREAM TRANSFORMER MODEL (THE READING ROOM)                                                                                                 |
| REASONING| (Bypasses LLM entirely)    | (Autoregressive Generation, Chain of Thought, Tree of Thoughts, Self-Consistency, Reflexion)                                                      |
+----------+----------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------+
| COGNITIVE| ┌────────────────────────┐ | ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐ |
| SYNTHESIS| │ Return exact cache     │ | │ 1. [Ingest] Merge verified context, tool state, or raw prompt into context window. Assess abstain/clarify conditions.                           │ |
|          | │ Zero inference cost    │ | │ 2. [Synthesize] Apply instructed reasoning paths (CoT, ToT) and evaluate against safety guardrails.                                         │ |
|          | └────────────────────────┘ | │ 3. [Generate] Sample and stream final output tokens deterministically based on consolidated semantic state.                                   │ |
|          |                            | └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘ |
+==========+============================+=================================================================================================================================================+