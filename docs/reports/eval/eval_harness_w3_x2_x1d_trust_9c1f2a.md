# Eval Harness W3 X2/X1D Trust

Plan: `eval-harness-adg-mcp-open-replan-9c1f2a`  
Wave: `W3`  
Implementation worktree: `C:\Git\eval-harness`  
Branch: `eval-harness`  
Result: `DONE_WITH_W1_MCP_CAVEAT`

## Scope

W3 added eval-side hard-line contracts for X2 micro-evals and X1D calibration trust without editing `agentic_core`.

Files added in the eval worktree:

- `tools/eval/x2_micro_eval.py`
- `tools/eval/x1d_calibration_trust.py`
- `data/eval/x2_micro/fixtures.json`
- `tests/unit/tools/eval/test_x2_micro_eval.py`
- `tests/unit/tools/eval/test_x1d_calibration_trust.py`

Core Author-Gate was not consumed because W3 stayed in eval tooling, fixtures, and tests only. The plan-level Author-Gate requirement still applies before any future `agentic_core` contract change.

## W3.1 X2 Micro-Evals

`tools/eval/x2_micro_eval.py` validates deterministic X2 hard-line fixtures. It treats product validators as the owner of gate logic and checks whether the fixture's observed gate outputs match the expected disposition.

Required fixture families:

- `numeric_precision`
- `sentence_boundaries`
- `leakage_self_check_separation`
- `unknown_hard_lines`
- `mock_not_allowed`

Canonical fixtures live in `data/eval/x2_micro/fixtures.json`. The CLI fails if any required family is missing, if a `BLOCK` fixture has no failed hard gate, or if an `ALLOW` fixture contains a failed hard gate.

## W3.2 Calibration Metric

`tools/eval/x1d_calibration_trust.py` establishes one canonical trust metric:

- `quadratic_weighted_kappa`

Raw agreement is explicitly rejected with `RAW_AGREEMENT_NOT_ACCEPTED`. Calibration must meet its threshold and carry `status=FRESH`.

## W3.3 Snapshot And Quorum Binding

The X1D trust contract requires:

- calibration snapshot ID present
- every trusted judge score bound to the matching calibration snapshot ID
- judge provider mode matching the receipt provider mode
- unique provider quorum meeting `required_provider_count`

Missing/stale calibration, snapshot mismatch, provider-mode mismatch, and no quorum all fail closed.

## Verification

Commands run from `C:\Git\eval-harness`:

- `python -m pytest -p pytest_timeout tests/unit/tools/eval/test_x2_micro_eval.py tests/unit/tools/eval/test_x1d_calibration_trust.py -q`
  - Result: `9 passed`
- `python -m py_compile tools/eval/x2_micro_eval.py tools/eval/x1d_calibration_trust.py`
  - Result: passed
- `python tools/eval/x2_micro_eval.py --fixtures data/eval/x2_micro`
  - Result: passed; `fixture_count=5`, `missing_required_families=[]`
- `python tools/eval/x1d_calibration_trust.py --help`
  - Result: passed

## Residual Caveat

W1 remains blocked for direct Codex ADG MCP calls: the final `mcp__adg_sqlite.adg_health` probe for this wave still returned `Transport closed`. W3 did not require ADG MCP to implement eval-side trust contracts, but later CI/UWG promotion binding must continue to treat direct ADG MCP transport as unresolved.
