# Infrastructure Wiring Inventory
**Generated:** 2026-04-08
**Purpose:** Baseline inventory of all infrastructure surfaces in Agentic-Workflow repository

## Executive Summary

This inventory catalogs all infrastructure surfaces (Redis, SQLite, ChromaDB, OpenAI, Anthropic, HTTP clients, Boto3, OpenTelemetry, Google, Pytest) across the codebase. Each surface is classified by owner layer, intended role, active consumers, adapter reachability, and wiring status.

**Total Surfaces Identified:** 10 infrastructure classes
**Active Approved:** 7
**Active Miswired:** 2
**Dormant Unwired:** 1
**Experimental Isolated:** 0
**Deprecated Pending Removal:** 0

---

## Raw Infrastructure Entrypoints

### 1. Redis (Caching/Coordination)
**Primary Files:**
- `agentic_core/cache/redis_cache_client.py` - DeterministicRedisCache (L2 cache adapter)
- `agentic_core/L2_execution/reasoning/RedisSovereignAgent.py` - RedisSovereignAgent (L2 execution agent)
- `tools/adg/cache/redis_cache.py` - ADG Redis hot cache (tools layer)
- `tools/memory/adg_memory_server.py` - Memory MCP Redis backend (tools layer)
- `tools/mcp/redis_mcp_server.py` - Redis MCP server (tools layer)

**Layer Assignment:**
- **Owner Layer:** L2 (Execution) - RedisSovereignAgent
- **Adapter Layer:** L2 - redis_cache_client.py
- **Tools Layer:** tools/adg, tools/memory, tools/mcp (MCP infrastructure)

**Intended Role:**
- Hot cache for L0/L1/L3/L5 routing, execution, orchestration, safety
- Coordination leases for L2 execution locks
- Operational workspace for per-trace, team-sync, replay-assist, novelty

**Active Consumers:**
- RedisSovereignAgent (L2)
- EmbeddingSovereignAgent (L2) - via RedisCacheMixin
- SovereignRedisOrchestrator (L3)
- CachedStateLedger (L4)
- ADG query services (tools)
- Memory MCP server (tools)

**Adapter Reachability:** ✅ APPROVED - DeterministicRedisCache is the sanctioned adapter

**apps_* Direct Imports:** ❌ NONE detected

**Weak Architecture Edges:** ⚠️ Multiple direct redis.Redis imports in tools layer (acceptable for infrastructure code)

**Status:** ACTIVE_APPROVED

---

### 2. SQLite (Relational Storage)
**Primary Files:**
- `tools/memory/sqlite_memory_store.py` - Memory graph persistence (tools layer)
- `tools/utils/query_violations.py` - Violation query tool (tools layer)
- `tools/guardian/guardian_sweep.py` - Guardian analysis (tools layer)
- `tools/generate/generate_*.py` - ADG generation scripts (tools layer)

**Layer Assignment:**
- **Owner Layer:** L4 (State) - canonical storage layer
- **Adapter Layer:** tools/memory (infrastructure wrapper)
- **Tools Layer:** tools/utils, tools/guardian, tools/generate (tooling infrastructure)

**Intended Role:**
- Memory graph persistence (knowledge graph)
- ADG artifact storage (indexed SQLite)
- Violation tracking and analysis
- Guardian anti-pattern detection storage

**Active Consumers:**
- Memory MCP server (mcp6)
- ADG generation pipeline
- Guardian analysis tools
- Violation query tools

**Adapter Reachability:** ✅ APPROVED - sqlite_memory_store.py is the sanctioned adapter

**apps_* Direct Imports:** ❌ NONE detected

**Weak Architecture Edges:** ⚠️ Direct sqlite3 imports in tools layer (acceptable for infrastructure code)

**Status:** ACTIVE_APPROVED

---

### 3. ChromaDB (Vector Database)
**Primary Files:**
- `agentic_core/L4_state/utils/client/chroma_client.py` - SovereignChromaClient (L4 state client)
- `tools/mcp/vector_db_server.py` - Vector DB MCP server (tools layer)
- `apps_rfp/engines/proposal_retrieval_engine.py` - RFP retrieval engine (apps layer)

**Layer Assignment:**
- **Owner Layer:** L4 (State) - SovereignChromaClient
- **Adapter Layer:** L4 - chroma_client.py
- **Tools Layer:** tools/mcp (MCP infrastructure)
- **Apps Layer:** apps_rfp (application surface)

