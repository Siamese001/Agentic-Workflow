┌───────────────────────────────────────────────┬───────────────────────────────────────────────┐
│ DENSE / BI-ENCODER                            │ CROSS-ENCODER                                 │
│ Fast candidate finder                         │ Slower pairwise judge / reranker / veto       │
├───────────────────────────────────────────────┼───────────────────────────────────────────────┤
│ INPUT                                         │ INPUT                                         │
│                                               │                                               │
│ Query:                                        │ Query + candidate together:                   │
│ "What does semantic cache do?"                │                                               │
│                                               │ "[Query] What does semantic cache do?          │
│ Candidate:                                    │  [Candidate] Explain semantic caching again." │
│ "Explain semantic caching again."             │                                               │
├───────────────────────────────────────────────┼───────────────────────────────────────────────┤
│ MODEL CALL PATTERN                            │ MODEL CALL PATTERN                            │
│                                               │                                               │
│ Query goes through encoder alone.             │ Query and candidate go through model together. │
│ Candidate was usually encoded earlier.        │ The model directly compares both texts.        │
│                                               │                                               │
│ Query ───────────► Encoder ──► query_vec       │ Query + Candidate ─► Cross-Encoder ─► score    │
│ Candidate ───────► Encoder ──► cand_vec        │                                               │
├───────────────────────────────────────────────┼───────────────────────────────────────────────┤
│ COMPARISON METHOD                             │ COMPARISON METHOD                             │
│                                               │                                               │
│ Compare two vectors.                          │ Compare token-to-token / phrase-to-phrase      │
│                                               │ inside the same attention pass.                │
│                                               │                                               │
│ query_vec ─┐                                  │ "Does this candidate actually answer           │
│            ├─ cosine similarity = 0.87         │  this exact query?"                            │
│ cand_vec ──┘                                  │                                               │
├───────────────────────────────────────────────┼───────────────────────────────────────────────┤
│ OUTPUT                                        │ OUTPUT                                        │
│                                               │                                               │
│ Similarity score:                             │ Relevance / equivalence score:                 │
│ 0.87                                          │ 0.94                                          │
│                                               │                                               │
│ Meaning:                                      │ Meaning:                                      │
│ "These are semantically close."               │ "This candidate is actually a good match."     │
├───────────────────────────────────────────────┼───────────────────────────────────────────────┤
│ STRENGTH                                      │ STRENGTH                                      │
│                                               │                                               │
│ Fast.                                         │ More precise.                                  │
│ Scales to millions of cached entries/chunks.  │ Better at detecting subtle mismatch.           │
│ Good for first-pass retrieval.                │ Good for reranking/vetoing top candidates.     │
├───────────────────────────────────────────────┼───────────────────────────────────────────────┤
│ WEAKNESS                                      │ WEAKNESS                                      │
│                                               │                                               │
│ Can overmatch related but different requests. │ Slower and more expensive.                     │
│ Less sensitive to exact wording constraints.  │ Cannot cheaply score millions of candidates.   │
│ Needs metadata/policy gates around it.        │ Needs top_k candidates from dense/BM25 first.  │
├───────────────────────────────────────────────┼───────────────────────────────────────────────┤
│ BEST USE                                      │ BEST USE                                      │
│                                               │                                               │
│ Recall stage:                                 │ Precision stage:                               │
│ "Find likely matches."                        │ "Decide which likely match is truly usable."   │
│                                               │                                               │
│ Used in:                                      │ Used in:                                      │
│ - semantic cache candidate lookup             │ - semantic cache reuse validation              │
│ - vector search                               │ - retrieval reranking                          │
│ - broad document/chunk retrieval              │ - cache veto before short-circuit reuse        │
├───────────────────────────────────────────────┼───────────────────────────────────────────────┤
│ RUNTIME ROLE                                  │ RUNTIME ROLE                                  │
│                                               │                                               │
│ Proposes candidates.                          │ Judges candidates.                             │
│                                               │                                               │
│ "Here are 20 possible cache hits."            │ "Only candidate 3 is equivalent enough."       │
└───────────────────────────────────────────────┴───────────────────────────────────────────────┘