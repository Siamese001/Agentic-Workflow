# ADG Accelerators - Optimized 3-Tool Suite

This folder contains the **optimized** ADG accelerator architecture.

## Architecture: 7 Tools → 3 Tools

### Original 7 Tools (Consolidated)
1. `adg_test_accelerator.py` → **adg_test.py**
2. `adg_test_selector.py` → **adg_test.py**
3. `fast_test.py` → **adg_test.py**
4. `p0_batch_wirer.py` → **adg_harden.py**
5. `p1_batch_wire.py` → **adg_harden.py**
6. `adg_incremental_update.py` → **adg_lifecycle.py**
7. `generate_full_adg.py` → **adg_lifecycle.py**

### New 3 Optimized Tools

| Tool | Purpose | Commands |
|------|---------|----------|
| **adg_test.py** | Unified testing | `gap`, `scope`, `run`, `check`, `preflight` |
| **adg_harden.py** | Unified hardening | `p0`, `p1`, `p2`, `check`, `full` |
| **adg_lifecycle.py** | Unified lifecycle | `generate`, `update`, `sync`, `status`, `maintain` |

## Usage

### Testing Accelerator
```bash
# Gap analysis
python tools/adg/adg_test.py gap --top 20 --layer L5

# Scoped test selection
python tools/adg/adg_test.py scope --changed file.py --from-diff

# Run tests with ADG scoping
python tools/adg/adg_test.py run --adg-scope --parallel 4

# Collection safety check
python tools/adg/adg_test.py check --json out.json

# CI preflight (all-in-one)
python tools/adg/adg_test.py preflight --strict
```

### Hardening Accelerator
```bash
# P0 dimension hardening
python tools/adg/adg_harden.py p0 --dim evidence --layer L3 --apply

# P1 orchestration hardening
python tools/adg/adg_harden.py p1 --apply

# Check coverage across all phases
python tools/adg/adg_harden.py check --all --json out.json

# Full hardening (P0-P4)
python tools/adg/adg_harden.py full --micro-wave
```

### Lifecycle Accelerator
```bash
# Full generation with cache
python tools/adg/adg_lifecycle.py generate --cache

# Incremental update
python tools/adg/adg_lifecycle.py update --changed file1.py file2.py

# Check status
python tools/adg/adg_lifecycle.py status

# Auto-maintain (check → update → sync)
python tools/adg/adg_lifecycle.py maintain --from-git --sync-redis
```

## CI Integration

### Streamlined Pipeline (1 workflow, 4 jobs)

```yaml
# .github/workflows/adg-pipeline.yml
jobs:
  test-preflight:      # adg_test.py preflight
  harden-check:        # adg_harden.py check --all
  lifecycle-maintain:  # adg_lifecycle.py maintain
  pipeline-summary:    # Summary aggregation
```

### Pre-Commit Integration

```yaml
# T10.6: ADG Preflight hook
- id: adg-preflight
  name: "ADG Preflight — Gap analysis + collection safety"
  entry: python tools/adg/adg_test.py preflight --quick
```

## Folder Structure

```
tools/adg/
├── adg_test.py          # Unified testing accelerator
├── adg_harden.py        # Unified hardening accelerator
├── adg_lifecycle.py     # Unified lifecycle accelerator
├── ACCELERATOR_OPTIMIZATION_PLAN.md  # Optimization rationale
├── accelerators/        # Legacy unified folder (shims)
│   ├── __init__.py
│   ├── __main__.py      # CLI entry point (delegates to new tools)
│   ├── orchestrator.py
│   ├── testing/         # Proxies to adg_test.py
│   ├── hardening/       # Proxies to adg_harden.py
│   └── incremental/     # Proxies to adg_lifecycle.py
└── ... (other ADG modules)
```

## Migration Path

1. **Immediate**: New tools available alongside old ones
2. **CI**: New `adg-pipeline.yml` replaces old workflows
3. **Pre-commit**: New `adg-preflight` hook added
4. **Legacy**: Old 7 tools remain as shims for backward compatibility

## Benefits

- **Simpler**: 3 tools instead of 7
- **Unified CLI**: Consistent `verb --flags` pattern
- **Reduced CI**: 1 workflow instead of 2, 4 jobs instead of 10
- **Better composability**: Tools can chain together
- **Easier maintenance**: Shared code in one place
