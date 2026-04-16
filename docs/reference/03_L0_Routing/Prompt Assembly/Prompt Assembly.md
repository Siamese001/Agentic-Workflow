│ 🔵 Ingress: Query Intent Vector
                         │ 🟠 Ingress: Cited Raw Text Chunks
                         │ 🟢 Ingress: Entity Subgraph
                         │ 📄 Ingress: [Evidence Contract]
                         ▼
==========================================================================================
[PA] PROMPT ASSEMBLY - EXPLODED ARCHITECTURE
==========================================================================================

  ┌─────────────────────────────────────────────┐       ┌────────────────────────────────┐
  │ [PA.1] LOAD: SYSTEM TEMPLATE & SCHEMA       │       │ [ L4 STATE / DATA STORES ]     │
  │  ├─► Fetch Persona / System Prompt          │◄──────┼──►│ [DB] SYSTEM TEMPLATES      │
  │  ├─► Load Expected Output Schema (JSON/XML) │◄──────┼──►│ [DB] OUTPUT SCHEMAS        │
  │  └─► Initialize Conversation History        │◄──────┼──►│ [DB] CONVO HISTORY (KV)    │
  └──────────────────────┬──────────────────────┘       └────────────────────────────────┘
                         │ (Base Framework)
                         ▼
  ┌─────────────────────────────────────────────┐
  │ [PA.2] SLOT: INJECT CONTEXT & GUARDRAILS    │
  │  ├─► Inject 🟠 Raw Text into Context Block  │
  │  ├─► Inject 🟢 Graph Triples into Knowledge │
  │  └─► Append Contradiction / Fallback Rules  │
  └──────────────────────┬──────────────────────┘
                         │ (Draft Prompt String)
                         ▼
  ┌─────────────────────────────────────────────┐
  │ [PA.3] BUDGET: TOKEN TRIM & RESERVE         │
  │  ├─► Tokenize Draft Prompt                  │
  │  ├─► Reserve Tokens for Target Output Size  │
  │  └─► Truncate Context / Hist (FIFO) if over │
  └──────────────────────┬──────────────────────┘
                         │ (Budget-Validated Prompt)
                         ▼
  ┌─────────────────────────────────────────────┐
  │ [PA.4] EMIT: SECURE ENVELOPE GENERATION     │
  │  ├─► Compile Final Prompt Envelope          │
  │  ├─► Generate HMAC Signature for Integrity  │
  │  └─► Attach Routing Meta (Model ID, Temp)   │
  └──────────────────────┬──────────────────────┘
                         │
=========================▼================================================================
                     [SIGNED PROMPT ENVELOPE]
                         │
                         ├─► System / Persona Template
                         ├─► Bound Evidence & Graph Context
                         ├─► User Query & History
                         ├─► Model Routing Headers
                         │
                         ▼
                   [Dispatch to L2_EXECUTE / Reading Room]