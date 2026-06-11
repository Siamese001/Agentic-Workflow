---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\infra_adg_enrichment.md'
original_relative_path: 'infra_adg_enrichment.md'
source_sha256: c4aab2e9ed6c6793019e80f4c9507fef4f9f41c50a01415d39e18b1795257dbf
recovered_status: LOST_RECOVERED
last_commit: 'e08d9e2d38a'
last_commit_date: '2026-04-08 17:27:54 -0400'
created_date: '2026-04-08'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG Enrichment for Infrastructure Wiring
**Generated:** 2026-04-08
**Purpose:** Define structural relations to teach ADG to see infrastructure wiring, not just generic imports

## Executive Summary

This document defines new ADG structural relations required to detect infrastructure wiring violations. These relations extend the existing import/call graph with infrastructure-specific semantics to enable automated enforcement of the ownership matrix defined in Phase 1.

**Relations to Add:** 12 new relation types
**Extraction Strategy:** Concrete, conservative, based on file/symbol evidence
**Implementation Priority:** High (required for Phase 3 violation detection)

---

## Proposed New Structural Relations

### 1. owns_infra_surface
**Description:** A layer or module owns a specific infrastructure surface
**Direction:** layer/module → infra_surface
**Example:** L2 → Redis, L4 → ChromaDB
**Extraction Logic:**
- Map files to layers based on directory structure (agentic_core/L0, L1, L2, etc.)
- Identify infra surface by import pattern (import redis, import chromadb, etc.)
- Create edge from layer node to infra surface node
**SQLite Query:**
```sql
SELECT 
    n1.id as layer_id,
    n1.file_path as layer_file,
    n2.id as infra_surface_id,
    n2.file_path as infra_file
FROM nodes n1, nodes n2
WHERE n1.layer IN ('L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6')
  AND n2.file_path LIKE '%redis_cache_client.py'
  AND n2.file_path LIKE '%agentic_core%'
```

### 2. wraps_infra_surface
**Description:** An adapter/wrapper class wraps a raw infrastructure client
**Direction:** adapter_class → raw_infra_client
**Example:** DeterministicRedisCache → redis.Redis, SovereignChromaClient → chromadb.PersistentClient
**Extraction Logic:**
- Identify adapter classes by naming pattern (DeterministicRedisCache, SovereignChromaClient, etc.)
- Identify raw infra client by import statement (import redis, import chromadb)
- Create edge from adapter class node to infra surface node
**SQLite Query:**
```sql
SELECT 
    n1.id as adapter_id,
    n1.name as adapter_name,
    n2.id as infra_id,
    n2.name as infra_name
FROM nodes n1, nodes n2, edges e
WHERE n1.type = 'class'
  AND n1.name LIKE '%Cache%' OR n1.name LIKE '%Client%' OR n1.name LIKE '%Wrapper%'
  AND e.relation_type = 'imports'
  AND e.src_id = n1.id
  AND e.tgt_id = n2.id
  AND n2.name IN ('redis', 'chromadb', 'sqlite3', 'boto3', 'openai', 'anthropic')
```

### 3. uses_raw_infra_client
**Description:** A module or class directly imports and uses a raw infrastructure client (P0 violation)
**Direction:** consumer → raw_infra_client
**Example:** apps_rfp/engines/proposal_retrieval_engine.py → chromadb
**Extraction Logic:**
- Detect direct imports of infra SDKs (import redis, import chromadb, import boto3, etc.)
- Exclude files in tools/ and infrastructure/ layers (allowed there)
- Flag imports in agentic_core/ and apps_* layers as violations
**SQLite Query:**
```sql
SELECT 
    n1.id as consumer_id,
    n1.file_path as consumer_file,
    n2.id as infra_id,
    n2.name as infra_name
FROM nodes n1, nodes n2, edges e
WHERE e.relation_type = 'imports'
  AND e.src_id = n1.id
  AND e.tgt_id = n2.id
  AND n2.name IN ('redis', 'chromadb', 'sqlite3', 'boto3', 'openai', 'anthropic', 'httpx', 'requests')
  AND n1.file_path NOT LIKE 'tools/%'
  AND n1.file_path NOT LIKE 'infrastructure/%'
```

