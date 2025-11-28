# v10.0 Test Suite - Quick Start Guide

## TL;DR
```bash
# Install dependencies
pip install -r requirements_test.txt

# Run all tests with coverage
pytest --cov=. --cov-report=html -v

# View coverage report
open htmlcov/index.html
```

## 5-Minute Setup

### 1. Install Dependencies
```bash
pip install -r requirements_test.txt
```

### 2. Start Redis (Optional - for integration tests)
```bash
# Using Docker
docker run -d -p 6379:6379 --name redis-test redis:7

# Or skip Redis tests
pytest -m "not redis" -v
```

### 3. Run Tests
```bash
# All tests
pytest -v

# With coverage
pytest --cov=. --cov-report=term -v

# Fast (unit tests only)
pytest -m unit -v
```

## Essential Commands

### Run by Component
```bash
# Core components (dependency injection, caching, state)
pytest test_core_v10_0.py -v

# Main workflow (async execution, CLI)
pytest test_main_v10_0.py -v

# Batch processing (concurrency, circuit breaker)
pytest test_batch_v10_0.py -v

# Meta-learning (pattern finding, proposals)
pytest test_learning_v10_0.py -v
```

### Run by Test Type
```bash
# Unit tests (fast, no external dependencies)
pytest -m unit -v

# Integration tests (slower, may need Redis)
pytest -m integration -v

# Async tests
pytest -m asyncio -v

# All except slow tests
pytest -m "not slow" -v
```

### Debugging
```bash
# Stop on first failure
pytest -x -v

# Show print statements
pytest -s -v

# Detailed failure info
pytest -vv --tb=long

# Run last failed tests
pytest --lf -v
```

### Coverage
```bash
# Terminal report
pytest --cov=. --cov-report=term -v

# HTML report
pytest --cov=. --cov-report=html -v
open htmlcov/index.html

# XML report (for CI)
pytest --cov=. --cov-report=xml -v
```

### Performance
```bash
# Parallel execution (4 workers)
pytest -n 4 -v

# Auto-detect CPU count
pytest -n auto -v

# Show slowest 10 tests
pytest --durations=10 -v
```

## Test Coverage by Component

| Component | Test File | Coverage Target | Key Tests |
|-----------|-----------|-----------------|-----------|
| Core (DI, State) | test_core_v10_0.py | >90% | WorkflowContext, CacheManager, CostTracker |
| Main Workflow | test_main_v10_0.py | >85% | Async execution, PII sanitization, CLI |
| Batch Processing | test_batch_v10_0.py | >80% | Concurrency, circuit breaker, shared cache |
| Meta-Learning | test_learning_v10_0.py | >75% | Pattern finding, hypotheses, proposals |

## Common Scenarios

### First-Time Setup
```bash
# 1. Install
pip install -r requirements_test.txt

# 2. Verify installation
pytest --version

# 3. Run smoke test
pytest test_core_v10_0.py::TestWorkflowContext::test_context_initialization -v

# 4. Run all tests
pytest -v
```

### Before Committing Code
```bash
# 1. Run all tests with coverage
pytest --cov=. --cov-report=term-missing -v

# 2. Check coverage meets minimum (85%)
# 3. Fix any failures
# 4. Commit
```

### Debugging a Failed Test
```bash
# 1. Run failed test with details
pytest test_main_v10_0.py::TestAsyncWorkflow::test_run_workflow_async_success -vv --tb=long

# 2. Add breakpoint if needed
pytest --pdb

# 3. Check logs
cat logs/pytest.log
```

### Adding New Tests
```bash
# 1. Add test to appropriate file
# 2. Run new test
pytest test_core_v10_0.py::TestNewFeature -v

# 3. Check coverage
pytest test_core_v10_0.py::TestNewFeature --cov=core_v10_0 --cov-report=term

# 4. Run full suite
pytest -v
```

## Test Structure at a Glance

