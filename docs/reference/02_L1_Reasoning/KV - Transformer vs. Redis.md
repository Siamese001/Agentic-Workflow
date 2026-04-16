=====================================================================================================================
|             TRANSFORMER KV (INSIDE MODEL)              |             REDIS KEY-VALUE (OUTSIDE MODEL)              |
|                 "How the model thinks"                 |       "How you avoid needing the model to think"         |
=====================================================================================================================
| [INPUT TOKENS] discrete ids                            | [USER QUERY] "Why did claims increase?"                  |
|       |                                                |       |                                                  |
|       v                                                |       v                                                  |
| [TOKEN EMBEDDING] lookup table: vocab × hidden         | [NORMALIZE + HASH] key = SHA256(query)                   |
|       |                                                |       |                                                  |
|       v                                                |       v                                                  |
| [HIDDEN VECTORS (X)]                                   | [REDIS LOOKUP O(1)] key → cached_response                |
|       |                                                |       |                                                  |
|       v                                                |       +----------------------+                           |
| [LINEAR PROJECTIONS]                                   |       |                      |                           |
|  Q = X·Wq (what I’m looking for / reader's question)   |     [HIT]                  [MISS]                        |
|  K = X·Wk (what I contain / book index labels)         |       |                      |                           |
|  V = X·Wv (what info I provide / book contents)        |       v                      v                           |
|       |                                                | [RETURN ANSWER]     [EMBEDDING + RAG]                    |
|       v                                                |   (skip LLM)          (vector search)                    |
| [ATTENTION SCORES] score = Q·Kᵀ (match query to keys)  |   (skip librarian)           |                           |
|       |                                                |                              v                           |
|       v                                                |                     [LLM (TRANSFORMER)]                  |
| [SOFTMAX] (which tokens matter?)                       |                     (NOW KV ATTENTION USED)              |
|       |                                                |                                                          |
|       v                                                |                                                          |
| [WEIGHTED SUM] output = weights·V (retrieve info)      |                                                          |
|       |                                                |                                                          |
|       v                                                |                                                          |
| [NEXT LAYER / OUTPUT] (repeat across layers)           |                                                          |
=====================================================================================================================
|                                       HIGH SIGNAL ATTRIBUTE MATRIX                                                |
=====================================================================================================================
| PURPOSE  | Compute attention (reasoning)               | Avoid computation (caching/optimization gate)            |
| DATA     | Dense tensors: K, V ∈ ℝ^(seq_len×hidden_dim)| Hash map: key:string → value:string/json                 |
| LIFETIME | Ephemeral (per request/layer, reused gen)   | Persistent (seconds→days TTL, shared across users)       |
| LOCATION | GPU / model memory                          | External RAM (Redis server)                              |
| SCALING  | #layers × seq_len × hidden_dim              | #queries × cache size                                    |
| TIMING   | ALWAYS used during inference                | Used BEFORE inference (optimization gate)                |
| ANALOGY  | Librarian reads and reasons                 | Prewritten answer on a question card                     |
=====================================================================================================================