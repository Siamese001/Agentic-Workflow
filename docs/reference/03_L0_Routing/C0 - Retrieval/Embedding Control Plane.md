======================================================================================================================================
                                     🧠 EMBEDDING CONTROL PLANE — ONE MONSTER VIEW
======================================================================================================================================

                                           ┌──────────────────────────────────────────────┐
                                           │            USER / SYSTEM INPUT               │
                                           │  (query text OR document chunk text)        │
                                           └──────────────────────┬───────────────────────┘
                                                                  │
                                                                  ▼
                                            ┌──────────────────────────────────────────┐
                                            │        L1 INTERPRET (NO EMBEDDING)       │
                                            │ - parse intent                           │
                                            │ - decide if retrieval needed             │
                                            └──────────────────────┬───────────────────┘
                                                                  │
                                                                  ▼
                                            ┌──────────────────────────────────────────┐
                                            │        L0 ROUTE DECISION                 │
                                            │                                          │
                                            │  R1 cache? ───────────────► (skip all)   │
                                            │  R5 fallback? ────────────► (skip all)   │
                                            │  R2 retrieval needed? ─────► YES         │
                                            └──────────────────────┬───────────────────┘
                                                                  │
                                                                  ▼
======================================================================================================================================
                                     🔑 EMBEDDING PROVIDER CONTROL (THIS IS THE PROBLEM ZONE)
======================================================================================================================================

                                     ┌──────────────────────────────────────────────┐
                                     │ EMBEDDING FACTORY (SINGLE SOURCE OF TRUTH)   │
                                     │                                              │
                                     │ provider =                                   │
                                     │   explicit param?                            │
                                     │   else ENV?                                  │
                                     │   else DEFAULT                               │
                                     └───────────────┬──────────────────────────────┘
                                                     │
                              ┌──────────────────────┼──────────────────────────────┐
                              │                      │                              │
                              ▼                      ▼                              ▼
                    provider="bge-m3"        provider="openai"              ❌ BAD STATE
                    (desired default)        (explicit only)                (today)
                              │                      │                              │
                              │                      │                              │
                              │                      │                    provider omitted
                              │                      │                    OR hardcoded call
                              │                      │                              │
                              │                      │                              ▼
                              │                      │                   ┌────────────────────┐
                              │                      │                   │ SILENT FALLBACK    │
                              │                      │                   │ TO OPENAI          │
                              │                      │                   │ (BUG)              │
                              │                      │                   └─────────┬──────────┘
                              │                      │                             │
                              ▼                      ▼                             ▼
======================================================================================================================================
                             🟢 BGE LANE (CORRECT)                        🔴 OPENAI LANE (EXPLICIT ONLY)
======================================================================================================================================

┌──────────────────────────────────────────────┐          ┌──────────────────────────────────────────────┐
│ BGE-M3 ENCODER (LOCAL / vLLM)                │          │ OPENAI EMBEDDINGS API                         │
│                                              │          │                                              │
│ - encoder-only transformer                   │          │ - external network call                      │
│ - runs inside your infra                     │          │ - $$$ + latency + non-determinism            │
│ - no external dependency                     │          │ - should be rare                             │
│                                              │          │                                              │
│ INPUT: text                                 │          │ INPUT: text                                  │
│ OUTPUT: vector                              │          │ OUTPUT: vector                               │
└───────────────────────┬──────────────────────┘          └───────────────────────┬──────────────────────┘
                        │                                                         │
                        └──────────────┬──────────────────────────────────────────┘
                                       │
                                       ▼
======================================================================================================================================
                                      🧮 SAME DOWNSTREAM PATH (MODEL-AGNOSTIC)
======================================================================================================================================

                    ┌──────────────────────────────────────────────────────────────┐
                    │ VECTOR PRODUCED (IDENTICAL INTERFACE)                        │
                    │                                                              │
                    │ IF INGEST:   🟠 FACT VECTOR (stored knowledge)               │
                    │ IF QUERY:    🔵 INTENT VECTOR (live search)                  │
                    └──────────────────────────────┬───────────────────────────────┘
                                                   │
                                                   ▼
                    ┌──────────────────────────────────────────────────────────────┐
                    │ VECTOR DB / RETRIEVAL (Chroma / FAISS / etc)                │
                    │                                                              │
                    │ 🔵 query vector                                              │
                    │        vs                                                     │
                    │ 🟠 stored vectors                                             │
                    │                                                              │
                    │ → similarity search (cosine / hybrid)                        │
                    └──────────────────────────────┬───────────────────────────────┘
                                                   │
                                                   ▼
                    ┌──────────────────────────────────────────────────────────────┐
                    │ EVIDENCE RETURNED                                            │
                    │ - top K chunks                                               │
                    │ - provenance                                                 │
                    └──────────────────────────────┬───────────────────────────────┘
                                                   │
                                                   ▼
                    ┌──────────────────────────────────────────────────────────────┐
                    │ PROMPT ASSEMBLY                                              │
                    │ - slot evidence                                              │
                    │ - enforce grounding                                          │
                    └──────────────────────────────┬───────────────────────────────┘
                                                   │
                                                   ▼
                    ┌──────────────────────────────────────────────────────────────┐
                    │ DECODER LLM (GENERATION ONLY)                                │
                    │ - Claude / GPT / Gemini                                      │
                    │ - produces answer                                            │
                    └──────────────────────────────────────────────────────────────┘


======================================================================================================================================
                                      🔥 ROOT CAUSE OF YOUR CURRENT ISSUE
======================================================================================================================================

   The system is behaving like this:

   "If provider not specified → default to OpenAI"

   That violates your architecture intent:

   "If provider not specified → MUST default to BGE"


======================================================================================================================================
                                      ✅ THE FIX (WHAT YOU SHOULD DO)
======================================================================================================================================

   RULE 1:
   provider = os.getenv("AGENTIC_EMBEDDING_PROVIDER", "bge-m3")

   RULE 2:
   REMOVE all direct calls:
       openai_embeddings(...)
       OpenAIEmbeddingClient(...)

   RULE 3:
   NO SILENT FALLBACK:

        BGE FAILS
            │
            ├─► ❌ DO NOT call OpenAI automatically
            │
            └─► return controlled failure OR approved fallback path

   RULE 4:
   OPENAI ONLY IF:

        provider == "openai"
        AND explicit config
        AND audited


======================================================================================================================================
                                      🧪 WHAT “DONE RIGHT” LOOKS LIKE
======================================================================================================================================

   DEFAULT RUNTIME
   ───────────────
   text → factory → BGE → vector → retrieval → LLM
   (0 OpenAI calls)

   EXPLICIT TEST / FALLBACK
   ────────────────────────
   text → factory(provider=openai) → OpenAI → vector

   FAILURE CASE
   ────────────
   BGE down → return error / escalate
   NOT → silently switch to OpenAI


======================================================================================================================================
                                      🧠 WHY THIS MATTERS (ARCHITECTURALLY)
======================================================================================================================================

   Embedding = ENCODER phase (retrieval)
   Generation = DECODER phase (LLM)

   Mixing providers silently breaks:
   - determinism
   - cost control
   - latency predictability
   - evaluation consistency

   Your system is designed so:

      encoder (BGE) → retrieval → decoder (LLM)

   NOT:

      encoder (sometimes OpenAI, sometimes BGE randomly)


======================================================================================================================================
                                             FINAL TRUTH
======================================================================================================================================

   BGE does NOT depend on OpenAI.
   Your code path does.

   Fix the provider routing, and OpenAI disappears from production.
======================================================================================================================================