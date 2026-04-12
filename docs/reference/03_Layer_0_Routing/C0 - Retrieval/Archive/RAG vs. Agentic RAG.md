========================================================================================================================================================================
                                                CONCEPTUAL COMPARISON: TRADITIONAL vs. AGENTIC RAG FLOWS
========================================================================================================================================================================

            [ TRADITIONAL RAG (Linear, One-Shot) ]                                            [ AGENTIC RAG (Iterative, Multi-Step, Self-Correcting) ]

                     +------------------+                                                                    +------------------+
                     | [ USER REQUEST ] |                                                                    | [ USER REQUEST ] |
                     +------------------+                                                                    +------------------+
                               |                                                                                       |
                               v                                                                                       v
+-------------------------------------------------------------+                      +-------------------------------------------------------------------------+
| 1. RETRIEVE (Single fixed query)                            |                      | 1. L1 AGENT: REASON & PLAN (Decompose request, formulate strategy)      |
|    - Query Vector DB once                                   |                      |    - "What info do I need? Which tools can get it?"                     |<-----\
|    - Fetch top-K documents                                  |                      +-------------------------------------------------------------------------+      |
+-------------------------------------------------------------+                                        | (Select Tool / Formulate Query)                              |
                               |                                                                       v                                                              |
                               | (Fixed Context)                                     +-------------------------------------------------------------------------+      |
                               v                                                     | 2. TOOL USE: RETRIEVAL (Dynamic, multi-turn capability)                 |      |
+-------------------------------------------------------------+                      |    - Call Search/Vector DB tools with specific queries                  |      |
| 2. AUGMENT & GENERATE (Context window stuffing)             |                      |    - [L4 Gateway & Infra Adapters manage this access]                   |      |
|    - Combine original query + retrieved context             |                      +-------------------------------------------------------------------------+      |
|    - LLM generates final response in one pass               |                                        | (Retrieved Evidence)                                         |
+-------------------------------------------------------------+                                        v                                                              |
                               |                                                     +-------------------------------------------------------------------------+      |
                               v                                                     | 3. EVALUATE & REFINE (Reasoning on retrieved data)                      |      |
                     +------------------+                                            |    - "Is this info sufficient/relevant? Do I need more?"                |------/
                     | [ FINAL ANSWER ] |                                            +-------------------------------------------------------------------------+
                     +------------------+                                                              |                                               (Insufficient)
                                                                                                       | (Sufficient Info)
                                                                                                       v
                                                                                     +-------------------------------------------------------------------------+
                                                                                     | 4. SYNTHESIZE RESPONSE (Final Generation)                               |
                                                                                     |    - Compile all relevant findings into a coherent answer               |
                                                                                     +-------------------------------------------------------------------------+
                                                                                                                       |
                                                                                                                       v
                                                                                                             +------------------+
                                                                                                             | [ FINAL ANSWER ] |
                                                                                                             +------------------+

========================================================================================================================================================================
                                              AGENTIC SYSTEM — L1/L4 RAG INFRASTRUCTURE & DATA FLOW (TECHNICAL DRILL-DOWN)
========================================================================================================================================================================

 [ L1: COGNITIVE COMPUTE ]          [ L4: MODEL & SIGNAL STATE ]       [ L4: INFRASTRUCTURE ADAPTERS ]    [ EXTERNAL INFRASTRUCTURE ]        [ L1: REASONING & ALIGNMENT ]      [ L6: OBSERVABILITY ]
 (High-Inference Logic Engine)      (Persistent Knowledge Substrate)   (The Physical I/O Surface)         (Hardware & Data Persistence)      (Final Cognitive Alignment)        (The Telemetry Engine)

+-------------------------------+  +-------------------------------+  +-------------------------------+  +-------------------------------+  +-------------------------------+  +-------------------------------+
| L1.A: QUERY ENCODER (COMPUTE) |  | L4.A: KNOWLEDGE ANCHOR        |  | L4.C: RETRIEVAL GATEWAY       |  | [ VECTOR DB ]                 |  | L1.C: HIGH-RES RERANKER       |  | L6.A: RETRIEVAL METRICS       |
| - [EMBEDDING] Inference       |<-| [READ: Embedder_ID/Weights]   |  | - Enforces Rate Limits        |  | - Pinecone / Milvus           |  | - [CROSS-ENCODER] Inference   |<-| [READ: Hit Rate/Latency]      |
| - Text -> Vector Projection   |->| [WRITE: Encoder_Telemetry]    |<-| [READ: Auth/Max_K/Budgets]    |<-| - Metadata Partitioning       |<-| - Context Compression         |->| [WRITE: Quality_Signals]      |
+-------------------------------+  +-------------------------------+  | - Validates JSON Schemas      |->| - Hardware Acceleration       |->| - Factuality Grounding        |  +-------------------------------+
               |                                   |                  +-------------------------------+  +-------------------------------+  +-------------------------------+                  ^
 [L1 WRITES query_vector]          [L4 READS Auth/Budgets]                            |                                  |                                  ^                                  |
               v                                   v                                  v                                  v                                  |                    [L6 WRITES Quality metrics]
