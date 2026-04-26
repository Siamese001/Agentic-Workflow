========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical folder: C0_Context_Engine
Canonical file: Anthropic Contextual Retrieval Architecture.md
Overwrite mode: full-file, no-overlap, implementation-grade, source-refreshed
Source refreshed from: Anthropic Contextual Retrieval Architecture.md
Owner summary: C0 retrieval/evidence engine. Owns retrieval planning, fetch/hydration, graph expansion, shaping, verification, evidence contract, and weak-support refinement. Does not answer or assemble prompts.

GLOBAL NO-OVERLAP LAW
- 00A L5 owns governance certification evidence, not live runtime dispositions and not durable write admission.
- 00B L4/UWG owns durable system-of-record state and durable write admission, not planning, routing, retrieval, execution, Exit disposition, or L6 learning mechanics.
- 00C Runtime Gates owns G01-G29 current-run GateVerdict law, not final Exit X3 aggregation and not L5 certification evidence.
- 00X owns traceability and no-loss mapping only.
- 01 Intake owns request envelope validation and identity/session/tenant baseline only.
- 02 L1 owns advisory interpretation and planning only.
- 03 L0/L3 owns deterministic route selection and optional workflow orchestration only.
- C0 owns retrieval/evidence contracts only.
- PA owns prompt packet construction only.
- 04 L2 owns bounded execution and sealing only.
- 05 Exit owns current-run checkout aggregation and exactly one X3 disposition only.
- 06 L6 owns completed-run evaluation, RCA, and future-run learning proposals only.
- 99 owns proof harnesses only; it does not own runtime behavior.

REFERENCE POINTERS
- Cross-cutting governance/certification evidence: 00A_L5_Governance_Safety/
- Durable state and Universal Write Gateway: 00B_L4_State_Archive_and_UWG/
- Current-run reusable gate mesh: 00C_Runtime_Gates_Current_Run_Mesh/
- Traceability and zero-loss proof: 00X_Requirements_Traceability_and_No_Loss_Map.md
- End-to-end runtime proof harness: 99_End_to_End_Runtime_Proof_and_Acceptance/
========================================================================================================================

Bottom line: **ADR-045 adds a Claude-powered contextualization lane inside offline ingestion, not inside normal runtime retrieval or generation.**

