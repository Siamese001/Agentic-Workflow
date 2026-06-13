# Utility Silent Swallower Hardening Plan

**Objective**: Eliminate silent swallower risks in utility/ops scripts that could mask system health issues

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Risk Model & Classification

| Category | Impact | Treatment |
|----------|--------|-----------|
| Core runtime silent swallowers | CRITICAL | Already eliminated (640→0) |
| Validator/CI silent swallowers | CRITICAL | Zero tolerance - must fail loudly |
| Utility diagnostics swallowers | HIGH | Must emit failure signals |
| Local dev convenience scripts | LOW | Acceptable if isolated |

## Mandatory Rules Implementation

### 1. NO SILENT FAILURE IN GOVERNANCE PATHS
Any script used by CI, repo audits, anti-pattern scans, dependency graph generation, validator orchestration, or safety checks must fail loudly.

**Required Pattern**:
```python
except Exception as e:
    logger.exception("validator failure")
    raise
```

**Or**:
```python
except Exception as e:
    raise RuntimeError("scan failed") from e
```

### 2. RETRY LOOPS MUST TERMINATE LOUDLY
Retry logic may catch exceptions but MUST rethrow on final attempt.

**Valid Pattern**:
```python
for attempt in range(MAX_RETRIES):
    try:
        ...
        break
    except Exception as e:
        if attempt == MAX_RETRIES - 1:
            raise
        sleep(backoff)
```

### 3. UTILITY SCRIPTS MUST EMIT FAILURE SIGNALS
When failure occurs, scripts must produce at least one of:
- Non-zero exit code
- Structured log event
- Stderr message
- CI artifact

**Forbidden Pattern**:
```python
except Exception:
    pass
```

### 4. SCANNER FALSE POSITIVE CONTROL
Anti-pattern scanner must ignore:
- Retry-with-reraise patterns (explicit rethrow on final attempt)
- Explicitly annotated exceptions (`# guardian: allow-silent-swallower` with justification)

### 5. UTILITY SCRIPT CLASSIFICATION
Utility scripts must declare operational category:
- `RUNTIME_CRITICAL`
- `GOVERNANCE_CRITICAL`
- `DIAGNOSTIC_ONLY`
- `LOCAL_DEV_ONLY`

Only `LOCAL_DEV_ONLY` scripts may contain allowed swallowers.

## Implementation Plan

### Phase 1: Scanner Enhancement
- [ ] Enhance anti-pattern scanner to classify swallowers by context
- [ ] Add retry-with-reraise pattern detection
- [ ] Add guardian annotation validation
- [ ] Implement utility script classification detection

### Phase 2: Utility Script Remediation
- [ ] Identify all utility/ops scripts with silent swallowers
- [ ] Classify each script by operational category
- [ ] Remediate GOVERNANCE_CRITICAL scripts (zero tolerance)
- [ ] Add proper failure signaling to DIAGNOSTIC_ONLY scripts
- [ ] Annotate LOCAL_DEV_ONLY scripts with justification

### Phase 3: CI Guardrail Implementation
- [ ] Add CI rule to fail build if utility script swallows exceptions
- [ ] Implement deterministic failure principle enforcement
- [ ] Add structured failure reporting for governance scripts

### Phase 4: Validation & Testing
- [ ] Test failure propagation in CI pipeline
- [ ] Verify scanner accuracy for retry patterns
- [ ] Validate failure signal emission
- [ ] Ensure no false positives for legitimate retry logic

## Expected Outcome

- **Runtime code**: ✅ Zero silent swallowers (already achieved)
- **Governance/CI scripts**: ✅ Zero silent swallowers
- **Retry loops**: ✅ Allowed with mandatory rethrow
- **Local dev scripts**: ✅ Explicitly annotated exceptions only

**Core Principle**: The platform must never report a clean health state if any validator, scanner, or governance script failed internally.

## Success Metrics

1. Zero silent swallower violations in governance paths
2. All utility scripts emit failure signals
3. CI fails on hidden governance failures
4. Scanner accurately distinguishes retry patterns from true silent failures
5. Complete observability of utility script failures

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

