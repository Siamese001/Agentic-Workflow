# ADG Accelerators

Unified collection of Architecture Dependency Graph (ADG) accelerators for testing, hardening, and incremental updates.

## Structure

```
tools/adg/accelerators/
├── __init__.py              # Package init
├── __main__.py              # CLI entry point
├── orchestrator.py          # Core orchestration functions
├── testing/                 # Testing accelerators
│   ├── adg_test_accelerator.py -> ../../adg_test_accelerator.py
│   ├── adg_test_selector.py -> ../../adg/adg_test_selector.py
│   └── README.md
├── hardening/               # Hardening accelerators
│   ├── p0_batch_wirer.py -> ../../../p0_batch_wirer.py
│   ├── p1_batch_wire.py -> ../../../p1_batch_wire.py
│   └── README.md
├── incremental/             # Incremental accelerators
│   ├── adg_incremental_update.py -> ../../../adg_incremental_update.py
│   ├── generate_full_adg.py -> ../../../generate_full_adg.py
│   └── README.md
└── README.md                # This file
```

## Usage

### Unified CLI

```bash
# Testing accelerators
python -m tools.adg.accelerators testing gap [--top 20] [--layer L5]
python -m tools.adg.accelerators testing scope --changed file.py
python -m tools.adg.accelerators testing groups --workers 4
python -m tools.adg.accelerators testing collection-safety [--json out.json]

# Hardening accelerators
python -m tools.adg.accelerators hardening p0 --layer L3 --dim evidence --apply
python -m tools.adg.accelerators hardening p1 --apply
python -m tools.adg.accelerators hardening p2 --apply

# Incremental accelerators
python -m tools.adg.accelerators incremental update --changed file1.py file2.py
python -m tools.adg.accelerators incremental scan --cache

# Fast test runner
python -m tools.adg.accelerators fast [--adg] [--dry-run]
```

### Direct Usage

You can still use the accelerators directly:

```bash
# Testing
python tools/adg_test_accelerator.py gap --top 20
python tools/adg/adg_test_selector.py --from-diff

# Hardening
python tools/p0_batch_wirer.py --layer L3 --dim evidence --apply
python tools/p1_batch_wire.py --apply

# Incremental
python tools/adg_incremental_update.py file1.py file2.py
python tools/generate_full_adg.py --use-cache
```

## CI Integration

The ADG accelerators CI workflow (`.github/workflows/adg-accelerators-ci.yml`) provides:

- **Testing**: Collection safety, gap analysis, scoped selection
- **Hardening**: P0, P1, P2 coverage checks
- **Incremental**: Fast ADG scanning with cache

### Manual Trigger

```bash
# Run specific accelerator via GitHub Actions
gh workflow run adg-accelerators-ci.yml -f accelerator=testing-collection-safety
gh workflow run adg-accelerators-ci.yml -f accelerator=full-suite
```

## Accelerator Categories

### Testing Accelerators

1. **adg_test_accelerator.py**: Main testing accelerator
   - Gap analysis (uncovered modules by fan-in)
   - Scoped selection (test files for changed production files)
   - Parallel groups (balanced pytest-xdist groups)
   - Full report (JSON combining all)
   - Collection safety (import safety analysis)

2. **adg_test_selector.py**: Smart test selection
   - Selects tests based on ADG dependency graph
   - Integrates with pytest for efficient test runs

3. **fast_test.py**: Fast test runner
   - ADG-scoped testing mode
   - Parallel execution support

### Hardening Accelerators

1. **p0_batch_wirer.py**: P0 dimension hardening
   - Wires evidence, governance, trace, runtime dimensions
   - Micro-wave batch processing (15 modules at a time)

2. **p1_batch_wire.py**: P1 orchestration hardening
   - Routes to agent, dispatches execution plan
   - Validates agent capability, checks agent registry

3. **p2_batch_wire.py**: P2 execution capability hardening
   - Authorizes and executes, validates capability
   - Routes to capability, writes via UWG

### Incremental Accelerators

1. **adg_incremental_update.py**: Incremental ADG updates
   - Patches files → impacted closure → rescan only impacted
   - Updates SQLite with FK node resolution
   - 16.4s for 12 patched files vs 5+ min full regen

2. **generate_full_adg.py**: Full ADG generation
   - Complete scan with caching support
   - Cache stats: hits, misses, rate

## Configuration

The `config/eager_import_risk.yml` file defines:

- **Risky import roots**: agentic_core, apps_*, system_learning.runtime
- **Safe import roots**: standard library, pytest, numpy, pandas
- **Risky patterns**: registry, bootstrap, initialize, client, etc.

## Testing

Tests for the accelerators are in `tests/adg/`:

```bash
pytest tests/adg/test_adg_test_selector.py -v
pytest tests/adg/test_accelerator_wiring.py -v
pytest tests/adg/test_adg_accelerator_*.py -v
```

## Enforcement

Pre-commit hook (T10.5): `eager-import-lint`

CI gate: `pytest-collection-gate.yml`

Standards: `docs/STANDARDS.md` (Test Import Discipline section)
