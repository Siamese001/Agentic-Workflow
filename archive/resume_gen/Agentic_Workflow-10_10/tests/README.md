# Test Suite Documentation

## Overview

This directory contains the comprehensive test suite for the Agentic-Workflow-10_10 system, organized by architectural layers and functional components.

## 📁 Directory Structure

```text
tests/
├── unit/                    # Unit tests by layer
│   ├── l1_planning/         # L1 Planning layer tests
│   ├── l2_execution/        # L2 Execution layer tests  
│   ├── l3_orchestration/    # L3 Orchestration layer tests
│   ├── l4_state/           # L4 State & Memory layer tests
│   ├── l5_safety/          # L5 Safety & Policy layer tests
│   └── test_dependency_injection.py  # DI system tests
├── features/               # Feature-specific tests
│   ├── knowledge_graph/    # KG components (triplets, entities)
│   ├── retrieval/          # RAG, vector search, meta-ranking
│   ├── prompts/            # Prompt system (v6, instructional)
│   └── agents/             # Agent component tests
├── integration/            # Cross-layer integration tests
│   ├── cross_layer/        # Tests spanning multiple layers
│   └── end_to_end/         # Full workflow tests
└── utilities/              # Test utilities and verification
    └── verify_phase_a.py   # Phase A component verification
```

## 🏗️ Test Organization Philosophy

### Layer-Based Testing (unit/)
- **L1 Planning**: Test prompt generation, query planning, strategy creation
- **L2 Execution**: Test retrieval, drafting, QA, safety execution
- **L3 Orchestration**: Test DAG building, execution order, workflow coordination
- **L4 State**: Test triplet storage, entity resolution, memory management
- **L5 Safety**: Test injection detection, policy enforcement, arbitration

### Feature-Based Testing (features/)
- **Knowledge Graph**: Triplet store, entity resolution, KG retrieval
- **Retrieval**: Vector search, hybrid search, meta-ranking
- **Prompts**: V6 instructional prompts, many-shot examples
- **Agents**: Cognitive agents, agent interactions

### Integration Testing (integration/)
- **Cross-Layer**: Test interactions between layers
- **End-to-End**: Test complete workflows from input to output

## 🚀 Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run tests by category
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -m security          # Security tests only
pytest -m kg               # Knowledge graph tests only

# Run tests by layer
pytest -m l1               # L1 Planning tests
pytest -m l2               # L2 Execution tests
pytest -m l3               # L3 Orchestration tests
pytest -m l4               # L4 State tests
pytest -m l5               # L5 Safety tests

# Run specific test files
pytest tests/unit/l5_safety/test_injection_detection.py
pytest tests/features/knowledge_graph/test_triplet_store_and_entities.py

# Run tests with coverage (if coverage plugin installed)
pytest --cov=. --cov-report=html

