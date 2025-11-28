# v10.0 Test Suite Documentation

Comprehensive pytest test suite for Resume Generation Engine v10.0 covering modularity, caching, and async performance improvements.

## Overview

This test suite validates all major v10.0 components:
- **ROW 4 (Modularity)**: Dependency injection via WorkflowContext, state decomposition
- **ROW 5 (Caching)**: Redis-based LLM response caching with CacheManager
- **ROW 6 (Performance)**: Async execution with asyncio, parallel bullet critique

## Test Files

### test_core_v10_0.py
**Coverage**: Core components, dependency injection, state management, caching
- WorkflowContext initialization and model client caching
- MainGraphState serialization/deserialization
- CacheManager functionality (key generation, set/get, statistics)
- CostTracker with ceiling checks and multi-agent tracking
- Exception types (CostCeilingExceededError, ModelAPIError, etc.)
- Integration tests for context + state + cache

**Key Tests**:
- `test_context_initialization`: Verifies all dependencies initialized
- `test_cache_key_generation`: Validates SHA256 deterministic keys
- `test_cost_ceiling_check_fail`: Confirms cost ceiling enforcement
- `test_state_round_trip`: Tests serialization integrity

**Run**: `pytest test_core_v10_0.py -v`

### test_main_v10_0.py
**Coverage**: Async workflow execution, CLI interface, integration with LangGraph
- `run_workflow_async()` success and failure paths
- PII sanitization (v9.9 security preserved)
- Cost ceiling enforcement during workflow
- Cache statistics logging
- CLI argument parsing and exit codes
- Integration tests with real state objects

**Key Tests**:
- `test_run_workflow_async_success`: Full workflow validation
- `test_run_workflow_async_cost_ceiling_exceeded`: Cost overflow handling
- `test_run_workflow_async_pii_sanitization`: Security verification
- `test_main_cli_success`: CLI interface validation

**Run**: `pytest test_main_v10_0.py -v`

### test_batch_v10_0.py
**Coverage**: Async batch processing, concurrency control, circuit breaker
- `process_single_job_async()` with various outcomes
- `run_batch_async()` with semaphore-based concurrency
- Shared WorkflowContext across batch jobs
- Circuit breaker triggering
- CSV summary generation
- Meta-learning trigger after batch

**Key Tests**:
- `test_process_single_job_success`: Single job processing
- `test_run_batch_async_concurrency_limit`: Verifies max_concurrent_llm_calls
- `test_run_batch_async_mixed_results`: Handles success/failure mix
- `test_run_batch_async_cache_sharing`: Validates shared cache

**Run**: `pytest test_batch_v10_0.py -v`

### test_learning_v10_0.py
**Coverage**: Async meta-learning, pattern finding, hypothesis generation
- LogReaderAgent reading feedback/preference logs
- AsyncPatternFinderAgent finding recurring failures
- AsyncHypothesisGeneratorAgent with critique incorporation
- AsyncProposalDrafterAgent creating change proposals
- AsyncProposalCritiqueAgent validation
- MetaPlannerAgent writing proposals to disk
- Full meta-learning graph execution

**Key Tests**:
- `test_find_patterns_success`: Pattern detection from logs
- `test_generate_hypotheses_with_critique`: Iterative refinement
- `test_critique_proposal_pass`: Proposal validation
- `test_run_meta_learning_full_flow`: End-to-end integration

**Run**: `pytest test_learning_v10_0.py -v`

### conftest.py
**Shared fixtures and configuration**:
- `sample_config`: Mock configuration object
- `mock_redis_client`: Stateful Redis mock with data storage
- `mock_anthropic_client`, `mock_gemini_client`: Async LLM mocks
- `sample_job_data`, `sample_resume_data`: Realistic test data
- `mock_validation_results`: QA validation fixtures
- `mock_cost_summary`: Cost tracking fixtures
- `mock_cache_stats`: Cache performance fixtures

## Installation

```bash
# Install test dependencies
pip install -r requirements_test.txt

# Verify installation
pytest --version
```

## Running Tests

### Run All Tests
```bash
pytest -v
```

### Run Specific Test File
```bash
pytest test_core_v10_0.py -v
```

### Run Specific Test
```bash
pytest test_core_v10_0.py::TestCacheManager::test_cache_set_and_get -v
```

### Run Tests by Marker
```bash
# Unit tests only
pytest -m unit -v

# Integration tests only
pytest -m integration -v

# Skip slow tests
pytest -m "not slow" -v
```

### Run with Coverage
```bash
# Generate coverage report
pytest --cov=. --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html
```

### Run in Parallel
```bash
# Use 4 workers
pytest -n 4 -v

# Auto-detect CPU count
pytest -n auto -v
```

### Run with Detailed Output
```bash
# Show print statements
pytest -v -s

# Show local variables on failure
pytest -v -l

# Stop on first failure
pytest -v -x
```

## Test Organization

