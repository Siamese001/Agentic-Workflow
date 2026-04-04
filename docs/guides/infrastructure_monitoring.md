# Infrastructure Monitoring CLI Tools

Command-line tools for monitoring Architecture Dependency Graph (ADG) health, violations, and drift.

## Overview

Three CLI tools provide real-time visibility into architectural health:

| Tool | Purpose | Key Features |
|------|---------|--------------|
| `adg_health` | Quick health checks | Node/edge counts, layer distribution, violation summary |
| `adg_violations` | Violation analysis | Filter by layer, file, type; CSV export for CI |
| `adg_drift` | Snapshot comparison | Detect added/deleted modules; CI mode with thresholds |

All tools work directly with ADG SQLite files—no Redis required.

---

## Quick Start

```bash
# Health check (auto-detects latest ADG)
python -m infrastructure.adg_health

# Violations in L0 layer
python -m infrastructure.adg_violations --layer L0

# Compare latest two ADG snapshots
python -m infrastructure.adg_drift
```

---

## adg_health

Quick health overview of the Architecture Dependency Graph.

### Usage

```bash
python -m infrastructure.adg_health [OPTIONS]
```

### Options

| Option | Description |
|--------|-------------|
| `--adg PATH` | Path to ADG SQLite file (auto-detects if omitted) |
| `--format {table,json,markdown}` | Output format (default: table) |
| `--repo-root PATH` | Repository root for auto-detection |
| `--self-test` | Run self-test and exit |

### Examples

```bash
# Basic health check
python -m infrastructure.adg_health

# JSON output for automation
python -m infrastructure.adg_health --format json

# Specific ADG file
python -m infrastructure.adg_health --adg artifacts/adg/adg_indexed_04042026_0614.sqlite
```

### Sample Output

```
================================================================================
ADG HEALTH REPORT
================================================================================
ADG File:    artifacts/adg/adg_indexed_04042026_0614.sqlite
Timestamp:   2026-04-04 06:14
--------------------------------------------------------------------------------
Total Nodes: 176,672
Total Edges: 735,236
Modules:     10,413
Symbols:     166,190
--------------------------------------------------------------------------------
LAYER DISTRIBUTION
--------------------------------------------------------------------------------
  L_TEST           3,439
  L_OPS            1,444
  L_TOOLS          1,398
  ...
--------------------------------------------------------------------------------
VIOLATIONS:  26
--------------------------------------------------------------------------------
  L0->L4                         5
  L0->L_PG                       2
  ...
================================================================================
```

---

## adg_violations

Query and analyze architectural layer boundary violations.

### Usage

```bash
python -m infrastructure.adg_violations [OPTIONS]
```

### Options

| Option | Description |
|--------|-------------|
| `--adg PATH` | Path to ADG SQLite file |
| `--layer LAYER` | Filter by layer (repeatable) |
| `--file PATTERN` | Filter by file glob pattern |
| `--type TYPE` | Filter by violation type |
| `--limit N` | Limit results (default: 100) |
| `--format {table,json,csv,markdown}` | Output format |
| `--output PATH` | Output file (for CSV) |

### Examples

```bash
# All violations
python -m infrastructure.adg_violations

# L0 layer violations only
python -m infrastructure.adg_violations --layer L0

# Multiple layers
python -m infrastructure.adg_violations --layer L0 --layer L_TOOLS

# File pattern filter
python -m infrastructure.adg_violations --file "agentic_core/L0*"

# CSV export for CI
python -m infrastructure.adg_violations --format csv --output violations.csv
```

---

## adg_drift

Compare two ADG snapshots to detect architectural drift.

### Usage

```bash
python -m infrastructure.adg_drift [OPTIONS]
```

### Options

| Option | Description |
|--------|-------------|
| `--baseline PATH` | Baseline ADG SQLite file |
| `--current PATH` | Current ADG SQLite file |
| `--format {table,json,csv,markdown}` | Output format |
| `--output PATH` | Output file (for CSV) |
| `--ci` | CI mode - exit non-zero if drift detected |
| `--max-added N` | Max allowed added modules (CI) |
| `--max-deleted N` | Max allowed deleted modules (CI) |

### Examples

```bash
# Compare two latest snapshots (auto-detect)
python -m infrastructure.adg_drift

# Specific snapshots
python -m infrastructure.adg_drift --baseline old.sqlite --current new.sqlite

# CI mode - fail if more than 10 modules added
python -m infrastructure.adg_drift --ci --max-added 10

# JSON output
python -m infrastructure.adg_drift --format json
```

### CI Integration

```yaml
# .github/workflows/adg-drift-check.yml
- name: Check ADG Drift
  run: |
    python -m infrastructure.adg_drift --ci --max-added 5 --max-deleted 5
```

---

## Testing

Run the test suite:

```bash
python -m pytest tests/infrastructure/ -v
```

Self-test each tool:

```bash
python -m infrastructure.adg_health --self-test
python -m infrastructure.adg_violations --self-test
python -m infrastructure.adg_drift --self-test
```

---

## Architecture

These tools are part of the `infrastructure/` cross-cutting layer:

```
infrastructure/
├── adg_health.py       # Health monitor CLI
├── adg_violations.py   # Violations tracker CLI
├── adg_drift.py       # Drift detector CLI
└── __init__.py        # Package exports
```

All tools:
- Use SQLite directly (no Redis dependency)
- Follow existing `tools/adg/` CLI patterns
- Support machine-readable output (JSON/CSV)
- Include self-test functionality

---

## Related

- `tools/adg/adg_direct.py` - Direct ADG query tool
- `tools/adg/adg_mcp_server.py` - MCP server for IDE integration
- `tools/generate_full_adg.py` - ADG generation script
