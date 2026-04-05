# ADG Persistence Architecture Guide

## Overview

The ADG system uses a **multi-layered persistence strategy** that ensures data is stored reliably across different storage mechanisms. Here's how to check and understand each layer:

## 📁 Persistence Layers

### 1. SQLite ADG Database (Primary Storage) ✅ **Persistent**

**Location**: `artifacts/adg/adg_indexed_YYYYMMDD_HHMM.sqlite`

**Purpose**: Source of truth for all ADG data (nodes, edges, metadata)

**How to Check**:
```bash
# List all SQLite databases
ls -la artifacts/adg/*.sqlite

# Check database contents
python -c "
import sqlite3
conn = sqlite3.connect('artifacts/adg/adg_indexed_03232026_0655.sqlite')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM nodes')
print('Nodes:', cursor.fetchone()[0])
cursor.execute('SELECT COUNT(*) FROM edges')
print('Edges:', cursor.fetchone()[0])
cursor.execute('SELECT COUNT(DISTINCT layer) FROM nodes')
print('Layers:', cursor.fetchone()[0])
conn.close()
"
```

**Current Status**:
- `adg_indexed_03232026_0655.sqlite`: 140,313 nodes, 589,244 edges (147.86 MB)
- `adg_indexed_03232026_0617.sqlite`: 140,217 nodes, 589,059 edges (147.68 MB)
- **Data Integrity**: 100% (no null fields after gap closure)

---

### 2. JSON Graph Artifacts (Analysis Storage) ✅ **Persistent**

**Location**: `artifacts/adg/adg_*_graph_YYYYMMDD_HHMM.json`

**Files**:
- `adg_snapshot_*.json` - Compact metadata (7 KB)
- `adg_file_graph_*.json` - File-level relationships (77 MB)
- `adg_symbol_graph_*.json` - Symbol relationships (32 MB)
- `adg_governance_graph_*.json` - Governance relationships (20 MB)

**Purpose**: Analysis artifacts for different graph views

**How to Check**:
```bash
# List all JSON artifacts
ls -la artifacts/adg/adg_*_graph_*.json

# Check snapshot contents
python -c "
import json
with open('artifacts/adg/adg_snapshot_03232026_0655.json') as f:
    snapshot = json.load(f)
print('Snapshot:', snapshot.get('timestamp'))
print('Entities:', snapshot.get('entities'))
print('Relations:', snapshot.get('relations'))
"
```

---

### 3. Scan Cache (Performance Storage) ✅ **Persistent**

**Location**: `artifacts/adg/cache/scan_result_cache.json`

**Purpose**: Fast module scanning cache (99.8% hit rate)

**How to Check**:
```bash
# Check cache size and contents
ls -la artifacts/adg/cache/
python -c "
import json
with open('artifacts/adg/cache/scan_result_cache.json') as f:
    cache = json.load(f)
print('Cache version:', cache.get('version'))
print('Cached entries:', len(cache.get('entries', {})))
"
```

**Current Status**: 261.95 MB, 6,570 cached modules, 99.8% hit rate

---

### 4. Redis Hot Cache (Runtime Storage) ⚠️ **In-Memory**

**Purpose**: Hot access layer for ADG queries

**How to Check**:
```bash
# Check Redis connection and ADG keys
python -c "
import redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
r.ping()
adg_keys = r.keys('adg:*')
print('ADG keys in Redis:', len(adg_keys))
print('ADG status:', r.get('adg:status'))
"
```

**Current Status**:
- ✅ Redis connection active
- 1,003,208 ADG keys stored
- Latest timestamp: 03232026_0655
- **Rebuildable**: Can be regenerated from SQLite

---

### 5. Memory MCP Server (Session Storage) ❌ **Not Persistent**

**Architecture**: Uses in-memory SQLite by default

**Fallback**: Can use persistent SQLite at `artifacts/memory/knowledge_graph.sqlite`

