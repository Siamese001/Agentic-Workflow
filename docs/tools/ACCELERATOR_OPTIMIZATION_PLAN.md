# ADG Accelerators - Optimized 3-Tool Architecture

## Consolidation: 7 Tools → 3 Tools

### 1. `tools/adg/adg_test.py` - Unified Testing Accelerator
**Merges:** `adg_test_accelerator.py` + `adg_test_selector.py` + `fast_test.py`

```bash
# Gap analysis
python tools/adg/adg_test.py gap --top 20 --layer L5

# Scoped test selection  
python tools/adg/adg_test.py scope --changed file.py --from-diff

# Run tests with ADG scoping
python tools/adg/adg_test.py run --adg-scope [--parallel 4]

# Collection safety
python tools/adg/adg_test.py check [--json out.json]

# CI preflight (combines collection + gap + eager-lint)
python tools/adg/adg_test.py preflight --strict
```

### 2. `tools/adg/adg_harden.py` - Unified Hardening Accelerator
**Merges:** `p0_batch_wirer.py` + `p1_batch_wire.py` (+ p2/p3/p4 support)

```bash
# P0 dimension hardening
python tools/adg/adg_harden.py p0 --dim evidence --layer L3 --apply

# P1 orchestration hardening
python tools/adg/adg_harden.py p1 --apply

# P2 execution hardening
python tools/adg/adg_harden.py p2 --apply

# Check coverage across all phases
python tools/adg/adg_harden.py check --all

# Full hardening (P0-P4)
python tools/adg/adg_harden.py full --micro-wave
```

### 3. `tools/adg/adg_lifecycle.py` - Unified ADG Lifecycle
**Merges:** `generate_full_adg.py` + `adg_incremental_update.py`

```bash
# Full generation with cache
python tools/adg/adg_lifecycle.py generate [--cache]

# Incremental update
python tools/adg/adg_lifecycle.py update --changed file1.py file2.py

# Redis sync
python tools/adg/adg_lifecycle.py sync --to-redis

# Freshness check
python tools/adg/adg_lifecycle.py status

# Auto-maintain (check freshness → update if needed → sync)
python tools/adg/adg_lifecycle.py maintain [--on-changed file.py]
```

## CI Workflow Consolidation

### Before: 2 Workflows, 10 Jobs
- `pytest-collection-gate.yml` (3 jobs)
- `adg-accelerators-ci.yml` (7 jobs)

### After: 1 Workflow, 4 Jobs
```yaml
# .github/workflows/adg-pipeline.yml
jobs:
  test-preflight:      # adg_test.py preflight
  harden-check:        # adg_harden.py check --all
  lifecycle-maintain:  # adg_lifecycle.py maintain
  full-report:         # Summary aggregation
```

## Pre-Commit Integration

### Before: Only eager-import-lint
```yaml
- id: eager-import-lint
  entry: python tools/lint_eager_imports.py tests --strict
```

### After: ADG Preflight Gate
```yaml
- id: adg-preflight
  name: "ADG Preflight - Collection safety + gap check"
  entry: python tools/adg/adg_test.py preflight --strict --quick
```

## Migration Path

1. **Phase 1:** Create 3 new unified accelerators (backward compatible)
2. **Phase 2:** Update CI workflows to use new accelerators
3. **Phase 3:** Update pre-commit hooks
4. **Phase 4:** Deprecate old 7 accelerators (keep as shims)

## Benefits

- **Simpler mental model**: 3 tools instead of 7
- **Unified CLI patterns**: All use `verb --flags` structure
- **Reduced CI complexity**: 1 workflow instead of 2
- **Better composability**: Tools can call each other
- **Easier maintenance**: Shared code in one place
