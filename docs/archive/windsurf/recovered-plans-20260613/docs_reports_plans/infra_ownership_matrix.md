# Infrastructure Ownership Matrix — Phase 1 Policy Contract
**Generated:** 2026-04-11
**Based on:** Phase 0 inventory (ADG snapshot 04112026_1142, 78,517 nodes / 628,872 edges)
**Purpose:** Explicit policy contract for infrastructure wiring. Defines allowed owner layers, approved callers, forbidden callers, access types, and lifecycle state for every infra surface. Grounded in observed repo reality only.

## A. Executive Summary

This matrix covers **13 infrastructure surface classes** identified in Phase 0. The prior 2026-04-08 matrix covered 10 — **Neo4j, Prometheus, and vLLM/aiohttp were missing entirely**.

Key corrections vs. the prior matrix:
- **Canonical OTel adapter**: `apps_shared/utils/open_telemetry_tracing_adapter_util.py` (NOT `tools/otel/otel_mcp_server.py` as previously documented)
- **`apps_rfp` ChromaDB P0**: RESOLVED — the direct import is now a comment; no active P0 violations
- **`infrastructure/sdks_mcps/__init__.py`**: Labeled "temporary minimal wrapper for migration" in the file itself — factory functions are thin real wrappers; client classes (`OpenAIClient`, `AnthropicClient`, `VertexClient`) are empty `pass` stubs with no behavior
- **4 new provider bypass instances** discovered in `agentic_core/` (not in `_PROVIDER_EXEMPT_PREFIXES`)
- **`neo4j_store.py`**: Re-raises `ImportError` on missing dep (not silently swallows it); the `GraphDatabase = None` fallback is **unreachable dead code**; its only caller guards with `(ValueError, TypeError, RuntimeError)` — NOT `ImportError`

| Metric | Count |
|---|---|
| Total infra surfaces | 13 |
| Active, P0/P1 COMPLIANT | 8 |
| Active, known issues (P2 accepted ceiling) | 3 |
| Unregistered (not in FORBIDDEN_IMPORTS or _APPROVED_ADAPTER_PATHS) | 3 |
| Dormant / experimental (P3) | 5 |
| Deprecated | 0 |
| Prior P0 violations now resolved | 1 |

---

## B. Ownership Matrix

Columns: `infra_surface | infra_class | owner_layer | approved_entrypoints | approved_callers | forbidden_callers | access_type | state | apps_direct_allowed? | issues | evidence`

> Wide table — all 13 surfaces. For full detail on each surface see Section C (policy rules) and Section D (exemptions/edge cases).

