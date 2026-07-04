# L6 Shadow apps_eval Grain Parity

Plan ID: `l6-shadow-apps-eval-grain-parity-f8a6c2`
Branch/worktree: `codex-apps-rg-l6-eval-grain-parity`
Primary contract: user-supplied Codex plan attachment, "L6 Shadow Observability Grain Parity with apps_eval"

## Status Tables

### Wave Progress

| Wave | Scope | Status | Evidence |
| --- | --- | --- | --- |
| W0 | Worktree, readiness, ADG evidence | Complete | Locked worktree created from `origin/main`; ADG MCP repaired once but later closed, so user-approved SQLite fallback was used. |
| W1 | Core L6 grain parity builder and microstep alignment metadata | Complete | `agentic_core/L6_observability/shadow_eval/grain_parity.py` plus alignment metadata in `microsteps.py`. |
| W2 | apps_rg L6 adapter and section-runner parity refs | Complete | `l6_apps_eval_grain_parity.json` emitted and bound into section L6 packages. |
| W3 | Post-X3 success and failure-path parity bridge binding | Complete | Success binds apps_eval rows; early failure terminals emit future-run-only WARN bridge/parity artifacts. |
| W4 | apps_eval optional artifact roles and verifier | Complete | Optional roles registered and `l6_apps_eval_grain_parity_verified` gate wired. |
| W5 | Targeted tests and smoke verification | Complete | 19 targeted tests passed; py_compile and `git diff --check` passed. |

### Phase Progress

| Phase | Status | Notes |
| --- | --- | --- |
| Planning | Complete | User approved implementation and later approved degraded local ADG fallback. |
| Evidence | Complete | DEGRADED_FALLBACK: reason=adg_mcp_transport_closed. Local SQLite snapshot `adg_indexed_07032026_2302.sqlite` was used for structural evidence. |
| Execution | Complete | Implementation landed in locked worktree branch `codex-apps-rg-l6-eval-grain-parity`. |
| Verification | Complete | Targeted pytest suite passed: 19 passed in 1.61s. |

## Objective

Make `apps_rg` L6 shadow observability emit and verify one future-run-only observation at the same microstep join grain as required `apps_eval` ScorecardRows, without giving L6 current-run authority.

## Constraints

- L6 remains post-run and future-run-only.
- L6 must not mutate current-run X2, X3, Exit, UWG, L4, retrieval, route, provider, prompt, policy, rubric, registry, or durable L4 state.
- `apps_eval` remains the eval row authority.
- Contract-only pseudo-row parity warns; real apps_eval-bound parity can pass.
- Missing rows, verdict mismatches, malformed join keys, or authority mismatch fail parity.

## ADG Evidence

ADG Provenance: backend=degraded_sqlite, snapshot=adg_indexed_07032026_2302.sqlite

DEGRADED_FALLBACK: reason=adg_mcp_transport_closed. Active `mcp__adg_sqlite.adg_health` succeeded once, then `adg_process_identity` and later `adg_health` returned `Transport closed`; user explicitly approved local fallback. Direct SQLite queries were used only for structural evidence and were not replaced with grep dependency analysis.

Target-file fallback fan evidence:

| File | Nodes | Fan-in Edges | Fan-out Edges |
| --- | ---: | ---: | ---: |
| `agentic_core/L6_observability/shadow_eval/microsteps.py` | 17 | 47 | 130 |
| `agentic_core/L6_observability/shadow_eval/__init__.py` | 50 | 115 | 375 |
| `apps_rg/runtime/shadow/l6_microstep_observability.py` | 4 | 24 | 95 |
| `apps_rg/runtime/spine/l6_shadow_eval_runner.py` | 4 | 14 | 52 |
| `apps_rg/runtime/post_x3_completion.py` | 4 | 34 | 127 |
| `apps_eval/coverage/apps_rg.py` | 1 | 18 | 126 |
| `apps_eval/l6_shadow_bridge.py` | 1 | 29 | 77 |

## Definition of Done

| Criterion | Status | Evidence |
| --- | --- | --- |
| `l6_apps_eval_grain_parity.json` emitted | Complete | apps_rg runner, apps_eval bridge, post-X3 tests. |
| Real apps_eval-bound path reports PASS with `apps_eval_rows_bound=true` | Complete | apps_eval bridge and e2e tests. |
| Section-only path reports WARN with `contract_only_pseudo_rows` | Complete | apps_rg section runner tests. |
| Failure paths emit non-mutating L6 failure bridge | Complete | post-X3 failure tests. |
| Missing L6 observations fail parity | Complete | core parity unit test. |
| Verdict mismatch fails parity | Complete | core parity unit test. |
| Authority mismatch fails parity | Complete | core parity unit test. |
| Existing apps_eval microstep coverage remains stable | Complete | apps_eval/e2e tests. |
| No L6 current-run or durable L4 mutation authority added | Complete | parity builder authority checks and post-X3 tests. |

## Verification Commands

```bash
python -m py_compile agentic_core/L6_observability/shadow_eval/grain_parity.py agentic_core/L6_observability/shadow_eval/microsteps.py agentic_core/L6_observability/shadow_eval/__init__.py apps_rg/runtime/shadow/l6_microstep_observability.py apps_rg/runtime/spine/l6_shadow_eval_runner.py apps_rg/runtime/post_x3_completion.py apps_eval/coverage/apps_rg.py apps_eval/l6_shadow_bridge.py tests/unit/agentic_core/L6_observability/shadow_eval/test_microsteps.py tests/apps_rg/test_l6_v40_shadow_eval_runner.py tests/apps_eval/test_l6_shadow_bridge.py tests/unit/apps_rg/test_post_x3_completion.py tests/e2e/test_l6_v40_apps_rg_apps_eval.py
python -m pytest tests/unit/agentic_core/L6_observability/shadow_eval/test_microsteps.py tests/apps_rg/test_l6_v40_shadow_eval_runner.py tests/apps_eval/test_l6_shadow_bridge.py tests/unit/apps_rg/test_post_x3_completion.py tests/e2e/test_l6_v40_apps_rg_apps_eval.py -q --tb=short
git diff --check
python scripts/governance/verify_codex_run_receipt.py artifacts/codex/run_receipts/l6-shadow-apps-eval-grain-parity-f8a6c2.json
```
