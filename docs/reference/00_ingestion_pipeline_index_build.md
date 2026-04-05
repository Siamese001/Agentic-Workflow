╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ [00] 📥 INGESTION + 🧱 INDEX BUILD                                                                                             ║
║      offline pre-runtime • builds the 🟠 document-side knowledge substrate for C0 / L0 / L1                                  ║
║                                                                                                                              ║
║ PEDAGOGICAL LEGEND (MANTRA: 🔵 Blue asks, 🟠 Orange knows)                                                                   ║
║ 🔵 Blue      = Query-side semantic seeker vector (query_vec)                                                                 ║
║ 🟠 Orange    = Document-side knowledge representation (raw_text_vector / contextual_text_vector)                             ║
║ raw_text     = Literal text rail (canonical truth, bypasses vector math)                                                     ║
║ route_signal = Routing / policy / control signal (distinct from retrieval vector)                                            ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

[ RAW SOURCES ]
📄 PDFs  📘 Word Docs  🗃️ Relational DBs  🏢 SharePoint  🌐 Web Fetch  📡 Execution Telemetry  🚨 Incident Traces
       │
       │ [ raw byte streams ]
       ▼
╔══════════════════════╗
║ [00.1] 📥 INTAKE     ║
║ modality detect      ║
╚══════╤═══════════════╝
       │ Route based on content type (The Intake Clerk)
       ├──> 📝 Text Extractor     → prose / event logs / flat text files
       └──> 🖼️ Visual Detector    → tables / charts / diagrams / scanned pages / engineering illustration visuals
       │
       │ [ parsed content items ]
       ▼
╔══════════════════════╗
║ [00.2] 🧾 CANONICAL  ║
║ RAW UNIT             ║
╚══════╤═══════════════╝
       │ Establish the base immutable record
       └──> raw text • source identifier • parent identifier • visual modality flag
       │
       │ [ base data records ]
       ▼
╔══════════════════════╗
║ [00.3] 🔁 LIFECYCLE  ║
║ + STATE SYNC         ║
╚══════╤═══════════════╝
       │ Operational Update Path:
       └──> 🔍 Dedupe Checksum → 🆚 Version Compare → 🪦 Tombstone Stale Data → 🔗 Preserve Graph Lineage → ♻️ Reindex
       │
       │ [ active clean records ]
       ▼
╔══════════════════════╗
║ [00.4] ✂️ CHUNKING   ║
║ POLICY               ║
╚══════╤═══════════════╝
       │ Corpus Classifier: Route to specific chunking strategy. No generic defaults.
       ├──> 📜 Policy / Long Docs   → section-aware boundaries • parent-child hydrate markers • eval-tuned overlap
       ├──> 🚨 Incident / Trace     → event-boundary chunks • temporal adjacency metadata • strict no-paragraph splitting
       ├──> 💻 Code / Config        → symbol and block-aware extraction • file lineage • dependency metadata tags
       └──> 📊 Visuals / Tables     → page or element-aware units • multimodal flag assignment
       │
       │ [ unannotated chunks ]
       ▼
