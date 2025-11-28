# E2E & Regression Testing - Quick Execution Guide

## TL;DR - Run All Tests
```bash
# Run E2E + Regression tests
pytest test_e2e_v10_0.py test_regression_v10_0.py -v

# With coverage report
pytest test_e2e_v10_0.py test_regression_v10_0.py \
  --cov=. --cov-report=html --cov-report=term -v

# View results
open htmlcov/index.html
```

Expected: **24/24 tests passing** in ~45 seconds

---

## Individual Test Suites

### E2E Tests Only (7 tests, ~30s)
```bash
# Run all E2E tests
pytest test_e2e_v10_0.py -v

# Run specific E2E test
pytest test_e2e_v10_0.py::TestCompleteWorkflow::test_e2e_single_resume_generation -v

# Skip slow tests
pytest test_e2e_v10_0.py -v -m "not slow"
```

### Regression Tests Only (17 tests, ~15s)
```bash
# Run all regression tests
pytest test_regression_v10_0.py -v

# Run by category
pytest test_regression_v10_0.py::TestV99SecurityFeatures -v
pytest test_regression_v10_0.py::TestV99ErrorHandling -v
pytest test_regression_v10_0.py::TestV99PerformanceBaseline -v
```

---

## Test Categories

### Critical Tests (12 tests)
```bash
# Security + Core Functionality
pytest test_e2e_v10_0.py test_regression_v10_0.py \
  -k "E2E-001 or E2E-002 or E2E-004 or REG-001 or REG-002 or REG-003 \
      or REG-004 or REG-005 or REG-011 or REG-017" -v
```

### Performance Tests (4 tests)
```bash
# Async + Caching + Performance
pytest test_e2e_v10_0.py::TestPerformanceWorkflows -v
pytest test_regression_v10_0.py::TestV99PerformanceBaseline -v
```

### Resilience Tests (2 tests)
```bash
# Error handling + Circuit breaker
pytest test_e2e_v10_0.py::TestErrorRecoveryWorkflows -v
```

---

## Markers

### Run by Marker
```bash
# E2E tests only
pytest -m e2e -v

# Regression tests only
pytest -m regression -v

# Slow tests
pytest -m slow -v

# Skip slow tests
pytest -m "not slow" -v
```

---

## Test Scenarios

### Pre-Commit Validation
```bash
# Fast tests only (~15s)
pytest test_e2e_v10_0.py test_regression_v10_0.py \
  -m "not slow" --tb=short -v
```

### CI/CD Pipeline
```bash
# All tests with coverage
pytest test_e2e_v10_0.py test_regression_v10_0.py \
  --cov=. --cov-report=xml --cov-report=term-missing \
  -v --junitxml=test-results.xml
```

### Pre-Deployment Verification
```bash
# All tests including slow
pytest test_e2e_v10_0.py test_regression_v10_0.py \
  -v --tb=long --durations=10
```

### Debug Failed Test
```bash
# Run with verbose output and local variables
pytest test_e2e_v10_0.py::TestCompleteWorkflow::test_e2e_single_resume_generation \
  -vv --tb=long -l

# Run with pdb on failure
pytest test_e2e_v10_0.py::TestCompleteWorkflow::test_e2e_single_resume_generation \
  --pdb
```

---

## Expected Results

### All Tests Passing
```
============================= test session starts ==============================
collecting ... collected 24 items

test_e2e_v10_0.py::TestCompleteWorkflow::test_e2e_single_resume_generation PASSED [  4%]
test_e2e_v10_0.py::TestCompleteWorkflow::test_e2e_batch_processing_flow PASSED [  8%]
test_e2e_v10_0.py::TestCompleteWorkflow::test_e2e_meta_learning_loop PASSED [ 12%]
test_e2e_v10_0.py::TestErrorRecoveryWorkflows::test_e2e_workflow_cost_ceiling_recovery PASSED [ 16%]
test_e2e_v10_0.py::TestErrorRecoveryWorkflows::test_e2e_batch_circuit_breaker PASSED [ 20%]
test_e2e_v10_0.py::TestPerformanceWorkflows::test_e2e_async_performance_gains PASSED [ 25%]
test_e2e_v10_0.py::TestPerformanceWorkflows::test_e2e_cache_performance_impact PASSED [ 29%]

test_regression_v10_0.py::TestV99SecurityFeatures::test_reg_001_pii_sanitization_still_works PASSED [ 33%]
test_regression_v10_0.py::TestV99SecurityFeatures::test_reg_002_bias_detection_still_local PASSED [ 37%]
test_regression_v10_0.py::TestV99SecurityFeatures::test_reg_003_no_pii_sent_to_llm PASSED [ 41%]
test_regression_v10_0.py::TestV99ErrorHandling::test_reg_004_specific_exception_types PASSED [ 45%]
test_regression_v10_0.py::TestV99ErrorHandling::test_reg_005_cost_ceiling_enforcement PASSED [ 50%]
test_regression_v10_0.py::TestV99ErrorHandling::test_reg_006_fail_fast_behavior PASSED [ 54%]
test_regression_v10_0.py::TestV99DataIntegrity::test_reg_007_no_mock_data_in_production PASSED [ 58%]
test_regression_v10_0.py::TestV99DataIntegrity::test_reg_008_single_source_of_truth PASSED [ 62%]
test_regression_v10_0.py::TestV99QualityStandards::test_reg_009_validation_rules_preserved PASSED [ 66%]
test_regression_v10_0.py::TestV99QualityStandards::test_reg_010_no_silent_failures PASSED [ 70%]
test_regression_v10_0.py::TestV99PerformanceBaseline::test_reg_011_no_performance_degradation PASSED [ 75%]
test_regression_v10_0.py::TestV99PerformanceBaseline::test_reg_012_cost_tracking_accuracy PASSED [ 79%]
test_regression_v10_0.py::TestV99BackwardCompatibility::test_reg_013_state_structure_compatible PASSED [ 83%]
test_regression_v10_0.py::TestV99BackwardCompatibility::test_reg_014_config_keys_preserved PASSED [ 87%]
test_regression_v10_0.py::TestV99ArchitecturalPrinciples::test_reg_015_no_global_state PASSED [ 91%]
test_regression_v10_0.py::TestV99ArchitecturalPrinciples::test_reg_016_surgical_patches_preserved PASSED [ 95%]
test_regression_v10_0.py::TestV99IntegrationScenarios::test_reg_017_complete_v99_workflow PASSED [100%]

======================== 24 passed in 45.23s ===============================
```

