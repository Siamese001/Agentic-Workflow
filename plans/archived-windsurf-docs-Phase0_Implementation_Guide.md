---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\Phase0_Implementation_Guide.md'
original_relative_path: 'Phase0_Implementation_Guide.md'
source_sha256: 46a1a944499c7e189cb3062215e6158a8a557516fdd4db986d7c8f83b226da03
recovered_status: LOST_RECOVERED
last_commit: 'd394c2f55f8'
last_commit_date: '2026-03-25 13:09:42 -0400'
created_date: '2026-03-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Phase 0 Implementation Guide

**Timeline**: 1-2 days
**Objective**: Immediate performance recovery with minimal risk

---

## Wave 0.1: Bootstrap Emitter Cleanup (Day 1)

### Overview
Remove top-level `_emit_*()` calls from 30 test files that import `lifecycle_trace_contract`. These calls execute at module import time, causing ~30s overhead during test collection.

### Files Created
- `tools/strip_test_emitters.py` - Tool to identify and strip emitter calls
- `tests/unit/test_phase0_adg_performance.py` - Test suite for Phase 0
- `tools/verify_phase0.py` - Verification script

### Implementation Steps

```bash
# 1. Dry run - see what will be changed
python tools/strip_test_emitters.py --dry-run

# 2. Apply changes
python tools/strip_test_emitters.py --apply

# 3. Verify changes
python tools/strip_test_emitters.py --verify
```

### Expected Changes
Each target file will have emitter calls commented out:
```python
# Before:
_emit_records_execution_trace("test", "module", "action")
_emit_applies_guardrail("test", "file", "rule")

# After:
# REMOVED: _emit_records_execution_trace("test", "module", "action")
# REMOVED: _emit_applies_guardrail("test", "file", "rule")
```

### Verification
```bash
# Run unit tests for emitter cleanup
python -m pytest tests/unit/test_phase0_adg_performance.py::TestBootstrapEmitterCleanup -v

# Run verification
python tools/verify_phase0.py --emitters
```

### Success Criteria
- ✅ All 30 target files have emitter calls removed
- ✅ Test collection time reduced by ~30s
- ✅ Unit tests pass
- ✅ No syntax errors introduced

---

## Wave 0.2: Session-Scoped ADG Fixture (Day 1)

### Overview
Create session-scoped ADG fixtures to eliminate redundant scans across test modules. This saves 3-5 minutes per test session.

### Files Created
- `tests/conftest_adg_phase0.py` - Session fixtures implementation

### Implementation Steps

```bash
# 1. Test session fixtures
python -m pytest tests/unit/test_phase0_adg_performance.py::TestSessionADGFixtures -v

# 2. Test performance logging
python -m pytest tests/unit/test_phase0_adg_performance.py::TestPerformanceLogger -v

# 3. Test integration
python -m pytest tests/unit/test_phase0_adg_performance.py::TestPhase0Integration -v
```

### Key Fixtures

1. **`session_adg_scan`** - Full ADG scan cached for session
2. **`fast_adg_scan`** - Lightweight structural-only scan
3. **`mock_adg`** - Instant mock for unit tests
4. **`adg_performance_logger`** - Performance monitoring

### Usage in Tests

```python
def test_my_feature(session_adg_scan):
    """Use full ADG scan result."""
    edges = session_adg_scan["result"].edges
    assert len(edges) > 0

@pytest.mark.fast_adg
def test_my_feature_fast(fast_adg_scan):
    """Use lightweight scan for performance."""
    edges = fast_adg_scan["result"].edges
    # Structural analysis only

@pytest.mark.mock_adg_only
def test_my_feature_unit(mock_adg):
    """Use mock ADG for pure unit tests."""
    # No actual scanning
    assert mock_adg["edge_count"] == 0
```

### Verification
```bash
# Run all Phase 0 tests
python -m pytest tests/unit/test_phase0_adg_performance.py -v

# Verify fixtures
python tools/verify_phase0.py --fixtures

# Performance benchmark
python -m pytest tests/unit/test_phase0_adg_performance.py::TestPhase0Benchmarks -v
```

### Success Criteria
- ✅ Session scan completes in <300s
- ✅ Mock ADG creates in <0.001s
- ✅ Fast scan provides structural-only data
- ✅ All fixture tests pass

---

## Testing Strategy

### Unit Tests
Each component has comprehensive unit tests:

1. **Emitter Cleanup Tests**
   - Pattern matching validation
   - Call detection accuracy
   - Edge case handling

2. **Fixture Tests**
   - Structure validation
   - Performance requirements
   - Caching verification

3. **Performance Tests**
   - Timing benchmarks
   - Memory usage
   - Cache effectiveness

### Integration Tests
- Session vs mock performance comparison
- Fast vs full scan structure validation
- End-to-end workflow testing

### Verification Script
`tools/verify_phase0.py` provides automated verification:
```bash
# Run complete verification
python tools/verify_phase0.py --all

# Generate report
python tools/verify_phase0.py --all --output phase0_results.json
```

---

## Risk Mitigation

### Coverage Loss
- **Risk**: Removing emitters reduces ADG coverage
- **Mitigation**: Track coverage metrics before/after
- **Acceptance**: Test coverage is not production-critical

### Test Regression
- **Risk**: Changes break existing tests
- **Mitigation**: Run full test suite after each wave
- **Rollback**: Git commits enable easy rollback

### Performance Regression
- **Risk**: New fixtures slow down tests
- **Mitigation**: Benchmark at each checkpoint
- **Monitoring**: Performance logger tracks metrics

---

## Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Test collection time | ~60s | <30s | `pytest --collect-only` |
| Session scan time | N/A | <300s | Fixture timing |
| Mock ADG creation | N/A | <0.001s | Fixture timing |
| Unit test pass rate | N/A | 100% | Test results |
| Emitter calls removed | 0 | 2,280+ | Verification script |

---

## Troubleshooting

### Common Issues

1. **Emitter cleanup fails**
   ```bash
   # Check file permissions
   ls -la tests/unit_min_deps/
   
   # Verify pattern matching
   python tools/strip_test_emitters.py --dry-run | head -20
   ```

2. **Session fixture timeout**
   ```bash
   # Check cache directory
   ls -la /tmp/pytest-*
   
   # Test with smaller scope
   python -m pytest tests/unit/test_phase0_adg_performance.py::TestSessionADGFixtures::test_mock_adg_structure -v
   ```

3. **Performance regression**
   ```bash
   # Run benchmarks
   python -m pytest tests/unit/test_phase0_adg_performance.py::TestPhase0Benchmarks -v -s
   
   # Check memory usage
   python -c "import psutil; print(f'Memory: {psutil.virtual_memory().percent}%')"
   ```

---

## Next Steps

After Phase 0 completion:
1. **Validate improvements** in CI/CD pipeline
2. **Document baseline metrics** for future comparison
3. **Begin Phase 1** - Scanner architecture cleanup
4. **Monitor performance** in daily development

---

## Rollback Plan

If issues arise:
```bash
# Rollback emitter changes
git checkout HEAD~1 -- tests/unit_min_deps/ tests/unit/agentic_core/L2_execution/enforcement/

# Rollback fixtures
git checkout HEAD~1 -- tests/conftest_adg_phase0.py

# Remove Phase 0 files
rm tools/strip_test_emitters.py tools/verify_phase0.py tests/unit/test_phase0_adg_performance.py
```

Phase 0 is designed to be **low-risk, high-impact** with easy rollback capabilities.
