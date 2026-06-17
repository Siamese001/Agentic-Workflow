# G2b — Env-Key Consumer Map

Every `os.getenv` / `os.environ[...]` read in `agentic_core/`, `apps_*/`, `infrastructure/`, `tools/`, mapped to consumer modules. **Names only — no values anywhere.**

**ADG snapshot**: `artifacts/adg/adg_indexed_04172026_0611.sqlite` (04172026_0611).
**Scan totals**: 269 reads, 154 unique env keys, **114 reader files**. Scan excludes `__pycache__/` and `archive/`.

## 1. Classification

| Class | Key count | Severity |
|---|---:|---|
| **Secret** (api key / password / token) | 16 | must not leak; `.env`-only |
| **Endpoint / URL** | 7 | may be sensitive in some deployments |
| **Provider / model ID** | 15 | config |
| **Toggle / feature flag** | 38 | config |
| **Tunable (timeout / budget / threshold)** | 63 | config |
| **Path override** | 15 | config |

## 2. Secrets (16 keys)

| Env key | Consumer modules | Egress binding |
|---|---|---|
| `OPENAI_API_KEY` | `infrastructure/sdks_mcps/__init__.py`, `apps_shared/types/model_router_types.py`, `agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py`, `agentic_core/L4_state/reasoning/retrieval_layers.py` | EGRESS-OPENAI-01 |
| `ANTHROPIC_API_KEY` | `infrastructure/sdks_mcps/__init__.py`, `apps_shared/types/model_router_types.py` | EGRESS-ANTHROPIC-01 |
| `GOOGLE_API_KEY` | `infrastructure/sdks_mcps/__init__.py`, `apps_shared/utils/providers_google_genai_client_util.py`, `agentic_core/evaluation/judges/provider_registry.py`, `agentic_core/L1_cognition/reasoning/codebase_mapper.py`, `agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py`, `agentic_core/L5_safety/utils/verify_semantic_meta_learning_util.py`, `agentic_core/L5_safety/validators/dependencygraph_validator.py`, `apps_lic/tools/GoogleSearchClient.py` | EGRESS-GEMINI-01 + EGRESS-GOOGLE-CSE-01 |
| `GEMINI_API_KEY` | `infrastructure/sdks_mcps/__init__.py`, `apps_shared/utils/providers_google_genai_client_util.py`, `apps_shared/types/app_config_types.py`, `agentic_core/evaluation/judges/provider_registry.py` | EGRESS-GEMINI-01 |
| `GOOGLE_CSE_ID` | `apps_lic/tools/GoogleSearchClient.py` | EGRESS-GOOGLE-CSE-01 |
| `NEO4J_USERNAME` | `agentic_core/L4_state/enforcement/neo4j_store.py`, `agentic_core/config/env_loader.py` | EGRESS-NEO4J-01 |
| `NEO4J_PASSWORD` | `agentic_core/L4_state/enforcement/neo4j_store.py`, `agentic_core/config/env_loader.py` | EGRESS-NEO4J-01 |
| `NEO4J_URI` | `agentic_core/L4_state/enforcement/neo4j_store.py`, `agentic_core/config/env_loader.py` | EGRESS-NEO4J-01 |
| `REDIS_PASSWORD` | `agentic_core/cache/redis_cache_client.py`, `agentic_core/config/env_loader.py`, `apps_shared/utils/resource_manager_types_util.py` | EGRESS-REDIS-01 |
| `REDIS_URL` | `agentic_core/L3_orchestration/reasoning/engines/sovereign_redis_orchestrator.py`, `agentic_core/L4_state/reasoning/CachedStateLedger.py`, `agentic_core/L4_state/utils/memory/semantic_cache_manager.py` | EGRESS-REDIS-01 |
| `ADG_REDIS_URL` | `tools/adg/adg_redis_ingest.py`, `tools/memory/adg_memory_server.py`, `tools/adg/core/service.py` | EGRESS-REDIS-01 (ADG bucket) |
| `PINECONE_INDEX_NAME` | `apps_shared/utils/etl_pipeline_util.py` | EGRESS-PINECONE-STUB-01 |
| `LLM_GATEWAY_SECRET` | `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py` | internal HMAC for gateway signature check |
| `AGENTIC_AUTHORITY_SECRET` | `agentic_core/runtime/engine/execution_bound_token.py` | internal authority token signing |
| `RG_VALIDATION_SECRET` | `apps_rg/validators/validation_gate_validator.py` | internal APP-RG validation signing |
| `NOTION_TOKEN` | `.mcp.json` (env block; NOT repo code) | MCP-NOTION (loopback via npx subprocess) |