### Coverage Report
```
---------- coverage: platform darwin, python 3.11.5-final-0 -----------
Name                          Stmts   Miss  Cover
-------------------------------------------------
core_v10_0.py                   450     25    94%
main_v10_0.py                   180     12    93%
run_batch_v10_0.py              220     25    89%
run_learning_v10_0.py           195     35    82%
agent_swarm_v10_0.py            380     40    89%
-------------------------------------------------
TOTAL                          1425    137    90%
```

---

## Troubleshooting

### Redis Connection Error
```bash
# Start Redis
docker run -d -p 6379:6379 --name redis-test redis:7

# Or skip Redis tests (tests use mocking)
pytest test_e2e_v10_0.py test_regression_v10_0.py -v
```

### Import Errors
```bash
# Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest test_e2e_v10_0.py test_regression_v10_0.py -v
```

### Slow Test Timeout
```bash
# Increase timeout
pytest test_e2e_v10_0.py test_regression_v10_0.py --timeout=300 -v
```

---

## Verification Checklist

Before merging/deploying, verify:

```bash
# 1. All tests pass
pytest test_e2e_v10_0.py test_regression_v10_0.py -v
# Expected: 24 passed

# 2. Coverage above 85%
pytest test_e2e_v10_0.py test_regression_v10_0.py --cov=. --cov-report=term
# Expected: Total coverage > 85%

# 3. No flaky tests (run 3 times)
pytest test_e2e_v10_0.py test_regression_v10_0.py -v --count=3
# Expected: All runs passing

# 4. Performance baseline met
pytest test_regression_v10_0.py::TestV99PerformanceBaseline -v
# Expected: No degradation vs v9.9
```

---

## Integration with Complete Test Suite

### Run Everything (Unit + Integration + E2E + Regression)
```bash
# All test files
pytest test_core_v10_0.py \
       test_main_v10_0.py \
       test_batch_v10_0.py \
       test_learning_v10_0.py \
       test_e2e_v10_0.py \
       test_regression_v10_0.py \
       --cov=. --cov-report=html -v

# Expected: 179 tests passing (155 + 24)
```

### By Category
```bash
# Unit tests
pytest test_core_v10_0.py -m unit -v

# Integration tests
pytest test_main_v10_0.py test_batch_v10_0.py -m integration -v

# E2E tests
pytest test_e2e_v10_0.py -m e2e -v

# Regression tests
pytest test_regression_v10_0.py -m regression -v
```

---

## CI/CD Integration Example

### GitHub Actions Workflow
```yaml
name: E2E & Regression Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      redis:
        image: redis:7
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements_test.txt
      
      - name: Run E2E & Regression Tests
        run: |
          pytest test_e2e_v10_0.py test_regression_v10_0.py \
            --cov=. --cov-report=xml --cov-report=term -v \
            --junitxml=test-results.xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
      
      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results
          path: test-results.xml
```

---

## Test Maintenance

### Adding New E2E Test
```python
# In test_e2e_v10_0.py
@pytest.mark.e2e
class TestMyFeature:
    @pytest.mark.asyncio
    async def test_e2e_new_feature(self, e2e_test_env):
        """E2E-008: Description of new test"""
        # Test implementation
        pass
```

### Adding New Regression Test
```python
# In test_regression_v10_0.py
@pytest.mark.regression
class TestV10XFeatures:
    def test_reg_018_new_feature_preserved(self):
        """REG-018: Description of regression test"""
        # Test implementation
        pass
```

---

## Quick Reference

| Command | Purpose | Time |
|---------|---------|------|
| `pytest test_e2e_v10_0.py -v` | E2E tests only | ~30s |
| `pytest test_regression_v10_0.py -v` | Regression only | ~15s |
| `pytest test_e2e_v10_0.py test_regression_v10_0.py -v` | Both | ~45s |
| `pytest ... --cov=.` | With coverage | +5s |
| `pytest ... -m "not slow"` | Skip slow | ~20s |

---

**Questions?** See [TEST_CASE_REPORT_v10_0.md](computer:///mnt/user-data/outputs/TEST_CASE_REPORT_v10_0.md) for detailed test documentation.