╔══════════════════════╗
║ [00.5] 🏷️ METADATA   ║
║ BINDING              ║
╚══════╤═══════════════╝
       │ (CRITICAL: Metadata is bound here to enable strict pre-retrieval gating in the Inference Pipeline)
       ├──> 🔐 Access Control Lists • 🏢 tenant identifiers • 🔒 confidentiality tiers
       └──> 🕒 freshness bands • 📅 effective/expiry dates • 🧬 embedding schema versions
       │
       │ [ bounded data chunks ]
       ▼
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ [00.6] 🧠 DUAL REPRESENTATION                                                                                                ║
║ [ CORE LOGIC: SEMANTIC ENRICHMENT & DUAL EMBEDDING ]                                                                         ║
║ Maintain canonical raw text integrity WHILE generating contextualized semantic overlays. Both become Document-Side Vectors.  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

         RAW PATH                                                  CONTEXTUAL PATH
  ┌──────────────────────┐                                  ┌──────────────────────────────┐
  │ Canonical Raw Text   │                                  │ Enricher / Reference Note    │
  │ literal truth rail   │                                  │ title / summary / concepts   │
  └──────────┬───────────┘                                  └────────────┬─────────────────┘
             │                                                           │
             │ [ exact text bounds ]                                     │ [ enriched summaries ]
             ▼                                                           ▼
  ┌──────────────────────┐                                  ┌──────────────────────────────┐
  │ 🟠 raw_text_vector   │                                  │ 🟠 contextual_text_vector    │
  │ literal semantic map │                                  │ semantic overlay map         │
  └──────────┬───────────┘                                  └────────────┬─────────────────┘
             └────────────────────────────────┬──────────────────────────┘
                                              │
                                              │ [ dual embedded chunks ]
                                              ▼
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ [00.7] 🗂️ MULTI-VECTOR MASTER ARCHIVES  +  🏛️ METADATA & CANONICAL STORE                                                     ║
║ Stores [Identifier : 🟠 raw_text_vector] and [Identifier : 🟠 contextual_text_vector]                                        ║
║ Relational Truth (Canonical Data, Telemetry, Lineage edges)                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

          ┌──────────────────────────────┐      ┌──────────────────────────────┐
          │ 1. 🧠 DENSE SEARCH INDEX     │      │ 2. 🔎 SPARSE KEYWORD INDEX   │
          │ meaning match (vectors)      │      │ exact term / code match      │
          │ stores 🟠 raw_text_vector    │      │ lexical retrieval rail       │
          │ and 🟠 contextual_text_vector│      │                              │
          └──────────────┬───────────────┘      └──────────────┬───────────────┘
                         │                                     │
                         └──────────────────┬──────────────────┘
                                            │
                                            │ [ index bindings ]
                                            ▼
          ┌──────────────────────────────┐      ┌──────────────────────────────┐
          │ 3. 🧾 CANONICAL RAW STORE    │      │ 4. 🔗 PARENT-CHILD INDEX     │
          │ complete unaltered text      │      │ graph routing & lineage      │
          │ relational truth / telemetry │      │ hydrate / expand / ancestry  │
          └──────────────┬───────────────┘      └──────────────┬───────────────┘
                         │                                     │
                         └──────────────────┬──────────────────┘
                                            │
                                            │ [ unified storage state ]
                                            ▼
                               🟠 KNOWLEDGE SUBSTRATE READY

╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ [00.8] 📏 INDEX EVAL + FEEDBACK LOOP                                                                                         ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

   📊 Recall@K   📊 NDCG/MRR   📊 citation precision   📊 support rate   📊 drift/staleness   📊 reindex trigger
        │
        │ [ grading metrics ]
        ▼
   tune future:
   ✂️ chunking
   🧠 enrichment
   🗂️ dense/sparse balance
   ♻️ partial/full reindex

╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ [00.9] 🔌 HANDOFF TO INFERENCE PIPELINE / 01-06                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

   [00] publishes:
      • 🟠 raw_text_vector
      • 🟠 contextual_text_vector
      • 🔎 sparse keyword surfaces
      • 🧾 canonical raw chunks
      • 🔗 parent-child lineage

   then later at inference:
      🔵 query_vec
          │
          │ [ semantic retrieval request ]
          ├──> dense recall against 🟠 raw_text_vector + 🟠 contextual_text_vector
          ├──> sparse recall against exact term / code / schema
          └──> hydrate canonical truth + parent-child expansion

╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ [00.10] 📚 LIBRARY ANALOGY                                                                                                   ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

📥 Intake Clerk      → receives books / scans / ledgers / logs
🧾 Cataloger         → creates official accession record
🔁 Preservation Desk → dedupe / edition compare / retirement / lineage
✂️ Shelving Team     → decides how material is split for findability
🏷️ Access Desk       → stamps clearance / tenant / freshness / validity
🧠 Subject Indexer   → creates literal and conceptual card-catalog entries
🗂️ Stack Builder     → publishes vector shelves + keyword shelves + canonical archive + lineage map

Bottom line:
[00] is where the vector DB and keyword retrieval surfaces are built.
[03]/C0 later query them.