## 3. Endpoint / URL (7)

| Env key | Consumer modules | Notes |
|---|---|---|
| `OTEL_EXPORTER_OTLP_HTTP_ENDPOINT` | `apps_shared/utils/open_telemetry_tracing_adapter_util.py` | optional external OTel collector |
| `OTEL_EXPORTER_OTLP_GRPC_ENDPOINT` | `apps_shared/utils/open_telemetry_tracing_adapter_util.py` | optional external OTel collector |
| `REDIS_HOST` | 7 files (`agentic_core/cache/redis_cache_client.py`, `agentic_core/config/redis_config.py`, `apps_shared/utils/resource_manager_types_util.py`, `tools/adg/queries/adg_redis_live_query.py`, `tools/adg/queries/adg_rlhf_sft_query.py`, `tools/adg/queries/adg_rlhf_sft_query2.py`, `tools/mcp/redis_mcp/config.py`) | EGRESS-REDIS-01 |
| `REDIS_PORT` | 6 files (same set minus `env_loader.py`) | EGRESS-REDIS-01 |
| `REDIS_DB` | 5 files | EGRESS-REDIS-01 |
| `REDIS_TIMEOUT` | 1 file (`tools/mcp/redis_mcp/config.py`) | EGRESS-REDIS-01 |
| `CANON_REMOTE_REPO` | 1 file | git remote override |

## 4. Provider / model ID (15)

| Env key | Consumer count | Category |
|---|---:|---|
| `OPENAI_MODEL` | 2 | OpenAI default model |
| `OPENAI_MAX_TOKENS` | 1 | OpenAI tunable |
| `OPENAI_TEMPERATURE` | 1 | OpenAI tunable |
| `ANTHROPIC_MODEL` | 2 | Anthropic default model |
| `GEMINI_MODEL` | 6 | Gemini default model |
| `GEMINI_PRO_MODEL` | 4 | Gemini pro variant |
| `EMBEDDING_MODEL_ID` | 2 | embedding backend |
| `EMBEDDING_DIMENSION` | 1 | embedding dimension sanity check |
| `EMBEDDING_ENABLED` | 4 | embedding toggle |
| `EMBEDDING_LOCAL_FILES_ONLY` | 2 | HF offline mode |
| `VECTOR_DB_EMBEDDING_MODEL` | 2 | vector DB embedding model |
| `VECTOR_DB_CHROMA_PATH` | 2 | ChromaDB root path |
| `VECTOR_DB_DEVICE` | 1 | embedding device (cpu/gpu) |
| `HIVE_MIND_EMBEDDING_MODEL_VERSION` | 1 | hive-mind embed model version |
| `HIVE_MIND_RETRIEVAL_CONFIG_HASH` | 1 | hive-mind retrieval config hash |

## 5. Toggles / feature flags (38)

Selected:

| Env key | Consumer modules (primary) | Effect |
|---|---|---|
| `EGRESS_GUARD_DISABLED` | `agentic_core/L2_execution/enforcement/network_egress_guard.py` | **disables egress guard** — severity: high. B7-G2b-06 |
| `ADG_SKIP_REDIS` | `tools/generate/generate_full_adg.py` | skip Redis ingest after ADG regen |
| `ADG_SKIP_GIT` | `tools/generate/generate_full_adg.py` | skip auto-commit after ADG regen |
| `ADG_SKIP_SELF_TEST` | ADG scanner | skip scanner self-test |
| `ADG_ENABLE_DETERMINISM_PROBE` | `tools/generate/generate_full_adg.py` | run determinism probe |
| `ADG_SCANNER_SELF_TEST` | ADG scanner | toggle self-test |
| `SEQUENTIAL_THINKING_ENABLED` | `tools/utils/planning/workflows/sequential_thinking_workflow.py` | SR_MANDATE active |
| `SEQUENTIAL_THINKING_AUTO_TRIGGER` | same | auto-trigger SR |
| `AGENTIC_ALLOW_MUTATION_FOR_TESTS` | runtime | test override |
| `DISABLE_RUNTIME_MUTATION_GUARD` | runtime | guard kill-switch — severity: high |
| `SOVEREIGN_AUTO_APPROVE` | 2 files | auto-approve governance |
| `CACHE_METRICS_ENABLED` | cache | metrics toggle |
| `GRACEFUL_DEGRADATION` | 1 | graceful degrade toggle |
| `TRACE_ENABLED` | 1 | trace toggle |
| `V15_ENFORCEMENT` | 2 | v15 enforcement switch |
| `V15_TEST_SIGNING` | 1 | signing test mode |
| `HF_HUB_OFFLINE` | 6 | HF offline mode |
| `TOKENIZERS_PARALLELISM` | 5 | HF tokenizer parallelism |
| `TQDM_DISABLE` | 6 | disable tqdm bars |
| `USE_REDIS_CACHE` | 1 | Redis cache toggle |
| `ENABLE_REDIS` | 1 | Redis enable toggle |
| `BACKGROUND_PREWARM_ENABLED` (via `VECTOR_DB_ENABLE_STARTUP_PREWARM`) | `tools/retrieval/vector_config.py` | embedding prewarm |
| `VECTOR_DB_ALLOW_MODEL_DOWNLOAD` | 2 | permit HF Hub fetch |
| `BGE_ALLOW_MODEL_DOWNLOAD` | 2 | permit BGE model fetch |
| `ARCHIVE_BATCH_ACCEPT` | 1 | archive batch accept |
| `ENABLE_FUZZ` | 1 | fuzz testing |
| `SEMANTIC_CACHE_D2_ENABLED` | 2 | semantic cache tier |
| `MODULE_COLLISION_UPDATE_BASELINE` | 1 | testing support |
| `HIVE_MIND_STRICT_MODE` | 1 | strict mode |
| `OTEL_MCP_ALLOW_MOCK_TRACES` | `tools/otel/otel_config.py` | permit mock traces |
| (remaining 8 toggles) | — | various |

## 6. Tunables (63)

All tunables with 1-file consumer; full list available by scan. Grouped by subsystem:

