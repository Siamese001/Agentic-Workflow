# Pre-Code Generation Gate

MANDATORY before any code changes. Declares scope and required test coverage.

## Gate Checklist

1. **Graph-backed scope** — dependency graph confirms exact files to be changed
2. **Surface inventory** — list every changed function/class/method
3. **Coverage gaps** — for each surface, identify existing tests via ADG edges
4. **Required new tests** — for each gap, specify test name and assertion target
5. **Dimensions covered** — confirm edge cases, state transitions, determinism, fail-closed, matrix

## Evidence Format

```
## PRE_CODE_GATE
**Changed surfaces**:
  - path/to/file.py::ClassName.method_name
**Existing test coverage** (per ADG):
  - tests/unit/test_file.py::test_method — covers happy path
**Coverage gaps**:
  - ClassName.method_name — no edge case test for empty input
**Required new tests**:
  - test_method_empty_input: assert raises ValueError on empty input
  - test_method_boundary: assert returns default on None
**Dimensions**:
  - Edge cases: ✅ planned
  - State transitions: ✅ planned
  - Determinism: ✅ (no randomness in surface)
  - Fail-closed: ✅ planned
```

## Blocked Conditions

Do not proceed with code changes if:
- Any required test is not yet written
- Any coverage gap has no planned test
- ADG graph analysis is incomplete