**Intended Role:**
- Persistent semantic memory layer
- Document retrieval for RFP applications
- Fallback hash-based embeddings (Wave 1)

**Active Consumers:**
- RetrievalLayers (L4)
- ProposalRetrievalEngine (apps_rfp)
- Vector DB MCP server

**Adapter Reachability:** ✅ APPROVED - SovereignChromaClient is the sanctioned adapter

**apps_* Direct Imports:** ⚠️ YES - apps_rfp/engines/proposal_retrieval_engine.py imports chromadb directly

**Weak Architecture Edges:** ⚠️ Direct chromadb import in apps_rfp (should use L4 adapter)

**Status:** ACTIVE_MISWIRED (apps_* direct import violation)

---

### 4. OpenAI (Model Provider)
**Primary Files:**
- `system_learning/engines/openai_embedder.py` - OpenAIEmbedder (system_learning layer)
- `agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py` - EmbeddingSovereignAgent (L2 execution)
- `agentic_core/embeddings/embedding_factory.py` - Embedding client factory (L2 infrastructure)

**Layer Assignment:**
- **Owner Layer:** L2 (Execution) - EmbeddingSovereignAgent
- **Adapter Layer:** L2 - embedding_factory.py
- **System Learning Layer:** system_learning/engines (meta-learning infrastructure)

**Intended Role:**
- Text embedding generation (text-embedding-3-large, text-embedding-3-small)
- Semantic search embeddings
- Meta-learning embedding pipeline

**Active Consumers:**
- EmbeddingSovereignAgent (L2)
- SemanticRetriever (L1)
- EmbeddingSovereignAgent (L2) - via factory
- OpenAIEmbedder (system_learning)

**Adapter Reachability:** ✅ APPROVED - embedding_factory.py is the sanctioned adapter

**apps_* Direct Imports:** ❌ NONE detected

**Weak Architecture Edges:** ⚠️ Direct openai import in system_learning/engines (acceptable for meta-learning infrastructure)

**Status:** ACTIVE_APPROVED

---

### 5. Anthropic (Model Provider)
**Primary Files:**
- `infrastructure/sdks_mcps/__init__.py` - Anthropic client wrapper (infrastructure layer)
- `apps_shared/types/model_router_types.py` - Model router types (apps_shared layer)

**Layer Assignment:**
- **Owner Layer:** infrastructure/sdks_mcps (infrastructure abstraction layer)
- **Adapter Layer:** infrastructure/sdks_mcps
- **Apps Shared Layer:** apps_shared/types (shared types)

**Intended Role:**
- Anthropic Claude model access
- Model routing abstraction
- Provider-agnostic model interface

**Active Consumers:**
- Model router (apps_shared)
- Infrastructure MCP wrappers

**Adapter Reachability:** ✅ APPROVED - infrastructure/sdks_mcps is the sanctioned adapter

**apps_* Direct Imports:** ❌ NONE detected (apps_shared is shared infrastructure, not application surface)

**Weak Architecture Edges:** None identified

**Status:** ACTIVE_APPROVED

---

### 6. HTTP Clients (httpx/requests)
**Primary Files:**
- `tools/mcp/enhanced_http_server.py` - Enhanced HTTP MCP server (tools layer)
- `agentic_core/gateway/api_gateway_integration.py` - API gateway integration (L0/L1 boundary)
- `agentic_core/mixins/cst_healer_mixin.py` - CST healer mixin (L2 execution)

**Layer Assignment:**
- **Owner Layer:** L0 (Routing) - API gateway integration
- **Adapter Layer:** tools/mcp (MCP infrastructure)
- **Execution Layer:** L2 - CST healer mixin

**Intended Role:**
- External API calls
- Gateway integration
- Healing API calls
- MCP HTTP capabilities

**Active Consumers:**
- API gateway (L0/L1)
- CST healer (L2)
- Enhanced HTTP MCP server

**Adapter Reachability:** ✅ APPROVED - enhanced_http_server.py is the sanctioned adapter

**apps_* Direct Imports:** ❌ NONE detected

**Weak Architecture Edges:** None identified

**Status:** ACTIVE_APPROVED

---

