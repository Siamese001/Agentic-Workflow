# ADG Archiving Strategy

## Overview

The ADG archiving system maintains a clean, performant `artifacts/adg/` directory while preserving historical data for analysis and rollback.

## Retention Policy

### Active Files (Never Archived)

**LATEST Files** - Always current, auto-updated:
- `adg_LATEST.sqlite`
- `adg_LATEST_full.json`
- `adg_LATEST_snapshot.json`
- `adg_LATEST_file_graph.json`
- `adg_LATEST_symbol_graph.json`
- `adg_LATEST_test_graph.json`
- `adg_LATEST_governance_graph.json`

### Recent Runs (Keep in Main Directory)

**Default:** Last 5 complete runs

Each run consists of 7-8 timestamped artifacts:
- `adg_snapshot_<ts>.json`
- `adg_full_<ts>.json`
- `adg_indexed_<ts>.sqlite`
- `adg_file_graph_<ts>.json`
- `adg_symbol_graph_<ts>.json`
- `adg_test_graph_<ts>.json`
- `adg_governance_graph_<ts>.json`
- `adg_graphsnap_<ts>.json` (E7 snapshot)

### Archived Runs (Compressed Storage)

**Location:** `artifacts/adg/_archive/<YYYY-MM>/`

**Compression:** ~90% space savings (gzip)
- JSON files: ~85-90% compression
- SQLite files: ~90-95% compression

**Archive Retention:** 6 months (configurable)

## Archiving Script

### Basic Usage

```bash
# Dry run (show what would be archived)
python tools/archive_old_adg.py

# Actually archive files
python tools/archive_old_adg.py --execute

# Keep last 10 runs instead of default 5
python tools/archive_old_adg.py --execute --keep-runs 10

# Also cleanup archives older than 6 months
python tools/archive_old_adg.py --execute --cleanup-old
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--execute` | False | Actually archive files (default is dry run) |
| `--keep-runs N` | 5 | Number of recent runs to keep |
| `--compress` | True | Compress archived files with gzip |
| `--no-compress` | False | Disable compression |
| `--archive-months N` | 6 | Keep archives for N months |
| `--cleanup-old` | False | Remove archives older than --archive-months |

### Example Output

```
[ADG Archive] Scanning artifacts/adg...
[ADG Archive] Found 52 timestamped runs

[ADG Archive] Retention policy: keep 5 most recent runs
[ADG Archive] Runs to archive: 47

[ADG Archive] Archiving run 20260311T160257Z (7 files)...
    → artifacts/adg/_archive/2026-03
    → 7 files, 124.4 MB → 12.0 MB

[ADG Archive] Summary:
    Runs archived: 47
    Files archived: 145
    Original size: 2.3 GB
    Archived size: 198.1 MB
    Space saved: 2.1 GB (91.6%)
```

## Archive Directory Structure

```
artifacts/adg/
├── adg_LATEST.sqlite              ← Always current
├── adg_LATEST_full.json           ← Always current
├── adg_LATEST_snapshot.json       ← Always current
├── adg_LATEST_*.json              ← Always current (4 more)
│
├── adg_full_20260312T101941Z.json      ← Recent run 1
├── adg_indexed_20260312T101941Z.sqlite
├── adg_snapshot_20260312T101941Z.json
├── adg_*_20260312T101941Z.json         ← (4 more files)
│
├── adg_full_20260311T231210Z.json      ← Recent run 2
├── adg_indexed_20260311T231210Z.sqlite
├── ... (5 more files)
│
├── ... (3 more recent runs)
│
└── _archive/
    ├── 2026-03/
    │   ├── adg_full_20260311T160257Z.json.gz      ← Compressed
    │   ├── adg_indexed_20260311T160257Z.sqlite.gz
    │   ├── adg_snapshot_20260311T160257Z.json.gz
    │   └── ... (many more compressed files)
    │
    ├── 2026-02/
    │   └── ... (older archives)
    │
    └── 2025-12/
        └── ... (even older archives)
```

## Compression Ratios

Based on actual test results:

