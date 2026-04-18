# G4b — Defaults and Reload Policy

ADG snapshot: `artifacts/adg/adg_indexed_04172026_0611.sqlite` (04172026_0611).

This document records only defaults directly observable in source code or `.windsurf/mcp_config.json` env blocks. If not observable, value is `unknown`.

## 1. Reload behavior taxonomy

- `import_time`: value captured into module-level constants at import and effectively frozen.
- `process_start`: value loaded during service/client/server initialization and not refreshed automatically.
- `per_call`: value read inside request/execution path each call.
- `lazy_first_use`: value read once on first singleton/client construction, then reused.
- `unknown`: read site could not be proven in this wave.

## 2. Import-time knobs (highest drift risk)

| Key | Observable default | Reader | Reload behavior | Impact |
|---|---|---|---|---|
| `VECTOR_DB_CHROMA_PATH` | `${REPO_ROOT}/data/cache/chromadb` | `tools/retrieval/vector_config.py` | `import_time` | selects `STORE-CHROMA-CANONICAL` |
| `VECTOR_DB_EMBEDDING_MODEL` | `BAAI/bge-m3` | `tools/retrieval/vector_config.py` | `import_time` | embedding provider path |
| `VECTOR_DB_ALLOW_MODEL_DOWNLOAD` | `0` | `tools/retrieval/vector_config.py` | `import_time` | HF egress gate |
| `VECTOR_DB_DEVICE` | `cpu` | `tools/retrieval/vector_config.py` | `import_time` | runtime backend mode |
| `VECTOR_DB_MODEL_LOAD_TIMEOUT` | `120` | `tools/retrieval/vector_config.py` | `import_time` | model boot budget |
| `VECTOR_DB_CHROMA_INIT_TIMEOUT` | `30` | `tools/retrieval/vector_config.py` | `import_time` | Chroma init budget |
| `VECTOR_DB_ENCODE_TIMEOUT` | `20` | `tools/retrieval/vector_config.py` | `import_time` | encode budget |
| `VECTOR_DB_ENCODE_QUEUE_WAIT_TIMEOUT` | `20` | `tools/retrieval/vector_config.py` | `import_time` | queue wait budget |
| `VECTOR_DB_QUERY_COLLECTION_TIMEOUT` | `40` | `tools/retrieval/vector_config.py` | `import_time` | per-collection query budget |
| `VECTOR_DB_SEARCH_PER_COLLECTION_TIMEOUT` | `20` | `tools/retrieval/vector_config.py` | `import_time` | search phase budget |
| `VECTOR_DB_SEARCH_GLOBAL_TIMEOUT` | `60` | `tools/retrieval/vector_config.py` | `import_time` | global search budget |
| `VECTOR_DB_COUNT_CACHE_TTL` | `60` | `tools/retrieval/vector_config.py` | `import_time` | cache retention window |
| `VECTOR_DB_ENABLE_STARTUP_PREWARM` | `1` | `tools/retrieval/vector_config.py` | `import_time` | bootstrap branch |
| `VECTOR_DB_MAX_QUERY_RESULTS` | `100` | `tools/retrieval/vector_config.py` | `import_time` | result cap |
| `VECTOR_DB_MAX_BATCH` | `32` | `tools/retrieval/vector_config.py` | `import_time` | batch sizing |
| `VECTOR_DB_MAX_SEARCH_RESULTS` | `20` | `tools/retrieval/vector_config.py` | `import_time` | result cap |
| `USE_REDIS_CACHE` | `true` | `agentic_core/config/constants_config.py` | `import_time` | cache branch selection |
| `GRACEFUL_DEGRADATION` | `true` | `agentic_core/config/constants_config.py` | `import_time` | failure-mode behavior |
| `CACHE_METRICS_ENABLED` | `false` | `agentic_core/config/constants_config.py` | `import_time` | observability-only |

## 3. Process-start knobs

