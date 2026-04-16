
+=========================================================================================================================================================================================+
| PEDAGOGICAL LEGEND (MANTRA: 🔵 Blue asks, 🟠 Orange knows)                                                                                                                              |
| 🔵 Blue   = Query-side semantic seeker vector (query_vec)                                                                                                                               |
| 🟠 Orange = Document-side knowledge representation (raw_text_vector / contextual_text_vector)                                                                                           |
| raw_text  = Literal text rail (canonical truth, bypasses vector math)                                                                                                                   |
| route_signal = Routing / policy / control signal (distinct from retrieval vector)                                                                                                       |
+=========================================================================================================================================================================================+

+=========================================================================================================================================================================================+
|                                                                 PIPELINE B: INGESTION & INDEX BUILD (OFFLINE PRE-RUNTIME)                                                               |
+=========================================================================================================================================================================================+
| [ RAW SOURCES ] -> PDFs, Word Documents, Relational Databases, SharePoint, Web Fetch, Execution Telemetry, Incident Traces                                                              |
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
|       |                            Maintain canonical raw text integrity WHILE generating contextualized semantic overlays. Both become Document-Side Knowledge Vectors.                |
|       +--> Raw Path:               [ Canonical Raw Text ]  ==> [ 🟠 KNOWLEDGE VECTOR (raw_text_vector) ]                                                                                |
|       \--> Contextual Path:        [ Enricher / Reference Note ] ==> [ Title / Summary / Pattern Concepts ] ==> [ 🟠 KNOWLEDGE VECTOR (contextual_text_vector) ]                        |
|       |                                                                                                                                                                                 |
|       v                                                                                                                                                                                 |
|  [ MULTI-VECTOR MASTER ARCHIVES ]                                           [ METADATA & CANONICAL STORE: THE KNOWLEDGE SUBSTRATE ]                                                     |
|  Stores [Identifier : 🟠 raw_text_vector] and [Identifier : 🟠 contextual_text_vector] Relational Truth (Canonical Data, Telemetry, Lineage edges)                                      |
|  ┌────────────────────────────┐ ┌────────────────────────────┐              ┌────────────────────────────┐ ┌────────────────────────────┐                                               |
|  │ 1. Dense Search Index      │ │ 2. Sparse Keyword Index    │              │ 1. Canonical Raw Chunk     │ │ 2. Parent-Child Index      │                                               |
|  ├────────────────────────────┤ ├────────────────────────────┤              ├────────────────────────────┤ ├────────────────────────────┤                                               |
|  │ Meaning match (Vectors)    │ │ Exact term/code match      │              │ Complete unaltered text    │ │ Graph routing & lineage    │                                               |
|  └────────────────────────────┘ └────────────────────────────┘              └────────────────────────────┘ └────────────────────────────┘                                               |
+=========================================================================================================================================================================================+