### 4. uses_approved_infra_adapter
**Description:** A module or class uses a sanctioned infrastructure adapter
**Direction:** consumer → approved_adapter
**Example:** RedisSovereignAgent → DeterministicRedisCache
**Extraction Logic:**
- Identify approved adapters from ownership matrix (redis_cache_client.py, chroma_client.py, etc.)
- Detect imports of these adapter classes
- Create edge from consumer to adapter
**SQLite Query:**
```sql
SELECT 
    n1.id as consumer_id,
    n1.file_path as consumer_file,
    n2.id as adapter_id,
    n2.file_path as adapter_file
FROM nodes n1, nodes n2, edges e
WHERE e.relation_type = 'imports'
  AND e.src_id = n1.id
  AND e.tgt_id = n2.id
  AND n2.file_path IN (
    'agentic_core/cache/redis_cache_client.py',
    'agentic_core/L4_state/utils/client/chroma_client.py',
    'agentic_core/embeddings/embedding_factory.py',
    'infrastructure/sdks_mcps/__init__.py',
    'tools/mcp/enhanced_http_server.py'
  )
```

### 5. bypasses_infra_adapter
**Description:** A module bypasses the sanctioned adapter and uses raw client directly
**Direction:** consumer → raw_infra_client (with bypass flag)
**Example:** apps_rfp/engines/proposal_retrieval_engine.py → chromadb (bypasses SovereignChromaClient)
**Extraction Logic:**
- Combine uses_raw_infra_client with layer check
- If consumer is in apps_* or agentic_core and raw import exists, flag as bypass
- Check if approved adapter exists in same layer
**SQLite Query:**
```sql
SELECT 
    n1.id as consumer_id,
    n1.file_path as consumer_file,
    n2.id as infra_id,
    n2.name as infra_name
FROM nodes n1, nodes n2, edges e
WHERE e.relation_type = 'imports'
  AND e.src_id = n1.id
  AND e.tgt_id = n2.id
  AND n2.name IN ('redis', 'chromadb', 'sqlite3', 'boto3', 'openai', 'anthropic')
  AND n1.file_path LIKE 'apps_%/'
  AND NOT EXISTS (
    SELECT 1 FROM edges e2, nodes n3
    WHERE e2.relation_type = 'imports'
      AND e2.src_id = n1.id
      AND e2.tgt_id = n3.id
      AND n3.file_path IN (
        'agentic_core/cache/redis_cache_client.py',
        'agentic_core/L4_state/utils/client/chroma_client.py'
      )
  )
```

### 6. provider_path_bypasses_control_plane
**Description:** Provider SDK usage bypasses the infrastructure/sdks_mcps control plane
**Direction:** consumer → provider_sdk (bypass)
**Example:** Direct openai import bypasses infrastructure/sdks_mcps wrapper
**Extraction Logic:**
- Detect direct provider SDK imports (openai, anthropic, google)
- Check if import is from infrastructure/sdks_mcps
- Flag non-infrastructure imports as bypass
**SQLite Query:**
```sql
SELECT 
    n1.id as consumer_id,
    n1.file_path as consumer_file,
    n2.id as provider_id,
    n2.name as provider_name
FROM nodes n1, nodes n2, edges e
WHERE e.relation_type = 'imports'
  AND e.src_id = n1.id
  AND e.tgt_id = n2.id
  AND n2.name IN ('openai', 'anthropic', 'google')
  AND n1.file_path NOT LIKE 'infrastructure/sdks_mcps/%'
  AND n1.file_path NOT LIKE 'tools/%'
  AND n1.file_path NOT LIKE 'system_learning/%'
```

### 7. write_path_bypasses_uwg
**Description:** Write operation bypasses Universal Write Gate (UWG)
**Direction:** writer → infra_surface (bypass)
**Example:** Direct SQLite write without UWG
**Extraction Logic:**
- Identify write operations (execute, commit, set, insert, update, delete)
- Check if write goes through sanctioned adapter
- Flag direct writes to infra as UWG bypass
**SQLite Query:**
```sql
SELECT 
    n1.id as writer_id,
    n1.file_path as writer_file,
    n2.id as infra_id,
    n2.name as infra_name
FROM nodes n1, nodes n2, edges e
WHERE e.relation_type = 'calls'
  AND e.src_id = n1.id
  AND e.tgt_id = n2.id
  AND n2.name IN ('execute', 'commit', 'set', 'insert', 'update', 'delete')
  AND n1.file_path NOT LIKE '%cache%'
  AND n1.file_path NOT LIKE '%adapter%'
  AND n1.file_path NOT LIKE 'tools/%'
```

