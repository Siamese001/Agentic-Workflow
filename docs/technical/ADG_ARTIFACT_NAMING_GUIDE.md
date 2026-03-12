# ADG Artifact Naming & Usage Guide

## Quick Start: Which File Do I Need?

**For most use cases, use the LATEST files:**

- **`adg_LATEST.sqlite`** ← **PRIMARY** - Use this for queries and analysis
- **`adg_LATEST_full.json`** - Complete graph backup (offline analysis)

## File Naming Convention

### LATEST Files (Easy Discovery)

The system automatically creates/updates these files after each ADG run:

| File | Purpose | Size | Use When |
|------|---------|------|----------|
| `adg_LATEST.sqlite` | **Primary queryable database** | ~38 MB | Running queries, layer checks, impact analysis |
| `adg_LATEST_full.json` | Complete normalized graph | ~35 MB | Offline analysis, debugging, archival |
| `adg_LATEST_snapshot.json` | Metrics summary only | ~4 KB | CI checks, quick health status |
| `adg_LATEST_file_graph.json` | File-level imports only | ~18 MB | File dependency analysis |
| `adg_LATEST_symbol_graph.json` | Symbol-level relationships | ~22 MB | Symbol usage tracking |
| `adg_LATEST_test_graph.json` | Test coverage relationships | ~8 MB | Test impact analysis |
| `adg_LATEST_governance_graph.json` | Layer violations & governance | ~8 MB | Compliance audits |

### Timestamped Files (Historical Archive)

All artifacts are also saved with timestamps for historical tracking:

**Format:** `adg_<type>_<timestamp>.{json|sqlite}`

**Example:** `adg_full_20260311T160257Z.json`

- Timestamp format: `YYYYMMDDTHHMMSSZ` (ISO 8601 UTC)
- Sorted lexicographically (newest = highest timestamp)
- Kept for historical comparison and rollback

## Three-Tier Architecture

### Tier 1: Snapshot (Metrics Only)
- **File:** `adg_snapshot_<ts>.json` or `adg_LATEST_snapshot.json`
- **Size:** ~4 KB
- **Contents:** Counts, digests, graph plane metrics, top-20 hotspots
- **Use for:** CI gates, drift detection, quick health checks
- **Does NOT contain:** Full entities or edges

### Tier 2: Full Graph (Complete Export)
- **File:** `adg_full_<ts>.json` or `adg_LATEST_full.json`
- **Size:** ~35 MB
- **Contents:** All nodes and edges in normalized format (schema v4.0.0)
- **Use for:** Offline analysis, ADG CLI commands, comprehensive audits
- **Format:** Compact integer-indexed edges for efficiency

### Tier 3: SQLite Index (Queryable Database) ⭐
- **File:** `adg_indexed_<ts>.sqlite` or `adg_LATEST.sqlite`
- **Size:** ~38 MB
- **Contents:** Three tables: `nodes`, `edges`, `meta`
- **Use for:** Fast queries, layer-authority checks, mutation-path scans
- **Schema:**
  - `nodes`: id, adg_name, entity_type, layer, identity_kind, confidence, resolved_path
  - `edges`: id, src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol
  - `meta`: key-value metadata (schema_version, commit_sha, digests, counts)

## Split-Plane Sub-Graphs

Four specialized views of the dependency graph:

### File Graph
- **File:** `adg_file_graph_<ts>.json` or `adg_LATEST_file_graph.json`
- **Size:** ~18 MB
- **Contains:** File-level import relationships only
- **Use for:** Understanding module dependencies, refactoring planning

### Symbol Graph
- **File:** `adg_symbol_graph_<ts>.json` or `adg_LATEST_symbol_graph.json`
- **Size:** ~22 MB
- **Contains:** Symbol-level relationships (classes, functions, variables)
- **Use for:** Symbol usage tracking, dead code detection

### Test Graph
- **File:** `adg_test_graph_<ts>.json` or `adg_LATEST_test_graph.json`
- **Size:** ~8 MB
- **Contains:** Test coverage relationships (`covers` edges)
- **Use for:** Test impact analysis, coverage gaps

### Governance Graph
- **File:** `adg_governance_graph_<ts>.json` or `adg_LATEST_governance_graph.json`
- **Size:** ~8 MB
- **Contains:** Layer violations, governance edges (`violates`, `bypasses_uwg`)
- **Use for:** Compliance audits, architectural enforcement

## Common Usage Patterns

### Pattern 1: Quick Health Check
```python
import json
from pathlib import Path

snapshot = json.loads(Path("artifacts/adg/adg_LATEST_snapshot.json").read_text())
print(f"Modules: {snapshot['counts']['module_count']}")
print(f"Layer violations: {snapshot['counts']['layer_violation_count']}")
```

### Pattern 2: Query the Database
```python
import sqlite3

conn = sqlite3.connect("artifacts/adg/adg_LATEST.sqlite")
cursor = conn.execute("""
    SELECT n.adg_name, n.layer, COUNT(*) as fan_in
    FROM nodes n
    JOIN edges e ON e.dst_id = n.id
    WHERE e.relation_type = 'imports'
    GROUP BY n.id
    ORDER BY fan_in DESC
    LIMIT 10
""")
for row in cursor:
    print(row)
```

### Pattern 3: Analyze File Dependencies
```python
import json
from pathlib import Path

file_graph = json.loads(Path("artifacts/adg/adg_LATEST_file_graph.json").read_text())
# Work with file-level imports only
```

## Finding the Latest Artifacts

### Method 1: Use LATEST Files (Recommended)
```python
from pathlib import Path

# Always points to newest
db_path = Path("artifacts/adg/adg_LATEST.sqlite")
```

### Method 2: Sort Timestamped Files
```python
from pathlib import Path

adg_dir = Path("artifacts/adg")
latest_db = sorted(adg_dir.glob("adg_indexed_*.sqlite"))[-1]
```

## File Lifecycle

1. **Generation:** ADG scan runs → creates 7 timestamped artifacts
2. **LATEST Update:** System updates all `adg_LATEST_*` files to point to newest
3. **Retention:** Old timestamped files remain for historical comparison
4. **Cleanup:** Manually delete old timestamped files if needed (keep LATEST files)

## Migration Notes

### Before (Confusing)
- `adg_full_20260311T160257Z.json` vs `adg_full_20260311T160428Z.json` - which is newer?
- "full" vs "indexed" - which do I use?
- No clear entry point

### After (Clear)
- Use `adg_LATEST.sqlite` for queries (primary)
- Use `adg_LATEST_full.json` for offline analysis (backup)
- Timestamped files kept for history, but not primary workflow

## Technical Details

### Symlink Behavior
- **Unix/Linux/macOS:** Creates actual symlinks
- **Windows (no admin):** Falls back to file copies
- Both approaches work transparently for consumers

### Schema Versions
- Tier 1 (snapshot): `snapshot-1.0`
- Tier 2 (full): `4.0.0` (NormalizedGraph format)
- Tier 3 (sqlite): Embedded in `meta` table

### Generation Command
```bash
python tools/generate_full_adg.py
```

This creates all 7 artifacts + LATEST files in `artifacts/adg/`.

## Summary

**Core principle:** Use `adg_LATEST.sqlite` for 90% of use cases. It's the primary queryable database that's always up-to-date.

**When to use others:**
- `adg_LATEST_snapshot.json` - Quick metrics check
- `adg_LATEST_full.json` - Offline analysis or debugging
- Split-plane graphs - Specialized analysis (files, symbols, tests, governance)
- Timestamped files - Historical comparison or rollback
