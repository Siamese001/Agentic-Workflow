# Canon Validator Engine (E1) - Zero-Loss Merge (ZLM) Implementation

## Overview

The Canon Validator Engine is an L5 Sub-Atomic Agentic system that implements Zero-Loss Merge (ZLM) compliance with autonomous self-correction capabilities. The engine ensures code quality through a multi-phase validation pipeline with built-in retry logic and provenance tracking.

## Architecture

### Core Phases

#### P1: AST Syntax Validation (Non-Negotiable Gate)
- **Purpose**: Validate Python syntax using AST parsing
- **Behavior**: Immediate rejection on syntax errors (no retry)
- **Exit**: `P1_SYNTAX_VIOLATION` if failed

#### P2: Docker Sandbox Test Execution
- **Purpose**: Execute tests in isolated environment
- **Behavior**: Triggers P6 self-correction on failure
- **Retry**: Up to MAX_P6_ATTEMPTS (default: 3)

#### P5: Logging and Process Registration
- **Purpose**: Watchdog monitoring and audit trail
- **Implementation**: Process registration, action logging
- **Output**: `logs/canon_validator_zlm.log`

#### P6: Self-Correction Loop
- **Purpose**: Autonomous fix generation via L5 consensus
- **Max Attempts**: 3 (configurable)
- **Behavior**: Query L5 consensus, apply fix, restart P2
- **Exit**: `P6_LIMIT_REACHED` if max attempts exhausted

#### P7: File Integrity Monitoring
- **Purpose**: Canary trap for canonical file protection
- **Behavior**: Ensures fixes only target staging files
- **Integration**: Monitors inline fix application

#### P9: Provenance and GPG Signing
- **Purpose**: Cryptographic commit signing
- **Behavior**: Sign and commit with GPG key
- **Exit**: `P9_SUCCESS` on successful commit

## Zero-Loss Merge (ZLM) Loop

```
┌─────────────────────────────────────────────────────────────┐
│                     ZLM VALIDATION LOOP                     │
└─────────────────────────────────────────────────────────────┘

1. P1 Gate Check (AST Syntax)
   ├─ PASS → Continue to P2
   └─ FAIL → EXIT (P1_SYNTAX_VIOLATION)

2. P2 Sandbox Test
   ├─ PASS → P9 Provenance → EXIT (P9_SUCCESS)
   └─ FAIL → P6 Self-Correction

3. P6 Self-Correction Loop
   ├─ Query L5 Consensus
   ├─ Apply Fix (if available)
   ├─ Check Attempt Limit
   │  ├─ < MAX_ATTEMPTS → Restart P2
   │  └─ >= MAX_ATTEMPTS → EXIT (P6_LIMIT_REACHED)
   └─ Loop Back to P2
```

## Test Coverage

### TC-ZLM-101: Standard Successful Merge
- **Scenario**: Valid code, P1/P2 pass on first attempt
- **Expected**: Immediate P9 commit, no P6 loop
- **Status**: ✅ PASS

### TC-ZLM-201: P2 Failure, P6 Single-Pass Fix
- **Scenario**: P2 fails, L5 returns correct fix on attempt 1
- **Expected**: P2 passes on attempt 2, P9 commit
- **Status**: ✅ PASS

### TC-ZLM-202: P2 Failure, P6 Multi-Pass Fix
- **Scenario**: P2 fails multiple times, fix succeeds on attempt 3
- **Expected**: P2 passes on attempt 4, P9 commit
- **Status**: ✅ PASS

### TC-ZLM-203: ZLM Hard Stop Condition
- **Scenario**: P2 fails, no fix after 3 attempts
- **Expected**: EXIT with P6_LIMIT_REACHED
- **Status**: ✅ PASS

### TC-ZLM-301: P5 Logging Integrity
- **Scenario**: Full P2/P6/P9 cycle
- **Expected**: Complete audit trail in logs
- **Status**: ✅ PASS

### TC-ZLM-302: P7 File Integrity Check
- **Scenario**: P6 applies fix to staging file
- **Expected**: No canonical file modification
- **Status**: ✅ PASS

### TC-ZLM-303: L5 Audit Trail
- **Scenario**: Full validation cycle
- **Expected**: Four distinct L5 observation nodes
- **Status**: ✅ PASS

## Usage

### Command Line

```bash
# Run ZLM validator on staged files
python agentic_core/engines/canon_validator_engine_zlm.py

# Run test suite
python tests/test_canon_validator_zlm.py
```

### Programmatic Usage

```python
from agentic_core.engines.canon_validator_engine_zlm import (
    CanonValidatorEngineZLM,
    ExitReason
)

# Initialize with staged files
staged_files = ['file1.py', 'file2.py']
engine = CanonValidatorEngineZLM(staged_files)

# Run validation
exit_reason, message = engine.run()

# Check result
if exit_reason == ExitReason.P9_SUCCESS:
    print("✅ Validation successful")
else:
    print(f"❌ Validation failed: {exit_reason.value}")
```