| File Type | Original Size | Compressed Size | Savings |
|-----------|---------------|-----------------|---------|
| `adg_full_*.json` | 34.1 MB | 2.8 MB | 91.8% |
| `adg_indexed_*.sqlite` | 37.2 MB | 3.5 MB | 90.6% |
| `adg_snapshot_*.json` | 4 KB | 0.5 KB | 87.5% |
| `adg_file_graph_*.json` | 19.5 MB | 1.8 MB | 90.8% |
| `adg_symbol_graph_*.json` | 22.0 MB | 2.0 MB | 90.9% |
| `adg_test_graph_*.json` | 9.2 MB | 0.9 MB | 90.2% |
| `adg_governance_graph_*.json` | 8.6 MB | 0.8 MB | 90.7% |

**Overall:** ~91% space savings

## Restoring Archived Files

To restore an archived run:

```bash
# Navigate to archive directory
cd artifacts/adg/_archive/2026-03/

# Decompress files
gunzip adg_full_20260311T160257Z.json.gz
gunzip adg_indexed_20260311T160257Z.sqlite.gz
# ... decompress other files

# Move back to main directory
mv adg_*_20260311T160257Z.* ../../
```

Or use Python:

```python
import gzip
import shutil
from pathlib import Path

archive_dir = Path("artifacts/adg/_archive/2026-03")
main_dir = Path("artifacts/adg")

# Restore a specific run
ts = "20260311T160257Z"

for gz_file in archive_dir.glob(f"*{ts}*.gz"):
    output_file = main_dir / gz_file.stem  # Remove .gz extension
    
    with gzip.open(gz_file, 'rb') as f_in:
        with open(output_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    print(f"Restored: {output_file.name}")
```

## Automated Archiving

### CI Integration

Add to CI pipeline to run after ADG generation:

```yaml
- name: Archive old ADG runs
  run: python tools/archive_old_adg.py --execute --keep-runs 5
```

### Cron Job

Run weekly to keep directory clean:

```bash
# Add to crontab
0 2 * * 0 cd /path/to/repo && python tools/archive_old_adg.py --execute --cleanup-old
```

### Pre-commit Hook

Archive before committing new ADG runs:

```bash
#!/bin/bash
# .git/hooks/pre-commit

python tools/archive_old_adg.py --execute --keep-runs 3
```

## Storage Estimates

### Without Archiving

- 50 runs × 8 files × ~17 MB avg = **6.8 GB**

### With Archiving (keep 5 runs)

- 5 recent runs × 8 files × 17 MB = **680 MB** (active)
- 45 archived runs × 8 files × 1.5 MB compressed = **540 MB** (archived)
- **Total: 1.2 GB** (82% savings vs no archiving)

## Best Practices

### When to Archive

1. **After major ADG runs** - Keep directory clean
2. **Before commits** - Don't commit massive timestamped files
3. **Weekly/monthly** - Regular maintenance schedule
4. **Before disk space issues** - Proactive management

### Retention Recommendations

| Environment | Keep Runs | Archive Months | Rationale |
|-------------|-----------|----------------|-----------|
| Development | 3-5 | 3 | Fast iteration, less history needed |
| CI/CD | 5-10 | 6 | Balance between history and storage |
| Production | 10-20 | 12 | More history for incident analysis |

### What NOT to Archive

- LATEST files (always current)
- Files modified in last 24 hours (might be in use)
- Non-timestamped files (e.g., `artifact_manifest.json`)

## Troubleshooting

### "No runs to archive"

All runs are within retention policy. Either:
- Reduce `--keep-runs` value
- Wait for more ADG runs to accumulate

### "Permission denied" on Windows

Run with administrator privileges or use `--no-compress` to avoid symlink issues.

### Archive directory growing too large

Run with `--cleanup-old` to remove archives older than retention period:

```bash
python tools/archive_old_adg.py --execute --cleanup-old --archive-months 3
```

### Decompression fails

Ensure gzip is available:

```bash
# Test gzip
python -c "import gzip; print('gzip available')"
```

## Related Documentation

- **Naming Guide:** `docs/technical/ADG_ARTIFACT_NAMING_GUIDE.md`
- **Quick Reference:** `artifacts/adg/README.md`
- **Implementation:** `tools/archive_old_adg.py`
