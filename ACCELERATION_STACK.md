# Development Acceleration Stack — Installation Complete

## What Was Installed

### Core Acceleration Packages
- **pytest-xdist** (3.8.0) — Parallel test execution across CPU cores
- **pytest-testmon** (2.2.0) — Run only tests affected by code changes
- **pytest-timeout** (2.4.0) — Terminate hanging tests automatically
- **pytest-rerunfailures** (16.1) — Retry flaky tests
- **uv** (0.10.9) — Ultra-fast Python package installer
- **watchfiles** (1.1.1) — Efficient file watching for auto-reload workflows

### Already Installed (from previous setup)
- **pre-commit** (3.7.0+) — Git hook framework
- **pip-tools** (7.4.0+) — Dependency management
- **black**, **ruff**, **mypy** — Code quality tools

## New Files Created

### 1. `pytest_fast.ini` — Fast Local Test Profile
Fast feedback loop configuration:
- ✅ Parallel execution (`-n auto`)
- ✅ Fail-fast on first error (`-x`)
- ✅ 180s timeout per test
- ✅ **NO coverage overhead** (3-5x faster)
- ✅ Minimal output verbosity

**Usage:**
```bash
pytest -c pytest_fast.ini                    # All tests (fast)
pytest -c pytest_fast.ini tests/unit         # Unit tests only
pytest -c pytest_fast.ini -k test_name       # Specific pattern
pytest -c pytest_fast.ini --lf               # Last failures
```

### 2. `fast_test.py` — Python-First Test Runner
Convenience wrapper with ADG integration:
```bash
python fast_test.py                    # Run all tests (fast mode)
python fast_test.py unit               # Unit tests only
python fast_test.py --adg              # ADG-scoped (changed files only)
python fast_test.py --adg --dry-run    # Show ADG scope
```

**Environment variables:**
- `FAST_TEST_VERBOSE=1` — Enable verbose output
- `FAST_TEST_NO_PARALLEL=1` — Disable parallel execution

### 3. `FAST_DEV_COMMANDS.md` — Quick Reference
Complete command reference for all acceleration tools.

### 4. `ACCELERATION_STACK.md` — This file
Installation summary and usage guide.

## ADG Accelerators (Repo-Native)

All ADG tools use Python module invocation (`python -m`):

### Core ADG Operations
```bash
python -m tools.adg_cli build --rebuild              # Fresh ADG scan
python -m tools.adg_cli health                       # Health check
python -m tools.adg_cli stats                        # Statistics
python -m tools.adg_cli impact --file <path>         # Impact analysis
```

### ADG-Powered Development Tools
```bash
# Check ADG freshness (run before starting work)
python -m tools.adg.adg_stale_guard

# Select only affected tests (10-100x reduction)
python -m tools.adg.adg_test_selector --from-diff

# Incremental type checking (5-20x faster)
python -m tools.adg.adg_type_check --from-diff

# Query ADG nodes
python -m tools.adg.adg_redis_query search-nodes --query <term>
```

## Recommended Workflow

### Inner Loop (Fast Iteration)
```bash
# 1. Check ADG freshness
python -m tools.adg.adg_stale_guard

# 2. Make code changes

# 3. Run ADG-scoped tests (fastest)
python fast_test.py --adg

# 4. Run incremental type check
python -m tools.adg.adg_type_check --from-diff
```

### Pre-Commit Validation
```bash
# 5. Stage changes
git add .

# 6. Run pre-commit hooks
python -m pre_commit run

# 7. Full validation (if needed)
pytest  # Uses pytest.ini with coverage
```

## Performance Comparison

### Test Execution Speed
| Profile | Command | Speed | Coverage | Use Case |
|---------|---------|-------|----------|----------|
| **Fast** | `pytest -c pytest_fast.ini` | 3-5x faster | ❌ No | Inner loop |
| **ADG-Scoped** | `python fast_test.py --adg` | 10-100x faster | ❌ No | Changed files only |
| **Standard** | `pytest` | Baseline | ✅ Yes | Pre-commit/CI |

### Type Checking Speed
| Method | Command | Speed | Scope |
|--------|---------|-------|-------|
| **ADG Incremental** | `python -m tools.adg.adg_type_check --from-diff` | 5-20x faster | Blast radius only |
| **Full Repo** | `mypy .` | Baseline | Entire codebase |

## Key Optimizations Applied

1. **Parallel Execution** — `pytest-xdist` uses all CPU cores (`-n auto`)
2. **Fail-Fast** — Stop on first failure (`-x`) for rapid feedback
3. **Timeout Protection** — 180s limit prevents hanging tests
4. **No Coverage Overhead** — `pytest_fast.ini` skips coverage for speed
5. **ADG Test Selection** — Run only tests affected by changes
6. **ADG Type Checking** — Type-check only import blast radius
7. **Python-First Commands** — No PowerShell, all `python -m` invocation

## Troubleshooting

### ADG Redis unavailable
```bash
# Check status
python -m tools.adg.adg_stale_guard --json

# Regenerate if stale
python tools/generate_full_adg.py
python tools/adg/adg_redis_ingest.py --force
```

### Tests not found by ADG
```bash
# Show coverage gaps
python -m tools.adg.adg_test_selector --from-diff --show-gaps

# Fallback to file-level
pytest -c pytest_fast.ini <test_file.py>
```

### Pre-commit hooks failing
```bash
# Run auto-fixers
python -m pre_commit run ruff --all-files
python -m pre_commit run ruff-format --all-files
```

## Next Steps

1. **Try the fast profile:**
   ```bash
   pytest -c pytest_fast.ini tests/unit
   ```

2. **Try ADG-scoped testing:**
   ```bash
   python fast_test.py --adg --dry-run  # See what would run
   python fast_test.py --adg            # Run it
   ```

3. **Integrate into your workflow:**
   - Use `pytest_fast.ini` for inner loop development
   - Use ADG tools for surgical test/type-check runs
   - Use standard `pytest` for final validation before commit

## References

- **Quick Commands:** `FAST_DEV_COMMANDS.md`
- **Fast Test Config:** `pytest_fast.ini`
- **Standard Test Config:** `pytest.ini`
- **Dependencies:** `pyproject.toml` → `[project.optional-dependencies.dev]`
- **Pre-commit Hooks:** `.pre-commit-config.yaml`
