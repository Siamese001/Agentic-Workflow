# Incremental Accelerators

Incremental ADG update and scan accelerators.

## Files

- **adg_incremental_update.py**: Incremental ADG updates (symlink to ../../../adg_incremental_update.py)
  - Patched files → impacted closure → rescan only impacted
  - Update SQLite with FK node resolution
  - Recompute metrics
  - Performance: 12 patched files → 129 impacted → 16.4s (vs 5+ min full regen)

- **generate_full_adg.py**: Full ADG generation with caching (symlink to ../../../generate_full_adg.py)
  - Complete scan with cache support
  - Cache stats: hits, misses, rate
  - Incremental updates via cache

## Usage

```bash
# Via unified CLI
python -m tools.adg.accelerators incremental update --changed file1.py file2.py
python -m tools.adg.accelerators incremental scan --cache

# Direct usage
python tools/adg_incremental_update.py file1.py file2.py
python tools/generate_full_adg.py --use-cache
```

## Cache

Cache file: `artifacts/adg/scan_result_cache.json` (~453MB)
- All modules cached after first run
- Cache stats: hits=6288 misses=3 rate=100.0%

## Incremental Update Process

1. Identify patched files
2. Compute impacted closure (import neighbors)
3. Rescan only impacted modules
4. Update SQLite (delete + insert with FK node resolution)
5. Recompute metrics

## CI Integration

CI workflow: `.github/workflows/adg-accelerators-ci.yml`
- Job: `incremental-scan`

## Memory Reference

See MEMORY[9118722b-bb0b-413d-bdd9-fb9aaf51a039] for RCA on ADG cache and incremental update engine.
