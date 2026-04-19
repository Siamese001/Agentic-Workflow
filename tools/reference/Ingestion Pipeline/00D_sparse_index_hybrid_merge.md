==============================================================================================================================
[00D] 🔎 SPARSE INDEX + HYBRID MERGE
     Scope: Exact words, IDs, clauses, fields, and code symbols.
     Core Rule: Dense = Find Meaning | Sparse = Find Exact Wording | Hybrid = Combine Both
==============================================================================================================================

[ 🧱 BUILD TIME ]

  [ Raw Chunk ]
       │
       ▼
╭──────────────────────────────────────── THE SPARSE PIPELINE ─────────────────────────────────────────╮
│                                                                                                    │
│  [1] 🧹 NORMALIZE  ──►  [2] ⛏️ EXTRACT        ──►  [3] 🧩 TOKENIZE      ──►  [4] ⚖️ WEIGHT        │
│  (text copy)            (IDs, fields, terms)       (phrases, symbols)        (title/field boost)   │
╰────────────────────────────────────────────────────────────────────────────────────────────────────╯
                                           │
           ╭───────────────────────────────┴───────────────────────────────╮
           ▼                                                               ▼
╭───────────────────────────────────────────────────╮        ╭──────────────────────────────╮
│ [5] 🗂️ INVERTED INDEX BUILD                       │        │ 🧾 EXAMPLES EXTRACTED        │
│ Map: term/phrase ──► postings list                │        │ ├─ "14.2"                    │
│      [chunk_id, field, position, weight]          │        │ ├─ "policy_hash"             │
│                                                   │        │ ├─ "Article I Section 8"     │
│ "policy_hash"   ──► [chunk_07, chunk_19]          │        │ ├─ "build_prompt_envelope"   │
│ "14.2"          ──► [chunk_03]                    │        │ └─ "decision_status enum"    │
│ "decision_st.." ──► [chunk_31, chunk_32]          │        ╰──────────────────────────────╯
╰────────────────────────┬──────────────────────────╯
                         │
            ┌────────────┴────────────┐
            ▼                         ▼
  ╭─────────────────────╮   ╭─────────────────────────╮
  │ [6] 🗄️ SPARSE STORE │   │ [7] 🏛️ CANONICAL STORE │
  │ (Postings lists)    │   │ (Raw text & metadata)   │
  ╰─────────────────────╯   ╰─────────────────────────╯

==============================================================================================================================
[ 🏃‍♂️ QUERY TIME ]

                                       [ 👤 USER QUERY ]
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       ▼                                           ▼
            ╭────────────────────────╮                  ╭────────────────────────╮
            │ [8] 🔎 SPARSE PATH      │                  │ [9] 🧠 DENSE PATH       │
            │ (Literal / Quoted / ID)│                  │ (Semantic / Paraphrase)│
            │ ├─ Dep: [6] Sparse     │                  │ ├─ Dep: Vector DB      │
            ╰──────────┬─────────────╯                  ╰──────────┬─────────────╯
                       │                                           │
                [ Postings Hit ]                            [ Vector Hits ]
                       │                                           │
                       └──────────────────┐     ┌──────────────────┘
                                          ▼     ▼
                              ╭─────────────────────────────╮
                              │ [10] 🤝 HYBRID MERGE         │
                              │ ├─ Dep: [8] + [9]           │
                              │ ├─ Logic: Union & Rerank    │
                              │ └─ Note: Sparse wins on IDs │
                              ╰─────────────┬───────────────╯
                                            │
                              ╭─────────────▼───────────────╮
                              │ [11] 🛡️ GOVERNANCE FILTERS  │
                              │ ├─ Dep: [10] Candidates     │
                              │ └─ Check: ACL, Freshness    │
                              ╰─────────────┬───────────────╯
                                            │
                              ╭─────────────▼───────────────╮
                              │ [12] 💧 HYDRATE              │
                              │ ├─ Dep: [7] Canonical Store │
                              │ └─ Action: Fetch raw text,  │
                              │    citations, lineage edges │
                              ╰─────────────┬───────────────╯
                                            │
                              ╭─────────────▼───────────────╮
                              │ [13] 📤 C0 OUTPUT            │
                              │ ├─ Dep: [12] Grounding      │
                              │ └─ Yields: Verified chunks  │
                              │    ready for prompt         │
                              ╰─────────────────────────────╯

==============================================================================================================================
[ 🔬 MICRO WALKTHROUGHS ]
==============================================================================================================================

╭──────────────────────────────────────────────╮  ╭──────────────────────────────────────────────╮
│ A: "Article I Section 8"                     │  │ B: "where is build_prompt_envelope defined?" │
│                                              │  │                                              │
│ 🔎 Sparse: Exact hit ──► [chunk_11]          │  │ 🔎 Sparse: Symbol hit ──► [chunk_44]         │
│ 🧠 Dense : Semantic neighbor                 │  │ 🧠 Dense : Semantic neighbor                 │
│            ──► [chunk_10, 11, 45]            │  │            ──► [chunk_44, 47]                │
│                                              │  │                                              │
│ 🤝 Merge : chunk_11 wins                     │  │ 🤝 Merge : chunk_44 wins                     │
│   (literal match + semantic support combined)│  │   (symbol exact beats paraphrase fuzz)       │
╰──────────────────────────────────────────────╯  ╰──────────────────────────────────────────────╯