### Markers
Tests are automatically marked based on location and naming:
- `@pytest.mark.unit`: Unit tests (test_core, test_agent)
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.asyncio`: Async tests (auto-detected)
- `@pytest.mark.slow`: Long-running tests

### Naming Conventions
- Test files: `test_<module>_v10_0.py`
- Test classes: `Test<ComponentName>`
- Test functions: `test_<scenario>_<expected_outcome>`

Examples:
- `test_cache_set_and_get`: Unit test for cache operations
- `test_workflow_async_success`: Integration test for workflow
- `test_batch_handles_exception_in_job`: Error handling test

## CI/CD Integration

### GitHub Actions Example
```yaml
name: v10.0 Test Suite

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
      
      - name: Run tests with coverage
        run: |
          pytest --cov=. --cov-report=xml --cov-report=term -v
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Test Coverage Goals

- **Core Components**: >90% coverage
- **Main Workflow**: >85% coverage
- **Batch Processing**: >80% coverage
- **Meta-Learning**: >75% coverage
- **Overall**: >85% coverage

## Debugging Failed Tests

### View Detailed Failure Info
```bash
pytest -vv --tb=long
```

### Run with PDB on Failure
```bash
pytest --pdb
```

### Capture Logs
```bash
pytest -v --log-cli-level=DEBUG
```

### Run Single Failed Test
```bash
pytest --lf  # Last failed
pytest --ff  # Failed first
```

## Mocking Strategy

### External Dependencies
- **Redis**: Mocked with stateful dictionary in conftest.py
- **LLM APIs**: Mocked with AsyncMock returning predictable responses
- **File I/O**: Uses tmp_path fixtures for isolation

### Dependency Injection
All agents receive `WorkflowContext`, making them testable:
```python
# Production
context = WorkflowContext(CONFIG, redis_client)
agent = BulletGeneratorAgent(context)

# Testing
mock_context = MagicMock(spec=WorkflowContext)
agent = BulletGeneratorAgent(mock_context)
```

## Performance Testing

### Benchmark Tests
```bash
pytest test_main_v10_0.py::TestPerformance -v --benchmark-only
```

### Async Performance
Tests verify:
- Workflow completes within timeout (5s mocked)
- Batch respects concurrency limits
- Parallel bullet critique speedup

## Common Issues

### Redis Connection Errors
If tests fail with Redis connection errors:
```bash
# Start Redis locally
docker run -d -p 6379:6379 redis:7

# Or skip Redis-dependent tests
pytest -m "not integration" -v
```

### Async Test Failures
Ensure pytest-asyncio is installed:
```bash
pip install pytest-asyncio
```

### Import Errors
Make sure project root is in PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest -v
```

## Best Practices

1. **Isolate Tests**: Use fixtures for setup/teardown
2. **Mock External Calls**: Never hit real APIs in tests
3. **Test Edge Cases**: Include error conditions, empty inputs, boundary values
4. **Async Testing**: Use `@pytest.mark.asyncio` and `AsyncMock`
5. **Parametrize**: Use `@pytest.mark.parametrize` for multiple scenarios
6. **Fast Tests**: Keep unit tests <1s, integration tests <10s

## Example Test Pattern

```python
@pytest.mark.asyncio
async def test_agent_with_context(mock_workflow_context):
    """Test agent using dependency injection"""
    # Arrange
    mock_client = mock_workflow_context.get_model_client.return_value
    mock_client.chat_completion_async.return_value = {
        "content": "Expected response"
    }
    
    agent = MyAgent(mock_workflow_context)
    
    # Act
    result = await agent.run_async(input_data)
    
    # Assert
    assert result['status'] == 'SUCCESS'
    mock_client.chat_completion_async.assert_called_once()
```

## Continuous Improvement

### Adding New Tests
1. Identify untested code paths using coverage report
2. Add test in appropriate test file
3. Use existing fixtures from conftest.py
4. Follow naming conventions
5. Add docstring explaining test purpose

### Maintaining Tests
- Update tests when adding v10.1+ features
- Remove obsolete tests for deprecated functionality
- Refactor duplicated test code into fixtures
- Keep test data realistic but minimal

## Test Metrics

Track these metrics over time:
- **Test Count**: Should grow with codebase
- **Coverage %**: Target >85% overall
- **Test Duration**: Keep suite <5min total
- **Flakiness**: Zero flaky tests allowed
- **Failure Rate**: <1% on main branch

## Support

For test issues:
1. Check this README
2. Review conftest.py fixtures
3. Run with `-vv --tb=long` for details
4. Check GitHub Issues for known problems

## Version History

- **v10.0**: Initial comprehensive test suite
  - 200+ test cases covering core, main, batch, meta-learning
  - Async test support with pytest-asyncio
  - Shared fixtures in conftest.py
  - 85%+ coverage target

---

**Last Updated**: 2025-01-09
**Test Suite Version**: 10.0.0
**Python Version**: 3.11+
**Pytest Version**: 7.4.3+
