# H13 — Mixed-Control Reduction Validation

wave: H13
adg_snapshot: artifacts/adg/adg_indexed_04182026_2044.sqlite
adg_snapshot_timestamp: "04182026_2044"

## Scope

- `B7-G6-05`

## Accepted threshold

Closure threshold (carry-forward accepted):
- unresolved mixed-control blocker surfaces must be `0`.

## Measurement method

Measurement test:
- `tests/unit/docs/wave_h/test_h13_mixed_control_threshold.py`

Source of truth measured:
- `docs/wave_g/G7_integrated_runtime_map/ownership_matrix.md`

Count rule:
- count matrix rows with class column value `mixed-control` in G7 ownership matrix.

## Measured value after H13 remediation

- `measured_value = 5`
- `threshold = 0`

## Pass/fail result

- threshold pass: **fail**
- rationale: unresolved mixed-control surfaces remain above closure target.

## Reproducible validation steps

1. Run: `pytest -v tests/unit/docs/wave_h/test_h13_mixed_control_threshold.py`
2. Confirm asserted values:
   - threshold `0`
   - measured mixed-control unresolved count `5`
   - measured value exceeds threshold

## Blocker result

- `B7-G6-05`: remains below score `3` in H13 due to threshold miss.
