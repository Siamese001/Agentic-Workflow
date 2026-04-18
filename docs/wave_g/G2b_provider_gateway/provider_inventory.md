# G2b — Provider Inventory

External providers, local-only stubs, and the canonical gateway / router surfaces that bind them.

**ADG snapshot**: `artifacts/adg/adg_indexed_04172026_0611.sqlite` (04172026_0611).

## 1. Headline inventory

| # | Provider | Kind | Wrapper module | Canonical caller | SDK import sites |
|---|---|---|---|---|---:|
| P01 | **OpenAI** (chat, embeddings) | external https | `infrastructure/sdks_mcps/__init__.py::create_openai_client` (+sync variant) | `SovereignLLMGateway` / `ModelRouter` / `EmbeddingSovereignAgent` | 2 (`import openai`) |
| P02 | **Anthropic** (Claude) | external https | `infrastructure/sdks_mcps/__init__.py::create_anthropic_client` | `SovereignLLMGateway` / `ModelRouter` | 2 (`import anthropic`) |
| P03 | **Google GenAI / Gemini** (chat, embeddings) | external https | `apps_shared/utils/providers_google_genai_client_util.py`, `infrastructure/sdks_mcps/__init__.py::create_vertex_client`, `apps_shared/types/hardened_gemini_executor_types.py` | `SovereignLLMGateway` / `ModelRouter` / `EmbeddingSovereignAgent` / LLM judge | 3 (`import google.generativeai`) |
| P04 | **Google Custom Search** | external https | `apps_lic/tools/GoogleSearchClient.py` | APP-LIC only | 1 (`googleapiclient.discovery.build`) |
| P05 | **HuggingFace Hub** (embedding weights) | external https (gated) | `tools/retrieval/embedder.py` via `sentence_transformers.SentenceTransformer` | `vector_db` MCP server; `agentic_core/embeddings/` local fallback | 1 (`sentence_transformers` import chain) |
| P06 | **Qwen vLLM** (local inference) | localhost http | `agentic_core/L3_orchestration/inference/qwen_vllm/engines/optimized_vllm_client.py` + `hardened_vllm_client.py` | `qwen_inference_gateway.py` → 6 apps | 1 (`import aiohttp`) |
| P07 | **Redis** (cache + state) | localhost tcp | `agentic_core/cache/redis_cache_client.py` + `tools/mcp/redis_mcp/` | `RedisSovereignAgent`, `sovereign_redis_orchestrator`, `CachedStateLedger`, `semantic_cache_manager`, memory MCP, ADG ingest | 19 (`import redis`) |
| P08 | **Neo4j** | localhost bolt | `agentic_core/L4_state/enforcement/neo4j_store.py` | L4 graph-memory bridge | 1 (`from neo4j`) |
| P09 | **ChromaDB** (embedded local) | embedded sqlite/duckdb | `tools/retrieval/vector_store.py` + `agentic_core/L4_state/utils/client/chroma_client.py` | retrieval_layers, semantic_retriever, hybrid_search_engine, vector_db MCP | 39 (`import chromadb`) — **excluded from egress_points.yaml: embedded, not network** |
| P10 | **OTel collector** (spans) | external http/grpc (optional) | `apps_shared/utils/open_telemetry_tracing_adapter_util.py` | observability adapters | 0 `opentelemetry-sdk` direct; env-driven only |
| P11 | **Pinecone** (declared, not imported) | external https (stub) | none | none | **0** (`import pinecone` → zero matches) — B7-G2b-02 |
| P12 | **deepwiki MCP** (external) | external https | `.windsurf/mcp_config.json` entry only | Cascade IDE client | — |

## 2. Canonical gateway and router surfaces

### 2.1 `SovereignLLMGateway` (L2 enforcement)

- Path: `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py` (769 lines).
- Intended **sole outbound seam** for LLM provider calls.
- `class ProviderType(Enum)`: `OPENAI | ANTHROPIC | VERTEX_AI | AZURE_OPENAI | LOCAL_VLLM`.
- Features documented inline: signature verification for `CompiledPromptArtifact`, provider abstraction, telemetry ledger.
- Retry posture: `retries: int = 3` (default).
- Secret binding: reads `LLM_GATEWAY_SECRET` env key.
- **Not all provider calls route through here.** Direct SDK calls exist in:
  - `apps_shared/utils/providers_google_genai_client_util.py` (documented as "ONLY place where google.generativeai is imported" — narrow `run_llm` interface).
  - `infrastructure/sdks_mcps/__init__.py` (migration wrappers).
  - `apps_shared/types/hardened_gemini_executor_types.py` (tenacity-wrapped Gemini).
  - `apps_shared/types/model_router_types.py` (router imports `openai`, `anthropic` directly).

