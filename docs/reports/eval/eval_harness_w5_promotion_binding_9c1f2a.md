# Eval Harness W5 Promotion Binding

Plan: `eval-harness-adg-mcp-open-replan-9c1f2a`  
Wave: `W5`  
Implementation worktree: `C:\Git\eval-harness`  
Branch: `eval-harness`  
Result: `DONE`

## Scope

W5 added eval-side promotion binding so CI/UWG promotion evidence can fail closed unless the harness has current receipts for replay, X2, X1D, L6 graduation, and direct ADG transport.

Files added in the eval worktree:

- `tools/eval/eval_harness_promotion_gate.py`
- `ops_scripts/ci/check_eval_harness_promotion_evidence.py`
- `docs/runbooks/eval_harness_promotion_binding.md`
- `tests/unit/tools/eval/test_eval_harness_promotion_gate.py`

No `agentic_core` files were edited. Core Author-Gate was not consumed because W5 stayed in eval tooling, CI wrapper, runbook, and tests.

## W5.1 CI Triggers And Gates

`ops_scripts/ci/check_eval_harness_promotion_evidence.py` wraps the promotion gate for CI use.

The gate records trigger coverage for promotion-sensitive paths:

- `tools/eval/`
- `data/eval/`
- `apps_rg/runtime/judges/`
- `apps_rg/runtime/shadow/`
- `apps_rg/runtime/spine/`
- `apps_rg/runtime/validators/`
- `agentic_core/UWG/`
- `ops_scripts/ci/`

The gate requires a manifest with all five receipt classes before promotion can pass.

## W5.2 UWG Promotion Evidence

`tools/eval/eval_harness_promotion_gate.py` requires:

- whole-spine replay receipt with `passed=true`, baseline status `MATCH`, and runtime receipt hash
- X2 micro-eval receipt with no missing fixture families
- X1D trust receipt with canonical metric `quadratic_weighted_kappa`, calibration snapshot, quorum, and trusted status
- L6 graduation receipt with `graduated=true` and target corpus path
- ADG transport receipt with `status=ok`, no degraded SQLite fallback, PID, snapshot ID, SQLite path, and healthy Redis. Prefer startup nonce when `adg_runtime_info` is exposed; when Codex exposes only `adg_health`/`adg_status`, the receipt must prove direct MCP health and explicitly record runtime-info unavailability.

This preserves the hard line that offline eval evidence informs promotion but does not waive live runtime gate verdicts.

## W5.3 Final Verification Evidence

Commands run from `C:\Git\eval-harness`:

- `python -m pytest -p pytest_timeout tests/unit/tools/eval/test_eval_harness_promotion_gate.py -q`
  - Initial result: duplicate `pytest_timeout` plugin registration because plugin autoload was enabled.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -p pytest_timeout tests/unit/tools/eval/test_eval_harness_promotion_gate.py -q`
  - Result: `6 passed`
- `python -m py_compile tools/eval/eval_harness_promotion_gate.py ops_scripts/ci/check_eval_harness_promotion_evidence.py`
  - Result: passed
- `python ops_scripts/ci/check_eval_harness_promotion_evidence.py --help`
  - Result: passed
- `python ops_scripts/ci/check_eval_harness_promotion_evidence.py --manifest artifacts/eval/promotion/w5_final/evidence_manifest.json --out artifacts/eval/promotion/w5_final/final_gate_report.json`
  - Result: passed

Final gate report:

- `C:\Git\eval-harness\artifacts\eval\promotion\w5_final\final_gate_report.json`

The final report passes all required evidence checks:

- replay receipt
- X2 micro-eval receipt
- X1D trust receipt
- L6 graduation receipt
- ADG transport receipt

Trigger coverage is complete across `tools/eval/`, `data/eval/`, `apps_rg/runtime/{validators,judges,shadow,spine}/`, `agentic_core/UWG/`, and `ops_scripts/ci/`.

## Final ADG Transport Check

Direct Codex ADG MCP calls now succeed. Out-of-band supervisor evidence also reports the backend and Redis healthy.

Final transport check on 2026-06-10 after Codex restart:

- Direct MCP `adg_health`: `status=ok`
- Direct MCP `adg_status`: `status=ok`
- Direct MCP `adg_nodes_by_layer(layer=L6, limit=3)`: `status=ok`, `backend_used=redis`
- Out-of-band helper `tools/mcp/check_adg_sqlite_transport.py --json`: `status=open`
- SQLite snapshot: `06082026_1212`
- SQLite path: `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\adg_indexed_06082026_1212.sqlite`
- Node count: `182313`
- Edge count: `1072457`
- Redis status: `healthy`
- Supervisor PID: `47756`
- Runtime nonce: not exposed by the current Codex `mcp__adg_sqlite` tool list; the final ADG receipt records `runtime_info_available=false` rather than inventing a nonce.