### 8. infra_reachable_from_app
**Description:** Infrastructure surface is reachable from apps_* layer (check if approved)
**Direction:** apps_* module → infra_surface
**Example:** apps_rfp → ChromaDB (via SovereignChromaClient = approved, direct = violation)
**Extraction Logic:**
- Trace import/call graph from apps_* to infra
- Check if path goes through approved adapter
- Flag direct paths as violations
**SQLite Query:**
```sql
WITH RECURSIVE app_to_infra AS (
  SELECT 
    n1.id as app_id,
    n1.file_path as app_file,
    n2.id as target_id,
    n2.file_path as target_file,
    1 as hops,
    e.relation_type
  FROM nodes n1, nodes n2, edges e
  WHERE n1.file_path LIKE 'apps_%/'
    AND e.relation_type IN ('imports', 'calls')
    AND e.src_id = n1.id
    AND e.tgt_id = n2.id
  
  UNION ALL
  
  SELECT 
    a.app_id,
    a.app_file,
    n3.id,
    n3.file_path,
    a.hops + 1,
    e.relation_type
  FROM app_to_infra a, nodes n3, edges e
  WHERE e.relation_type IN ('imports', 'calls')
    AND e.src_id = a.target_id
    AND e.tgt_id = n3.id
    AND a.hops < 5
)
SELECT * FROM app_to_infra
WHERE target_file LIKE '%redis%' 
   OR target_file LIKE '%chromadb%'
   OR target_file LIKE '%sqlite%'
   OR target_file LIKE '%boto3%'
   OR target_file LIKE '%openai%'
   OR target_file LIKE '%anthropic%'
```

### 9. infra_has_no_approved_callers
**Description:** Infrastructure surface has zero approved callers (dormant infra)
**Direction:** infra_surface → (no callers)
**Example:** Old ChromaDB wrapper with no consumers
**Extraction Logic:**
- Count incoming edges to infra surface
- Check if any callers are in approved layers
- Flag infra with zero approved callers as dormant
**SQLite Query:**
```sql
SELECT 
    n1.id as infra_id,
    n1.file_path as infra_file,
    n1.name as infra_name,
    COUNT(e.tgt_id) as caller_count
FROM nodes n1
LEFT JOIN edges e ON e.tgt_id = n1.id
WHERE n1.file_path LIKE '%redis_cache_client.py'
   OR n1.file_path LIKE '%chroma_client.py'
   OR n1.file_path LIKE '%embedding_factory.py'
GROUP BY n1.id
HAVING caller_count = 0
```

### 10. infra_not_on_agentic_spine
**Description:** Infrastructure surface is not attached to the runtime agentic spine
**Direction:** infra_surface → (no spine attachment)
**Example:** Standalone infra script not used by agents
**Extraction Logic:**
- Check if infra surface is reachable from L0-L6 spine
- Flag infra with no spine attachment as isolated
**SQLite Query:**
```sql
SELECT 
    n1.id as infra_id,
    n1.file_path as infra_file,
    n1.name as infra_name
FROM nodes n1
WHERE n1.file_path LIKE '%redis%'
   OR n1.file_path LIKE '%chromadb%'
   OR n1.file_path LIKE '%sqlite%'
   OR n1.file_path LIKE '%boto3%'
   OR n1.file_path LIKE '%openai%'
   OR n1.file_path LIKE '%anthropic%'
  AND NOT EXISTS (
    SELECT 1 FROM edges e
    WHERE e.tgt_id = n1.id
      AND e.relation_type IN ('imports', 'calls')
  )
```

### 11. observability_surface_used_live_for_mutation
**Description:** L6 observability surface used for live state mutation (violation)
**Direction:** L6 module → mutable_operation
**Example:** OTel store used to mutate production state
**Extraction Logic:**
- Identify L6 modules (observability layer)
- Detect write operations (set, update, delete, execute)
- Flag L6 writes as violations (L6 should be read-only for telemetry)
**SQLite Query:**
```sql
SELECT 
    n1.id as l6_id,
    n1.file_path as l6_file,
    n2.id as operation_id,
    n2.name as operation_name
FROM nodes n1, nodes n2, edges e
WHERE n1.layer = 'L6'
  AND e.relation_type = 'calls'
  AND e.src_id = n1.id
  AND e.tgt_id = n2.id
  AND n2.name IN ('set', 'update', 'delete', 'execute', 'commit')
  AND n1.file_path NOT LIKE '%telemetry_store%'  -- telemetry writes are OK
```

