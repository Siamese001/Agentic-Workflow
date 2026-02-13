# Phase 3: The Soul - Agent Unit Tests

This directory contains the unit testing framework for agents, implementing comprehensive testing patterns to ensure agent reliability and correctness.

## Architecture

The unit testing structure mirrors the agent hierarchy:

```text
tests/unit/
├── agentic_core/
│   ├── base_agents/          # Base agent testing
│   ├── L0_routing/       # Maintenance agents
│   ├── L1_cognition/         # Cognition agents
│   ├── L2_execution/         # Execution agents
│   ├── L3_orchestration/     # Orchestration agents
│   ├── L4_state/            # State management agents
│   ├── L5_safety/           # Safety and validation agents
│   └── L6_observability/    # Observability agents
├── apps_lic/
│   ├── engines/             # LIC engine agents
│   └── domain/              # LIC domain agents
├── apps_rg/
│   ├── engines/             # RG engine agents
│   └── domain/              # RG domain agents
├── apps_shared/
│   └── common_utils/        # Shared utility agents
├── test_agent_template.py   # Master template (copy this)
└── test_agent_template_demo.py  # Working demo example
```

## Testing Patterns

### 1. State Integrity Testing

- **Purpose**: Verify `self.state` remains immutable after initialization
- **Coverage**: Dataclass field validation, type checking, default values
- **Example**: `test_state_integrity_after_init()`

### 2. Logic Branching Testing

- **Purpose**: Mock LLM outputs to verify tool selection logic
- **Coverage**: Decision trees, prompt-to-tool mapping, conditional flows
- **Example**: `test_logic_branching_with_mocked_llm()`

### 3. Fuzzing Testing

- **Purpose**: Inject garbage/None types to test Mixin error handling
- **Coverage**: Input validation, error boundaries, graceful degradation
- **Example**: `test_fuzzing_input_validation()`

### 4. Network Isolation Testing

- **Purpose**: Verify zero network requests during unit tests
- **Coverage**: Redis, OpenAI, Anthropic, HTTP requests blocking
- **Example**: `test_network_call_isolation()`

### 5. Error Handling Robustness

- **Purpose**: Test Mixin error handling catches issues gracefully
- **Coverage**: Exception propagation, error recovery, fallback mechanisms
- **Example**: `test_error_handling_robustness()`

### 6. Signature Compliance

- **Purpose**: Verify agent follows expected interface patterns
- **Coverage**: Required methods, callable signatures, capability flags
- **Example**: `test_agent_signature_compliance()`

### 7. Performance Baseline

- **Purpose**: Ensure agent operations complete within reasonable time
- **Coverage**: Execution time limits, resource usage, efficiency
- **Example**: `test_performance_baseline()`

## Usage Guide

### Creating New Agent Tests

1. **Copy the template**:

```bash
cp tests/unit/test_agent_template.py tests/unit/your_agent_path/test_your_agent.py
```

1. **Customize the class**:

```python
class TestYourAgent(AgentUnitTestTemplate):
    AGENT_CLASS = YourAgent  # Import your actual agent class
    AGENT_MODULE_PATH = 'path.to.your.agent'
    DEFAULT_INIT_PARAMS = {
        'config': {'your': 'config'},
        'enable_healing': True
    }
```

1. **Add agent-specific tests**:

```python
def test_your_agent_specific_logic(self, agent_instance):
    # Your custom test logic here
    pass
```

### Running Tests

```bash
# Run all unit tests
python -m pytest tests/unit/ -v

# Run specific agent tests
python -m pytest tests/unit/agentic_core/L5_safety/validators/test_location_agent.py -v

# Run with coverage
python -m pytest tests/unit/ --cov=agentic_core --cov-report=html

# Run performance-focused tests
python -m pytest tests/unit/ -k "performance" -v
```

## Network Call Prevention

The framework automatically prevents network calls during unit tests:

- **Redis**: Mocked via `patch('redis.Redis')`
- **OpenAI**: Mocked via `patch('openai.ChatCompletion.create')` or `patch('openai.chat.completions.create')`
- **Anthropic**: Mocked via `patch('anthropic.Completions.create')` or `patch('anthropic.messages.create')`
- **HTTP**: Blocked via `patch('requests.*')` and `patch('urllib.request.urlopen')`

If a network call is detected, tests will fail with:

```text
NetworkCallDetectedError: Network calls detected: [(args, kwargs)]
```

## Mock Strategy

### LLM Response Mocking

```python
def _mock_llm_response(self, response_data):
    """Helper method to mock LLM responses"""
    return patch('path.to.llm.method', return_value=response_data)

# Usage
with self._mock_llm_response({'choices': [{'message': {'content': 'response'}}]}):
    result = agent_instance.execute("test input")
```

### State Inspection

```python
# Capture initial state
initial_state = asdict(agent_instance.state)

# Perform operations
agent_instance.execute("test")

# Verify state changes
assert agent_instance.state.last_action is not None
```

## Requirements

- **pytest**: Test framework
- **unittest.mock**: Mocking utilities
- **dataclasses**: For state validation
- **redis, openai, anthropic**: Mocked (not required for testing)

## Best Practices

1. **Zero Network Calls**: All tests must run without external dependencies
2. **Comprehensive Coverage**: Test all public methods and error paths
3. **Fast Execution**: Each test should complete within 5 seconds
4. **Clear Assertions**: Use descriptive assertion messages
5. **Mock Consistency**: Use the same mock patterns across all tests
6. **State Validation**: Always verify agent state after operations
7. **Error Scenarios**: Test both success and failure cases

## Integration with CI/CD

These unit tests integrate with the existing Three Pillars testing architecture:

- **Phase 1**: Pre-commit hooks (<5 seconds)
- **Phase 2**: Guardian tests (architectural integrity)
- **Phase 3**: Unit tests (agent logic and state) ← **YOU ARE HERE**

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `AGENT_CLASS` is properly imported
2. **Mock Failures**: Check mock paths match actual module structure
3. **Network Calls**: Verify all external services are properly mocked
4. **State Mutations**: Ensure state is properly copied before comparison

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Issues

If tests are slow:

1. Check for unintended network calls
2. Verify mock setup is efficient
3. Consider using `@pytest.mark.skipif` for expensive tests

## Contributing

When adding new agent tests:

1. Follow the template structure
2. Include all 7 testing patterns
3. Add agent-specific test cases
4. Verify zero network calls
5. Update this README for new patterns

## Status

✅ **COMPLETE**: Phase 3 implementation with comprehensive unit testing framework
- Template and demo working
- All 7 testing patterns implemented
- Network isolation verified
- Performance baselines established
