# Eval Harness ADG MCP W1 Transport Matrix

Plan: `eval-harness-adg-mcp-open-replan-9c1f2a`  
Wave: `W1`  
Checked: `2026-06-10T15:01:12Z`  
Result: `BLOCKED_FOR_AGENT_FACING_MCP`

## Transport Evidence

Direct Codex MCP evidence:

- `mcp__adg_sqlite.adg_health` failed with `Transport closed`.
- Earlier direct W1 probes for `adg_runtime_info`, `adg_status`, `adg_nodes_by_layer`, and `adg_violations` also failed with `Transport closed`.
- Therefore W1 cannot satisfy the acceptance criterion that ADG evidence use the agent-facing MCP transport first.

Out-of-band supervisor evidence:

- `tools/mcp/check_adg_sqlite_transport.py --json` returned `status=open`.
- Heartbeat markers were fresh for `tools.mcp.launch_adg_sqlite_mcp`, `tools.adg.mcp.server`, and `tools/adg/mcp/server`.
- Supervisor state reported launcher PID `45204`; process inventory also showed launcher PID `44324` and ADG server PID `45032`.
- SQLite preflight: `status=ok`, snapshot `06082026_1212`, node count `182313`, edge count `1072457`.
- Redis preflight: `configured=true`, `status=healthy`.

Conclusion: the ADG backend and Redis hot path are healthy, but the Codex client channel to the ADG MCP server is closed. This is a client-channel mismatch, not a SQLite or Redis backend outage.

## Degraded Fallback ADG Sampling

Mode: `DEGRADED_FALLBACK_SQLITE`, because MCP tools were not callable.

Sampled ADG views from `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\adg_indexed_06082026_1212.sqlite`:

| View | Rows | W1 Signal |
|---|---:|---|
| `mv_runtime_spine_gaps` | 7 | Runtime spine connectivity gaps exist across layers; sampled L6 gap rate was `64.6%`. |
| `mv_replay_surface_gaps` | 1024 | Mutation-capable surfaces often lack replay links; sampled files include `apps_rg/runtime/internal/final_resume_assembler.py` and `agentic_core/runtime/prove_requirements/writers.py`. |
| `mv_trace_replay_eval_gaps` | 480 | Trace, replay, and eval links are not consistently bound to spine nodes. |
| `mv_exit_disposition_coverage` | 818 | Terminal disposition coverage gaps remain in core execution surfaces. |
| `mv_gateway_bypass_paths` | 0 | No gateway bypass paths were present in the sampled snapshot view. |
| `mv_eval_coverage_by_path` | 12 | Action node eval coverage is zero in sampled L0-L4 rows. |

## Harness Seam Gap Matrix

| Proposed Seam | Current Evidence | ADG/Fallback Signal | Gap | Rectification Wave |
|---|---|---|---|---|
| Whole-spine replay | `tools/eval/run_capability_regression.py`, `ops_scripts/ci/check_replay_proof.py`, `ops_scripts/verification/verify_trace_replay_coverage.py`, core contract spine tests | `mv_replay_surface_gaps=1024`, `mv_trace_replay_eval_gaps=480` | Replay assets exist, but they do not yet prove a pinned U0-to-L6 replay receipt for every promotion-relevant seam. | W2 |
| X2 micro-evals | `apps_rg/runtime/validators/*_x2.py`, `tests/_core_contract/test_ag5_x2_aggregator.py`, `apps_rg/runtime/evidence/canonical_evidence_x2.py` | `mv_eval_coverage_by_path` sampled action nodes with `coverage_pct=0.0` for L0-L4 | X2 validators exist, but canonical offline fixture families for numeric precision, sentence boundaries, leakage, unknown hard-lines, and mock rejection are not first-class. | W3.1 |
| X1D calibration trust | `tools/eval/kappa_promotion_gate.py`, `tools/exit_eval/run_judge_calibration.py`, `ops_scripts/calibration/*judge*`, `apps_rg/runtime/judges/x1d_panel_*` | Literal fallback found both kappa/agreement calibration surfaces and UWG calibration proof fields | Calibration surfaces exist, but metric semantics and snapshot identity are not consistently bound to every X1D score and promotion claim. | W3.2-W3.3 |
| L6 exhaust-to-corpus promotion | `apps_rg/runtime/shadow/*_l6.py`, `apps_rg/runtime/spine/l6_eval_before_learn_receipt.py`, `ops_scripts/apps_rg/l6_benchmarks/*` | `mv_runtime_spine_gaps` sampled L6 gap rate `64.6%`; `mv_replay_surface_gaps` shows replay-link misses | L6 findings can be emitted and benchmarked, but there is no sealed, reviewed, deterministic graduation flywheel from exhaust to corpus. | W4 |
| CI/UWG promotion binding | `agentic_core/UWG/package_driven_write_admission.py`, `ops_scripts/ci/run_eval_pipeline_acceptance.py`, `ops_scripts/ci/check_rationale_judge_calibration.py` | `mv_gateway_bypass_paths=0`; UWG code requires replay, regression, safety, calibration, and rollback refs on promotion requests | Promotion fields exist, but CI/UWG still need to require current replay, calibration, ADG transport, and baseline receipts together. | W5 |

## W1 Decision

W1 is blocked until `mcp__adg_sqlite.adg_health` and `mcp__adg_sqlite.adg_runtime_info` succeed from Codex.

No Notion status update was performed during the wave attempt. Filesystem SSOT now records the blocked W1 evidence.

## Verification

- `python tools/mcp/check_adg_sqlite_transport.py --json` with `PYTHONPATH=C:/Git/Agentic-Workflow-FRESH`: passed, `status=open`.
- `python -m pytest -p pytest_timeout tests/unit/tools/adg/test_adg_mcp_supervisor.py -q` with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`: `9 passed`.