### Git Pre-Commit Hook Integration

```bash
#!/bin/bash
# .git/hooks/pre-commit

python agentic_core/engines/canon_validator_engine_zlm.py
exit $?
```

## Configuration

### Environment Variables

```bash
# GPG Key ID for P9 signing
export CANON_VALIDATOR_GPG_KEY="your-gpg-key-id"

# Max P6 retry attempts (default: 3)
export MAX_P6_ATTEMPTS=3

# Log level (default: INFO)
export LOG_LEVEL=INFO
```

### Custom Configuration

```python
# Customize MAX_P6_ATTEMPTS
engine = CanonValidatorEngineZLM(staged_files)
engine.MAX_P6_ATTEMPTS = 5  # Increase retry limit

# Custom commit message
engine.COMMIT_MESSAGE = "Custom ZLM commit message"

# Custom GPG key
engine.GPG_KEY_ID = "custom-gpg-key-id"
```

## Exit Codes

| Exit Code | Reason | Description |
|-----------|--------|-------------|
| 0 | P9_SUCCESS | All validations passed, commit signed |
| 1 | P1_SYNTAX_VIOLATION | AST syntax error, manual fix required |
| 1 | P6_LIMIT_REACHED | Max retry attempts exhausted |
| 1 | CRITICAL_ERROR | Unexpected system error |

## Logging

### Log Levels

- **INFO**: Normal operation events (P1, P2, P6, P9 phases)
- **WARNING**: P2 failures, retry attempts
- **ERROR**: Critical failures, ZLM limit reached

### Log Format

```
2025-12-16 20:52:36,633 - agentic_core.engines.canon_validator_engine_zlm - INFO - P5_REGISTER: CanonValidatorEngine (PID: 9772)
2025-12-16 20:52:36,634 - agentic_core.engines.canon_validator_engine_zlm - INFO - ZLM ENGINE START: Canon Validator Engine (E1)
2025-12-16 20:52:36,634 - agentic_core.engines.canon_validator_engine_zlm - INFO - P1_PASS: AST syntax validation successful
2025-12-16 20:52:36,635 - agentic_core.engines.canon_validator_engine_zlm - WARNING - P2_FAIL: Runtime failure on attempt 1
2025-12-16 20:52:36,635 - agentic_core.engines.canon_validator_engine_zlm - INFO - P6_START: Triggering L5/P6 consensus
2025-12-16 20:52:36,636 - agentic_core.engines.canon_validator_engine_zlm - INFO - ZLM_SUCCESS: Code passed P2
```

## L5 Integration

### Observation Events

- `P1_FAIL_REJECTION`: Syntax validation failure
- `P2_FAIL_ATTEMPT_N`: P2 test failure on attempt N
- `P6_NO_FIX_RETURNED`: L5 consensus returned no fix
- `ZLM_FAIL_MAX_ATTEMPTS`: Max retry limit reached

### Consensus Query

```python
# L5 consensus integration point
p6_fix = L5Consensus.query_consensus(
    code_block=source_code,
    error_message=error_stderr
)

# Expected response
P6FixResult(
    status=PhaseStatus.SUCCESS,
    corrected_code="fixed code",
    fix_description="Applied fix for...",
    confidence=0.95
)
```

## Future Enhancements

### Planned Features

1. **P3: Static Analysis Integration**
   - Integrate ruff, mypy, pylint
   - Configurable rule sets

2. **P4: Security Scanning**
   - Bandit integration
   - Dependency vulnerability checks

3. **P8: Performance Profiling**
   - Execution time tracking
   - Resource usage monitoring

4. **Enhanced L5 Consensus**
   - Multi-model consensus
   - Confidence-weighted fixes
   - Learning from successful fixes

### Integration Roadmap

- [ ] GitHub Actions workflow
- [ ] GitLab CI/CD pipeline
- [ ] Pre-commit framework plugin
- [ ] VS Code extension
- [ ] CLI tool with rich output

## Troubleshooting

### Common Issues

**Issue**: P1 syntax validation fails
- **Solution**: Fix syntax errors manually, ZLM cannot auto-fix syntax

**Issue**: P6 limit reached
- **Solution**: Review error logs, increase MAX_P6_ATTEMPTS, or fix manually

**Issue**: GPG signing fails
- **Solution**: Configure GPG key, ensure git config has signing key

**Issue**: L5 consensus not integrated
- **Solution**: Implement L5Consensus.query_consensus() method

## References

- [Zero-Loss Merge Specification](./ZLM_Specification.md)
- [L5 Sub-Atomic Architecture](./L5_Architecture.md)
- [P1-P9 Phase Documentation](./Phase_Documentation.md)
- [Test Case Specifications](./Test_Cases.md)

## License

Copyright © 2025 Agentic Workflow Project
Licensed under MIT License
