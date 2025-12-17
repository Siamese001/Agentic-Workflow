# Apps CV Test Suite

Comprehensive test suite for the Canon Validator Engine, providing granular testing of L1-L5 multi-layer interactions.

## Structure

```
apps_cv/
├── __init__.py                 # Suite documentation
├── conftest.py                 # Shared fixtures and utilities
├── README.md                   # This file
├── unit_mocks/                 # Phase I: Unit Tests
│   ├── __init__.py
│   ├── test_cv_u001.py        # GitKraken Input Sanitization
│   ├── test_cv_u002.py        # Redis Timeout Handling
│   ├── test_cv_u003.py        # Figma Version Parity Check
│   └── test_cv_u004.py        # MEMemory Payload Format
├── integration_logic/          # Phase II: Integration Tests
│   ├── __init__.py
│   ├── test_cv_i001.py        # Cost-Governed RAG Success Path
│   ├── test_cv_i002.py        # Design-First Correction Flow
│   ├── test_cv_i003.py        # Filesystem Dependency Check
│   └── test_cv_i004.py        # Atomic State Fix Application
├── adversarial_hardening/      # Phase III: Security Tests
│   ├── __init__.py
│   ├── test_cv_a001.py        # Chain Prompt Hijacking
│   ├── test_cv_a002.py        # Temporal Rollback Attack
│   ├── test_cv_a003.py        # Failure Logging Backpressure
│   └── test_cv_a004.py        # API Response Evasion
└── emergency_protocol/         # Phase IV: Emergency Tests
    ├── __init__.py
    ├── test_ebp_001.py        # Immediate Cessation
    ├── test_ebp_002.py        # State Rollback
    └── test_ebp_003.py        # Observability & Notification
```

## Running Tests

### Run all apps_cv tests:
```bash
cd tests
pytest apps_cv/ -v
```

### Run specific phases:
```bash
# Phase I: Unit Mocks
pytest apps_cv/unit_mocks/ -v -m unit_mocks

# Phase II: Integration Logic
pytest apps_cv/integration_logic/ -v -m integration_logic

# Phase III: Adversarial Hardening
pytest apps_cv/adversarial_hardening/ -v -m adversarial_hardening

# Phase IV: Emergency Protocol
pytest apps_cv/emergency_protocol/ -v -m emergency_protocol
```

### Run by layer:
```bash
# L1 Tests (Filesystem, GitKraken)
pytest apps_cv/ -v -m l1

# L2 Tests (Figma, Design Tokens)
pytest apps_cv/ -v -m l2

# L3 Tests (Pinecone, Brave Search)
pytest apps_cv/ -v -m l3

# L4 Tests (Redis, Atomic Transactions)
pytest apps_cv/ -v -m l4

# L5 Tests (MEMemory, Policy Layer)
pytest apps_cv/ -v -m l5
```

## Test Coverage

### Phase I: Unit Mocks (CV-U-001 to CV-U-004)
- **CV-U-001**: GitKraken input sanitization, unsafe flag removal
- **CV-U-002**: Redis timeout handling, L4_STATE_UNAVAILABLE errors
- **CV-U-003**: Figma version parity, stale version detection
- **CV-U-004**: MEMemory payload format, JSON schema compliance

### Phase II: Integration Logic (CV-I-001 to CV-I-004)
- **CV-I-001**: Cost-governed RAG, Brave vs Pinecone selection
- **CV-I-002**: Design-first correction, live version updates
- **CV-I-003**: Filesystem dependency checks, pre-flight failures
- **CV-I-004**: Atomic state fixes, L4 transaction handling

### Phase III: Adversarial Hardening (CV-A-001 to CV-A-004)
- **CV-A-001**: Chain prompt hijacking, hidden instruction quarantine
- **CV-A-002**: Temporal rollback attacks, timestamp validation
- **CV-A-003**: Failure logging backpressure, critical event priority
- **CV-A-004**: API response evasion, malformed JSON handling

### Phase IV: Emergency Bailout Protocol (EBP-001 to EBP-003)
- **EBP-001**: Immediate cessation, tool chain deregistration
- **EBP-002**: State rollback, Git reset and Redis reversion
- **EBP-003**: Observability, critical logging and notifications

## Integration with Hydrofoil Tests

The apps_cv suite complements the existing Hydrofoil test suite:
- **Hydrofoil**: High-level integration/smoke tests (16 tests)
- **apps_cv**: Deep unit and adversarial tests (15 tests)

Both suites can be run together:
```bash
pytest hydrofoil_*.py apps_cv/ -v
```

## Fixtures

Common fixtures defined in `conftest.py`:
- `mock_validator`: Basic validator with mocked dependencies
- `mock_validator_with_all_dependencies`: Full L1-L5 mocked validator
- `sample_violating_code`: Code with security violations
- `sample_compliant_code`: Clean code for testing
- `mock_time`: Consistent timestamp for testing
- `mock_redis_transaction`: Atomic transaction mock
- `mock_figma_versions`: Sample Figma version data
- `mock_rag_responses`: Mock RAG search responses

## Test Markers

Use pytest markers to organize and filter tests:
- `@pytest.mark.unit_mocks`: Phase I tests
- `@pytest.mark.integration_logic`: Phase II tests
- `@pytest.mark.adversarial_hardening`: Phase III tests
- `@pytest.mark.emergency_protocol`: Phase IV tests
- `@pytest.mark.l1` through `@pytest.mark.l5`: Layer-specific tests

## Example Test Output

```
============================= test session starts ==============================
collected 15 items

apps_cv/unit_mocks/test_cv_u001.py::TestCVU001::test_unsafe_flag_sanitization PASSED
apps_cv/unit_mocks/test_cv_u002.py::TestCVU002::test_redis_timeout_translation PASSED
...
apps_cv/emergency_protocol/test_ebp_003.py::TestEBP003::test_operator_notification PASSED

============================== 15 passed in 2.34s ==============================
```

## Maintenance

When adding new tests:
1. Follow the naming convention: `test_cv_[phase][number].py`
2. Use appropriate markers for phase and layer
3. Leverage shared fixtures from `conftest.py`
4. Document test purpose in docstring
5. Include assertions for both success and failure cases