### 7. Boto3 (AWS SDK)
**Primary Files:**
- `agentic_core/L4_state/utils/memory/canonical_store.py` - Canonical state store (L4 state)
- `agentic_core/L4_state/utils/memory/blob_storage_provider.py` - Blob storage provider (L4 state)

**Layer Assignment:**
- **Owner Layer:** L4 (State) - canonical_store.py, blob_storage_provider.py
- **Adapter Layer:** L4 - both files serve as adapters

**Intended Role:**
- AWS S3 blob storage
- Canonical state persistence
- Durable write backend

**Active Consumers:**
- State ledger (L4)
- Blob storage consumers (L4)

**Adapter Reachability:** ✅ APPROVED - Both files are sanctioned L4 adapters

**apps_* Direct Imports:** ❌ NONE detected

**Weak Architecture Edges:** None identified

**Status:** ACTIVE_APPROVED

---

### 8. OpenTelemetry (Observability)
**Primary Files:**
- `tools/otel/otel_mcp_server.py` - OTel MCP server (tools layer)
- `system_learning/stores/otel_telemetry_store.py` - OTel telemetry store (system_learning layer)
- `apps_shared/mixins/apps_tracing_mixin.py` - Apps tracing mixin (apps_shared layer)
- `agentic_core/mixins/integrated_tracing_mixin.py` - Integrated tracing mixin (agentic_core layer)

**Layer Assignment:**
- **Owner Layer:** L6 (Observability) - telemetry_store.py
- **Adapter Layer:** tools/otel (MCP infrastructure)
- **System Learning Layer:** system_learning/stores (meta-learning infrastructure)
- **Apps Shared Layer:** apps_shared/mixins (shared tracing)
- **Agentic Core Layer:** agentic_core/mixins (core tracing)

**Intended Role:**
- Distributed tracing
- Telemetry collection
- Observability data storage
- Performance monitoring

**Active Consumers:**
- OTel MCP server
- Telemetry store (system_learning)
- Apps tracing (apps_shared)
- Core tracing (agentic_core)

**Adapter Reachability:** ✅ APPROVED - otel_mcp_server.py is the sanctioned adapter

**apps_* Direct Imports:** ❌ NONE detected (apps_shared is shared infrastructure)

**Weak Architecture Edges:** None identified

**Status:** ACTIVE_APPROVED

---

### 9. Google (Gemini/Vertex AI)
**Primary Files:**
- `infrastructure/sdks_mcps/__init__.py` - Google GenAI client wrapper (infrastructure layer)
- `apps_shared/utils/providers_google_genai_client_util.py` - Google GenAI client utility (apps_shared layer)
- `agentic_core/evaluation/judges/provider_registry.py` - Provider registry (L5 safety)

**Layer Assignment:**
- **Owner Layer:** infrastructure/sdks_mcps (infrastructure abstraction layer)
- **Adapter Layer:** infrastructure/sdks_mcps
- **Apps Shared Layer:** apps_shared/utils (shared utilities)
- **Safety Layer:** L5 - provider_registry.py

**Intended Role:**
- Gemini embeddings
- Vertex AI model access
- Provider abstraction
- Evaluation judge integration

**Active Consumers:**
- EmbeddingSovereignAgent (L2) - via infrastructure wrapper
- Provider registry (L5)
- Apps shared utilities

**Adapter Reachability:** ✅ APPROVED - infrastructure/sdks_mcps is the sanctioned adapter

**apps_* Direct Imports:** ❌ NONE detected (apps_shared is shared infrastructure)

**Weak Architecture Edges:** None identified

**Status:** ACTIVE_APPROVED

---

### 10. Pytest (Testing Framework)
**Primary Files:**
- `tools/mcp/pytest_server.py` - Pytest MCP server (tools layer)
- `tools/generate/generate_test_stubs.py` - Test stub generator (tools layer)

**Layer Assignment:**
- **Owner Layer:** tools/mcp (MCP infrastructure)
- **Tools Layer:** tools/generate (tooling infrastructure)

**Intended Role:**
- Test execution via MCP
- Test stub generation
- Test discovery and running

**Active Consumers:**
- Pytest MCP server
- Test generation tools

**Adapter Reachability:** ✅ APPROVED - pytest_server.py is the sanctioned adapter

**apps_* Direct Imports:** ❌ NONE detected

**Weak Architecture Edges:** None identified

