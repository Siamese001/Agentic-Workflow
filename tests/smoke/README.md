# Smoke Test Suite

This directory contains comprehensive smoke tests for the entire agentic_core system.

## Purpose

Smoke tests verify that:
1. All modules can be imported without syntax errors
2. Basic module structure exists
3. Unimplemented modules are gracefully skipped (not failed)

## Test Structure

```
tests/smoke/
├── run_comprehensive_smoke_tests.py  # Main test runner
├── README.md                          # This file
├── conftest.py                        # Pytest configuration
└── [domain]/                          # Test directories
    ├── test_[domain]_smoke.py         # Main domain tests
    └── test_[subdomain]_smoke.py      # Subdomain tests
```

## Running Tests

### Run ALL smoke tests (recommended):
```bash
python tests/smoke/run_comprehensive_smoke_tests.py
# or
python -m pytest tests/smoke/
```

### Run specific domain tests:
```bash
python -m pytest tests/smoke/adg/
python -m pytest tests/smoke/alerting/
# etc.
```

## Test Guidelines

1. **Always use `pytest.skip()` for unimplemented modules**
   ```python
   try:
       from agentic_core.some_module import SomeClass
       assert SomeClass is not None
   except ImportError as e:
       pytest.skip(f"some_module not yet implemented: {e}")
   ```

2. **Never use `pytest.fail()` for missing modules**
   - This causes test failures for unimplemented features
   - Use `pytest.skip()` instead

3. **Mark all smoke tests with `@pytest.mark.smoke`**
   ```python
   @pytest.mark.smoke
   def test_something_importable():
       ...
   ```

## Coverage

The smoke test suite covers **ALL** domains in agentic_core:
- Core infrastructure (ADG, config, embeddings, health)
- Monitoring & observability (alerting, audit, compliance, logging, metrics, monitoring, observability, telemetry)
- Execution & orchestration (automation, deployment, infrastructure, interfaces, layers, operations, orchestration, performance, recovery, runtime, security)
- Data & analytics (analytics, backup, dashboards, reporting)
- Advanced features (experimental, experimental_features, beta_features, future_capabilities)
- Development tools (development, maintenance, optimization, research, testing, tracing, visualization)
- Integration (integration, workflows)

## History

Previously, smoke tests were run in 5 phases. This approach missed several directories that were not included in any phase. The comprehensive approach ensures ALL directories are tested consistently.

## Troubleshooting

If tests fail:
1. Check if the module actually exists
2. If the module doesn't exist, change `pytest.fail()` to `pytest.skip()`
3. If the module exists but has import errors, fix the import issues
4. Re-run the comprehensive test suite