### 12. mixed_direct_and_wrapped_usage
**Description:** Same infra surface used both directly and via adapter (inconsistent)
**Direction:** infra_surface → (mixed usage pattern)
**Example:** Some modules use redis.Redis, others use DeterministicRedisCache
**Extraction Logic:**
- Count direct imports of raw infra client
- Count imports of approved adapter
- If both > 0, flag as mixed usage
**SQLite Query:**
```sql
SELECT 
    n2.name as infra_name,
    COUNT(DISTINCT CASE 
      WHEN n2.file_path NOT LIKE '%cache%' 
           AND n2.file_path NOT LIKE '%adapter%'
           AND n2.file_path NOT LIKE 'tools/%'
      THEN n1.id 
    END) as direct_usage_count,
    COUNT(DISTINCT CASE 
      WHEN n2.file_path LIKE '%cache%' 
           OR n2.file_path LIKE '%adapter%'
      THEN n1.id 
    END) as wrapped_usage_count
FROM nodes n1, nodes n2, edges e
WHERE e.relation_type = 'imports'
  AND e.src_id = n1.id
  AND e.tgt_id = n2.id
  AND n2.name IN ('redis', 'chromadb', 'sqlite3', 'boto3', 'openai', 'anthropic')
GROUP BY n2.name
HAVING direct_usage_count > 0 
  AND wrapped_usage_count > 0
```

---

## Extraction Implementation Notes

### Conservative Extraction Strategy

1. **File-Based Detection:** Use file path patterns to identify layers and infra classes
2. **Import Pattern Matching:** Use AST import statements to detect infra usage
3. **Exclusion Lists:** Explicitly exclude tools/ and infrastructure/ from violation checks
4. **Layer Mapping:** Map directory structure to layers (agentic_core/L0 = L0, etc.)
5. **Adapter Registry:** Maintain explicit list of approved adapters from ownership matrix

### File Path to Layer Mapping

```
agentic_core/L0_* → L0 (Routing)
agentic_core/L1_* → L1 (Cognition/Reasoning)
agentic_core/L2_* → L2 (Execution)
agentic_core/L3_* → L3 (Orchestration)
agentic_core/L4_* → L4 (State)
agentic_core/L5_* → L5 (Safety)
agentic_core/L6_* → L6 (Observability)
infrastructure/sdks_mcps/* → infrastructure (Provider abstraction)
tools/* → tools (Infrastructure/tooling)
system_learning/* → system_learning (Meta-learning)
apps_*/* → apps_* (Application surfaces)
```

### Approved Adapter Registry

| Infra Surface | Approved Adapter File | Adapter Class |
|--------------|----------------------|---------------|
| Redis | agentic_core/cache/redis_cache_client.py | DeterministicRedisCache |
| ChromaDB | agentic_core/L4_state/utils/client/chroma_client.py | SovereignChromaClient |
| OpenAI | agentic_core/embeddings/embedding_factory.py | create_embedding_client |
| Anthropic | infrastructure/sdks_mcps/__init__.py | AnthropicClientWrapper |
| Google | infrastructure/sdks_mcps/__init__.py | GoogleGenAIWrapper |
| HTTP | tools/mcp/enhanced_http_server.py | EnhancedHTTPMCP |
| SQLite | tools/memory/sqlite_memory_store.py | SqliteMemoryStore |
| Boto3 | agentic_core/L4_state/utils/memory/canonical_store.py | CanonicalStore |
| OpenTelemetry | tools/otel/otel_mcp_server.py | OTelMCPServer |
| Pytest | tools/mcp/pytest_server.py | PytestMCPServer |

---

## SQLite Views for Violation Detection

### View: P0_Violations apps_* Direct Infra Imports
```sql
CREATE VIEW v_p0_apps_direct_infra AS
SELECT 
    n1.id as violation_id,
    n1.file_path as violating_file,
    n2.name as infra_surface,
    'P0: apps_* direct infra import' as violation_type,
    'apps_* surfaces must not directly own raw infra clients' as description
FROM nodes n1, nodes n2, edges e
WHERE e.relation_type = 'imports'
  AND e.src_id = n1.id
  AND e.tgt_id = n2.id
  AND n1.file_path LIKE 'apps_%/'
  AND n2.name IN ('redis', 'chromadb', 'sqlite3', 'boto3', 'openai', 'anthropic', 'httpx', 'requests')
  AND n1.file_path NOT LIKE 'apps_shared/%'  -- apps_shared is shared infra
```

### View: P0_Violations Provider Control Plane Bypass
```sql
CREATE VIEW v_p0_provider_bypass AS
SELECT 
    n1.id as violation_id,
    n1.file_path as violating_file,
    n2.name as provider,
    'P0: provider control plane bypass' as violation_type,
    'Provider SDKs must route through infrastructure/sdks_mcps' as description
FROM nodes n1, nodes n2, edges e
WHERE e.relation_type = 'imports'
  AND e.src_id = n1.id
  AND e.tgt_id = n2.id
  AND n2.name IN ('openai', 'anthropic', 'google')
  AND n1.file_path NOT LIKE 'infrastructure/sdks_mcps/%'
  AND n1.file_path NOT LIKE 'tools/%'
  AND n1.file_path NOT LIKE 'system_learning/%'
  AND n1.file_path NOT LIKE 'agentic_core/embeddings/%'  -- embedding_factory is approved
```

