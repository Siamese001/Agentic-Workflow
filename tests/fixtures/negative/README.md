# Negative fixtures for post-ADG gate precision audit (W4 P4.5)

This directory holds **known-bad fixtures** — synthetic inputs that SHOULD
trigger each post-ADG gate's violation-detection path. The audit harness at
`tests/unit/ops_scripts/ci/test_gate_precision_audit.py` asserts each gate
correctly detects its bad fixture.

A gate that **fails to detect** its own violation is classified **HOLLOW** and
scheduled for rewrite in W4 P4.6 (rewrite weak gates on graph-layer primitives).

## Fixture taxonomy

| Directory | Target gate | Known-bad pattern |
|---|---|---|
| `config_refs/` | `check_config_references.py` | `os.getenv("P45_FAKE_FLAG_DO_NOT_DECLARE")` — flag never declared in `.env.example` |
| `lifecycle_pairs/` | `check_lifecycle_pairs.py` | `sqlite3.connect(":memory:")` — no `.close()`, no `with`, no `self.*` assignment |

Other gates (`check_expected_wiring`, `check_exception_contract`,
`check_test_harness_coverage`) are audited via synthetic **in-process** inputs
— yaml rows and SQLite fixtures constructed in the test — because their
violation surface is config-driven rather than file-driven.

## Do NOT ship these fixtures to production

These files are deliberately broken. Every fixture file must live under
`tests/fixtures/negative/` and be excluded from:

- ADG extraction (snapshots must not see these as "real" code)
- Production lint / Column-5 contract scans
- Module-collision gates
- Test discovery as top-level tests (files are imported from the audit
  harness, not collected directly)

See the audit harness for import patterns.
