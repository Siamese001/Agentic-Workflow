# Testing and Coverage

To run the full validation suite used by CI:

```bash
pytest tests/unit -q
pytest tests/integration -q
pytest tests/e2e -q
pytest tests/regression -q
tools/run_tests_with_coverage.py
```

The `tools/run_tests_with_coverage.py` helper executes pytest under Python's
standard-library `trace` module so the 90% coverage gate can be enforced even in
restricted environments where third-party plugins cannot be installed. Pass
additional pytest arguments after ``--`` if you need to narrow the run.
