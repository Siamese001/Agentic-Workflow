# Flattened test view

`tests_flat/` is the production test surface. Every file in this directory is
automatically generated from the canonical sources in `tests/` by running
`python tools/flatten_tests.py`. The generator embeds each source module
verbatim so pytest can execute the flattened copies without mutating the
original hierarchy.

Key guarantees:
- The canonical suite under `tests/` remains untouched and authoritative.
- Each flattened file contains an embedded copy of its source plus a lightweight
  execution shim so imports and fixtures work when pytest runs against
  `tests_flat/`.
- `tests_flat/manifest.json` records the source→flat mapping and feeds
  `tests/test_flat_equivalence_v10_7.py`, which enforces byte-for-byte parity.

Workflow reminders:
- Do **not** edit files in `tests_flat/` by hand. Regenerate them with
  `python tools/flatten_tests.py`.
- Add new tests under `tests/` first; the manifest and flattened copies must be
  refreshed afterward.
- Pytest is configured to collect from `tests_flat/` only, so keeping the
  flattened mirror in sync is required for a green test run.
