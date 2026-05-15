# Collection Execution Integrity

Test counts are invariants. Unexpected drops = CI failure.

## Count Invariant Rules

- `collected == executed` for every test run — ANY deselection = CRITICAL FAILURE
- Count drops from baseline = FAIL
- `xfail` increases = FAIL
- Skip count increases = FAIL
- Intentional reduction requires commit justification and manual baseline update

## Baseline

`tests/_config/test_count_baseline.json` — tracked in version control.

## Validation Commands

```bash
# Collect without running
pytest --collect-only -q 2>&1 | tail -1

# Run and compare counts
pytest --tb=no -q 2>&1 | tail -3
```

## TEST_COUNT_AUDIT Evidence Format

```
## TEST_COUNT_AUDIT
**Baseline collected**: <N>
**This run collected**: <N>
**This run executed**: <N>
**Deselected**: <N> (must be 0)
**xfail count**: <N> (must not exceed baseline)
**Skip count**: <N> (must not exceed baseline)
**Result**: PASS / FAIL
```

## CI Enforcement

- `ops_scripts/ci/check_test_integrity.py` — count invariants
- `ops_scripts/ci/check_no_unconditional_xfail.py` — xfail without strict=True