### View: P0_Violations L6 Live Mutation
```sql
CREATE VIEW v_p0_l6_mutation AS
SELECT 
    n1.id as violation_id,
    n1.file_path as violating_file,
    n2.name as operation,
    'P0: L6 live mutation' as violation_type,
    'L6 observability layer cannot mutate live state' as description
FROM nodes n1, nodes n2, edges e
WHERE n1.layer = 'L6'
  AND e.relation_type = 'calls'
  AND e.src_id = n1.id
  AND e.tgt_id = n2.id
  AND n2.name IN ('set', 'update', 'delete', 'execute', 'commit')
  AND n1.file_path NOT LIKE '%telemetry_store%'
```

### View: P1_Violations Zero Caller Infra
```sql
CREATE VIEW v_p1_zero_caller_infra AS
SELECT 
    n1.id as violation_id,
    n1.file_path as infra_file,
    n1.name as infra_name,
    'P1: infra with no approved callers' as violation_type,
    'Infrastructure surface has zero approved callers (dormant)' as description
FROM nodes n1
LEFT JOIN edges e ON e.tgt_id = n1.id
WHERE n1.file_path IN (
    'agentic_core/cache/redis_cache_client.py',
    'agentic_core/L4_state/utils/client/chroma_client.py',
    'agentic_core/embeddings/embedding_factory.py',
    'infrastructure/sdks_mcps/__init__.py'
)
GROUP BY n1.id
HAVING COUNT(e.tgt_id) = 0
```

### View: P2_Violations Mixed Direct and Wrapped Usage
```sql
CREATE VIEW v_p2_mixed_usage AS
SELECT 
    n2.name as infra_surface,
    'P2: mixed direct and wrapped usage' as violation_type,
    'Same infra used both directly and via adapter (inconsistent)' as description,
    COUNT(DISTINCT CASE 
      WHEN n2.file_path NOT LIKE '%cache%' 
           AND n2.file_path NOT LIKE '%adapter%'
           AND n2.file_path NOT LIKE 'tools/%'
      THEN n1.id 
    END) as direct_count,
    COUNT(DISTINCT CASE 
      WHEN n2.file_path LIKE '%cache%' 
           OR n2.file_path LIKE '%adapter%'
      THEN n1.id 
    END) as wrapped_count
FROM nodes n1, nodes n2, edges e
WHERE e.relation_type = 'imports'
  AND e.src_id = n1.id
  AND e.tgt_id = n2.id
  AND n2.name IN ('redis', 'chromadb', 'sqlite3', 'boto3', 'openai', 'anthropic')
GROUP BY n2.name
HAVING direct_count > 0 AND wrapped_count > 0
```

---

## Implementation Priority

### Phase 2A: Critical Relations (P0 Detection)
- owns_infra_surface
- wraps_infra_surface
- uses_raw_infra_client
- bypasses_infra_adapter
- provider_path_bypasses_control_plane

**Priority:** CRITICAL (required for Phase 3 P0 violation detection)

### Phase 2B: Important Relations (P1/P2 Detection)
- uses_approved_infra_adapter
- infra_reachable_from_app
- infra_has_no_approved_callers
- infra_not_on_agentic_spine

**Priority:** HIGH (required for Phase 3 P1/P2 violation detection)

### Phase 2C: Optional Relations (P3 Detection)
- write_path_bypasses_uwg
- observability_surface_used_live_for_mutation
- mixed_direct_and_wrapped_usage

**Priority:** MEDIUM (useful for Phase 3 P3 violation detection)

---

## Uncertainties and Assumptions

### Uncertainties
1. **ADG Schema Extensibility:** Current ADG schema may not support custom relation types without schema migration
2. **Layer Detection Accuracy:** File path to layer mapping may have edge cases (mixed layers, shared modules)
3. **Adapter Registry Completeness:** Approved adapter registry may be incomplete or outdated

### Assumptions
1. **File Path Mapping:** Directory structure reliably indicates layer assignment
2. **Import Pattern Detection:** AST-based import detection is sufficient for infra usage identification
3. **Exclusion Lists:** tools/ and infrastructure/ directories are safe to exclude from violation checks
4. **apps_shared Classification:** apps_shared/ is shared infrastructure, not application surface

---

## Next Steps

1. **Phase 3:** Execute violation detection using ADG queries and SQLite views defined in this document
2. **Phase 4:** Generate prioritized repair plan based on detected violations
3. **Phase 5:** Design CI ratchet and scorecard for regression prevention
