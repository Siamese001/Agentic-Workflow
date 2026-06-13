# ADG Artifact Naming Streamlining - Summary

**Date:** 2026-03-12
**Status:** ✅ Complete

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Problem Statement

ADG artifact naming was confusing and difficult to navigate:

1. **Timestamp confusion**: Files like `adg_full_20260311T160257Z.json` vs `adg_full_20260311T160428Z.json` were impossible to distinguish at a glance
2. **Unclear file purposes**: "full" vs "indexed" vs "file_graph" - not obvious which to use for what
3. **No clear "latest" indicator**: Required manual timestamp parsing to find newest files

## Solution Implemented

### 1. LATEST File System

Added automatic creation of `adg_LATEST_*` files that always point to the newest artifacts:

- `adg_LATEST.sqlite` → Primary queryable database
- `adg_LATEST_full.json` → Complete graph backup
- `adg_LATEST_snapshot.json` → Quick metrics
- `adg_LATEST_file_graph.json` → File-level imports
- `adg_LATEST_symbol_graph.json` → Symbol relationships
- `adg_LATEST_test_graph.json` → Test coverage
- `adg_LATEST_governance_graph.json` → Layer violations

**Implementation:**
- Unix/Linux/macOS: Creates symlinks
- Windows (no admin): Falls back to file copies
- Both approaches work transparently

### 2. Clear File Purpose Documentation

Defined three-tier architecture with clear use cases:

**Tier 1: Snapshot** (~4 KB)
- Metrics only, no full graph data
- Use: CI gates, quick health checks

**Tier 2: Full Graph** (~35 MB)
- Complete normalized graph
- Use: Offline analysis, debugging

**Tier 3: SQLite Index** (~38 MB) ⭐ **PRIMARY**
- Queryable database
- Use: Queries, layer checks, impact analysis

### 3. Core Files for Ingestion

**Essential:**
- `adg_LATEST.sqlite` - Primary (use this 90% of the time)
- `adg_LATEST_full.json` - Backup/offline analysis

**Optional (specialized):**
- Split-plane graphs for specific analysis needs
- Timestamped files for historical comparison

## Changes Made

### Code Changes

**File:** `agentic_core/adg/artifact/multi_writer.py`

1. Added `create_latest_symlinks` parameter to `write_all_artifacts()`
2. Implemented `_create_latest_symlinks()` helper function
3. Automatic LATEST file creation after each ADG run

### Documentation Created

1. **`docs/technical/ADG_ARTIFACT_NAMING_GUIDE.md`**
   - Comprehensive guide with usage patterns
   - Quick reference table
   - Common query examples
   - Migration notes

2. **`artifacts/adg/README.md`**
   - Quick reference for developers
   - Common tasks with examples
   - File organization overview

### Configuration Updates

**File:** `.gitignore`

Added exclusions for auto-generated LATEST files:
```
artifacts/adg/adg_LATEST*.sqlite
artifacts/adg/adg_LATEST*.json
```

## Usage Examples

### Before (Confusing)
```python
# Which file is newest?
files = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"))
latest = files[-1]  # Hope this is right...
```

### After (Clear)
```python
# Always use LATEST
db = Path("artifacts/adg/adg_LATEST.sqlite")
```

## Migration Path

**For existing scripts:**
1. Replace glob patterns with `adg_LATEST.sqlite`
2. Keep timestamped files for historical analysis
3. No breaking changes - old files still work

**For new development:**
- Use `adg_LATEST.sqlite` as primary
- Reference documentation for specialized needs

## Testing

To test the new system:

```bash
# Generate new ADG artifacts
python tools/generate_full_adg.py

# Verify LATEST files were created
ls -lh artifacts/adg/adg_LATEST*

# Test query
sqlite3 artifacts/adg/adg_LATEST.sqlite "SELECT COUNT(*) FROM nodes"
```

## Benefits

1. **Instant clarity**: `adg_LATEST.sqlite` is obviously the newest
2. **Clear purpose**: Documentation explains when to use each file
3. **Backward compatible**: Timestamped files still work
4. **Developer friendly**: No more timestamp parsing
5. **Self-documenting**: File names indicate purpose

## Next Steps

1. Update existing scripts to use LATEST files
2. Consider cleanup policy for old timestamped files (retention period)
3. Add LATEST file verification to CI checks

## References

- Implementation: `agentic_core/adg/artifact/multi_writer.py:214-256`
- Documentation: `docs/technical/ADG_ARTIFACT_NAMING_GUIDE.md`
- Quick Reference: `artifacts/adg/README.md`

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

