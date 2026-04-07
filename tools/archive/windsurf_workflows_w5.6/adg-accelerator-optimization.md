---
description: Optimize ADG accelerators - streamline 7 tools into 3 unified tools with enhanced CI/pre-commit integration
---

# ADG Accelerator Optimization Workflow

## Overview

This workflow consolidates 7 ADG accelerators into 3 optimized tools:
- **Before**: `adg_test_accelerator.py`, `adg_test_selector.py`, `fast_test.py`, `p0_batch_wirer.py`, `p1_batch_wire.py`, `adg_incremental_update.py`, `generate_full_adg.py`
- **After**: `adg_test.py`, `adg_harden.py`, `adg_lifecycle.py`

## Execution Steps

### Step 1: Analyze Current Usage

Identify where accelerators are used:
- Pre-commit hooks (`.pre-commit-config.yaml`)
- CI workflows (`.github/workflows/`)
- Direct CLI usage

// turbo
```bash
# Check current accelerator usage
grep -r "adg_test_accelerator\|adg_test_selector\|fast_test\|p0_batch_wirer\|p1_batch_wire\|adg_incremental_update\|generate_full_adg" \
  .github/workflows/ .pre-commit-config.yaml ops_scripts/ --include="*.yml" --include="*.yaml" --include="*.py" 2>/dev/null | head -50
```

### Step 2: Create Unified Tools

Create 3 optimized accelerators in `tools/adg/`:

1. **`adg_test.py`** - Testing accelerator (merges 3 tools)
   - Commands: `gap`, `scope`, `run`, `check`, `preflight`

2. **`adg_harden.py`** - Hardening accelerator (merges 2+ tools)
   - Commands: `p0`, `p1`, `p2`, `check`, `full`

3. **`adg_lifecycle.py`** - Lifecycle accelerator (merges 2 tools)
   - Commands: `generate`, `update`, `sync`, `status`, `maintain`

### Step 3: Create Unified CI Pipeline

Replace 2 workflows + 10 jobs with 1 workflow + 4 jobs:

```yaml
# .github/workflows/adg-pipeline.yml
jobs:
  test-preflight:      # adg_test.py preflight --strict
  harden-check:        # adg_harden.py check --all
  lifecycle-maintain:  # adg_lifecycle.py maintain --from-git
  pipeline-summary:    # Aggregate reports
```

### Step 4: Update Pre-Commit Hooks

Add T10.6 ADG preflight hook:

```yaml
- id: adg-preflight
  name: "T10.6: ADG Preflight — Gap analysis + collection safety"
  entry: python tools/adg/adg_test.py preflight --quick
  language: system
  pass_filenames: false
  always_run: true
```

### Step 5: Update Accelerator Folder

Update `tools/adg/accelerators/` to proxy to new tools:
- `__main__.py` delegates to new unified CLI
- `testing/`, `hardening/`, `incremental/` subfolders use proxy pattern

### Step 6: Verify Integration

Test the optimized accelerators:

```bash
# Test new tools
python tools/adg/adg_test.py gap --top 10
python tools/adg/adg_harden.py check --all
python tools/adg/adg_lifecycle.py status

# Test unified CLI
python -m tools.adg.accelerators testing gap --top 10
python -m tools.adg.accelerators hardening check --all
python -m tools.adg.accelerators incremental status
```

## Usage Examples

### Testing Accelerator
```bash
# Gap analysis
python tools/adg/adg_test.py gap --top 20 --layer L5

# Scoped selection for changed files
python tools/adg/adg_test.py scope --changed file.py --from-diff

# Run tests with ADG scoping
python tools/adg/adg_test.py run --adg-scope --parallel 4

# CI preflight (all-in-one)
python tools/adg/adg_test.py preflight --strict
```

### Hardening Accelerator
```bash
# P0 dimension hardening
python tools/adg/adg_harden.py p0 --dim evidence --layer L3 --apply

# Check all hardening coverage
python tools/adg/adg_harden.py check --all --json out.json

# Full hardening across P0-P4
python tools/adg/adg_harden.py full --micro-wave
```

### Lifecycle Accelerator
```bash
# Generate with cache
python tools/adg/adg_lifecycle.py generate --cache

# Incremental update
python tools/adg/adg_lifecycle.py update --changed file1.py file2.py

# Auto-maintain (check → update if needed → sync)
python tools/adg/adg_lifecycle.py maintain --from-git --sync-redis
```

## Benefits

| Aspect | Before | After |
|--------|--------|-------|
| Tools | 7 separate | 3 unified |
| CI Workflows | 2 workflows | 1 workflow |
| CI Jobs | 10 jobs | 4 jobs |
| CLI Pattern | Inconsistent | Unified `verb --flags` |
| Mental Model | Complex | Simple: test/harden/lifecycle |

## Rollback

If issues arise:
1. Old 7 tools remain in original locations (backward compatible)
2. CI workflows coexist (old ones not deleted)
3. Pre-commit T10.5 still runs eager-import-lint

## Files Modified

- `tools/adg/adg_test.py` (new)
- `tools/adg/adg_harden.py` (new)
- `tools/adg/adg_lifecycle.py` (new)
- `tools/adg/ACCELERATOR_OPTIMIZATION_PLAN.md` (new)
- `.github/workflows/adg-pipeline.yml` (new)
- `.pre-commit-config.yaml` (add T10.6 hook)
- `tools/adg/accelerators/` (update to proxy to new tools)
