# Author-Gate Enforcement Fix — Deferred Scope

**Plan ID:** `author-gate-enforcement-deferred-d7f5e3`  
**Parent Plan:** `author-gate-enforcement-fix-c9d4e2` (Completed)  
**Status:** Deferred  
**Created:** 2026-05-09  
**Estimated Tokens:** ~3,500

---

## Problem Statement

The Author-Gate Enforcement Fix implementation (`c9d4e2`) successfully delivered W1-W7, but the Gap Register identified four residual items requiring future attention. These are non-blocking improvements, optimizations, and edge-case coverage that were descoped to preserve delivery velocity on the core enforcement hardening.

---

## Gap Items (from Parent Plan Gap Register)

### G1: ADG Query Timeout Edge Cases

**Description:**  
Current ADG queries in `_get_adg_fan_in()` and `_get_layers_from_adg()` have a 5-second timeout, but edge cases (slow filesystem, concurrent SQLite operations) may not be handled gracefully.

**Current State:**  
- Timeout is set in `GraphProjectionBackend` but not explicitly in Author-Gate query wrappers
- Degraded fallback (`DEGRADED_FALLBACK`) fires on query failure, but retry logic is absent

**Deferred Reason:**  
Complexity vs value — rare edge case; current fail-closed behavior is acceptable for v1.

**Resolution Path:**  
Add explicit `timeout` parameter to ADG query functions, implement 1-retry with exponential backoff, log retry events to `author_gate_violations.jsonl`.

**Files Affected:**  
- `.windsurf/scripts/pre_author_gate.py` (lines 464-561)

**Estimated Effort:** 800 tokens

---

### G2: Windows vs POSIX Path Matching in Sensitive Paths

**Description:**  
`SENSITIVE_PATH_PATTERNS` uses `/` separators and `fnmatch.fnmatch()` for glob matching. Windows paths with backslashes may have edge cases in pattern matching.

**Current State:**  
- `_is_sensitive_path()` normalizes backslashes to forward slashes
- `fnmatch` patterns may behave differently on Windows vs POSIX for complex globs

**Deferred Reason:**  
Test coverage shows current normalization works for standard cases; edge cases (escaped backslashes, UNC paths) are rare in this codebase.

**Resolution Path:**  
Add comprehensive Windows path test fixtures, verify `fnmatch` behavior on Windows CI runners, add path normalization unit tests.

**Files Affected:**  
- `.windsurf/scripts/pre_author_gate.py` (lines 405-429)
- `tests/unit/windsurf_scripts/test_pre_author_gate.py` (new test class)

**Estimated Effort:** 600 tokens

---

### G3: Concurrent ADG Writes During Read

**Description:**  
If `generate_full_adg.py` runs concurrently with Author-Gate evaluation, SQLite may return `SQLITE_BUSY` errors. Current code handles this with try/except, but retry-with-backoff is absent.

**Current State:**  
- `_get_adg_fan_in()` and `_get_layers_from_adg()` catch exceptions and return `None`
- `DEGRADED_FALLBACK` receipt emitted, which is correct but suboptimal

**Deferred Reason:**  
ADG generation is typically a CI/nightly process, not concurrent with developer loops; fail-closed behavior is acceptable.

**Resolution Path:**  
Implement SQLite WAL mode for ADG artifacts, add retry-with-backoff (max 3 attempts, 100ms delay), surface retry receipts.

**Files Affected:**  
- `tools/generate/graph_projection.py` (WAL mode setting)
- `.windsurf/scripts/pre_author_gate.py` (retry logic)

**Estimated Effort:** 1,000 tokens

---

### G4: Test Isolation for ADG-Dependent Tests

**Description:**  
Integration tests (`test_pre_author_gate_integration.py`) use real ADG artifacts if available, but test isolation could be improved with deterministic mock ADG fixtures.

**Current State:**  
- Tests skip if no ADG artifacts found (`@pytest.mark.skipif`)
- Mock ADG created in `create_mock_adg` fixture is good but could be more comprehensive

**Deferred Reason:**  
Current test coverage (26 unit + integration tests) is sufficient for v1; enhanced mock fixtures are polish.

**Resolution Path:**  
Create reusable `MockADGBackend` class in `tests/unit/windsurf_scripts/fixtures/adg_mock.py`, add parametrized tests for various ADG states (fresh, stale, missing, busy).

**Files Affected:**  
- `tests/unit/windsurf_scripts/fixtures/adg_mock.py` (new file)
- `tests/unit/windsurf_scripts/test_pre_author_gate.py` (enhance mocking)

**Estimated Effort:** 1,100 tokens

---

## Non-Goals

1. No changes to core enforcement logic (shadow/block modes, trigger evaluation)
2. No new trigger types or bypass conditions
3. No changes to packet emission or UI rendering
4. No changes to decision ledger schema

---

## Dependencies

- Parent plan `author-gate-enforcement-fix-c9d4e2` must be stable in production
- CI metrics on `DEGRADED_FALLBACK` frequency to prioritize G1/G3
- Windows CI runner availability for G2 validation

---

## Acceptance Criteria

- [ ] G1: ADG queries have explicit timeout handling and retry logging
- [ ] G2: Windows path matching has dedicated test coverage
- [ ] G3: SQLite busy errors retry with backoff (max 3 attempts)
- [ ] G4: Mock ADG fixture supports all ADG states deterministically

---

## Wave Structure (Proposed)

| Wave | Gap Items | Focus | Est. Tokens | Success Criteria |
|------|-----------|-------|-------------|------------------|
| W1 | G1 | ADG timeout edge cases | 800 | Timeout + retry logging implemented |
| W2 | G2 | Windows path coverage | 600 | CI passes on Windows runner |
| W3 | G3 | Concurrent ADG resilience | 1,000 | Retry tests pass with mocked busy errors |
| W4 | G4 | Test isolation improvement | 1,100 | All ADG states mockable, tests deterministic |

---

## Related Plans

- **Parent:** `author-gate-enforcement-fix-c9d4e2.md` (Completed)
- **Sibling:** `author-gate-deferred-scope-b8c1d4.md` (shadow→block tracking)

---

*This is a deferred scope plan — no implementation without explicit re-prioritization.*