| Key | Observable default | Reader | Reload behavior | Impact |
|---|---|---|---|---|
| `MEMORY_DB` | `${REPO_ROOT}/artifacts/memory/knowledge_graph.sqlite` | `tools/memory/adg_memory_server.py`, `sqlite_memory_store.py`, `purge_sync.py` | `process_start` | binds memory store (`STORE-MEMORY-SQLITE-*`) |
| `ADG_REDIS_URL` | `redis://localhost:6379/0` | `tools/adg/adg_redis_ingest.py`, `tools/adg/core/service.py`, `tools/memory/adg_memory_server.py` | `process_start` | binds ADG Redis cache |
| `REDIS_HOST` | `localhost` | `tools/mcp/redis_mcp/config.py` (+ core redis clients) | `process_start` | binds Redis endpoints |
| `REDIS_PORT` | `6379` | `tools/mcp/redis_mcp/config.py` | `process_start` | binds Redis endpoints |
| `REDIS_DB` | `0` | `tools/mcp/redis_mcp/config.py` | `process_start` | DB partition |
| `REDIS_TIMEOUT` | `5` | `tools/mcp/redis_mcp/config.py` | `process_start` | connection budget |
| `AGENT_TIMEOUT_SECONDS` | `300` | `agentic_core/config/constants_config.py` | `process_start` | runtime timeout budget |
| `MISSION_TIMEOUT_SECONDS` | `3600` | `agentic_core/config/constants_config.py` | `process_start` | runtime timeout budget |
| `OTEL_MCP_MAX_TRACE_CACHE` | `256` | `tools/otel/otel_config.py` | `process_start` | in-memory trace cache |
| `OTEL_MCP_ALLOW_MOCK_TRACES` | `0` | `tools/otel/otel_config.py` | `process_start` | test/mock branch |
| `OTEL_EXPORTER_OTLP_HTTP_ENDPOINT` | `http://localhost:4318` | `apps_shared/utils/open_telemetry_tracing_adapter_util.py` | `process_start` | optional external sink |
| `OTEL_EXPORTER_OTLP_GRPC_ENDPOINT` | `http://localhost:4317` | same | `process_start` | optional external sink |

## 4. Per-call / lazy-first-use knobs

| Key | Reader | Reload behavior | Notes |
|---|---|---|---|
| `EGRESS_GUARD_DISABLED` | `network_egress_guard.py` checks on guard install and per egress check | `per_call` | immediate effect; policy bypass |
| `DISABLE_RUNTIME_MUTATION_GUARD` | `RuntimeMutationGuard.install()` | `per_call` | immediate effect when install invoked |
| `SOVEREIGN_AUTO_APPROVE` | `archival_gatekeeper_gate.py` `_is_batch_mode`, `_request_approval` | `per_call` | immediate destructive-op bypass in archival gate only |
| `ARCHIVE_BATCH_ACCEPT` | same | `per_call` | same bypass class |
| `LLM_GATEWAY_SECRET` | `SovereignLLMGateway.get_llm_gateway()` singleton path | `lazy_first_use` | read once at singleton creation |
| `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `GEMINI_API_KEY` | provider client constructors | `lazy_first_use` | typically read during provider initialization |

## 5. MCP-injected env (not read by repo process directly)

From `.windsurf/mcp_config.json` env blocks:

| Key | MCP server(s) | Reload behavior | Runtime consequence |
|---|---|---|---|
| `ADG_DIR` | `adg_sqlite` | `process_start` | controls ADG sqlite search root for MCP queries |
| `MEMORY_DB` | `memory` MCP | `process_start` | controls memory sqlite path inside MCP subprocess |
| `VECTOR_DB_*`, `HF_HUB_OFFLINE`, `TOKENIZERS_PARALLELISM` | `vector_db` MCP | `process_start` | controls vector service behavior for MCP tool calls |
| `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, `REDIS_TIMEOUT` | `redis` MCP | `process_start` | redis MCP endpoint binding |
| `NOTION_TOKEN` | `notion` MCP | `process_start` | Notion auth only; no repo runtime branch change |
| `AGENTIC_REPO_ROOT`, `PYTHONPATH`, `PYTHONUNBUFFERED` | python MCPs | `process_start` | module resolution + process behavior |

## 6. Biggest default/reload ambiguities

1. `REDIS_URL` has multiple readers in core/L4 orchestrator paths with no single observable fallback default in those modules.
2. `BGE_ALLOW_MODEL_DOWNLOAD` is referenced by readers in env map, but direct default fallback is not uniformly observable.
3. Provider model keys (`OPENAI_MODEL`, `ANTHROPIC_MODEL`, `GEMINI_MODEL`) are present in env map but defaults are often layered through config objects, not direct `os.getenv(..., default)` fallbacks.
4. Some knobs are duplicated across MCP env injection and repo readers (e.g., `MEMORY_DB`, `VECTOR_DB_CHROMA_PATH`), so effective value depends on execution path (in-process vs MCP subprocess).

## 7. Practical operator rule

If a knob is `import_time` or `process_start`, **restart the affected process/subprocess** after changing it. Only `per_call` knobs can be treated as immediate-mode toggles.
