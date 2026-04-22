==============================================================================================================================
[C5] 📚 GROUNDED RETRIEVAL & PROMPT ASSEMBLY SUBSTRATE
     Library Persona: 🔎 Research Runner + 🧠 Reference Librarian + 🧵 Packet Binder
     Spans: 🏛️ L4 shelves -> C0 retrieval -> prompt builder -> 🛠️ L2
==============================================================================================================================

     CORE MANDATE: 
     🔎 C0 retrieves only | 🧵 Prompt Assembly packages only
     NEITHER side invents facts or policy.

    [ OFFLINE CATALOG BUILD ]
📄 Docs / 💻 Code / 📜 Logs / 📊 Tables
           │
           │
     [ raw data ingestion ]
           │
           ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ✂️ CHUNK + TAG + INDEX                                                                                                     │
│ - Meaning (Vectors) / Keyword (Lexical) / Lineage (Graph)                                                                  │
└────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┘
                                                         │
                                                         │
                                                [ indexed knowledge ]
                                                         │
                                                         ▼
                                              [ 🏛️ L4 READ SHELVES ]
                                                         │
                                                         │             [ RUNTIME ASK ]
                                                         │        🧠 L1 Plan + 🧭 L0 Route
                                                         │         (Command: "Ground this")
                                                         │                     │
                                                         │                     │
                                                         │             [ grounding request ]
                                                         │                     │
                                                         └─────────────────────┼──────────────────────┐
                                                                               │                      │
                                                                               ▼                      │
==============================================================================================================================
                                     🔎 C0 CONTEXT ENGINE (The Reference Desk)
==============================================================================================================================
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0.1 RETRIEVAL PLAN                                                                                                        │
│ - Scopes source, freshness, and ACL requirements                                                                           │
│ - Binds version, tenant, and retrieval mode                                                                                │
└────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┘
                                                         │
                                                         │
                                                [ search parameters ]
                                                         │
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0.2 EVIDENCE FETCH                                                                                                        │
│ - Executes fact_vec (Dense), lexical (Sparse), and cache lookups                                                           │
│ - Performs metadata hydration and parent-child expansion                                                                   │
└────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┘
                                                         │
                                                         │
                                                 [ candidate chunks ]
                                                         │
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0.3 EVIDENCE SHAPING                                                                                                      │
│ - Deduplicates, expands, and reranks results based on relevance                                                            │
│ - Preserves provenance, citations, and conflicting data points                                                             │
└────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┘
                                                         │
                                                         │
                                                 [ ranked evidence ]
                                                         │
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0.4 EVIDENCE CONTRACT                                                                                                     │
│ - Validates verified_chunks and cited_spans with source_ids                                                                │
│ - Identifies coverage, gaps, and recommended next steps                                                                    │
└────────────────────────────────────────────────────────┬───────────────────┬───────────────────────────────────────────────┘
                                                         │                   │
                                                         │                   │
                                               [ verified context ]   [ weak support? ]
                                                         │                   │
                                                         ▼                   ▼
====================================================================   [ ❌ REFINE / ABSTAIN ]
                      🧵 PROMPT ASSEMBLY (The Packet Builder)
====================================================================
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PA.1 LOAD STATIC BLOCKS                                                                                                    │
│ - Injects system, policy, and output schema templates                                                                      │
│ - Binds persona and invariant operational blocks                                                                           │
└────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┘
                                                         │
                                                         │
                                                  [ system frame ]
                                                         │
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PA.2 SLOT CONTEXT + TASK                                                                                                   │
│ - Maps must-use vs. optional evidence into citation anchors                                                                │
│ - Sets contradiction flags; enforces C0 precedence over U0 policy fields                                                   │
└────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┘
                                                         │
                                                         │
                                                [ assembled prompt ]
                                                         │
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PA.3 TOKEN BUDGETER                                                                                                        │
│ - Trims and stratifies payload while preserving instruction order                                                          │
│ - Reserves schema space; if overflow, triggers request refinement                                                          │
└────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┘
                                                         │
                                                         │
                                                [ budgeted payload ]
                                                         │
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PA.4 PROMPT CONTRACT                                                                                                       │
│ - Signs the PromptEnvelope and updates PromptAssemblyStatus                                                                │
│ - Binds HMAC and replay metadata for execution integrity                                                                   │
└────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┘
                                                         │
                                                         │
                                                 [ ✉️ bounded packet ]
                                                         │
                                                         ▼
                                                  [ DISPATCH TO 🛠️ L2 ]

==============================================================================================================================
[!] ANALOGY: Shelves -> Runner finds support -> Binder packs it -> Stack Staff execute with bounded context.
==============================================================================================================================