| Subsystem | Count | Examples |
|---|---:|---|
| `vector_db` / retrieval | 10 | `VECTOR_DB_MODEL_LOAD_TIMEOUT`, `VECTOR_DB_CHROMA_INIT_TIMEOUT`, `VECTOR_DB_ENCODE_TIMEOUT`, `VECTOR_DB_ENCODE_QUEUE_WAIT_TIMEOUT`, `VECTOR_DB_QUERY_COLLECTION_TIMEOUT`, `VECTOR_DB_SEARCH_PER_COLLECTION_TIMEOUT`, `VECTOR_DB_SEARCH_GLOBAL_TIMEOUT`, `VECTOR_DB_COUNT_CACHE_TTL`, `VECTOR_DB_ENABLE_STARTUP_PREWARM`, `VECTOR_DB_DEVICE` |
| healing / retry | 8 | `MAX_HEALING_PER_FILE`, `MAX_HEALING_ROUNDS`, `GLOBAL_HEALING_BUDGET`, `HEAL_POLICY_MODEL_ESCALATION`, `HEAL_MAX_ESCALATIONS_PER_RUN`, `HEAL_MAX_HIGH_TIER_PER_RUN`, `HEALING_LEASE_DURATION`, `HEALTH_SCORE_TTL` |
| agent retry | 2 | `AGENT_RETRY_COUNT`, `AGENT_RETRY_BACKOFF_BASE` |
| signal thresholds | 13 | `SIGNAL_EXCELLENT_MIN`, `SIGNAL_GOOD_MIN`, `SIGNAL_HIGH_MIN`, `SIGNAL_MARGINAL_MIN`, `SIGNAL_MIN_AUTHORITY`, `SIGNAL_MIN_CLAIM_CONFIDENCE`, `SIGNAL_MIN_COHERENCE`, `SIGNAL_MIN_FACT_VERIFICATION`, `SIGNAL_MIN_RELEVANCE`, `SIGNAL_MIN_SPECIFICITY`, `SIGNAL_MAX_HALLUCINATION_RISK`, `SIGNAL_MAX_REPETITION_RATIO`, `RAG_SIMILARITY_THRESHOLD` |
| sequential-thinking | 5 | `SEQUENTIAL_THINKING_MAX_THOUGHTS`, `SEQUENTIAL_THINKING_TOKEN_BUDGET`, `SEQUENTIAL_THINKING_COMPLEXITY_THRESHOLD`, `SEQUENTIAL_THINKING_AUTO_TRIGGER`, `SEQUENTIAL_THINKING_ENABLED` |
| governance / budget | 5 | `AGENTIC_BUDGET_USD`, `BUDGET_MAX_COST_USD`, `BUDGET_MAX_LATENCY_MS`, `GOVERNOR_SAFETY_THRESHOLD`, `MISSION_TIMEOUT_SECONDS` |
| limits / linting | 6 | `MAX_CLASS_LINES`, `MAX_CLASS_METHODS`, `MAX_FILE_LINES`, `MAX_FUNCTION_LINES`, `MAX_CYCLOMATIC_COMPLEXITY`, `MAX_VIOLATIONS_SHOWN` |
| OTel / tracing | 4 | `OTEL_MCP_MAX_TRACE_CACHE`, `TRACE_SAMPLE_RATE`, `TRACE_INIT_TIMEOUT`, `HIVE_MIND_TRACE_SAMPLING_RATE` |
| negotiation | 3 | `NEGOTIATION_MAX_ROUNDS`, `NEGOTIATION_RESPONSE_TIMEOUT`, `NEGOTIATION_AUTO_RESOLVE_THRESHOLD` |
| other | 7 | `AST_FUZZY_THRESHOLD`, `COVERAGE_SCORER_BUDGET_MS`, `COVERAGE_SCORER_MODE`, `MAX_LEASE_BACKOFF`, `HIVE_MIND_PROMOTION_THRESHOLD`, `VALIDATION_MAX_SIMILARITY_THRESHOLD`, `VALIDATION_TEMPERATURE` |

## 7. Path overrides (15)

| Env key | Consumer(s) | Purpose |
|---|---|---|
| `ADG_DIR` | `.mcp.json` (env block) | ADG artefacts directory |
| `ADG_REPO_ROOT` | ADG scanner | repo-root override |
| `AGENTIC_REPO_ROOT` | `.mcp.json` (bootstrap) | repo root resolution |
| `AGENTIC_CORE_DIR` | 1 | agentic_core path override |
| `PROJECT_ROOT` | 1 | generic project root |
| `MEMORY_DB` | 4 files (`tools/memory/*`, `agentic_core/L4_state/enforcement/graph_memory_bridge.py`) | memory SQLite path |
| `L4_STORAGE_ROOT` | 1 | L4 state root |
| `ADDITIONAL_REPO_ROOTS` | 1 | multi-repo scanner |
| `ADG_FATAL_LOG` | 1 | ADG fatal log path |
| `REDIS_SSL_CERT_PATH` | 1 | Redis TLS cert |
| `REDIS_SSL_KEY_PATH` | 1 | Redis TLS key |
| `REDIS_WINDOWS_PATHS` | 1 | Windows-path handling |
| `PATH` | 2 | process PATH override |
| `PYTHONPATH` | 1 | process PYTHONPATH override |
| `SOVEREIGN_ENV` | 1 | deployment-env label |

