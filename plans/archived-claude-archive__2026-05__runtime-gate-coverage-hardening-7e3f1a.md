---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\runtime-gate-coverage-hardening-7e3f1a.md'
original_relative_path: '_archive\\2026-05\\runtime-gate-coverage-hardening-7e3f1a.md'
source_sha256: 70968f22996adf8d9650068f82bc1fe8211b73515eb463eec8adcd37bf0bfa1d
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Runtime Gate Coverage Hardening

**Status**: In Progress
**Tier**: T3 (cross-layer, multi-file, architectural)
**ADG snapshot**: `04252026_0843` (84920 nodes / 593555 edges, sqlite+redis healthy)
**Created**: 2026-04-25

## Goal

Close the 6 runtime-gate coverage gaps identified vs Anthropic + OpenAI best practices:

1. **G7 Adversarial** — extend X1F to cover indirect injection (retrieved-context poisoning) + tool-result faithfulness
2. **G5 Output Quality** — promote X1D `groundedness` to hard veto sub-gate
3. **G9 Regression** — wire `eval_taxonomy` (capability vs regression) into `eval_policies.yaml` outcome rules + `RegressionDetector` per-class tolerance
4. **G10 Cost/Latency** — add latency-quality joint band to scorecard composite
5. **G11 Privacy/Cross-Context** — add `cross_context_leakage` LLM-judged dim
6. **G13 Calibration Drift** — automated drift detector reading `unknown_budget` breach rate

## ADG_HOTSPOT_REPORT

| Target File | Layer | fan_in (imports) | Surface | Archetype | Impact |
|---|---|---|---|---|---|
| `apps_eval/engines/regression_detector.py` | L_APP | low (eval-internal) | State (baselines)+Observability | STATE_NODE | M |
| `config/exit_eval_rubrics/x1f_v1.yaml` | config | n/a (consumed by exit_eval) | Security | SAFETY_GATEKEEPER | H |
| `config/exit_eval_rubrics/x1d_v1.yaml` | config | n/a | Output quality | SAFETY_GATEKEEPER | H |
| `config/judges/rubrics.yaml` | config | high (judges + scorecard) | Security+Quality | SAFETY_GATEKEEPER | H |
| `apps_eval/config/eval_policies.yaml` | config | high (gate policies) | Execution | CENTRAL_DEPENDENCY | H |

Targets are config-heavy by design — minimizes blast radius. Single code change in `RegressionDetector` is additive (new method, no signature change).

## ADG_GRAPH_LAYER_EVIDENCE

- **mv_hotspot_centrality**: `regression_detector.py` is consumer not producer → safe to extend
- **mv_dependency_cone_risk**: Rubric YAML files are leaf consumers via loader → no fan-out risk
- **v_p1_zero_caller_infra**: New rubric files (x1d_v2, x1f_v2) inherit no callers initially; intentional (added to loader allow-list separately)
- **Semantic edges (`reads_from`)**: `exit_eval.py` reads_from `config/exit_eval_rubrics/*.yaml` — versioning by filename suffix (v1→v2) preserves backward compat
- **P-views cross-ref**: targets are pre-classified `v_p2_duplicated_adapters`-clean (config-only adds, no adapter duplication)

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|---|---|---|---|---|
| W1 | W1.1, W1.2 | Rubric extensions (X1F v2, X1D v2, rubrics.yaml security/privacy dims) | 4000 | In Progress |
| W2 | W2.1, W2.2 | Policy enforcement (eval_policies.yaml taxonomy + latency, RegressionDetector taxonomy-aware) | 5000 | Pending |
| W3 | W3.1 | Calibration drift detector (`ops_scripts/eval/calibration_drift_detector.py`) | 3000 | Pending |
| W4 | W4.1, W4.2 | Tests + validation (pytest + py_compile + ADG check) | 4000 | Pending |
| W5 | W5.1 | Commit + push (scoped to changed files) | 1000 | Pending |

## Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.1 | X1F v2 + X1D v2 rubric files | `config/exit_eval_rubrics/x1f_v2.yaml` (NEW), `x1d_v2.yaml` (NEW) | YAML schema fidelity to v1; abstain semantics for new model dims | 1500 | todo |
| W1.2 | rubrics.yaml security + privacy dims | `config/judges/rubrics.yaml` — add `sec_indirect_injection_resistance`, `sec_tool_result_faithfulness`, `cross_context_leakage` | Veto-list maintenance; threshold calibration baseline | 2500 | todo |
| W2.1 | eval_policies.yaml taxonomy + latency bands | `apps_eval/config/eval_policies.yaml` — add `taxonomy_aware_regression`, `latency_quality_bands` | Backwards compat with existing `regression_policy.threshold` | 1500 | todo |
| W2.2 | RegressionDetector taxonomy-aware tolerance | `apps_eval/engines/regression_detector.py` — add `_per_class_tolerance()`, plumb taxonomy class | Existing `tolerance_delta` constant; ScorecardRow lacks taxonomy field — must derive from suite_id prefix | 3500 | todo |
| W3.1 | Calibration drift detector | `ops_scripts/eval/calibration_drift_detector.py` (NEW) — read scorecard JSONL, compute `unknown_budget` breach rate, emit alert | Where to read historical scorecards; alert sink (stderr first; Notion later) | 3000 | todo |
| W4.1 | Unit tests | `tests/unit/apps_eval/test_regression_taxonomy.py` (NEW), `tests/unit/ops_scripts/eval/test_calibration_drift.py` (NEW) | Mocking baseline files; deterministic pseudo-data | 3000 | todo |
| W4.2 | Validation: py_compile + targeted pytest + ADG check | All edited Python files | n/a | 1000 | todo |
| W5.1 | Commit + push | git add scoped paths, commit, push | Stay scoped to chat-changed files only (per user prior pref) | 1000 | todo |

## Success Criteria

- [ ] `x1f_v2.yaml` exists with 5 dims including `indirect_injection_resistance` (hard) + `tool_result_faithfulness` (model, abstain)
- [ ] `x1d_v2.yaml` exists with `groundedness` promoted to `is_hard_gate: true, threshold: 0.80`
- [ ] `rubrics.yaml` `security_dimensions` contains 4 dims (was 2); `privacy_dimensions` block added with `cross_context_leakage`
- [ ] `eval_policies.yaml` has `taxonomy_aware_regression_policy.{capability,regression}` blocks + `latency_quality_bands`
- [ ] `RegressionDetector.detect()` honors per-class tolerance when suite carries taxonomy hint
- [ ] `calibration_drift_detector.py` runnable as `python ops_scripts/eval/calibration_drift_detector.py --window 7d`
- [ ] All edited Python files pass `python -m py_compile`
- [ ] New unit tests pass (`pytest tests/unit/apps_eval/test_regression_taxonomy.py tests/unit/ops_scripts/eval/test_calibration_drift.py -x`)
- [ ] Git commit pushed to `origin/main` (scoped to ≤12 files)

## Out of Scope (deferred)

- Wiring calibration drift detector into a scheduled job (separate plan; needs infra decision)
- Promotion gates CI verification beyond static check (already covered by `evaluation-promotion-gate.md` rule)
- Migrating exit_eval consumers from x1d_v1/x1f_v1 → v2 (versioned coexistence by design)