+-------------------------------+  +-------------------------------+  +-------------------------------+  +-------------------------------+  +-------------------------------+  +-------------------------------+
| L1.B: SIMILARITY & FUSION     |  | L4.B: KNOWLEDGE SUBSTRATE     |  | L4.D: LEXICAL ADAPTER         |  | [ LEXICAL SEARCH / IDF ]      |  | L1.D: PROMPT AUGMENTOR        |  | L4.E: SIGNAL ANCHOR           |
| - [COSINE SIMILARITY SCORING] |<-| [READ: IDF_Stats/Vocab]       |  | - BM25 / Lucene Querying      |  | - Elasticsearch / OS          |  | - Injects Context Bundle      |<-| [READ: Scores/Drift]          |
| - [HYBRID FUSION (RRF)]       |->| [WRITE: Signal_Logs]          |<-| [READ: Statistical_IDF_Pull]  |<-| - Full-Text Sharding          |<-| - Reasoning Loop Alignment    |->| [WRITE: L6_Telemetry]         |
| - Score Normalization         |  | - [CHUNK_STORE / METADATA]    |->| [WRITE: Query_Performance]    |->| - Global IDF Statistics       |->| - Produces Non-Mutant Proposal|  +-------------------------------+
+-------------------------------+  +-------------------------------+  +-------------------------------+  +-------------------------------+  +-------------------------------+
               |                                   |                                  |                                  |                                  ^
      [L1 WRITES Fused Set]         [INFRA WRITES candidate vectors]      [L4 WRITES fetch request]         [L4 WRITES context bundle]     [L1 WRITES Materialization Req]
               v                                   v                                  v                                  v                                  |
+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                                                                    L4.F: CONTEXT MATERIALIZER & CHUNK STORE (THE BUS)                                                                                |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [ACTION: Hydrates Chunk_IDs -> Raw_Text]    [READ: S3 / SQL Document Store]    [WRITE: context_bundle.json]    [ENFORCE: Token Budgets]    [ANCHOR: Surgical Manifest / Citations]                   |
+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

========================================================================================================================================================================
                                                           TECHNICAL DATA FLOW & AUTHORITY MAPPING
========================================================================================================================================================================
| STEP | OPERATION             | L | DATA MOVEMENT (READ / WRITE)                                                                   | ARCHITECTURAL INVARIANT          |
|------|-----------------------|---|------------------------------------------------------------------------------------------------|----------------------------------|
| 1    | Query Encoding        | L1| L1 READS Model Weights from L4; L1 WRITES query_vector to context.                             | L1 does all high-inf compute.    |
| 2    | Gateway Validation    | L4| L4 READS Auth/Budgets; L4 WRITES authorized fetch request to Infrastructure.                   | L4 Gateway enforces boundaries.  |
| 3    | Raw Search            | IN| INFRA READS search intent; INFRA WRITES raw candidate vectors/IDs to L4.                       | Hardware provides persistence.   |
| 4    | Similarity & Fusion   | L1| L1 READS Raw Vectors & IDF Stats from L4; L1 WRITES Fused Rank Set.                            | L1 executes scoring logic.       |
| 5    | High-Res Reranking    | L1| L1 READS Cross-Encoder weights from L4; L1 WRITES Surgical Materialization Request.            | L1 Reranking optimizes tokens.   |
| 6    | Materialization       | L4| L4 READS raw bytes from S3/SQL; L4 WRITES context_bundle.json to L1 Reasoning.                 | L4 abstracts storage complexity. |
| 7    | Observability Loop    | L6| L6 READS retrieval signals from L4; L6 WRITES Quality/Drift metrics into L4 for Run t+1.       | L6 monitors without blocking.    |
========================================================================================================================================================================