## 8. MCP-config env keys (propagated by legacy editor)

These appear only in `.mcp.json` `env` blocks (not repo code) and are injected into MCP subprocesses at spawn time:

| Env key | MCP server(s) |
|---|---|
| `NOTION_TOKEN` | notion |
| `GITKRAKEN_GK_PATH` | GitKraken |
| `AGENTIC_REPO_ROOT` | all python MCPs |
| `ADG_REDIS_URL` | adg_sqlite, memory |
| `MEMORY_DB` | memory |
| `ADG_DIR` | adg_sqlite |
| `PYTHONPATH`, `PYTHONUNBUFFERED` | all python MCPs |
| `VECTOR_DB_*` | vector_db |
| `REDIS_*` | redis MCP |
| `TOKENIZERS_PARALLELISM`, `HF_HUB_OFFLINE` | vector_db |

## 9. Integrity guarantees

- **No secret values appear in this document**, only env-key names.
- All matches derived from literal-string scan of `os.getenv(...)`, `os.environ.get(...)`, `os.environ[...]`. Scan excludes `__pycache__/` and `archive/`.
- Every env key is bound to at least one consumer module. No orphan keys.
- Keys appearing in `mcp_config.json` env blocks but not repo code (e.g. `NOTION_TOKEN`) are explicitly noted in §8.

## 10. Hand-off to G4b

G4b is the canonical owner of the config-knob catalogue. The 154 env keys enumerated here are the seed set. G4b should:
1. Classify each key as `secret` / `provider_config` / `runtime_tunable` / `feature_flag` / `path_override`.
2. Add each key's **default** (from `os.getenv("KEY", default)` calls where available) — G2b did not catalogue defaults.
3. Cross-reference env-key names against v1.4 atoms that assume their presence.
4. Identify keys read by tests only (not production) and exclude from the runtime config-knob set.

## 11. L2 heal-confidence SSOT (paired env)

| Env key | Consumer module(s) | Notes |
|---|---|---|
| `HEALING_CONFIDENCE_HIGH` | `agentic_core/L2_execution/healers/routing_thresholds_ssot.py` | Inclusive HIGH band floor (`score ≥ HIGH`); fail-closed domain + ordering pairing with MEDIUM |
| `HEALING_CONFIDENCE_MEDIUM` | `agentic_core/L2_execution/healers/routing_thresholds_ssot.py` | Inclusive MEDIUM band floor; must satisfy `0 ≤ MEDIUM < HIGH ≤ 1` |

Executor-level thresholds remain separate:

| Env key | Consumer module(s) | Notes |
|---|---|---|
| `PRIMARY_HIGH_CONFIDENCE` | `agentic_core/L2_execution/healers/confidence_aware_executor.py` | PRIMARY-tier executor knobs — orthogonal to heal SSOT pairing |
| `PRIMARY_MEDIUM_CONFIDENCE` | `agentic_core/L2_execution/healers/confidence_aware_executor.py` | PRIMARY-tier executor knobs — orthogonal |

| Env key | Consumer module(s) | Notes |
|---|---|---|
| `DISABLE_QWEN_FALLBACK` | `agentic_core/L2_execution/healers/healing_router.py` | MEDIUM-tier fallback semantics |
| `ROUTING_POSTERIOR_N_FLOOR` | `agentic_core/L2_execution/healers/healing_router.py` | Posterior ledger n-floor |
| `ROUTING_POSTERIOR_DISABLED` | `agentic_core/L2_execution/healers/healing_router.py` | Posterior ledger opt-out |

Signal enhancer knobs (`SIGNAL_*`) are documented under `signal_quality_config` — they tune signal layers and do **not** retarget heal band math (see `.env.example` commentary).
