# Post-Code Validation

MANDATORY after any code changes.

## Validation Sequence

1. Run scoped tests (ADG-selected nodeids): `pytest <nodeids> -v`
2. Verify `collected == executed` — no deselection
3. Verify no new skips or xfail entries
4. Verify count did not drop from baseline
5. Run coverage if changed surface had no prior coverage
6. Emit `## POST_CODE_VALIDATION` in evidence

## ADG-Backed Test Selection

```bash
# Get test nodeids for changed files
python tools/adg/adg_test_selector.py --files <changed_files>

# Run selected nodeids
pytest <nodeids> -v --tb=short
```

If nodeid extraction fails: file-level fallback only, record as `## SCOPE_LOSSINESS`.

## Evidence Format

```
## POST_CODE_VALIDATION
**Tests run**: pytest <nodeids>
**Collected**: N
**Executed**: N
**Passed**: N
**Failed**: 0 (required)
**New skips**: 0 (required)
**New xfail**: 0 (required)
**Coverage delta**: +X% on changed surfaces
**Result**: PASS / FAIL
```

## Blocked Conditions

Do not commit if:
- Any test fails
- `collected != executed`
- New skips or xfail entries without allowlist entries
- Coverage dropped on changed surfaces
