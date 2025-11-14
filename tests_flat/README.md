# Flattened test view

The `tests_flat/` directory is an upload-friendly mirror of a subset of the
canonical suite that lives under `tests/`.  Each flattened module simply embeds
one or more source files verbatim so ChatGPT users can share ~12 aggregates
instead of dozens of individual files.

## Can we deprecate `tests/` now?

No.  The source tree in `tests/` remains the authoritative location for every
pytest module.  The flattened copies only exist for convenience and do not
replace or supersede the originals.  Several v10.7 additions (e.g. the new core
and HIL regression suites) currently live exclusively inside `tests/`, and the
spec explicitly forbids deleting or renaming those files.

To guard against the two layouts drifting apart, the repository contains
`tests/test_flat_equivalence_v10_7.py`, which parametrically compares every
embedded block against its source file and fails if any flattened snippet stops
matching.  This gives high confidence that `tests_flat/` remains a faithful
mirror while keeping the canonical hierarchy intact.
