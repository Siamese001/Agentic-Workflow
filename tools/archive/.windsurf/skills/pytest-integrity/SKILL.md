---
name: pytest-integrity
description: Ensures pytest collection and execution counts match, preventing silent test deselection. Use when pytest is part of phase acceptance criteria, when collected and executed counts differ, or when conftest hooks may be filtering tests. Provides collection vs execution protocol and conftest hook audit procedure.
enforcement_layer: pre-commit
enforcement_timing: after_work
enforcement_type: structural
---

# Pytest Integrity Skill

Two artifacts for pytest truthfulness:

## Files

- **`collection_vs_execution_protocol.md`** — Always run `pytest --collect-only -q` then `pytest -q`. Record both counts. STOP if collected count does not match executed + failed + error (unexplained deselection). "no tests ran" is automatic fail.

- **`conftest_hook_audit.md`** — Triggered when counts mismatch. Locates all `conftest.py` files, inspects `pytest_collection_modifyitems` hooks, documents marker filtering logic, verifies marker registration in `pytest.ini`, reconciles collected vs executed counts. STOP if mismatch cannot be explained.

## When to use

- Every time pytest is run as part of phase acceptance: use `collection_vs_execution_protocol.md`.
- When collected count > executed count (unexplained): use `conftest_hook_audit.md`.
- When adding new test markers: verify registration per `conftest_hook_audit.md` step 4.
