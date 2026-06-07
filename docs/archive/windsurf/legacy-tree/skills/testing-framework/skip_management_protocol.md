# Skip Management Protocol

Zero-tolerance for unauthorized skips and xfail drift.

## Hard Rules

- `pytest.mark.skip` without allowlist entry = CONSTITUTIONAL VIOLATION
- `pytest.mark.skipif` without allowlist entry = CONSTITUTIONAL VIOLATION
- `pytest.skip()` without allowlist entry = CONSTITUTIONAL VIOLATION
- `@pytest.mark.xfail` without `strict=True` = FORBIDDEN

## Allowlist Location

`tests/_config/skip_allowlist.py` — every entry must be documented.

## Required Metadata Per Skip Entry

```python
{
    "test": "test_function_name",
    "file": "tests/path/to/test_file.py",
    "skip_type": "skip | skipif | xfail",
    "reason": "<specific reason — not 'broken' or 'TODO'>",
    "ticket": "TICKET-123",
    "expiry_date": "2026-05-01",  # or "owner": "team-name"
}
```

## Forbidden Reasons

`"broken"`, `"TODO"`, `"fix later"`, `"not working"`, `"WIP"`, `"temporary"`, `"skip for now"`

## Pre-Existing Skip Registry

`artifacts/adg/pre_existing_skip_registry.json` — all pre-existing skips registered before any repair run.

Required fields per entry: `test_id`, `skip_reason`, `cluster_id`, `registered_at`, `owner`, `expiry_date` (within 30 days), `resolution_plan` (concrete).

## CI Enforcement

- `ops_scripts/ci/check_skip_convergence_gate.py`
- `ops_scripts/ci/skip_quarantine_check.py`
