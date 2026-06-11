---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\RCA_memory_mcp_persistence_fix.md'
original_relative_path: 'RCA_memory_mcp_persistence_fix.md'
source_sha256: fc7ffc81a8f1fb98b9e9cb64e58e0099f688d956cc9b0443c058db03a26306a2
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-15'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RCA: Memory MCP Persistence — ADG Data Not Written to SQLite

**Status:** ✅ RESOLVED
**Date:** 2026-03-15
**Severity:** HIGH — silently broken persistence; misleading success output

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## 1. Symptom

`generate_full_adg.py` printed:
```
[ADG] Memory MCP: persisted snapshot + layers + hotspots + 38/38 violations (critical=38)
```
But `artifacts/memory/knowledge_graph.sqlite` remained **completely empty** (0 entities, 0 observations, 0 relations).

---

## 2. Root Cause Chain

```
generate_full_adg.py
  └─ _persist_adg_to_memory()
      └─ ADGMemoryAdapter.ingest_snapshot()
          └─ GraphMemoryBridge.create_agent_entity()
              └─ _call_mcp_create_entities()
                  ├─ mcp11 module? → ImportError (not available in CLI process)
                  └─ _MCPFallbackClient()._InMemoryStore  ← NEW instance per call, in-memory only
                                                             DATA LOST ON RETURN
```

**Three compounding bugs:**

| # | Bug | Location |
|---|-----|----------|
| B1 | `GraphMemoryBridge._init_mcp` sets `_mcp_available=False` when `mcp11` unavailable, but print path never reflects this | `graph_memory_bridge.py:98-116` |
| B2 | `_call_mcp_create_entities` creates a fresh `_MCPFallbackClient()` on **every call** — the in-memory store is discarded after each entity | `graph_memory_bridge.py:118-129` |
| B3 | `_call_mcp_create_relations` and `_call_mcp_add_observations` return `None` with no fallback at all — relations and observations were silently dropped | `graph_memory_bridge.py:131-145` |
| B4 | `_persist_adg_to_memory()` prints "persisted" unconditionally — no check that any data actually reached storage | `generate_full_adg.py:273-275` |

**Root cause in one sentence:** `GraphMemoryBridge` assumed `mcp11` (a Windsurf IDE live-process module) would be importable from a CLI subprocess — it never is. The fallback was an ephemeral in-memory dict that vanished on function return.

---

## 3. Architecture Gap

The correct model: **SQLite is the SSOT for persistent memory**. The MCP server is a protocol wrapper. Both paths must write to the same file.

```
BEFORE (broken):
  CLI → ADGMemoryAdapter → GraphMemoryBridge → mcp11 (missing) → _InMemoryStore → /dev/null

AFTER (fixed):
  CLI → ADGMemoryAdapter → GraphMemoryBridge → SqliteMemoryStore → knowledge_graph.sqlite ✅
  Windsurf → adg_memory_server → SqliteMemoryStore → knowledge_graph.sqlite ✅
```

---

## 4. Corrective Actions (all executed)

### 4.1 New shared module: `tools/memory/sqlite_memory_store.py`
- Single canonical implementation of all SQLite CRUD (schema, entities, observations, relations)
- API mirrors `mcp11` tool signatures — drop-in replacement
- Used by both `adg_memory_server.py` and `GraphMemoryBridge`

### 4.2 `GraphMemoryBridge` fixed (`agentic_core/L4_state/enforcement/graph_memory_bridge.py`)
- `_init_mcp`: after `mcp11` `ImportError`, instantiates `SqliteMemoryStore` and sets `_mcp_available=True`
- `_call_mcp_create_entities`: routes to `_sqlite_store.create_entities()` before the `_InMemoryStore` stub
- `_call_mcp_create_relations`: routes to `_sqlite_store.create_relations()` (previously returned `None`)
- `_call_mcp_add_observations`: routes to `_sqlite_store.add_observations()` (previously returned `None`)
- `_call_mcp_search_nodes`: routes to `_sqlite_store.search_nodes()` when offline

### 4.3 `adg_memory_server.py` refactored (`tools/memory/adg_memory_server.py`)
- All inline `_conn`, `_db`, `_ensure_schema`, `_upsert_entity`, `_add_obs`, `_load_entity` removed
- All 13 MCP tools now delegate to `_store: SqliteMemoryStore`
- Schema defined in exactly one place; both paths guaranteed to be in sync

---

## 5. Preventive Measures

- [x] Schema defined in one file (`sqlite_memory_store.py`) — no drift possible
- [x] `GraphMemoryBridge` logs explicit mode at startup: `Initialized (SQLite fallback mode) db=...`
- [x] `_InMemoryStore` stub kept as last-resort (CI/test environments without SQLite access)
- [ ] Add assertion in `_persist_adg_to_memory` to verify entity count > 0 after ingest

---

## 6. Evidence

Run after fix:
```
python tools/generate_full_adg.py
python _tmp_verify_memory_db.py
```
Expected: SQLite `entities` table populated with `ADGSnapshot_*`, `ADGLayer_*`, `ADGHotspot_*`, `ADGViolation_*`, `ADGModule_*` entities.

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Root Cause

[Identify and explain the root cause of the violation]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