```text
================================================================================================================
                         ADR-045 CONTEXTUAL RETRIEVAL ARCHITECTURE
================================================================================================================

                                      OFFLINE / PRE-RUNTIME INGEST
                                      "Stock the shelves better"
                                      Requires ANTHROPIC_API_KEY only
                                      when Claude gateway is enabled
----------------------------------------------------------------------------------------------------------------

        📄 Source Docs / Code / Logs
                  │
                  │ raw text
                  ▼
        ┌──────────────────────────────┐
        │ 1. CHUNK + METADATA          │
        │ - split parent docs          │
        │ - preserve headings/path     │
        │ - attach source lineage      │
        └──────────────┬───────────────┘
                       │
                       │ chunk + parent context
                       ▼
        ┌──────────────────────────────────────────────────────────────────────────────┐
        │ 2. CONTEXTUAL CHUNK BUILDER                                                  │
        │ Decision: can we call Anthropic gateway?                                      │
        └──────────────┬───────────────────────────────────────────────┬───────────────┘
                       │                                               │
        ANTHROPIC_API_KEY set                              ANTHROPIC_API_KEY missing
                       │                                               │
                       ▼                                               ▼
        ┌──────────────────────────────┐                 ┌──────────────────────────────┐
        │ 2A. CLAUDE GATEWAY PATH      │                 │ 2B. HEURISTIC FALLBACK PATH  │
        │ - call claude-haiku-4-5      │                 │ - use headings/metadata      │
        │ - generate 50-100 token      │                 │ - synthetic context string   │
        │   narrative per chunk        │                 │ - no external API cost       │
        │ - real contextual retrieval  │                 │ - useful baseline only       │
        └──────────────┬───────────────┘                 └──────────────┬───────────────┘
                       │                                                │
                       └──────────────────────┬─────────────────────────┘
                                              │
                                              ▼
        ┌──────────────────────────────────────────────────────────────────────────────┐
        │ 3. ENRICHED CHUNK                                                            │
        │ contextual_prefix + original_chunk + metadata + lineage                       │
        │                                                                                │
        │ Example shape:                                                                 │
        │ "This chunk is from ADR-045 and explains why Anthropic contextual retrieval..."│
        │ + original chunk text                                                          │
        └──────────────────────────────┬───────────────────────────────────────────────┘
                                       │
                                       ▼
        ┌──────────────────────────────┐
        │ 4. ENCODER / EMBEDDING MODEL │
        │ - turns enriched chunk into  │
        │   🟧 fact vector              │
        └──────────────┬───────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────────────────────────────────────────────┐
        │ 5. L4 READ SHELVES / VECTOR DB                                                │
        │ - stores contextualized fact vectors 🟧                                        │
        │ - stores lexical/BM25 index if enabled                                        │
        │ - stores lineage/source pointers                                              │
        └──────────────────────────────────────────────────────────────────────────────┘


================================================================================================================
                                           RUNTIME RETRIEVAL
                                           "Ask the shelves a question"
                                           Does NOT require ANTHROPIC_API_KEY
----------------------------------------------------------------------------------------------------------------

        👤 User Request
             │
             ▼
        ┌──────────────────────────────┐
        │ U0 / INTAKE                  │
        │ - validate envelope          │
        │ - start trace_root           │
        └──────────────┬───────────────┘
                       ▼
        ┌──────────────────────────────┐
        │ L1 REASONING / PLAN          │
        │ - interpret ask              │
        │ - draft plan                 │
        │ - propose grounding if needed│
        └──────────────┬───────────────┘
                       ▼
        ┌──────────────────────────────┐
        │ L0 ROUTING                   │
        │ - exact cache?               │
        │ - semantic cache?            │
        │ - grounded read?             │
        │ - action/workflow?           │
        └───────┬───────────────┬──────┘
                │               │
        cache hit / fallback    │ grounded retrieval route
                │               ▼
                │       ┌──────────────────────────────┐
                │       │ C0 CONTEXT ENGINE             │
                │       │ - create 🟦 query vector       │
                │       │ - search 🟦 vs 🟧 vectors      │
                │       │ - retrieve evidence chunks    │
                │       │ - rerank / dedupe / verify    │
                │       └──────────────┬───────────────┘
                │                      ▼
                │       ┌──────────────────────────────┐
                │       │ PROMPT ASSEMBLY              │
                │       │ - system + task + evidence   │
                │       │ - citations/source anchors   │
                │       │ - bounded PromptEnvelope     │
                │       └──────────────┬───────────────┘
                │                      ▼
                │       ┌──────────────────────────────┐
                │       │ L2 EXECUTE                   │
                │       │ - call decoder/model/tool    │
                │       │ - generate answer/artifact   │
                │       │ - seal traces and receipts   │
                │       └──────────────┬───────────────┘
                │                      │
                └──────────────┬───────┘
                               ▼
        ┌──────────────────────────────┐
        │ EXIT EVAL + CONTROL          │
        │ - groundedness/support       │
        │ - policy/safety              │
        │ - allow/deny/escalate/commit │
        └──────────────┬───────────────┘
                       ▼
        ┌──────────────────────────────┐
        │ RESPONSE                     │
        └──────────────────────────────┘

                       async telemetry
                              │
                              ▼
        ┌──────────────────────────────┐
        │ L6 SHADOW EVAL / LEARNING    │
        │ - evaluate outcomes          │
        │ - RCA / drift                │
        │ - future-run promotion only  │
        └──────────────────────────────┘
```

### Where the API key sits

