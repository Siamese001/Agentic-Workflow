---
description: Memory graph purge sync — purge stale entities and re-import fresh ADG context
---

> **Cascade workflow note:** This workflow is a reusable procedural lane, not always-on policy. Use it to hold staged retrieval, evidence gathering, execution order, and verification steps that would otherwise overload rules. For deep research, separate retrieval, quote extraction, synthesis, and final verification into distinct phases.

## Memory Purge Sync Workflow

Invoke this workflow after every ADG regeneration to maintain a lean memory graph.

### When to Run

- **Trigger**: After `python tools/generate_full_adg.py` or any ADG regeneration
- **Frequency**: Historically every 3–7 days (based on ADG regeneration patterns)
- **Threshold**: Entities older than 7 days are purged

### Step 1 — Check ADG Freshness

Verify ADG has been regenerated since last purge:

```python
python -c "
from pathlib import Path
import json
adg_dir = Path('artifacts/adg')
sqlite_files = list(adg_dir.glob('adg_indexed_*.sqlite'))
if sqlite_files:
    latest = max(sqlite_files, key=lambda p: p.stat().st_mtime)
    print(f'Latest ADG: {latest.name}')
    print(f'Modified: {latest.stat().st_mtime}')
else:
    print('No ADG found')
"
```

If ADG unchanged since last purge, exit (idempotent).

### Step 2 — Pre-Purge Stats

// turbo
Capture baseline metrics:

```
python tools/memory/purge_sync.py --stats
```

### Step 3 — Execute Purge

// turbo
Purge entities older than 7 days (protected types never deleted):

```
python tools/memory/purge_sync.py --purge --older-than-days=7
```

**Protected types** (never deleted): `ArchitectureLayer`, `ProjectContext`, `ConstitutionalRule`

### Step 4 — Re-import ADG Context

// turbo
Refresh memory graph with current ADG context:

```
python tools/memory/purge_sync.py --import-adg
```

Imports:
- `Project:ADG` — project metadata with timestamp, node/edge counts
- `Layer:L0` through `Layer:L6` — architecture layer definitions

### Step 5 — Post-Purge Verification

// turbo
Verify clean state:

```
python tools/memory/purge_sync.py --stats
```

Success criteria:
- Entity count < 500
- Oldest non-protected entity age < 14 days
- Protected entities intact (`ArchitectureLayer` × 7, `ProjectContext` × 1)

### Step 6 — Evidence Artifact

Write telemetry summary:

```
python tools/memory/purge_sync.py --evidence
```

Output: `docs/reports/telemetry/memory_purge_YYYYMMDD_HHMMSS.json`

---

## One-Command Execution

All steps in sequence:

```
python tools/memory/purge_sync.py --full-sync
```

## CI Integration

Daily health check (alerts if bloat detected):

```
python ops_scripts/ci/check_memory_health.py
```

## Safety Features

1. **Protected types** — `ArchitectureLayer`, `ProjectContext`, `ConstitutionalRule` never purged
2. **Idempotent** — No-op if ADG unchanged
3. **Evidence trail** — Every purge logged with before/after stats
4. **Dry-run mode** — Preview what would be purged without deleting:
   ```
   python tools/memory/purge_sync.py --purge --dry-run
   ```
