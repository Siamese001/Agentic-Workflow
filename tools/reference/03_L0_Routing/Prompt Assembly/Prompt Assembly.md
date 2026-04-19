│ 🔵 Ingress: Query Intent Vector
                         │ 🟠 Ingress: Cited Raw Text Chunks
                         │ 🟢 Ingress: Entity Subgraph
                         │ 📄 Ingress: [Evidence Contract]
                         ▼
================================================================================================
[PA] PROMPT ASSEMBLY - EXPLODED ARCHITECTURE
================================================================================================

  ┌───────────────────────────────────────────────┐       ┌────────────────────────────────┐
  │ [PA.1] LOAD: SYSTEM TEMPLATE & SCHEMA         │       │ [ L4 STATE / DATA STORES ]     │
  │  ├─► Fetch Persona / System Prompt            │◄──────┼──►│ [DB] SYSTEM TEMPLATES      │
  │  │   ├─► Resolve dynamic persona variables    │       │   │                            │
  │  │   └─► Inject baseline safety instructions  │       │   │                            │
  │  ├─► Load Expected Output Schema (JSON/XML)   │◄──────┼──►│ [DB] OUTPUT SCHEMAS        │
  │  │   ├─► Validate syntax via JSONSchema spec  │       │   │                            │
  │  │   └─► Embed constraints into system block  │       │   │                            │
  │  └─► Initialize Conversation History          │◄──────┼──►│ [DB] CONVO HISTORY (KV)    │
  │      ├─► Fetch last N turns from state DB     │       │   │                            │
  │      └─► Compress multi-turn history contexts │       │   │                            │
  └──────────────────────┬────────────────────────┘       └────────────────────────────────┘
                         │ (Base Framework)
                         ▼
  ┌───────────────────────────────────────────────┐
  │ [PA.2] SLOT: INJECT CONTEXT & GUARDRAILS      │
  │  ├─► Inject 🟠 Raw Text into Context Block    │
  │  │   ├─► Apply semantic reranking to chunks   │
  │  │   └─► Format with explicit citation tags   │
  │  ├─► Inject 🟢 Graph Triples into Knowledge   │
  │  │   ├─► Serialize Entity Subgraph to text    │
  │  │   └─► Filter orphaned nodes via intent     │
  │  └─► Append Contradiction / Fallback Rules    │
  │      ├─► Inject hallucination mitigations     │
  │      └─► Set default zero-evidence responses  │
  └──────────────────────┬────────────────────────┘
                         │ (Draft Prompt String)
                         ▼
  ┌───────────────────────────────────────────────┐
  │ [PA.3] BUDGET: TOKEN TRIM & RESERVE           │
  │  ├─► Tokenize Draft Prompt                    │
  │  │   ├─► Select model-specific tokenizer      │
  │  │   └─► Calculate static/dynamic token size  │
  │  ├─► Reserve Tokens for Target Output Size    │
  │  │   ├─► Calc Max = Model Limit - Input size  │
  │  │   └─► Enforce minimum safety buffer tokens │
  │  └─► Truncate Context / Hist (FIFO) if over   │
  │      ├─► P1: Evict oldest convo history turns │
  │      └─► P2: Drop lowest-ranked evidence text │
  └──────────────────────┬────────────────────────┘
                         │ (Budget-Validated Prompt)
                         ▼
  ┌───────────────────────────────────────────────┐
  │ [PA.4] EMIT: SECURE ENVELOPE GENERATION       │
  │  ├─► Compile Final Prompt Envelope            │
  │  │   ├─► Assemble system/context/user roles   │
  │  │   └─► Stringify to target Messages array   │
  │  ├─► Generate HMAC Signature for Integrity    │
  │  │   ├─► Hash payload to prevent tampering    │
  │  │   └─► Append crypto nonce for idempotency  │
  │  └─► Attach Routing Meta (Model ID, Temp)     │
  │      ├─► Set dynamic hyperparams (Temp, TopP) │
  │      └─► Target specific L2 inference API URI │
  └──────────────────────┬────────────────────────┘
                         │
=========================▼======================================================================
                     [SIGNED PROMPT ENVELOPE]
                         │
                         ├─► System / Persona Template
                         ├─► Bound Evidence & Graph Context
                         ├─► User Query & History
                         ├─► Model Routing Headers
                         │
                         ▼
                   [Dispatch to L2_EXECUTE / Reading Room]