```text
ANTHROPIC_API_KEY
      │
      ▼
[Anthropic Context Gateway]
      │
      ▼
[Claude-generated contextual prefix]
      │
      ▼
[Contextualized chunk]
      │
      ▼
[Embedding model]
      │
      ▼
[Better 🟧 fact vector in vector DB]
```

It is **not** required for:

```text
Runtime query embedding  🟦
Vector DB search         🟦 vs 🟧
Cross-encoder rerank
Prompt assembly
L2 answer generation unless L2 itself is using Anthropic as the answer model
L6 evaluation unless the eval model is Anthropic
```

### Clean mental model

```text
WITHOUT ADR-045
Doc chunk ──► Embedding ──► 🟧 Vector DB
              "This chunk alone must carry enough meaning."

WITH ADR-045
Parent doc + chunk ──► Claude writes context prefix ──► Enriched chunk ──► Embedding ──► 🟧 Vector DB
                       "This chunk now carries its local text plus where it belongs."
```

Your current source docs already separate this correctly: ingestion creates **orange fact vectors**, runtime retrieval creates **blue intent vectors**, and generation happens downstream after evidence and prompt assembly are complete.  C5 also frames this as offline catalog build into L4 shelves, then runtime C0 retrieval and prompt assembly before L2 execution.

---

## As-shipped implementation (2026-04-24 amendment)

The architecture described above is accurate, but the **default backend** in this repo is **local Qwen 2.5-14B-Instruct-AWQ via vLLM** — not paid Claude. The technique (chunk-prefix contextualization) is unchanged; only the LLM that writes the 50-100 token prefix differs. Per ADR-045's 2026-04-24 amendment, Claude Haiku is available as an opt-in backend (`CONTEXT_GATEWAY=anthropic`) but not required.

### Shipped gateway selection

```text
CONTEXT_GATEWAY env var    Backend chain
─────────────────────────  ───────────────────────────────────────────────
unset / "auto" (default)   Qwen vLLM → Anthropic (if key) → heuristic
"qwen"                     Qwen vLLM only ($0 guarantee, no paid fallback)
"anthropic"                Anthropic only (paid — matches original ADR)
"heuristic" / "off"        Skip all LLMs; force metadata-only fallback
```

Both gateways implement the same `_GatewayProtocol.generate(...)` contract declared in `tools/ingestion/contextual_chunk_builder.py`. Selection lives in `tools/ingestion/ingest_code.py::_build_context_gateway`. Reachability probe (`GET {VLLM_BASE_URL}/models`, 2s timeout) decides whether the Qwen gateway is instantiated — unreachable server yields `None` and the builder falls back cleanly to heuristic.

### Why local-first (two-sentence version)

Claude Haiku produces excellent situated contexts, but at $5-$50 per full-repo re-index the paid path is economically unattractive for the iterate-and-A/B workflow this repo encourages. Qwen 2.5-14B-AWQ on 32 GB of local VRAM clears the quality bar for situated-context generation (which is faithful paraphrase, not frontier reasoning) and brings per-chunk cost to zero.

### Diagram update

```text
WITH ADR-045 (as shipped 2026-04-24)
Parent doc + chunk ──► Qwen vLLM writes context prefix (default)
                   └─► Claude writes context prefix (opt-in, CONTEXT_GATEWAY=anthropic)
                   └─► Heuristic metadata stamp (fallback when no LLM available)
                        ──► Enriched chunk ──► Embedding ──► 🟧 Vector DB
```

### See also

- `docs/architecture/adr/ADR-045-contextual-retrieval.md` — normative decision, amendment, backend selection matrix
- `tools/ingestion/qwen_context_gateway.py` — default gateway adapter (local, free)
- `tools/ingestion/anthropic_context_gateway.py` — opt-in paid gateway adapter
- `agentic_core/L3_orchestration/inference/qwen_vllm/reasoning/qwen_inference_gateway.py` — sanctioned L3 vLLM gateway the default path routes through
- `agentic_core/L0_routing/config/model_registry.py` — SSOT for `QWEN_LOCAL_MODEL_ID` and `VLLM_BASE_URL`