```
v10_0_tests/
├── conftest.py              # Shared fixtures and config
├── pytest.ini               # Pytest configuration
├── requirements_test.txt    # Test dependencies
├── README_TESTS.md          # Full documentation
├── QUICKSTART.md            # This file
│
├── test_core_v10_0.py       # 50+ tests
│   ├── TestWorkflowContext  # Dependency injection
│   ├── TestMainGraphState   # State management
│   ├── TestCacheManager     # Caching (ROW 5)
│   ├── TestCostTracker      # Cost tracking
│   └── TestCoreIntegration  # Integration tests
│
├── test_main_v10_0.py       # 40+ tests
│   ├── TestSetup            # Setup & initialization
│   ├── TestAsyncWorkflow    # Async execution (ROW 6)
│   ├── TestCLI              # CLI interface
│   └── TestMainIntegration  # End-to-end tests
│
├── test_batch_v10_0.py      # 35+ tests
│   ├── TestSingleJobAsync   # Single job processing
│   ├── TestBatchAsync       # Batch with concurrency (ROW 6)
│   └── TestBatchErrorHandling # Error scenarios
│
└── test_learning_v10_0.py   # 30+ tests
    ├── TestLogReaderAgent   # Log reading
    ├── TestAsyncPatternFinderAgent # Pattern detection
    ├── TestAsyncHypothesisGeneratorAgent # Hypothesis generation
    └── TestMetaLearningIntegration # Full meta-learning flow
```

## Expected Test Results

```
============================= test session starts ==============================
collecting ... collected 155 items

test_core_v10_0.py::TestWorkflowContext::test_context_initialization PASSED [ 0%]
test_core_v10_0.py::TestWorkflowContext::test_get_model_client_returns_client PASSED [ 1%]
...
test_learning_v10_0.py::TestMetaLearningIntegration::test_run_meta_learning_full_flow PASSED [100%]

---------- coverage: platform darwin, python 3.11.5-final-0 -----------
Name                      Stmts   Miss  Cover   Missing
-------------------------------------------------------
core_v10_0.py               450     25    94%   123-125, 234-236
main_v10_0.py               180     15    92%   45-47, 89-91
run_batch_v10_0.py          220     30    86%   156-158, 201-205
run_learning_v10_0.py       195     40    79%   89-95, 178-185
-------------------------------------------------------
TOTAL                      1045    110    89%

======================== 155 passed in 12.34s ==============================
```

## Troubleshooting

### "Redis connection refused"
```bash
# Start Redis
docker run -d -p 6379:6379 redis:7

# Or skip Redis tests
pytest -m "not redis" -v
```

### "Import error: No module named 'core_v10_0'"
```bash
# Add project to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest -v
```

### "Async test failed"
```bash
# Install pytest-asyncio
pip install pytest-asyncio

# Verify version
pip show pytest-asyncio
```

### "Tests hanging"
```bash
# Run with timeout
pytest --timeout=60 -v

# Or kill hung test
Ctrl+C
pytest --lf -v  # Re-run last failed
```

## CI/CD Integration

### Minimal GitHub Actions
```yaml
name: Tests
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements_test.txt
      - run: pytest --cov=. --cov-report=xml -v
```

## Next Steps

1. ✅ Run `pytest -v` to verify all tests pass
2. ✅ Check coverage: `pytest --cov=. --cov-report=html -v`
3. ✅ Review failing tests (if any)
4. ✅ Add tests for new features
5. ✅ Integrate into CI/CD pipeline

## Resources

- **Full Documentation**: `README_TESTS.md`
- **Pytest Docs**: https://docs.pytest.org
- **Pytest-Asyncio**: https://pytest-asyncio.readthedocs.io
- **Coverage.py**: https://coverage.readthedocs.io

---

**Questions?** Check `README_TESTS.md` for comprehensive documentation.
**Issues?** Review troubleshooting section above.
**Contributing?** Follow test patterns in existing test files.
