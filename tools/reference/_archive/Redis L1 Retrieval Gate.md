╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ EXECUTIVE SUMMARY: Redis serves as the L1 retrieval gate. By performing a deterministic O(1) key lookup   ║
║ before vector generation, the system averts expensive similarity searches and embedding operations.       ║
╠═════════════════════════════════════════╦═════════════════════════════════════════════════════════════════╣
║         SYSTEM ARCHITECTURE FLOW        ║               STRATEGIC RATIONALE & MECHANICS                   ║
╟─────────────────────────────────────────╫─────────────────────────────────────────────────────────────────╢
║                                         ║                                                                 ║
║      [ USER QUERY (Reader asks Q) ]     ║  [ PIPELINE LATENCY PROFILE ]                                   ║
║                     │                   ║   Step                     Latency         Memory Type          ║
║                     ▼                   ║   1. Redis Lookup          ~1 ms           Exact Memory         ║
║      ┌───────────────────────────┐      ║   2. Vector Search         ~10-50 ms       Similar Memory       ║
║      │ L1: QUERY NORMALIZATION   │      ║   3. Full RAG Pipeline     ~500-2000 ms    Reasoning/Synth.     ║
║      │ key = SHA256(norm_query)  │      ║                                                                 ║
║      │ [Librarian fingerprints Q]│      ║  [ THE LIBRARIAN ANALOGY (GRANULAR) ]                           ║
║      └──────────────┬────────────┘      ║   Reader asks a question:                                       ║
║                     │                   ║    ► REDIS (L1) = The "Rotating Book Cart" / "Index Drawer"     ║
║                     ▼                   ║      Librarian checks the front desk cart first (frequently     ║
║      ┌───────────────────────────┐      ║      used notes, research summary cards).                       ║
║      │ L1: REDIS SEMANTIC CACHE  │      ║      • HIT: Finds card on desk cart → Returns instant answer.   ║
║      │ O(1) Key-Value Hash Check ├─HIT─►║      • MISS: Librarian walks to the deep archive shelves.       ║
║      │ [Check rotating book cart]│      ║    ► VECTOR DB (L2) = The "Deep Archive Shelves"                ║
║      └──────────────┬────────────┘      ║      Librarian searches deep archives, synthesizes an answer,   ║
║                     │ MISS (Walk to     ║      and places the new book/card onto the front desk cart      ║
║                     │ deep archives)    ║      for the next visitor before handing it to the reader.      ║
║                     ▼                   ║                                                                 ║
║      ┌───────────────────────────┐      ║  [ EVIDENCE FROM ADG ARCHITECTURE ]                             ║
║      │ EMBEDDING GENERATION      │      ║   "Layer 1 (Redis): O(1) exact content hash matching ...        ║
║      │ embed(query) -> vector v_q│      ║    Layer 2 (InMemoryVectorStore): semantic similarity."         ║
║      │ *Only runs on cache miss  │      ║                                                                 ║
║      └──────────────┬────────────┘      ║  [ WHY THIS WORKS WITHOUT REDIS BEING A VECTOR DB ]             ║
║                     │                   ║   Redis is not querying by vector similarity. It acts as a      ║
║                     ▼                   ║   classic key-value store where the KEY is the deterministic    ║
║      ┌───────────────────────────┐      ║   SHA256 fingerprint of the normalized text. Embeddings are     ║
║      │ L2: VECTOR RETRIEVAL      │      ║   bypassed entirely on a cache hit.                             ║
║      │ FAISS / Vector DB         │      ║                                                                 ║
║      │ similarity(v_q, v_i)      │      ║  [ STORED ARTIFACTS IN REDIS (TTL: 24h) ]                       ║
║      │ [Search deep archives]    │      ║   • Full generated answers                                      ║
║      └──────────────┬────────────┘      ║   • Retrieved context bundles                                   ║
║                     │                   ║   • Prior reasoning paths                                       ║
║                     ▼                   ║                                                                 ║
║      ┌───────────────────────────┐      ║  [ CONCLUSION ]                                                 ║
║      │ L3: RAG PIPELINE          │      ║   Redis acts as the fastest possible retrieval gate. By         ║
║   ┌──┤ Context assembly +        │      ║   executing exact deterministic memory lookups *before* any     ║
║   │  │ Answer generation         │      ║   embedding or vector math occurs, it radically compresses      ║
║   │  │ [Write research summary]  │      ║   latency and computational overhead for repeated queries.      ║
║   │  └───────────────────────────┘      ║                                                                 ║
║   │                                     ║                                                                 ║
║   │                 ▲                   ║                                                                 ║
║   │  ┌──────────────┴────────────┐      ║                                                                 ║
║   └─►│ L1 WRITE-BACK             │      ║                                                                 ║
║      │ key = SHA256(query)       │      ║                                                                 ║
║      │ value = final_answer      │      ║                                                                 ║
║      │ [Place card on desk cart] │      ║                                                                 ║
║      └───────────────────────────┘      ║                                                                 ║
╚═════════════════════════════════════════╩═════════════════════════════════════════════════════════════════╝
