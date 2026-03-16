# Fast Development Commands — Quick Reference

## ADG Accelerators (Python Module Invocation)

All commands use `python -m` pattern for reliable execution.

### ADG Core CLI
```bash
python -m tools.adg_cli build --rebuild              # Fresh ADG scan + artifacts
python -m tools.adg_cli health                       # Trust gate health check
python -m tools.adg_cli stats                        # Print ADG statistics
python -m tools.adg_cli impact --file <path>         # Change impact analysis
python -m tools.adg_cli scoped-tests --changed-files <file1,file2>  # Map changes → tests
```

### ADG Accelerators (Direct Module Execution)
```bash
python -m tools.adg.adg_stale_guard                  # Check ADG Redis freshness
python -m tools.adg.adg_stale_guard --warn           # Non-blocking freshness warning
python -m tools.adg.adg_stale_guard --json           # JSON output for scripts

python -m tools.adg.adg_test_selector --from-diff    # Select tests for git diff HEAD
python -m tools.adg.adg_test_selector --staged       # Select tests for staged files
python -m tools.adg.adg_test_selector <file> [<file>...]  # Select tests for specific files
python -m tools.adg.adg_test_selector --from-diff --pytest-args  # Output pytest-ready args

python -m tools.adg.adg_type_check --from-diff       # Incremental type check (blast radius)
python -m tools.adg.adg_type_check --from-diff --depth 2  # Deeper blast radius
python -m tools.adg.adg_type_check --from-diff --strict    # Strict mypy mode
python -m tools.adg.adg_type_check --from-diff --dry-run   # Show scope without running

python -m tools.adg.adg_redis_query search-nodes --query <term>  # Search ADG nodes
python -m tools.adg.adg_redis_query search-nodes --query <term> --layer L3  # Filter by layer
python -m tools.adg.adg_redis_query search-nodes --query <term> --entity-type class  # Filter by type
```

## Fast Test Execution

### Fast Local Profile (parallel + fail-fast + timeout, no coverage)
```bash
pytest -c pytest_fast.ini                    # Run all tests (fast mode)
pytest -c pytest_fast.ini tests/unit         # Run unit tests only
pytest -c pytest_fast.ini -k test_name       # Run specific test pattern
pytest -c pytest_fast.ini --lf               # Re-run last failures
pytest -c pytest_fast.ini --ff               # Failures first, then rest
```

### ADG-Scoped Testing (fastest — only affected tests)
```bash
# Get exact test list from ADG, then run with fast profile
python -m tools.adg.adg_test_selector --from-diff --pytest-args | xargs pytest -c pytest_fast.ini
```

### Standard Profile (coverage + full validation)
```bash
pytest                           # Uses pytest.ini (coverage enabled)
pytest tests/unit                # Unit tests with coverage
```

## Pre-Commit Hooks

### Run All Hooks
```bash
python -m pre_commit run --all-files         # Run all hooks on all files
python -m pre_commit run --files <file>      # Run hooks on specific files
```

### Run Specific Hooks
```bash
python -m pre_commit run ruff --all-files              # Lint only
python -m pre_commit run ruff-format --all-files       # Format only
python -m pre_commit run adg-burndown-gate             # Burndown ratchet
python -m pre_commit run adg-stale-guard               # ADG freshness
```

## Fast Feedback Loop Workflow

### 1. Check ADG freshness before starting
```bash
python -m tools.adg.adg_stale_guard
```

### 2. Make code changes, then run scoped tests
```bash
python -m tools.adg.adg_test_selector --from-diff --pytest-args | xargs pytest -c pytest_fast.ini
```

### 3. Run incremental type check on blast radius
```bash
python -m tools.adg.adg_type_check --from-diff
```

### 4. Stage changes and run pre-commit
```bash
git add .
python -m pre_commit run
```

### 5. Full validation before commit (if needed)
```bash
pytest  # Uses pytest.ini with coverage
```

## Performance Tips

- **Use `pytest_fast.ini` for inner loop** — 3-5x faster than default profile
- **Use ADG test selector** — runs only affected tests (10-100x reduction in test count)
- **Use ADG type check** — scoped mypy runs (5-20x faster than full repo check)
- **Check ADG freshness first** — stale ADG = wrong test selection
- **Parallel execution** — `pytest_fast.ini` uses `-n auto` (CPU cores)
- **Fail-fast** — `pytest_fast.ini` uses `-x` (stops on first failure)

## Troubleshooting

### ADG Redis not available
```bash
# Check Redis status
python -m tools.adg.adg_stale_guard --json

# Regenerate ADG if stale
python tools/generate_full_adg.py

# Re-ingest into Redis
python tools/adg/adg_redis_ingest.py --force
```

### Tests not found by ADG selector
```bash
# Show coverage gaps
python -m tools.adg.adg_test_selector --from-diff --show-gaps

# Fallback to file-level selection
pytest -c pytest_fast.ini <changed_file_test.py>
```

### Pre-commit hooks failing
```bash
# Run auto-fixers first
python -m pre_commit run ruff --all-files
python -m pre_commit run ruff-format --all-files

# Check specific gate
python -m pre_commit run adg-burndown-gate --all-files
```