### 2.2 `ModelRouter` (apps_shared)

- Path: `apps_shared/types/model_router_types.py` (858 lines).
- Dynamic provider selection by `TaskComplexity` + budget.
- Retry posture: `retries: int = 3`.
- Decision surface: data-driven (rule / threshold / budget). Static analysis cannot enumerate every dispatch branch — recorded as dynamic selection, G3 should expand per-task.

### 2.3 `MultiProviderRouterAgent` (L5 guardrail)

- Path: `agentic_core/L5_safety/guardrails/multi_provider_router_agent.py` (per migration note in `infrastructure/sdks_mcps/__init__.py` line 39).
- Acts as a guardrailed router wrapping provider selection with L5 policy checks.
- Records the crossing of the admission spine (per G2 `canonical_request_walk.md` Stage 1).

### 2.4 `EmbeddingSovereignAgent` (L2 reasoning)

- Path: `agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py` (588 lines).
- Unified embedding gateway: Gemini, OpenAI, dimension validation, batch + Redis caching.
- Env-key consumers: `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `EMBEDDING_MODEL_ID`, `EMBEDDING_LOCAL_FILES_ONLY`, `EMBEDDING_DIMENSION`, `EMBEDDING_ENABLED`.

### 2.5 `agentic_core/gateway/api_gateway_integration.py`

- **Ingress-side gateway integration**, NOT provider egress.
- 822 lines wrapping Kong / Envoy / AWS API Gateway / NGINX / Traefik / Custom.
- Direct `import requests` for admin-API health checks (the only non-SovereignLLMGateway repo use of `requests` for anything that touches network — see B7-G2b-04).
- Does not originate LLM calls.

## 3. `agentic_core/embeddings/` — local embedding runtime

| Module | Purpose |
|---|---|
| `embedding_factory.py` | factory for embedding backends |
| `model_loader.py` | loads model weights (file path based) |
| `bge_runtime.py` | BAAI/bge-m3 runtime |
| `forward_pass.py`, `pipeline.py`, `tokenizer.py`, `tokenization_adapter.py`, `embedding_input_guard.py` | in-process embedding stack |

- Consumes HF model via `sentence_transformers` in `tools/retrieval/embedder.py`.
- Offline-by-default (`HF_HUB_OFFLINE=1` per `mcp_config.json`).
- External egress only if `VECTOR_DB_ALLOW_MODEL_DOWNLOAD=1` (default `0`). Captured in env-key map with severity note.

## 4. Retry and circuit-breaker posture

| Module | retry | backoff | circuit breaker | source |
|---|---|---|---|---|
| `SovereignLLMGateway` | 3 (default) | not set | not set | explicit `retries: int = 3` |
| `ModelRouter` | 3 (default) | not set | not set | explicit `retries: int = 3` |
| `hardened_vllm_client.py` | yes, configurable | exponential with jitter | **yes** (`CircuitBreakerConfig`) | docstring + `CircuitState` enum |
| `hardened_gemini_executor_types.py` | yes | exponential (`wait_exponential`) | **yes** (circuit breaker inline) | `tenacity.retry` decorator |
| `qwen_inference_gateway.py` | delegated to `OptimizedVLLMClient` / `hardened` variant | same as above | same | |
| `GoogleSearchClient` | no inline retry | — | **yes** (injected `CircuitBreakerProtocol`) | `__init__` signature |
| `api_gateway_integration.py` (ingress) | `retry_attempts: int = 3` | not set | not set | `GatewayConfig.retry_attempts` |
| `create_openai_client` / `create_anthropic_client` / `create_vertex_client` (migration wrappers) | none | — | — | bare SDK construction |
| `agentic_core/cache/redis_cache_client.py` | **unknown** | — | — | not enumerated here — G6 to verify |
| `agentic_core/L4_state/enforcement/neo4j_store.py` | **unknown** | — | — | B7-G2b-05 |
| `tools/mcp/http_mcp/client.py` (enhanced_http MCP) | default 3 (tool param) | per-client | no | tool signatures show `retries: int = 3` |

## 5. Real external egress vs MCP loopback vs local-only

| Class | Examples | egress_points.yaml ID prefix |
|---|---|---|
| **Real external egress** | OpenAI, Anthropic, Google GenAI, Google CSE, HF Hub, OTel collector (optional) | `EGRESS-OPENAI-*`, `EGRESS-ANTHROPIC-*`, `EGRESS-GEMINI-*`, `EGRESS-GOOGLE-CSE-*`, `EGRESS-HF-HUB-*`, `EGRESS-OTEL-*` |
| **Localhost / internal egress** | Qwen vLLM, Redis, Neo4j | `EGRESS-QWEN-VLLM-LOCAL-*`, `EGRESS-REDIS-*`, `EGRESS-NEO4J-*` |
| **MCP loopback transport** | adg_sqlite, memory, vector_db, otel_mcp, redis MCP, pytest_mcp, enhanced_http, filesystem, notion, task_manager | `MCP-LOOPBACK-*` (catalogued in `mcp_as_transport.md`) |
| **Embedded local (no network)** | ChromaDB, SQLite (ADG, memory), in-process memory caches | **not in egress_points.yaml** (G4 owns) |
| **Config stub (declared, not wired)** | Pinecone | `EGRESS-PINECONE-STUB-01` (severity=stub) |

## 6. Disambiguation of G2 findings

### 6.1 `agentic_core/interfaces/gateway.py` (G2 live interface subset)

Per G2 `seam_usage_report.md`, `interfaces/gateway.py` is one of the 3 live interface modules (imported by 2 apps + core). It is **not** a provider-egress gateway — it is the ingress-side gateway-integration protocol surface (the `GatewayClient` ABC in `agentic_core/gateway/api_gateway_integration.py` implements this interface for Kong / Envoy / etc.). Recorded here to prevent confusion; egress providers live in `SovereignLLMGateway` and per-provider wrappers.

### 6.2 `cache/redis_cache_client.py` bridge chokepoint

G2 `boundary_violations.md` recorded this as the single largest external-dependency bridge (fan_in=fan_out=70). In G2b, this module is the dominant consumer of `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`. Classified as `EGRESS-REDIS-01` with auth mode `password_env` (optional; Redis may be unauthenticated in dev).

### 6.3 App → L3 `qwen_vllm` (6 apps, 30 edges)

All 6 apps import from `agentic_core.L3_orchestration.inference.qwen_vllm`. The actual network call is in `optimized_vllm_client.py` (`aiohttp`) against a **localhost** vLLM endpoint. Egress ID `EGRESS-QWEN-VLLM-LOCAL-01`.

## 7. App → L4 `vllm_routing_predicates` (5 apps, 22 edges) — NOT egress

`agentic_core/L4_state/config/vllm_routing_predicates.py` exposes configuration predicates (rule data) used to *decide* whether to route to vLLM. It does not itself make network calls. Classified as **configuration coupling, not egress**. Carried forward to G4b as B7-G2b-01.

## 8. Dynamic-provider-selection surfaces

Per G2 §Class 3, three app-side sites use `importlib.import_module` in a way that may affect provider wiring:

| Site | Purpose |
|---|---|
| `apps_eval/integrations/governed_eval_exception.py` | dynamic handler load for governed exception routing |
| `apps_research/__main__.py` | dynamic runner selection at entry point |
| `apps_underwriting_ai/integrations/governed_uw_exception.py` | same pattern as eval |

None of these three directly selects a provider (OpenAI vs Anthropic vs Gemini). They select handlers that later call the canonical gateway. Dynamic provider selection proper lives inside `ModelRouter` — data-driven, not `importlib`-driven. Recorded here so G3 pipeline tracing does not mistake these for provider dispatch.

Additional static-dispatch registries containing runtime `importlib` per G2 scan (not app-side): `agentic_core/L2_execution/utils/static_dispatch_registry.py`, `agentic_core/L3_orchestration/reasoning/AgentFactory.py`, `agentic_core/L3_orchestration/reasoning/engines/orchestrator_engine.py`. These dispatch agents, not providers.

## 9. `.env` file

The repo uses a `.env` loader (`agentic_core/config/env_loader.py::SovereignEnv`) backed by `python-dotenv`. It loads from `<project_root>/.env`. G2b documents only env-key **names** that the loader and application code read — never values. `.env` is git-ignored.

## 10. Summary

- **12 egress points** catalogued (6 external, 3 localhost, 1 optional external, 1 stub, 1 local-embedded reclassification).
- **4 canonical gateway / router surfaces**: `SovereignLLMGateway`, `ModelRouter`, `MultiProviderRouterAgent`, `EmbeddingSovereignAgent`.
- **Retry + circuit-breaker posture**: strong for vLLM and Gemini hardened executor; default `retries=3` for SovereignLLMGateway and ModelRouter; unknown for Redis client and Neo4j store.
- **No raw SDK call exists outside** `infrastructure/sdks_mcps/__init__.py` **and the 3 `apps_shared` utility / type modules** for OpenAI, Anthropic, Google GenAI.