**Status:** ACTIVE_APPROVED

---

## Infrastructure Surface Classification Table

| Infra Surface | Owner Layer | Adapter Layer | Approved Entrypoints | Approved Callers | apps_* Direct Import? | Status |
|--------------|-------------|---------------|---------------------|------------------|----------------------|---------|
| Redis | L2 | L2 (redis_cache_client.py) | DeterministicRedisCache, RedisSovereignAgent | L2, L3, L4, tools | ❌ NO | ACTIVE_APPROVED |
| SQLite | L4 | tools/memory (sqlite_memory_store.py) | SqliteMemoryStore | tools, MCP | ❌ NO | ACTIVE_APPROVED |
| ChromaDB | L4 | L4 (chroma_client.py) | SovereignChromaClient | L4, tools, apps_rfp | ⚠️ YES (apps_rfp) | ACTIVE_MISWIRED |
| OpenAI | L2 | L2 (embedding_factory.py) | EmbeddingSovereignAgent, OpenAIEmbedder | L1, L2, system_learning | ❌ NO | ACTIVE_APPROVED |
| Anthropic | infrastructure | infrastructure/sdks_mcps | AnthropicClientWrapper | apps_shared, infrastructure | ❌ NO | ACTIVE_APPROVED |
| HTTP Clients | L0 | tools/mcp (enhanced_http_server.py) | EnhancedHTTPMCP, APIGateway | L0, L1, L2, tools | ❌ NO | ACTIVE_APPROVED |
| Boto3 (AWS) | L4 | L4 (canonical_store.py, blob_storage_provider.py) | CanonicalStore, BlobStorageProvider | L4 | ❌ NO | ACTIVE_APPROVED |
| OpenTelemetry | L6 | tools/otel (otel_mcp_server.py) | OTelMCPServer, TelemetryStore | L6, system_learning, apps_shared, agentic_core | ❌ NO | ACTIVE_APPROVED |
| Google (Gemini) | infrastructure | infrastructure/sdks_mcps | GoogleGenAIWrapper | L2, L5, apps_shared | ❌ NO | ACTIVE_APPROVED |
| Pytest | tools | tools/mcp (pytest_server.py) | PytestMCPServer | tools | ❌ NO | ACTIVE_APPROVED |

---

## apps_* Direct Import Violations

### P0 HARD FAIL: apps_rfp ChromaDB Direct Import
**File:** `apps_rfp/engines/proposal_retrieval_engine.py`
**Violation:** Direct `import chromadb` instead of using L4 SovereignChromaClient adapter
**Architecture Law Violated:** apps_* surfaces must not directly own raw infra clients
**Recommended Fix:** Import from `agentic_core.L4_state.utils.client.chroma_client` instead of direct chromadb
**Expected ADG Edge Change:** Remove `apps_rfp → chromadb` edge, add `apps_rfp → L4_chroma_client` edge

---

## Uncertainties and Assumptions

### Uncertainties
1. **ChromaDB Fallback Status:** The SovereignChromaClient uses hash-based fallback embeddings. It's unclear if this is temporary (Wave 1) or permanent.
2. **Boto3 Usage Extent:** Only two files import boto3, but the actual AWS usage pattern is not fully mapped.
3. **OpenTelemetry Collector:** The OTel MCP server exists, but collector connectivity status is unknown.

### Assumptions
1. **tools Layer as Infrastructure:** All files under `tools/` are treated as infrastructure/tooling, not production authority surfaces.
2. **apps_shared as Shared Infrastructure:** `apps_shared/` is treated as shared infrastructure layer, not application surface.
3. **Direct Imports in tools Layer:** Direct SDK imports in `tools/` layer are acceptable for infrastructure code.
4. **Memory MCP as Infrastructure:** Memory graph persistence via SQLite is treated as infrastructure, not application state.

---

## Next Steps

1. **Phase 1:** Create ownership matrix defining allowed layer ownership and caller policies
2. **Phase 2:** Enrich ADG with infra-specific relations (owns_infra_surface, wraps_infra_surface, uses_raw_infra_client, etc.)
3. **Phase 3:** Generate severity-ranked violations using ADG queries
4. **Phase 4:** Create prioritized repair plan for miswired surfaces
5. **Phase 5:** Design CI ratchet and scorecard for regression prevention