# Run tests in parallel (if xdist plugin installed)
pytest -n auto
```

### Test Markers

| Marker | Description | Example |
|--------|-------------|---------|
| `unit` | Unit tests for individual components | `pytest -m unit` |
| `integration` | Cross-component integration tests | `pytest -m integration` |
| `end_to_end` | Full workflow tests | `pytest -m end_to_end` |
| `security` | Security and policy tests | `pytest -m security` |
| `kg` | Knowledge graph tests | `pytest -m kg` |
| `retrieval` | Retrieval and RAG tests | `pytest -m retrieval` |
| `prompts` | Prompt system tests | `pytest -m prompts` |
| `l1-l5` | Layer-specific tests | `pytest -m l2` |
| `slow` | Long-running tests | `pytest -m "not slow"` |
| `external` | Tests requiring external dependencies | `pytest -m "not external"` |

## 📋 Test Categories

### 1. Unit Tests (`unit/`)

- **Purpose**: Test individual components in isolation
- **Scope**: Single classes, functions, or modules
- **Dependencies**: Mocked external dependencies
- **Speed**: Fast (milliseconds)

### 2. Feature Tests (`features/`)

- **Purpose**: Test complete feature functionality
- **Scope**: Multi-component features
- **Dependencies**: Some real dependencies, some mocked
- **Speed**: Medium (seconds)

### 3. Integration Tests (`integration/`)

- **Purpose**: Test component interactions
- **Scope**: Cross-layer workflows
- **Dependencies**: Real components, mocked external services
- **Speed**: Slower (seconds to minutes)

## 🛠️ Test Development Guidelines

### Writing New Tests

1. **Choose the right category**:
   - Unit test → `unit/layer_name/`
   - Feature test → `features/feature_name/`
   - Integration test → `integration/cross_layer/` or `integration/end_to_end/`

2. **Use descriptive naming**:
   ```python
   # Good
   def test_triplet_store_add_and_query():
   
   # Bad
   def test_ts_1():
   ```

3. **Include appropriate markers**:
   ```python
   @pytest.mark.unit
   @pytest.mark.l4
   @pytest.mark.kg
   def test_triplet_store_operations():
   ```

4. **Mock external dependencies**:
   ```python
   @patch('l4.pinecone_adapter.PineconeAdapter')
   def test_with_mock_pinecone(mock_adapter):
   ```

### Test Structure

```python
class TestComponentName:
    """Brief description of what this test class covers."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_adapter = Mock()
        self.component = Component(self.mock_adapter)
    
    def test_specific_functionality(self):
        """Test specific functionality with clear description."""
        # Arrange
        # Act
        # Assert
        assert result == expected
```

## 🔧 Configuration

### pytest.ini
- Configures test discovery, markers, and default options
- Located at project root
- Includes layer markers, feature markers, and execution settings

### conftest.py Files
Each test directory can include a `conftest.py` for shared fixtures:
```python
# tests/unit/l2_execution/conftest.py
@pytest.fixture
def mock_execution_context():
    return ExecutionContext(...)
```

## 📊 Test Coverage

### Current Coverage Areas
- ✅ L5 Safety & Security (injection detection - 17 tests passing)
- ⚠️ L4 State Management (triplet store, entity resolution - moved but broken imports)
- ⚠️ L2 Execution (retrieval profiles, vector search - moved but broken imports)
- ⚠️ L3 Orchestration (DAG execution, workflow - moved but broken imports)
- ⚠️ Knowledge Graph (triplets, entities, multi-hop retrieval - moved but broken imports)
- ⚠️ Prompt System (v6 instructional prompts - moved but broken imports)
- ⚠️ Integration (cross-layer, end-to-end workflows - moved but broken imports)

### Test Status Summary
- **Currently Working**: 33 tests organized by layer and feature:
  - L5 Safety & Security: 15 tests (injection detection)
  - Agents: 4 tests (agent bus, cards, registry, routing)
  - Prompts: 4 tests (compiler, meta integration, schema, store)
  - Retrieval: 3 tests (vector flow, imports)
  - Additional unit tests: 11 tests
- **Total Collectible**: 261 tests (including broken imports)
- **Deprecated**: Tests with non-existent module imports moved to deprecated/ folder

Many tests reference modules that don't exist (e.g., `prompts.cms.compiler`, `l5.arbitration_shim`) and have been moved to `tests/deprecated/` for future fixing.

### Areas for Expansion
- Performance testing
- Load testing
- Security penetration testing
- Accessibility testing

## 🐛 Debugging Tests

### Running Tests in Debug Mode
```bash
# Run with debugger
pytest --pdb

# Run specific test with debugger
pytest --pdb tests/unit/l5_safety/test_injection_detection.py::TestInjectionDetector::test_prompt_injection_detection

# Stop on first failure
pytest -x --pdb
```

### Common Issues

1. **Import Errors**: Check that imports match the new directory structure
2. **Mock Issues**: Ensure mocks are properly patched and configured
3. **Dependency Issues**: Use markers to skip tests with missing dependencies
4. **Timeout Issues**: Use `@pytest.mark.slow` for long-running tests

## 📝 Contributing

When adding new tests:

1. **Follow the naming convention**: `test_<feature>_<functionality>.py`
2. **Add appropriate markers**: Use layer and feature markers
3. **Include docstrings**: Explain what the test covers
4. **Mock external dependencies**: Don't rely on external services
5. **Test both success and failure cases**: Ensure comprehensive coverage

## 📞 Support

For test-related questions:
1. Check this README first
2. Look at existing test examples in the relevant category
3. Check pytest documentation: <https://docs.pytest.org/>
4. Check the project's CI/CD configuration for test execution details

---

**Last Updated**: 2025-01-24  
**Test Suite Version**: v10.10  
**Total Tests**: 218+ tests across all categories
