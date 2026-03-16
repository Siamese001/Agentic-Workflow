====================================================================================================
               EMBEDDING LIFECYCLE: FLOW DEPENDENCIES & ADG-ENHANCED PIPELINE
====================================================================================================
[ STAGE 1: INGESTION & VECTORIZATION ]          [ STAGE 2: RETRIEVAL, ROUTING & EXECUTION ]
+---------------------------------------+       +--------------------------------------------------+
| L2: INCIDENT DETECTION                |       | L1: VECTOR SEARCH (ANN SIMILARITY)               |
| - Stack traces / Invariants           |       | 1. Query: embed(normalized_text)                 |
| - Territory violations / Tests        |------>| 2. similarity(query_v, e_i)                      |
| ADG: reads_from (66,640)              |       | 3. Retrieve top_k nearest vectors                |
+-------------------|-------------------+       | ADG: retrieves_via (52 edges)                    |
                    v                           +-------------------|------------------------------+
+---------------------------------------+                           v
| L2: NORMALIZATION                     |       +--------------------------------------------------+
| - Parse traces / Extract signatures   |       | L0: HEALING DECISION -> L3: PATH SELECTION       |
| - Collect execution context           |       | - Decision: Uses metadata + cluster stats        |
+-------------------|-------------------+       | - Routing: Path A/B/C/D selection                |
                    v                           | - Advisory: Embeddings inform, L0 decides        |
+---------------------------------------+       +-------------------|------------------------------+
| L1: EMBEDDING GENERATION (bge-m3)     |                           v
| - FIXED Model (No retraining)         |       +--------------------------------------------------+
| - INPUT: normalized_failure_text      |       | L2: EXECUTION & HEALING AGENTS                   |
| - OUTPUT: failure_vector [v1...vd]    |------>| - Dependency / Architecture / Gravity / Test     |
| - Property: Knowledge grows via Index |       | - System Mutation: Performed & Validated         |
+---------------------------------------+       | ADG: writes_to (4,875)                           |
                                                +-------------------|------------------------------+
====================================================================v===============================
[ STAGE 3: LEARNING LOOP & SYSTEM GROWTH ]
+--------------------------------------------------------------------------------------------------+
| L4: STORAGE / L6: TELEMETRY — EVENT PERSISTENCE                                                  |
| 1. Re-embed failure (Fixed bge-m3) -> 2. Insert into Index -> 3. Index Grows: {e1...eN, e_new}   |
| ADG: stores_embedding (14 edges) tracks vector insertions                                        |
+--------------------------------------------------------------------------------------------------+
| META-LEARNING SYSTEM: CROSS-INCIDENT ANALYSIS                                                    |
| - Analyzes: Recurring signatures (clustering), healer efficacy, regression patterns              |
| - Property: Consumes vectors from memory; Proposes routing optimizations; Never retrains model   |
| ADG: emits_determinism_digest (3), chunks_into (1)                                               |
+--------------------------------------------------------------------------------------------------+

====================================================================================================
[ DEPENDENCY FLOW SUMMARY ]                             [ KEY PRINCIPLES ]
+----------------------------+-----------------------+  +------------------------------------------+
| TYPE       | FLOW          | ADG IMPACT            |  | 1. MODEL INVARIANT: bge-m3 stays FIXED   |
|------------|---------------|-----------------------|  | 2. INDEX GROWTH: Knowledge is cumulative |
| Parallel   | Meta + Embed  | Independent paths     |  | 3. BINDING: Vectors tied to healer/files |
| Sequential | Signal->Vector| Strict order 1-8      |  | 4. ADVISORY: L1 suggests, L0 authorizes  |
| Feedback   | Loop->Query   | Index expansion       |  | 5. META: Cross-incident optimization     |
| Cross-Layer| L2->L1 / L1->L4| Inter-layer edges     |  | 6. REPLAY: Determinism digests enabled   |
+------------+---------------+-----------------------+  +------------------------------------------+

ADG CACHE: Redis MCP Client | TIMESTAMP: 03132026_1424 | LAST UPDATED: 2026-03-14 08:17 UTC
TOPOLOGY: Nodes: 8,234 | Edges: 224,969 | L1: 106 mod | L2: 316 mod | L4: 154 mod
EDGES: reads_from(66,640), writes_to(4,875), retrieves_via(52), stores_embedding(14), digest(3)
====================================================================================================