**How to Check**:
```bash
# Check for persistent Memory MCP database
ls -la artifacts/memory/
ls -la .windsurf/memory/

# Check if persistent mode is enabled
python -c "
import os
print('MEMORY_DB env var:', os.environ.get('MEMORY_DB', 'Not set'))
"
```

**Current Status**:
- ❌ No persistent database found
- ⚠️ Uses in-memory storage (session-based)
- ✅ **Rebuildable**: Can be regenerated from ADG data

---

## 🔄 Persistence Strategy

### Data Flow
```
SQLite ADG (Source of Truth)
    ↓
Redis Hot Cache (Fast Access)
    ↓
Memory MCP (Session Knowledge)
```

### Recovery Capability
- **SQLite → Redis**: Auto-ingest on startup (`generate_full_adg.py`)
- **Cache → Scanner**: Fast regeneration (99.8% hit rate)
- **JSON → Analysis**: Direct file access
- **Memory MCP**: Session restart required

---

## 🛠️ How to Verify Persistence

### Quick Check Script
```bash
python tools/check_adg_persistence.py
```

### Manual Verification Steps

1. **SQLite Persistence**:
   ```bash
   sqlite3 artifacts/adg/adg_indexed_03232026_0655.sqlite "SELECT COUNT(*) FROM nodes;"
   ```

2. **Redis Hot Cache**:
   ```bash
   redis-cli keys "adg:*" | wc -l
   ```

3. **Memory MCP Status**:
   ```bash
   # Check if persistent mode is available
   python -c "from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge; bridge = GraphMemoryBridge.get_instance(); print('MCP Available:', bridge._mcp_available)"
   ```

---

## 📊 Current Persistence Status

| Layer | Status | Size | Persistence | Recovery |
|-------|--------|------|-------------|----------|
| SQLite ADG | ✅ Active | 147.86 MB | **Persistent** | N/A |
| JSON Graphs | ✅ Active | 130 MB | **Persistent** | N/A |
| Scan Cache | ✅ Active | 261.95 MB | **Persistent** | N/A |
| Redis Cache | ✅ Active | ~100 MB | **In-Memory** | ✅ Auto-rebuild |
| Memory MCP | ⚠️ Session | ~10 MB | **Not Persistent** | ✅ Session restart |

---

## 🔧 Configuration

### Enable Persistent Memory MCP
Set environment variable:
```bash
export MEMORY_DB="artifacts/memory/knowledge_graph.sqlite"
```

### Redis Configuration
Default: `localhost:6379, db=0`

### SQLite Configuration
Default: `artifacts/adg/adg_indexed_YYYYMMDD_HHMM.sqlite`

---

## 🚨 Important Notes

1. **SQLite ADG is the authoritative source** - all other layers are derived from it
2. **Redis cache is rebuildable** - don't worry if it's lost
3. **Memory MCP is session-based** - expect data loss on restart
4. **Gap closure ensures 100% data integrity** in SQLite
5. **Multiple SQLite versions** provide historical snapshots

---

## 📝 Best Practices

1. **Always check SQLite first** - it's the source of truth
2. **Monitor Redis cache hit rates** - should be >95%
3. **Regenerate Redis cache** if data seems stale: `python tools/generate_full_adg.py`
4. **Use Memory MCP for session data** - don't rely on it for persistence
5. **Back up SQLite databases** - they contain the complete ADG

---

## 🔍 Troubleshooting

### If Redis is empty:
```bash
python tools/generate_full_adg.py  # Regenerates Redis cache
```

### If Memory MCP has no data:
```bash
# Restart the session or enable persistent mode
export MEMORY_DB="artifacts/memory/knowledge_graph.sqlite"
```

### If SQLite seems corrupted:
```bash
# Use an older version or regenerate
python tools/generate_full_adg.py --force
```

---

**Bottom Line**: The ADG system has robust persistence through SQLite databases. The Memory MCP server is intentionally session-based for performance, but all critical data is preserved in the SQLite database and can be rebuilt at any time.
