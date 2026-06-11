---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\infra_wiring_inventory.md'
original_relative_path: 'infra_wiring_inventory.md'
source_sha256: b2fa9da2a167804a2ef18ae8c509ab9516dc1ac446e36cb55893f375963a3cf3
recovered_status: LOST_RECOVERED
last_commit: 'e941e3e9e0e'
last_commit_date: '2026-04-11 22:12:51 -0400'
created_date: '2026-04-08'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Infrastructure Wiring Inventory — Phase 0 Baseline
**Generated:** 2026-04-11
**ADG Snapshot:** 04112026_1142 (78,517 nodes / 628,872 edges)
**Purpose:** Phase 0 baseline inventory of all infrastructure surfaces in Agentic-Workflow repository.
**Scope:** All raw or wrapped infra surfaces — Redis/cache, SQLite/DB, vector DB/Chroma, provider SDKs, model clients, HTTP clients, queues, OTel/tracing, eval harnesses, file/object storage, auth/secrets adapters, feature flags/config, Prometheus metrics, graph DB.

## Executive Summary

This scan identified **13 distinct infrastructure surface classes** (prior 2026-04-08 inventory counted 10 — Neo4j, Prometheus, and vLLM/aiohttp were missing). The prior P0 violation (`apps_rfp` direct chromadb import) is **resolved** — that import is now a code comment only. The current ADG scorecard is P0=0, P1=0, P2=5 (at accepted ceiling), P3=5.

Three new surfaces discovered this pass are unregistered in both `infra_wiring_scan.py` `FORBIDDEN_IMPORTS` and `_APPROVED_ADAPTER_PATHS`:
- **Neo4j** (`agentic_core/L4_state/enforcement/neo4j_store.py`) — zero ADG callers; isolated/experimental
- **Prometheus** (`agentic_core/L6_observability/utils/metrics/`) — active but not in approved adapter registry
- **vLLM aiohttp** (`agentic_core/L3_orchestration/inference/qwen_vllm/engines/optimized_vllm_client.py`) — raw HTTP in L3, not sanctioned

The provider SDK control plane (`infrastructure/sdks_mcps/__init__.py`) is confirmed active but its client classes (`OpenAIClient`, `AnthropicClient`, `VertexClient`) are **empty stubs** — the real provider access flows through thin factory functions, not class instances.

| Metric | Count |
|---|---|
| Total surfaces identified | 13 |
| Active, approved (P0/P1 COMPLIANT) | 8 |
| Active, issues (P2 accepted ceiling) | 3 |
| Unregistered / no adapter entry | 3 |
| Dormant / experimental (P3) | 5 |
| Deprecated pending removal | 0 |
| Prior P0 violations resolved | 1 (apps_rfp chromadb) |

---

## Infra Surface Classification Table