| infra_surface | infra_class | owner_layer | approved_entrypoints | approved_callers | forbidden_callers | access_type | state | apps_direct_allowed? | issues | evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| Redis/cache | Cache/Coordination | L2 (cache seam, owned by `agentic_core/cache/`) | `agentic_core/cache/redis_cache_client.py` (DeterministicRedisCache); `agentic_core/L3_orchestration/reasoning/engines/sovereign_redis_orchestrator.py` (L3 writes only) | L0 read-cache, L1 read-cache, L2 (RedisSovereignAgent), L3 (SovereignRedisOrchestrator), L4 (CachedStateLedger, SemanticCacheManager), tools/* | apps_* direct import; L1 write ops; L6 write ops | APPROVED_ADAPTER | ACTIVE_APPROVED | ❌ NO | P2: duplicate adapter at `agentic_core/cache/core/redis_cache_client.py` not in `_APPROVED_ADAPTER_PATHS`; L4 raw users sanctioned by filename only | `agentic_core/cache/redis_cache_client.py` line 15: `import redis`; `RedisSovereignAgent.py` line 100: `import redis`; `sovereign_redis_orchestrator.py` line 97: `import redis` |
| SQLite/DB | Relational Storage | L4 (state authority) + tools (tooling) | `tools/memory/sqlite_memory_store.py`; `apps_shared/data_adapters/repo_signal_adapter.py` (read-only SELECT only) | L4 (graph_knowledge_store, chunk_manifest_registry, verdict_store, evidence_assembler, gptcache_client), tools/*, system_learning/* | apps_* direct import; L0–L3 direct writes (except tools) | APPROVED_ADAPTER for tools; RAW_SANCTIONED for L4 by filename | ACTIVE_APPROVED | ❌ NO | L4 raw users in SANCTIONED_ADAPTER_FILES but not in `_APPROVED_ADAPTER_PATHS` — view coverage gap; root-level diagnostic scripts (`_validate_adg.py` etc.) have unscoped sqlite3 | `sqlite3` grep: `tools/memory/sqlite_memory_store.py`; `agentic_core/L4_state/utils/memory/graph_knowledge_store.py`; `agentic_core/L4_state/cache/gptcache_client.py` |
| ChromaDB/vector | Vector DB | L4 (state authority) | `agentic_core/L4_state/utils/client/chroma_client.py` (SovereignChromaClient) | L4 (retrieval_layers, in_memory_vector_cache, gptcache_client), tools/mcp/vector_db_server | apps_* direct import; L0–L2 direct import | APPROVED_ADAPTER + P2_MIXED | ACTIVE_APPROVED | ❌ NO | P2 (3): `retrieval_layers.py` + `in_memory_vector_cache.py` + `gptcache_client.py` all import raw chromadb — at accepted ceiling | `agentic_core/L4_state/utils/client/chroma_client.py` line 11: `import chromadb`; `retrieval_layers.py` line 20: `import chromadb` |
| OpenAI (LLM+embed) | Provider SDK | L2 (embedding seam) + infrastructure/sdks_mcps (LLM seam) | `agentic_core/embeddings/embedding_factory.py`; `infrastructure/sdks_mcps/__init__.py` `create_openai_client()`, `create_openai_sync_client()` | L1 read-retrieval (via adapter), L2 (EmbeddingSovereignAgent), system_learning/* (BGEEmbedder), apps_shared/* | agentic_core direct raw import (except exempt prefixes); apps_* direct import | APPROVED_ADAPTER (exempt: agentic_core/embeddings/, tools/, system_learning/) | ACTIVE_APPROVED | ❌ NO | **RESOLVED**: `retrieval_layers.py` — `from openai import OpenAI` replaced with `create_openai_sync_client()` (2026-04-11); **PENDING**: `agentic_core/knowledge/enrichment/semantic_enricher.py` — lazy `from openai import OpenAI` inside `_init_default_client()` still present; Wave C R-B3 target | `retrieval_layers.py`: sanctioned seam in place; `semantic_enricher.py` line 136: `from openai import OpenAI` — pending |
| Anthropic (LLM) | Provider SDK | infrastructure/sdks_mcps | `infrastructure/sdks_mcps/__init__.py` `create_anthropic_client()` | apps_shared/* (lazy inline), infrastructure/* | agentic_core direct raw import; apps_* direct import | APPROVED_ADAPTER | ACTIVE_APPROVED | ❌ NO | **LOW**: `AnthropicClient` class in `infrastructure/sdks_mcps/__init__.py` is an empty `pass` stub with no behavior; `apps_shared/types/model_router_types.py` uses lazy raw anthropic (apps_shared exempt) | `infrastructure/sdks_mcps/__init__.py` lines 63–70: `create_anthropic_client()` thin wrapper; lines 89–90: `class AnthropicClient: pass` |
| Google Gemini/Vertex (LLM) | Provider SDK | infrastructure/sdks_mcps + apps_shared | `infrastructure/sdks_mcps/__init__.py` `create_vertex_client()`; `apps_shared/utils/providers_google_genai_client_util.py` | apps_shared/*, agentic_core/evaluation/judges/ (currently BYPASSING) | agentic_core direct raw import (except exempt prefixes) | APPROVED_ADAPTER (but bypassed in agentic_core/evaluation/) | ACTIVE_APPROVED | ❌ NO | **HIGH**: `agentic_core/evaluation/judges/llm_judge.py` — lazy `import google.generativeai` (GeminiJudge class); **HIGH**: `agentic_core/evaluation/judges/provider_registry.py` — lazy `import google.generativeai`; `agentic_core/evaluation/` is NOT in `_PROVIDER_EXEMPT_PREFIXES` | `agentic_core/evaluation/judges/llm_judge.py` contains `GeminiJudge` class with raw google.generativeai import |
| HTTP (requests/aiohttp/httpx) | Network Client | tools/mcp (process-boundary) + agentic_core/gateway (L0/L1 boundary) + agentic_core/L3 (vLLM seam) | `tools/mcp/enhanced_http_server.py` (process-boundary MCP); `agentic_core/gateway/api_gateway_integration.py` (gateway health check); `agentic_core/L3_orchestration/inference/qwen_vllm/engines/optimized_vllm_client.py` (approved vLLM seam) | L0/gateway, tools/*, L3 vLLM inference | agentic_core/* raw import (except sanctioned); apps_* direct import | APPROVED_ADAPTER for MCP path; RAW_SANCTIONED by filename for gateway; ACTIVE_APPROVED for vLLM seam | ACTIVE_APPROVED | ❌ NO | **RESOLVED (2026-04-11)**: `optimized_vllm_client.py` — vLLM Path A approved via `vllm_http_decision_packet.md`; added to `_APPROVED_ADAPTER_PATHS` and reclassified APPROVED in `SANCTIONED_ADAPTER_FILES`; seam contract comment added. ADG-blind by design (external PyPI package). | `optimized_vllm_client.py`: APPROVED seam, sanctioned contract in place; `api_gateway_integration.py` — sanctioned by filename |
| S3/Blob (boto3) | Object Storage | L4 (state authority) | `agentic_core/L4_state/utils/memory/canonical_store.py` (CanonicalStore — S3 + local filesystem); `agentic_core/L4_state/utils/memory/blob_storage_provider.py` | L4 state layer only | apps_* direct import; L0–L3 direct write | APPROVED_ADAPTER | ACTIVE_APPROVED | ❌ NO | **LOW**: `blob_storage_provider.py` in `SANCTIONED_ADAPTER_FILES` but absent from `_APPROVED_ADAPTER_PATHS` — view coverage gap; `canonical_store.py` uses lazy `import botocore.exceptions` guard but `blob_storage_provider.py` may have harder dependency | `canonical_store.py` lines 27–31: lazy `import botocore.exceptions` with `_HAS_BOTOCORE` flag; `blob_storage_provider.py` direct boto3 |
| OpenTelemetry (tracing) | Observability | apps_shared/utils (canonical adapter); tools/otel (MCP bridge) | `apps_shared/utils/open_telemetry_tracing_adapter_util.py` (`OpenTelemetryTracingAdapter`, `get_tracer()`) — OTLP gRPC/HTTP + console, graceful degradation via `OTEL_AVAILABLE` flag | system_learning/* (via adapter), agentic_core/* (via adapter), tools/otel (MCP bridge), apps_shared/* | apps_* direct import outside apps_shared | APPROVED_ADAPTER (graceful degradation when opentelemetry not installed) | ACTIVE_APPROVED | ❌ NO (apps_shared itself is the canonical host) | **RESOLVED (2026-04-11)**: `apps_shared/mixins/apps_tracing_mixin.py` now imports `OTEL_AVAILABLE` from canonical adapter and conditionally imports raw OTel symbols only when adapter confirms availability. Raw OTel bypass eliminated. | `open_telemetry_tracing_adapter_util.py` lines 93–118: try/except wrapped opentelemetry imports with `OTEL_AVAILABLE` flag; `apps_tracing_mixin.py`: canonical adapter import in place |
| Prometheus (metrics) | Metrics Emission | L6 (observability) | `agentic_core/L6_observability/utils/metrics/prometheus_metrics.py` (de facto adapter — defines `AGENTIC_REGISTRY`) | L6 metrics consumers | Any layer calling prometheus_client without going through `prometheus_metrics.py` | RAW_DIRECT (not yet in any approved registry) | ACTIVE_APPROVED | ❌ NO | **MEDIUM**: NOT in `FORBIDDEN_IMPORTS`; NOT in `_APPROVED_ADAPTER_PATHS`; NOT in `SANCTIONED_ADAPTER_FILES`; entire surface class unregistered in all wiring enforcement files; no ADG view covers Prometheus | `agentic_core/L6_observability/utils/metrics/prometheus_metrics.py` line 15: `from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, Info`; `metrics_server.py` lines 39–40: lazy prometheus_client |
| Embedding models (sentence_transformers/BGE) | ML Model Client | L2 (embedding seam, via EmbeddingFactory) | `agentic_core/embeddings/embedding_factory.py`; `system_learning/engines/openai_embedder.py` (BGEEmbedder) | L2/EmbeddingSovereignAgent, system_learning/*, tools/mcp/vector_db_server | agentic_core/* direct SentenceTransformer instantiation (except exempt) | APPROVED_ADAPTER (exempt: tools/, system_learning/, agentic_core/embeddings/) | ACTIVE_APPROVED | ❌ NO | **LOW**: `apps_shared/validators/cache_entry_validator.py`, `apps_shared/utils/late_interaction_reranker_util.py`, `apps_shared/enforcement/GlobalcacheStrategy.py` all instantiate `SentenceTransformer` directly — bypass embedding_factory; apps_shared is ALLOWED but this represents factory-bypass | `apps_shared/validators/cache_entry_validator.py`: direct SentenceTransformer; `apps_shared/enforcement/GlobalcacheStrategy.py`: direct SentenceTransformer |
| Neo4j (graph DB) | Graph Database | UNREGISTERED — no approved owner layer | NONE — no approved adapter registered | NONE — only caller is `apps_shared/utils/rank_observability_components_util.py` via try/except guard (WRONG exception types — see issues) | All layers (no approved path exists) | RAW_DIRECT — unregistered, no approval | EXPERIMENTAL_ISOLATED | ❌ NO | **MEDIUM critical**: NOT in `FORBIDDEN_IMPORTS` scanner; NOT in `_APPROVED_ADAPTER_PATHS`; zero ADG import-edge callers; `neo4j_store.py` re-raises ImportError (does NOT gracefully degrade — `GraphDatabase = None` is unreachable dead code after the raise); caller guard in `rank_observability_components_util.py` catches `(ValueError, TypeError, RuntimeError)` but NOT `ImportError` — meaning if neo4j is not installed, BOTH `neo4j_store.py` AND `rank_observability_components_util.py` fail to import | `neo4j_store.py` lines 88–94: try/raise pattern with dead `GraphDatabase = None`; `rank_observability_components_util.py` lines 186–189: wrong exception type guard |
| Feature flags/config | Config Control Plane | system_learning/ (FeatureFlagConfig) + agentic_core/runtime/ (FeatureFlag/FeatureFlagManager) | `system_learning/config/feature_flags.py` (`FeatureFlagConfig`, env-driven dataclass, `get_feature_flags()`); `agentic_core/runtime/config` (separate store) | system_learning/monitoring/*, agentic_core/runtime/* | External feature flag service dependencies (none exist — env-only) | LOCAL_CONFIG (no external infra dependency) | ACTIVE_APPROVED | ❌ N/A (no raw external SDK) | **INFO**: Two independent flag stores with no documented convergence path; `agentic_core/runtime/config` has `FeatureFlag`/`FeatureFlagManager` classes that may duplicate `system_learning/config/feature_flags.py` functionality | `system_learning/config/feature_flags.py` lines 13–194: pure Python dataclass with env overrides; `agentic_core/runtime/config` test file confirms `FeatureFlag`, `FeatureFlagManager` exist |

---

## C. Hard Pass/Fail Policy Rules

These rules derive from the 10 non-negotiable architecture laws in the SR_INTAKE and from observed enforcement in `infra_wiring_scan.py` and `infra_wiring_views.py`.

### R1 — Layer Authority Constraint

| Law | Rule | Violation Severity |
|---|---|---|
| L0 = route authority only | L0 MUST NOT import raw infra clients except HTTP (gateway integration) and Redis (routing cache read-only) | P0 HARD FAIL |
| L1 = reasoning/plan only | L1 MUST NOT write to Redis, ChromaDB, SQLite, or any provider SDK directly | P0 HARD FAIL |
| L2 = execution only through sanctioned gateways | L2 MAY own Redis (via RedisSovereignAgent), OpenAI (via EmbeddingSovereignAgent) — no other raw infra | P0 HARD FAIL for non-sanctioned raw infra |
| L3 = orchestration | L3 MUST NOT import raw HTTP clients except through `enhanced_http_server.py` or approved gateway | P0 HARD FAIL |
| L4 = canonical state/archive | L4 MAY own SQLite, ChromaDB, Boto3 — all durable writes MUST terminate through UWG | P0 HARD FAIL if UWG bypassed |
| L5 = policy/governance | L5 read-only for provider access (judge evaluation); MUST NOT directly write state | P0 HARD FAIL |
| L6 = observability/evidence only | L6 MUST NOT mutate production state; Prometheus and OTel writes are observability-only and exempt from UWG | P0 HARD FAIL for non-observability mutation |

### R2 — apps_* Prohibition
- apps_* layers MUST NOT directly import: `redis`, `chromadb`, `sqlite3`, `boto3`, `openai`, `anthropic`, `google.generativeai`, `httpx`, `requests`, `aiohttp`, `neo4j`, `prometheus_client`
- apps_* MUST route through L0–L6 sanctioned adapters
- **apps_shared** is formally NOT an apps_* surface — it is shared infrastructure and is ALLOWED to import raw SDKs
- Evidence: apps_rfp violation resolved; apps_shared is in `ALLOWED_DIRS`

### R3 — Provider SDK Control Plane
- All OpenAI/Anthropic/Google SDK calls in `agentic_core/*` (outside `agentic_core/embeddings/`) MUST route through `infrastructure/sdks_mcps/__init__.py` factory functions
- **Exempt prefixes** (observed from `_PROVIDER_EXEMPT_PREFIXES`): `infrastructure/sdks_mcps/`, `tools/`, `system_learning/`, `agentic_core/embeddings/`
- **NOT exempt**: `agentic_core/L4_state/`, `agentic_core/evaluation/`, `agentic_core/knowledge/`
- Current violations: 4 files in non-exempt agentic_core paths use raw provider imports

### R4 — Durable Write Gate (UWG)
- All durable writes to SQLite, ChromaDB, Boto3/S3 MUST terminate through UWG (`_emit_writes_via_uwg` trace contract)
- Redis writes are ephemeral — TTL-bounded — and are exempt from UWG
- OTel and Prometheus writes are observability events — exempt from UWG
- No apps_* surface may issue a durable write at all

### R5 — Infra Surface Registration
- Every raw infra client entrypoint MUST appear in EITHER `FORBIDDEN_IMPORTS` (scanner) OR `_APPROVED_ADAPTER_PATHS` (views) OR `SANCTIONED_ADAPTER_FILES` (scan exemptions)
- A surface not in any of these three lists is **UNREGISTERED** — it cannot be tracked, ratcheted, or enforced
- **Currently unregistered**: `neo4j`, `prometheus_client` (neither in FORBIDDEN_IMPORTS nor in any approved/sanctioned list)

### R6 — No Unclear Ownership
- Every infra client with an active import MUST have a declared owner layer
- Owner layer MUST have a sanctioned adapter file
- A raw import with no declared owner is a DORMANT_UNWIRED or EXPERIMENTAL_ISOLATED state and MUST be tracked in the scorecard
- **Currently unregistered state**: `neo4j_store.py` (zero ADG callers, no approved adapter, EXPERIMENTAL_ISOLATED but not in scorecard)

### R7 — Graceful Degradation for Optional Infra
- Optional infra (OTel, BGE embeddings, boto3/S3) SHOULD use `try/except ImportError` + availability flag pattern
- Hard infra (Redis, SQLite for ADG) SHOULD fail fast on missing dep
- `neo4j_store.py` VIOLATES this rule: it intends to be optional (guardian comment) but re-raises ImportError making it hard-fail

---

## D. Exemptions and Edge Cases

### D1 — `agentic_core/cache/` Exemption (Redis)
- `agentic_core/cache/redis_cache_client.py` and all files in `agentic_core/cache/` are formally exempt from the "agentic_core may not own raw infra" rule
- Basis: `AGENTIC_CORE_INFRA_SUBDIRS = ("adg", "cache", "embeddings")` in `infra_wiring_scan.py`
- `agentic_core/cache/core/redis_cache_client.py` is also in this subdirectory but is NOT in `_APPROVED_ADAPTER_PATHS` — this is a view coverage gap, not a policy violation

### D2 — `agentic_core/embeddings/` Exemption (Provider SDKs)
- `agentic_core/embeddings/embedding_factory.py` is in `_PROVIDER_EXEMPT_PREFIXES` — it may import `openai`, `anthropic`, `sentence_transformers` directly
- No other agentic_core subdirectory shares this exemption

### D3 — Process-Boundary Adapters (P1 Zero-Caller Exemption)
These adapters have zero Python import-chain callers by design (process-boundary invocation). Formally exempt from P1-zero-caller and P1-not-on-spine checks:

| Adapter | Why No Callers | Exemption Status |
|---|---|---|
| `infrastructure/sdks_mcps/__init__.py` | Launched as MCP server process | ✅ EXEMPT |
| `tools/mcp/enhanced_http_server.py` | Launched as MCP server process | ✅ EXEMPT |
| `agentic_core/L4_state/utils/memory/canonical_store.py` | Accessed via filesystem path, no static import chain | ✅ EXEMPT |
| `agentic_core/L3_orchestration/reasoning/engines/sovereign_redis_orchestrator.py` | Instantiated via registry, not static import | ✅ EXEMPT |
| `apps_shared/data_adapters/repo_signal_adapter.py` | Instantiated by collection scripts | ✅ EXEMPT (read-only) |

### D4 — `infrastructure/sdks_mcps/__init__.py` Migration Status
- File comment at line 40: **"Temporary minimal wrapper functions for migration"**
- `create_openai_client()`, `create_anthropic_client()`, `create_vertex_client()` are REAL, thin, working wrappers (lazy imports, env-key checks)
- `OpenAIClient`, `AnthropicClient`, `VertexClient` classes are **empty `pass` stubs** — they are NOT wrappers; they have no behavior
- `OpenAIConfig`, `AnthropicConfig`, `VertexConfig` classes are **empty `pass` stubs**
- Consumers MUST use factory functions, NOT class instantiation
- The `__all__` list exports the stub classes, which may mislead consumers

### D5 — `retrieval_layers.py` Mixed Usage (P2 Accepted)
- `agentic_core/L4_state/reasoning/retrieval_layers.py` has TWO raw infra imports at module level:
  - `import chromadb` (line 20) — P2 mixed usage (ChromaDB has SovereignChromaClient adapter)
  - `from openai import OpenAI` (line 21) — provider bypass (L4 is NOT in `_PROVIDER_EXEMPT_PREFIXES`)
- The chromadb raw import is captured in the P2 mixed-usage ceiling (3 accepted)
- The OpenAI raw import is **not captured** in the current P2 ceiling — it is a gap

### D6 — `neo4j_store.py` Broken Guard Pattern
- `neo4j_store.py` lines 88–94 have a try/except where the except block **re-raises** rather than swallowing
- `GraphDatabase = None` at line 94 is **unreachable dead code** (after `raise`)
- The `# guardian: allow-silent-swallow` comment is misapplied — there is no silent swallow
- The only caller (`rank_observability_components_util.py`) guards with `except (ValueError, TypeError, RuntimeError)` — which does NOT catch `ImportError`
- If `neo4j` is not installed: `neo4j_store.py` fails to import → `rank_observability_components_util.py` also fails to import (exception propagation on `ImportError`)
- This is a **hard failure chain** disguised as optional code

### D7 — `open_telemetry_tracing_adapter_util.py` — Correct Canonical Adapter
- Lines 93–118: proper try/except ImportError with `OTEL_AVAILABLE = False` fallback
- All three export paths gracefully degrade: OTLP gRPC (`OTEL_GRPC_EXPORTER_AVAILABLE`), OTLP HTTP (`OTEL_HTTP_EXPORTER_AVAILABLE`), console (always)
- `apps_shared/mixins/apps_tracing_mixin.py` imports `from opentelemetry import trace` directly — this bypasses the canonical adapter and will fail hard if opentelemetry is not installed (no try/except guard in mixin)

### D8 — `semantic_enricher.py` Lazy Provider Import (Risk Level)
- `from openai import OpenAI` inside `_init_default_client()` (line 136) — properly guarded with `except ImportError` → `llm_client = None`
- Graceful degradation is present; the risk is **policy** (wrong import path), not stability
- `agentic_core/knowledge/enrichment/` is NOT in `_PROVIDER_EXEMPT_PREFIXES`
- Should route via `infrastructure/sdks_mcps.create_openai_client()` or `agentic_core/embeddings/embedding_factory.py`

### D9 — Feature Flags (No External Infra)
- Both flag stores (`system_learning/config/feature_flags.py` and `agentic_core/runtime/config`) are pure Python env-variable-driven
- No external LaunchDarkly / Unleash / Flipper dependency exists
- Feature flags are NOT infra in the same sense as Redis/SQLite — no raw SDK import needed
- Included in scope because the SR_PLAN specified "feature/config control planes"

---

## E. Delta vs Current Scorecard and Registry Coverage

### What the Current Scorecard (`artifacts/infra_wiring_scorecard.json`) Misses

| Gap | Current State | Required Action |
|---|---|---|
| Neo4j surface | Not tracked anywhere (not in FORBIDDEN_IMPORTS, not in scorecard) | Add `neo4j` to FORBIDDEN_IMPORTS or add to SANCTIONED_ADAPTER_FILES; add to scorecard as P3/EXPERIMENTAL_ISOLATED |
| Prometheus surface | Not tracked anywhere | Add `prometheus_client` to FORBIDDEN_IMPORTS; declare `agentic_core/L6_observability/utils/metrics/prometheus_metrics.py` as sanctioned adapter |
| vLLM/aiohttp in L3 | Not in SANCTIONED_ADAPTER_FILES; not in scorecard | Add `optimized_vllm_client.py` to SANCTIONED_ADAPTER_FILES or remove raw aiohttp; needs ownership ruling |
| OpenAI raw import in `retrieval_layers.py` | Counted in P2 mixed usage (chromadb aspect) but the OpenAI aspect is not captured | The OpenAI raw import at L4 needs its own P2 or P1 entry |
| Google raw import in `agentic_core/evaluation/judges/` | `v_p0_provider_bypass` shows 0 — these files are not being counted | Either add `agentic_core/evaluation/` to `_PROVIDER_EXEMPT_PREFIXES` (needs decision) or count as P0 provider bypass |
| `semantic_enricher.py` raw openai | Not in any list | Add to SANCTIONED_ADAPTER_FILES or route via `create_openai_client()` |
| `apps_rfp` ChromaDB P0 | Still listed as ACTIVE_MISWIRED in prior matrix | Update to RESOLVED; state = ACTIVE_APPROVED |
| OTel canonical adapter | Prior matrix and scorecard named `tools/otel/otel_mcp_server.py`; actual canonical is `apps_shared/utils/open_telemetry_tracing_adapter_util.py` | Update `_APPROVED_ADAPTER_PATHS` to include canonical OTel path |
| `blob_storage_provider.py` adapter gap | In `SANCTIONED_ADAPTER_FILES` but not `_APPROVED_ADAPTER_PATHS` | Add to `_APPROVED_ADAPTER_PATHS` |
| `agentic_core/cache/core/redis_cache_client.py` | Counted in P2 duplicate ceiling but not in `_APPROVED_ADAPTER_PATHS` | Add to `_APPROVED_ADAPTER_PATHS` or remove duplicate |

### What the Forbidden/Approved Registries Fail to Encode

| Registry Gap | File | Missing Entry |
|---|---|---|
| `FORBIDDEN_IMPORTS` in `infra_wiring_scan.py` | — | `neo4j`, `prometheus_client`, `aiohttp` (vLLM case) |
| `_APPROVED_ADAPTER_PATHS` in `infra_wiring_views.py` | `agentic_core/L6_observability/utils/metrics/prometheus_metrics.py` | Missing — no approved Prometheus adapter entry |
| `_APPROVED_ADAPTER_PATHS` | `agentic_core/L4_state/utils/memory/blob_storage_provider.py` | Missing — in SANCTIONED but not in APPROVED |
| `_APPROVED_ADAPTER_PATHS` | `agentic_core/cache/core/redis_cache_client.py` | Missing — duplicate adapter not in approved list |
| `_PROVIDER_EXEMPT_PREFIXES` | `agentic_core/evaluation/` | Missing — but decision required (exempt or enforce) |
| `_PROCESS_BOUNDARY_ADAPTERS` | `apps_shared/utils/open_telemetry_tracing_adapter_util.py` | Should be listed as canonical OTel adapter |
| `SANCTIONED_ADAPTER_FILES` | `optimized_vllm_client.py` | Missing — raw aiohttp in L3 not sanctioned |

### What Must Become ADG Relations or CI Gates Later (Not Guesswork)

| Future Gate | ADG Relation Needed | CI Check |
|---|---|---|
| Prometheus surface tracking | `v_prometheus_unregistered` view; add `prometheus_client` to scanner | Gate: no new prometheus_client imports outside L6 |
| Neo4j state enforcement | Add `neo4j` to FORBIDDEN_IMPORTS; ADG node for `neo4j_store.py` | Gate: zero neo4j imports outside sanctioned path |
| Provider bypass in `agentic_core/evaluation/` | ADG edge: `v_p0_provider_bypass` must include `agentic_core/evaluation/` | Decision: add to exempt OR add to P0 gate |
| vLLM HTTP client in L3 | `uses_raw_http_client` edge for `optimized_vllm_client.py` | Gate: no raw aiohttp in agentic_core/L* outside gateway |
| OTel adapter path correction | Update `_APPROVED_ADAPTER_PATHS` in `infra_wiring_views.py` | Gate: `v_p0_provider_bypass` must correctly recognize OTel canonical path |

---

## F. Open Ambiguities Requiring Later ADG Enforcement

These cannot be resolved by documentation alone. Each requires an explicit decision before ADG relations or CI gates can be defined.

1. **Neo4j: deprecate or formalize?** — `neo4j_store.py` exists in L4 enforcement with a broken guard pattern and zero ADG callers. Two paths: (a) formally declare it DEPRECATED_PENDING_REMOVAL and add `neo4j` to FORBIDDEN_IMPORTS, or (b) formally approve it with a real optional-dependency guard and declared owner. Cannot remain unregistered.

2. **vLLM/aiohttp in L3: permanent or temporary?** — `optimized_vllm_client.py` is a real HTTP client for local vLLM inference (references `http://localhost:8000/v1`). If vLLM inference is a permanent feature, this needs a sanctioned HTTP seam in L3 (either add to SANCTIONED_ADAPTER_FILES or route via `enhanced_http_server.py`). If temporary/local-only, it should be removed or moved to tools/.

3. **`agentic_core/evaluation/` provider exemption decision** — `agentic_core/evaluation/judges/` uses `google.generativeai` directly. Two paths: (a) add `agentic_core/evaluation/` to `_PROVIDER_EXEMPT_PREFIXES` (evaluation harness is a legitimate provider consumer), or (b) require it to route via `infrastructure/sdks_mcps.create_vertex_client()`. The current scorecard counts `v_p0_provider_bypass = 0` suggesting the ADG view does not currently detect this — either the view's SQL is not matching these files, or they are already informally exempt.

4. **`infrastructure/sdks_mcps` migration completion** — The file comments "temporary minimal wrapper for migration." Unknown when migration completes. The empty stub classes (`OpenAIClient`, etc.) are in `__all__` and may mislead consumers. A migration completion marker or a formal stub-removal timeline is needed.

5. **Feature flag convergence** — Two flag stores with no documented relationship. `agentic_core/runtime/config` and `system_learning/config/feature_flags.py` may be converging or intentionally parallel. No ADG check can enforce consistency without knowing the intended relationship.

6. **Prometheus adapter formalization** — `prometheus_metrics.py` at L6 acts as the de facto adapter (defines `AGENTIC_REGISTRY`). If formally declared an approved adapter, it needs to be in `_APPROVED_ADAPTER_PATHS` and `prometheus_client` needs to be in `FORBIDDEN_IMPORTS` with `agentic_core/L6_observability/` as the only permitted direct-import path.

7. **`apps_tracing_mixin.py` direct OTel import** — This bypasses the `get_tracer()` canonical path and will hard-fail if opentelemetry is not installed (no guard). Decision: either add a try/except guard here, or redirect to `get_tracer()`. Low priority but needs resolution before OTel becomes a hard dependency in CI.

---

*Stop condition reached — Phase 1 ownership matrix and policy contract complete. ADG relation additions, CI gate changes, and code repairs deferred to subsequent phases.*