| infra_surface | owner_layer | approved_entrypoints | approved_callers | active? | issues |
|---|---|---|---|---|---|
| Redis/cache | L2 (cache seam) | `agentic_core/cache/redis_cache_client.py` (DeterministicRedisCache) | L2, L3, L4 agents; tools/adg, tools/mcp | ✅ YES | P2: duplicate adapter at `agentic_core/cache/core/redis_cache_client.py` not in `_APPROVED_ADAPTER_PATHS` |
| SQLite/ADG store | L4 + tools | `tools/memory/sqlite_memory_store.py`; `apps_shared/data_adapters/repo_signal_adapter.py` | tools/*, apps_shared signal collector | ✅ YES | L4 raw users (chunk_manifest_registry, graph_knowledge_store, etc.) sanctioned by filename only — not in `_APPROVED_ADAPTER_PATHS` |
| ChromaDB/vector | L4 | `agentic_core/L4_state/utils/client/chroma_client.py` (SovereignChromaClient) | L4 retrieval, tools/mcp/vector_db_server | ✅ YES | P2: `retrieval_layers.py` + `in_memory_vector_cache.py` + `gptcache_client.py` all import raw chromadb (3 mixed-usage counts at accepted ceiling) |
| OpenAI (embeddings+LLM) | L2/infra | `agentic_core/embeddings/embedding_factory.py`; `infrastructure/sdks_mcps/__init__.py` (`create_openai_client()`, `create_openai_sync_client()`) | L1, L2, system_learning, apps_shared | ✅ YES | **RESOLVED (2026-04-11)**: `retrieval_layers.py` — `from openai import OpenAI` replaced with `create_openai_sync_client()`; **PENDING**: `semantic_enricher.py` lazy raw openai — Wave C R-B3 target |
| Anthropic (LLM) | infrastructure | `infrastructure/sdks_mcps/__init__.py` (`create_anthropic_client()`) | apps_shared/types/model_router_types.py; infrastructure | ✅ YES | `infrastructure/sdks_mcps` stub classes (`AnthropicClient`) are empty `pass` — no real implementation |
| Google Gemini/Vertex (LLM) | infrastructure | `infrastructure/sdks_mcps/__init__.py` (`create_vertex_client()`); `apps_shared/utils/providers_google_genai_client_util.py` | apps_shared, agentic_core evaluation | ✅ YES | **R-B1/R-B2 RESOLVED (2026-04-11)**: `llm_judge.py` + `provider_registry.py` rerouted through `create_vertex_client()`; **PENDING**: `dependencygraph_validator.py` — Wave C R-C1 target |
| HTTP (requests/aiohttp/httpx) | tools/infra + L3 (vLLM seam) | `tools/mcp/enhanced_http_server.py` (process-boundary); `optimized_vllm_client.py` (approved vLLM seam) | MCP clients, tools, L3 vLLM inference | ✅ YES | **RESOLVED (2026-04-11)**: `optimized_vllm_client.py` — vLLM Path A approved; added to `_APPROVED_ADAPTER_PATHS`, APPROVED in `SANCTIONED_ADAPTER_FILES`, seam contract comment added |
| S3/Blob (boto3) | L4 | `agentic_core/L4_state/utils/memory/canonical_store.py`; `agentic_core/L4_state/utils/memory/blob_storage_provider.py` | L4 state only | ✅ YES | `blob_storage_provider.py` in `SANCTIONED_ADAPTER_FILES` but not in `_APPROVED_ADAPTER_PATHS` — view gap |
| OpenTelemetry (tracing) | apps_shared/L6 | `apps_shared/utils/open_telemetry_tracing_adapter_util.py` (`OpenTelemetryTracingAdapter`, `get_tracer()`) | system_learning, L3 orchestrator, tools/otel | ✅ YES | **RESOLVED (2026-04-11)**: `apps_tracing_mixin.py` now imports `OTEL_AVAILABLE` from canonical adapter; raw OTel bypass eliminated |
| Prometheus (metrics) | L6 | `agentic_core/L6_observability/utils/metrics/prometheus_metrics.py` | L6 observability metrics server | ✅ YES | **UNREGISTERED** — not in `FORBIDDEN_IMPORTS`, not in `_APPROVED_ADAPTER_PATHS`, not in `SANCTIONED_ADAPTER_FILES` |
| Embedding models (sentence_transformers) | L2/apps_shared | `agentic_core/embeddings/embedding_factory.py`; `system_learning/engines/openai_embedder.py` (BGEEmbedder) | L2, system_learning | ✅ YES | `apps_shared/validators/cache_entry_validator.py`, `apps_shared/utils/late_interaction_reranker_util.py`, `apps_shared/enforcement/GlobalcacheStrategy.py` instantiate `SentenceTransformer` directly — bypass embedding_factory |
| Neo4j (graph DB) | L4 | NONE — no approved adapter registered | `apps_shared/utils/rank_observability_components_util.py` (try/except only) | ⚠️ UNKNOWN | **UNREGISTERED** — `neo4j` not in `FORBIDDEN_IMPORTS`; `neo4j_store.py` not in `_APPROVED_ADAPTER_PATHS`; zero ADG import-edge callers; appears experimental/isolated |
| Feature flags/config | system_learning/agentic_core | `system_learning/config/feature_flags.py` (`FeatureFlagConfig`, env-driven); `agentic_core/runtime/config` (`FeatureFlag`, `FeatureFlagManager`) | system_learning monitoring, agentic_core runtime | ✅ YES | Two parallel flag stores (system_learning vs agentic_core); no external flag service dependency confirmed; env-var-driven only |

---

## Explicit Raw Infra Client Entrypoints

These are the files where raw infra packages are imported directly (not via adapter). Grouped by package.

### `redis` package
| File | Layer | Status | Justification |
|---|---|---|---|
| `agentic_core/cache/redis_cache_client.py` | L2/L_SHARED | ✅ APPROVED adapter | Canonical DeterministicRedisCache |
| `agentic_core/cache/core/redis_cache_client.py` | L2/L_SHARED | ⚠️ P2 DUPLICATE | Same filename, different directory; not in `_APPROVED_ADAPTER_PATHS` |
| `agentic_core/L2_execution/reasoning/RedisSovereignAgent.py` | L2 | ✅ SANCTIONED (filename) | Sovereign Redis agent |
| `agentic_core/L3_orchestration/reasoning/engines/sovereign_redis_orchestrator.py` | L3 | ✅ APPROVED adapter | Fail-closed orchestrator per ownership matrix |
| `agentic_core/L4_state/reasoning/CachedStateLedger.py` | L4 | ✅ SANCTIONED (filename) | L4 state ledger |
| `agentic_core/L4_state/utils/memory/semantic_cache_manager.py` | L4 | ✅ SANCTIONED (filename) | HiveMind semantic cache |
| `tools/adg/adg_redis_ingest.py` | tools | ✅ ALLOWED (tools/) | ADG ingest pipeline |
| `tools/adg/adg_stale_guard.py` | tools | ✅ ALLOWED (tools/) | Stale detection |
| `tools/adg/queries/adg_rlhf_sft_query*.py` | tools | ✅ ALLOWED (tools/) | Diagnostic queries |
| `tools/mcp/redis_mcp_server.py` | tools | ✅ ALLOWED (tools/) | Redis MCP server |
| `tools/memory/adg_memory_server.py` | tools | ✅ ALLOWED (tools/) | Memory graph MCP |
| `agentic_core/L4_state/cache/redis_mcp_client.py` | L4 | ✅ TOMBSTONED | Intentionally empty — see file header |

### `chromadb` package
| File | Layer | Status | Justification |
|---|---|---|---|
| `agentic_core/L4_state/utils/client/chroma_client.py` | L4 | ✅ APPROVED adapter | SovereignChromaClient |
| `agentic_core/L4_state/reasoning/retrieval_layers.py` | L4 | ⚠️ SANCTIONED + RAW OPENAI | Both chromadb AND openai raw imports at module level |
| `agentic_core/L4_state/utils/memory/in_memory_vector_cache.py` | L4 | ✅ SANCTIONED (filename) | In-memory vector cache |
| `agentic_core/L4_state/cache/gptcache_client.py` | L4 | ✅ SANCTIONED (filename) | Native L2 cache (SQLite+ChromaDB); renamed from GPTCache |
| `tools/mcp/vector_db_server.py` | tools | ✅ ALLOWED (tools/) | Vector DB MCP server |

### `sqlite3` package
| File | Layer | Status | Justification |
|---|---|---|---|
| `tools/memory/sqlite_memory_store.py` | tools | ✅ APPROVED adapter | Canonical memory graph persistence |
| `apps_shared/data_adapters/repo_signal_adapter.py` | L_APP | ✅ APPROVED adapter | Read-only signal introspection |
| `agentic_core/L4_state/utils/memory/graph_knowledge_store.py` | L4 | ✅ SANCTIONED (filename) | Knowledge graph store |
| `agentic_core/L4_state/utils/memory/chunk_manifest_registry.py` | L4 | ✅ SANCTIONED (filename) | Chunk manifest |
| `agentic_core/L4_state/utils/memory/completeness_snapshot_registry.py` | L4 | ✅ SANCTIONED (filename) | Completeness registry |
| `agentic_core/L4_state/utils/memory/retrieval_eval_registry.py` | L4 | ✅ SANCTIONED (filename) | Retrieval eval |
| `agentic_core/L4_state/utils/memory/verdict_store.py` | L4 | ✅ SANCTIONED (filename) | Verdict store |
| `agentic_core/L4_state/utils/memory/evidence_assembler.py` | L4 | ✅ SANCTIONED (filename) | Evidence assembler |
| `agentic_core/L4_state/cache/gptcache_client.py` | L4 | ✅ SANCTIONED (filename) | Native L2 cache SQLite backend |
| `tools/generate/generate_static_adg.py` + materialized_views/*.py | tools | ✅ ALLOWED (tools/) | ADG generation |
| Root-level debug scripts (`_validate_adg.py`, `_debug_hotspot.py`, etc.) | repo root | ⚠️ NOT PRODUCTION | Diagnostic scripts; not app code |

### `openai` / `anthropic` / `google.generativeai` packages
| File | Layer | Status | Justification |
|---|---|---|---|
| `infrastructure/sdks_mcps/__init__.py` | infrastructure | ✅ APPROVED adapter | Provider SDK control plane (factory functions) |
| `agentic_core/embeddings/embedding_factory.py` | L2 | ✅ APPROVED adapter (exempt prefix) | Canonical embedding seam |
| `apps_shared/utils/providers_google_genai_client_util.py` | apps_shared | ✅ ALLOWED (apps_shared) | Google Gemini client util |
| `apps_shared/types/model_router_types.py` | apps_shared | ✅ ALLOWED (apps_shared) | Lazy inline raw openai/anthropic |
| `system_learning/engines/openai_embedder.py` | system_learning | ✅ ALLOWED (system_learning) | OpenAI + BGE embedder |
| `agentic_core/L4_state/reasoning/retrieval_layers.py` | L4 | ❌ **ISSUE** | `from openai import OpenAI` at module level — not exempt; should route via `embedding_factory` or `infrastructure/sdks_mcps` |
| `agentic_core/knowledge/enrichment/semantic_enricher.py` | agentic_core | ❌ **ISSUE** | Lazy `from openai import OpenAI` in agentic_core — not in any exempt path |
| `agentic_core/evaluation/judges/llm_judge.py` | L5 | ❌ **ISSUE** | Lazy `import google.generativeai` — agentic_core/evaluation not in `_PROVIDER_EXEMPT_PREFIXES` |
| `agentic_core/evaluation/judges/provider_registry.py` | L5 | ❌ **ISSUE** | Lazy `import google.generativeai` — same issue as llm_judge.py |
| `apps_shared/types/hardened_gemini_executor_types.py` | apps_shared | ✅ ALLOWED (apps_shared) | Hardened executor type |

### `boto3` / `botocore` package
| File | Layer | Status | Justification |
|---|---|---|---|
| `agentic_core/L4_state/utils/memory/canonical_store.py` | L4 | ✅ APPROVED adapter | Canonical S3/filesystem store |
| `agentic_core/L4_state/utils/memory/blob_storage_provider.py` | L4 | ✅ SANCTIONED (filename) | Blob storage provider; not yet in `_APPROVED_ADAPTER_PATHS` |

### `aiohttp` / `requests` / `httpx` packages
| File | Layer | Status | Justification |
|---|---|---|---|
| `tools/mcp/enhanced_http_server.py` | tools | ✅ APPROVED adapter (process-boundary) | MCP HTTP server |
| `agentic_core/gateway/api_gateway_integration.py` | agentic_core | ✅ SANCTIONED (filename) | Kong/Envoy health check |
| `agentic_core/core/frameworks/documentation_framework.py` | agentic_core | ✅ SANCTIONED (filename) | Framework doc example |
| `agentic_core/L3_orchestration/inference/qwen_vllm/engines/optimized_vllm_client.py` | L3 | ❌ **ISSUE** | Direct `import aiohttp` — NOT in `SANCTIONED_ADAPTER_FILES`; no approved entrypoint for vLLM HTTP in L3 |

### `opentelemetry` package
| File | Layer | Status | Justification |
|---|---|---|---|
| `apps_shared/utils/open_telemetry_tracing_adapter_util.py` | apps_shared | ✅ CANONICAL adapter | `OpenTelemetryTracingAdapter`, `get_tracer()` — OTLP gRPC/HTTP + console export |
| `apps_shared/mixins/apps_tracing_mixin.py` | apps_shared | ⚠️ **ISSUE** | Direct `from opentelemetry import trace` — bypasses `get_tracer()` canonical path |

### `prometheus_client` package
| File | Layer | Status | Justification |
|---|---|---|---|
| `agentic_core/L6_observability/utils/metrics/prometheus_metrics.py` | L6 | ❌ **UNREGISTERED** | Direct top-level `prometheus_client` import — no approved adapter entry anywhere |
| `agentic_core/L6_observability/utils/engines/metrics_server.py` | L6 | ❌ **UNREGISTERED** | Lazy `prometheus_client` import — no approved adapter entry |

### `neo4j` package
| File | Layer | Status | Justification |
|---|---|---|---|
| `agentic_core/L4_state/enforcement/neo4j_store.py` | L4 | ❌ **UNREGISTERED** | `from neo4j import GraphDatabase` — not in `FORBIDDEN_IMPORTS` scanner; zero ADG import-edge callers; only caller is `apps_shared/utils/rank_observability_components_util.py` via try/except guard |

### `sentence_transformers` / `torch` packages
| File | Layer | Status | Justification |
|---|---|---|---|
| `agentic_core/embeddings/embedding_factory.py` | L2 | ✅ APPROVED (exempt prefix) | Canonical embedding seam |
| `system_learning/engines/openai_embedder.py` | system_learning | ✅ ALLOWED (system_learning) | BGEEmbedder via SentenceTransformer |
| `tools/mcp/vector_db_server.py` | tools | ✅ ALLOWED (tools/) | Embedding model in MCP server |
| `apps_shared/validators/cache_entry_validator.py` | apps_shared | ⚠️ ALLOWED but bypasses factory | Direct `SentenceTransformer` instantiation |
| `apps_shared/utils/late_interaction_reranker_util.py` | apps_shared | ⚠️ ALLOWED but bypasses factory | Direct `SentenceTransformer` + `torch` |
| `apps_shared/enforcement/GlobalcacheStrategy.py` | apps_shared | ⚠️ ALLOWED but bypasses factory | Direct `SentenceTransformer` instantiation |

---

## Initial Issues List

### P0 — Hard Fail (would block CI if triggered)
*No active P0 violations per current ADG scorecard (2026-04-08 scan). Prior violation resolved.*

| # | File | Package | Issue | Resolution Path |
|---|---|---|---|---|
| — | `apps_rfp/engines/proposal_retrieval_engine.py` | chromadb | ✅ **RESOLVED** — was a direct import; now a comment only | No action needed |

### P1 — Block (structural violations)
*No active P1 violations per current ADG scorecard.*

### P2 — Accepted at ceiling (mixed/duplicated adapters)
| # | File | Package | Issue |
|---|---|---|---|
| 1 | `agentic_core/cache/core/redis_cache_client.py` | redis | Duplicate adapter path; not in `_APPROVED_ADAPTER_PATHS`; separate from canonical `agentic_core/cache/redis_cache_client.py` |
| 2 | `agentic_core/L4_state/reasoning/retrieval_layers.py` | chromadb + openai | Mixed: raw chromadb AND raw openai at module level; sanctioned by filename but multi-infra |
| 3 | `agentic_core/L4_state/cache/gptcache_client.py` | chromadb + sqlite3 | Mixed: uses both raw chromadb and raw sqlite3; sanctioned but multi-infra |

### New Issues Discovered This Pass (not yet registered in scorecard/scan)

| Priority | File | Package | Finding |
|---|---|---|---|
| **HIGH** | `agentic_core/L4_state/reasoning/retrieval_layers.py` | openai | `from openai import OpenAI` at module level in agentic_core/L4; not in `_PROVIDER_EXEMPT_PREFIXES`; should route via `embedding_factory` or `infrastructure/sdks_mcps` |
| **HIGH** | `agentic_core/L3_orchestration/inference/qwen_vllm/engines/optimized_vllm_client.py` | aiohttp | Direct `import aiohttp` in L3 for vLLM HTTP; not in `SANCTIONED_ADAPTER_FILES` or `_APPROVED_ADAPTER_PATHS`; no sanctioned HTTP adapter for vLLM |
| **HIGH** | `agentic_core/evaluation/judges/llm_judge.py` | google.generativeai | Lazy raw import in agentic_core/evaluation; `agentic_core/evaluation/` not in `_PROVIDER_EXEMPT_PREFIXES` |
| **HIGH** | `agentic_core/evaluation/judges/provider_registry.py` | google.generativeai | Same as llm_judge.py — same file directory, same exemption gap |
| **MEDIUM** | `agentic_core/L6_observability/utils/metrics/prometheus_metrics.py` | prometheus_client | Not in `FORBIDDEN_IMPORTS`, not in `_APPROVED_ADAPTER_PATHS`; no sanctioned adapter entry for Prometheus |
| **MEDIUM** | `agentic_core/L6_observability/utils/engines/metrics_server.py` | prometheus_client | Same — unregistered Prometheus surface |
| **MEDIUM** | `agentic_core/L4_state/enforcement/neo4j_store.py` | neo4j | Completely unregistered infra surface; 0 ADG callers; `neo4j` not in `FORBIDDEN_IMPORTS`; `NEO4J_URI/USERNAME/PASSWORD` env vars required |
| **MEDIUM** | `agentic_core/knowledge/enrichment/semantic_enricher.py` | openai | Lazy raw OpenAI in agentic_core — not in any exempt path |
| **LOW** | `apps_shared/mixins/apps_tracing_mixin.py` | opentelemetry | Direct `from opentelemetry import trace` bypasses `get_tracer()` canonical path in `open_telemetry_tracing_adapter_util.py` |
| **LOW** | `infrastructure/sdks_mcps/__init__.py` | openai/anthropic/google | Client classes (`OpenAIClient`, `AnthropicClient`, `VertexClient`) are empty `pass` stubs — factory functions work, class instances do not |
| **LOW** | `agentic_core/L4_state/utils/memory/blob_storage_provider.py` | boto3 | In `SANCTIONED_ADAPTER_FILES` but missing from `_APPROVED_ADAPTER_PATHS` — view coverage gap |
| **INFO** | `agentic_core/cache/core/redis_cache_client.py` | redis | Second redis_cache_client.py at `core/` subdirectory — not in `_APPROVED_ADAPTER_PATHS`; duplicated adapter pattern already at P2 ceiling |

---

## Uncertainties and Assumptions

### Uncertainties
1. **Neo4j activation state**: `neo4j_store.py` has a guardian-annotated `ImportError` raise on missing dep. Unclear if neo4j is installed in any environment. Zero ADG callers suggests experimental/never activated.
2. **vLLM deployment status**: `optimized_vllm_client.py` references `http://localhost:8000/v1` (local RTX 5090). Unknown if this is active in CI or production environments.
3. **Prometheus collector connectivity**: Metrics server exists at L6; unknown if a Prometheus collector scrapes it in any running environment.
4. **`infrastructure/sdks_mcps` stub migration**: The empty client classes suggest an in-progress migration. Unknown if consumers are waiting for real class implementations or only use factory functions.
5. **`gptcache_client.py` name confusion**: File comments say "No GPTCache dependency" but the class exported as `GPTCacheClient` for backward compat. Unclear if callers expect GPTCache behavior or native behavior.
6. **Feature flag duplication**: Two flag systems (`system_learning/config/feature_flags.py` vs `agentic_core/runtime/config`) — unclear if they are converging or intentionally separate.
7. **Embedding factory bypass in apps_shared**: Three `SentenceTransformer` direct instantiations in `apps_shared`. These are in ALLOWED_DIRS but may indicate the factory seam is not enforced for apps_shared.

### Assumptions
1. `tools/` is non-production infrastructure tooling — direct SDK imports are acceptable.
2. `apps_shared/` is shared infrastructure (not application surface) — SDK imports are permitted.
3. `system_learning/` is meta-learning infrastructure — raw provider imports are permitted.
4. A surface with zero ADG callers AND a `try/except ImportError` guard is classified as experimental/isolated (P3).
5. The `infra_wiring_scan.py` `SANCTIONED_ADAPTER_FILES` set (by filename) and `infra_wiring_views.py` `_APPROVED_ADAPTER_PATHS` set (by path) are two independent lists; discrepancies between them are tracked as view coverage gaps, not P0 violations.
6. Root-level diagnostic scripts (`_validate_adg.py`, `_debug_hotspot.py`, etc.) are not production code — their direct sqlite3 imports are out of scope for wiring enforcement.

---

*Stop condition reached — Phase 0 inventory complete. Ownership rule changes, ADG extractor changes, and code repairs are deferred to subsequent phases.*
