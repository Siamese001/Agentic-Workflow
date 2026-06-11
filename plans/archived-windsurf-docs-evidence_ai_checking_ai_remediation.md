---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\evidence_ai_checking_ai_remediation.md'
original_relative_path: 'evidence_ai_checking_ai_remediation.md'
source_sha256: 2e06fd76210616b4e0c489dbc8102bb5bf4902f41851ec8759f05fa1905429ed
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-09'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# AI-Checking-AI Remediation — Phase Evidence

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Scope

Declared scope (git diff --name-only HEAD):

```
agentic_core/L5_safety/reasoning/RegressionOracleAgent.py
agentic_core/L5_safety/reasoning/SafetyInspectorAgent.py
agentic_core/config/core/reflection_config.py
apps_shared/types/judge_evaluator_types.py
```

New files created (not in diff; untracked):

```
ops_scripts/ci/scan_llm_validator_calls.py
ops_scripts/ci/llm_validator_allowlist.json
tests/guardian/test_llm_validator_no_new_gaps.py
tests/unit/test_ai_checking_ai_hardenings.py
```

No out-of-scope files modified.

---

## INSPECTED_FILES

| File | Gap | Change Summary |
|---|---|---|
| `agentic_core/config/core/reflection_config.py` | GAP-02 | Fail-closed for required criteria on CircuitOpenError or Exception; added missing Optional/Callable/Awaitable/validator imports; fallback CircuitBreakerFactory.get() added |
| `agentic_core/L5_safety/reasoning/SafetyInspectorAgent.py` | GAP-04 | `_socratic_verify` hardened: rate limit (max_socratic_calls), 5s timeout, structured `_socratic_audit_log`, snippet sanitization; fixed all LOGGER→Logger pre-existing bugs |
| `apps_shared/types/judge_evaluator_types.py` | GAP-01 | `evaluate()` appends structured audit entry per call; model_id tracking; heuristic anchor cross-check with configurable tolerance; anchor_alert flag; fixed missing Awaitable import |
| `agentic_core/L5_safety/reasoning/RegressionOracleAgent.py` | GAP-05 | MAX_CORRECTION_ITERATIONS=3 class constant; `_ast_safety_check()` static method rejects exec/eval/os.system/__import__/compile/subprocess before execution |
| `ops_scripts/ci/scan_llm_validator_calls.py` | Wave 1 | AST scanner: walks validation/scoring function bodies for LLM attr-root + call-name hits; compares against allowlist |
| `ops_scripts/ci/llm_validator_allowlist.json` | Wave 1 | 12-entry allowlist for all known GAP-01..GAP-08 sites with hardened flag and justification |
| `tests/guardian/test_llm_validator_no_new_gaps.py` | Wave 2 | 5 guardian tests: file existence, schema, zero new LLM calls, ML import ceiling, allowlist references real files |
| `tests/unit/test_ai_checking_ai_hardenings.py` | Wave 7 | 56 unit tests across all 4 gaps + full §1.5 edge-case matrix |

---

## Commands Executed

### §3.1 Scope check

```
git diff --name-only HEAD
```

Exit 0. Output: 5 files (4 logic + 1 rules). All within declared scope.

### §1.12 Full test execution

```
python -m pytest tests/unit/test_ai_checking_ai_hardenings.py tests/guardian/test_llm_validator_no_new_gaps.py -v --tb=short
```

Exit 0. Result: **56 passed, 0 failed, 0 skipped, 2 warnings** in 4.37s.

Collected == Executed: 56 == 56. No mismatch.

---

## BRANCH_INVENTORY

| Branch | Condition | Coverage |
|---|---|---|
| GAP-02 circuit-open + required criteria | `CircuitOpenError` raised, `is_required=True` | `test_fail_closed_required_criterion_on_circuit_open` |
| GAP-02 circuit-open + optional only | `CircuitOpenError` raised, `is_required=False` | `test_fail_open_optional_criterion_on_circuit_open` |
| GAP-02 unexpected exception + required | `RuntimeError`, `is_required=True` | `test_fail_closed_required_on_unexpected_exception` |
| GAP-02 empty criteria | `criteria=[]` | `test_empty_criteria_list_does_not_raise` |
| GAP-02 repeated circuit-open | same input × 2 | `test_circuit_open_is_deterministic_across_repeated_calls` |
| GAP-02 mixed required+optional | one of each | `test_mixed_criteria_required_dominates_on_circuit_open` |
| GAP-02 None content | `content=None` | `test_none_content_does_not_raise` |
| GAP-02 stats increment on fallback | circuit-open path | `test_stats_total_critiques_increments_on_circuit_open` |
| GAP-04 rate limit = 0 | first call blocked | `test_max_calls_zero_always_rate_limits`, `test_rate_limited_call_does_not_increment_counter` |
| GAP-04 rate limit = 1 exact boundary | second call blocked | `test_call_at_limit_is_rate_limited` |
| GAP-04 timeout path | `asyncio.TimeoutError` | `test_audit_log_populated_on_timeout` |
| GAP-04 audit log schema | all required keys | `test_audit_log_entry_schema` |
| GAP-04 counter increment | non-rate-limited call | `test_call_counter_increments` |
| GAP-04 snippet sanitization | credential line stripped | `test_snippet_sanitization_excludes_credential_lines` |
| GAP-04 audit log length == call count | 2 calls → 2 entries | `test_audit_log_length_matches_total_calls` |
| GAP-04 nonexistent file path | missing file | `test_nonexistent_file_path_does_not_raise` |
| GAP-01 audit log entry on heuristic path | no LLM client | `test_audit_log_entry_on_heuristic_evaluate` |
| GAP-01 model_id=heuristic when no LLM | llm_client=None | `test_model_id_defaults_to_heuristic_when_no_llm` |
| GAP-01 model_id=unknown when LLM no id | llm_client set, no model_id | `test_model_id_defaults_to_unknown_when_llm_no_model_id` |
| GAP-01 model_id stored when provided | explicit model_id | `test_model_id_stored_when_provided` |
| GAP-01 anchor=1.0 identical strings | output==expected | `test_heuristic_anchor_with_matching_expected` |
| GAP-01 anchor=0.0 empty output | output="" | `test_heuristic_anchor_empty_output` |
| GAP-01 evaluation_path=heuristic | no LLM | `test_audit_log_evaluation_path_is_heuristic` |
| GAP-01 anchor_alert on large deviation | tolerance=0.01 | `test_anchor_alert_set_on_large_deviation` |
| GAP-01 empty output | output="" | `test_empty_string_output_does_not_raise` |
| GAP-01 None expected | expected=None | `test_none_expected_produces_valid_result` |
| GAP-01 whitespace output | output="  \n\t" | `test_whitespace_only_output` |
| GAP-01 empty criteria list | criteria=[] | `test_empty_criteria_list_raises_or_returns_safely` |
| GAP-01 threshold=0.0 always passes | pass_threshold=0.0 | `test_threshold_exactly_met_is_passing` |
| GAP-01 threshold=1.0 mismatch fails | pass_threshold=1.0 | `test_threshold_above_max_score_always_fails` |
| GAP-01 replayed hash determinism | same input × 2 | `test_identical_input_produces_identical_audit_hash` |
| GAP-01 distinct inputs distinct hashes | A vs B | `test_distinct_inputs_produce_distinct_hashes` |
| GAP-01 LLM client raises | RuntimeError | `test_llm_client_exception_falls_back_gracefully` |
| GAP-01 anchor no-alert within tolerance | deviation < 0.5 | `test_anchor_no_alert_when_deviation_within_tolerance` |
| GAP-05 safe code passes | assert statement | `test_safe_code_passes` |
| GAP-05 exec flagged | exec() call | `test_exec_call_flagged` |
| GAP-05 os.system flagged | os.system() call | `test_os_system_flagged` |
| GAP-05 eval flagged | eval() call | `test_eval_flagged` |
| GAP-05 SyntaxError returns violation | invalid code | `test_syntax_error_returns_violation` |
| GAP-05 iteration cap bounded ≤5 | MAX_CORRECTION_ITERATIONS | `test_iteration_cap_constant_is_bounded` |
| GAP-05 compile flagged | compile() | `test_compile_flagged` |
| GAP-05 __import__ flagged | __import__() | `test_dunder_import_flagged` |
| GAP-05 empty string no violations | code="" | `test_empty_string_returns_no_violations` |
| GAP-05 whitespace no violations | code="  \n" | `test_whitespace_only_code_returns_no_violations` |
| GAP-05 pass statement safe | code="pass" | `test_single_pass_statement_is_safe` |
| GAP-05 replayed check deterministic | same code × 2 | `test_repeated_call_same_input_same_output` |
| GAP-05 nested exec in lambda | lambda: exec() | `test_nested_exec_inside_lambda_is_flagged` |
| GAP-05 assert not flagged | assert True | `test_assert_statement_not_flagged` |
| GAP-05 MAX_CORRECTION_ITERATIONS==3 | exact value | `test_max_correction_iterations_is_exactly_3` |

---

## ROBUSTNESS_MATRIX

| Changed Surface | Success Tests | Edge Tests | Failure Tests | Recovery Tests | Determinism Tests | Side-Effect Tests |
|---|---|---|---|---|---|---|
| `ReflectionEngine.evaluate` fail-closed | `test_fail_open_optional_*` | `test_empty_criteria_*`, `test_none_content_*` | `test_fail_closed_required_*` (x2) | `test_stats_total_critiques_*` | `test_circuit_open_is_deterministic_*` | stats increment verified |
| `SafetyInspectorAgent._socratic_verify` | `test_snippet_sanitization_*` | `test_max_calls_zero_*`, `test_call_at_limit_*`, `test_nonexistent_file_*` | `test_rate_limited_*`, `test_audit_log_populated_*` | verdict=YES on any failure | audit log entry count matches calls | `_socratic_call_count` does not increment on rate-limit |
| `JudgeEvaluator.evaluate` | `test_none_expected_*`, `test_threshold_exactly_met_*` | `test_empty_string_*`, `test_whitespace_*`, `test_empty_criteria_*`, `test_threshold_above_max_*` | `test_llm_client_exception_*` | fallback to heuristic on LLM error | `test_identical_input_*`, `test_distinct_inputs_*` | audit entry written on every call path |
| `RegressionOracleAgent._ast_safety_check` | `test_safe_code_*`, `test_assert_*` | `test_empty_string_*`, `test_whitespace_*`, `test_single_pass_*`, `test_nested_exec_*` | `test_exec_*`, `test_eval_*`, `test_os_system_*`, `test_compile_*`, `test_dunder_import_*`, `test_syntax_error_*` | N/A (pure static analysis) | `test_repeated_call_same_*` | no side effects (pure function) |
| `MAX_CORRECTION_ITERATIONS` constant | `test_iteration_cap_*` | exact boundary ≤5 | N/A | N/A | `test_max_correction_iterations_is_exactly_3` | N/A |
| AST scanner (`scan_llm_validator_calls.py`) | `test_no_new_llm_validator_calls` (PASS) | `test_allowlist_entries_reference_real_files` | scanner finds 0 new gaps | N/A | deterministic AST walk | no mutation |

---

## DEFECT_MODEL

| Defect Class | Gap | Test(s) That Must Fail If Defect Reintroduced |
|---|---|---|
| Fail-open on circuit breaker with required criteria | GAP-02 | `test_fail_closed_required_criterion_on_circuit_open` |
| Fail-open on unexpected exception with required criteria | GAP-02 | `test_fail_closed_required_on_unexpected_exception` |
| Optional criteria incorrectly fail-closed | GAP-02 | `test_fail_open_optional_criterion_on_circuit_open` |
| Required criterion dominated by optional on mixed list | GAP-02 | `test_mixed_criteria_required_dominates_on_circuit_open` |
| Stats not incremented on fallback path | GAP-02 | `test_stats_total_critiques_increments_on_circuit_open` |
| Rate limit not enforced (counter not checked) | GAP-04 | `test_max_calls_zero_always_rate_limits`, `test_call_at_limit_is_rate_limited` |
| Counter incremented on rate-limited call | GAP-04 | `test_rate_limited_call_does_not_increment_counter` |
| Audit entry not written on rate-limit | GAP-04 | `test_audit_log_entry_schema`, `test_audit_log_length_matches_total_calls` |
| Timeout not returning YES (fail-closed) | GAP-04 | `test_audit_log_populated_on_timeout` |
| Credential value leaked into LLM prompt | GAP-04 | `test_snippet_sanitization_excludes_credential_lines` |
| Audit log not written per evaluate() call | GAP-01 | `test_audit_log_entry_on_heuristic_evaluate` |
| model_id not tracked | GAP-01 | `test_model_id_defaults_to_heuristic_when_no_llm`, `test_model_id_stored_when_provided` |
| Heuristic anchor not computed | GAP-01 | `test_heuristic_anchor_with_matching_expected`, `test_heuristic_anchor_empty_output` |
| anchor_alert not set on large LLM deviation | GAP-01 | `test_anchor_alert_set_on_large_deviation` |
| Non-deterministic output_hash | GAP-01 | `test_identical_input_produces_identical_audit_hash` |
| LLM exception propagates out of evaluate() | GAP-01 | `test_llm_client_exception_falls_back_gracefully` |
| ZeroDivisionError on empty criteria | GAP-01 | `test_empty_criteria_list_raises_or_returns_safely` |
| exec/eval/os.system not rejected in generated code | GAP-05 | `test_exec_call_flagged`, `test_eval_flagged`, `test_os_system_flagged` |
| compile/__import__ not rejected | GAP-05 | `test_compile_flagged`, `test_dunder_import_flagged` |
| SyntaxError in generated code not surfaced | GAP-05 | `test_syntax_error_returns_violation` |
| Iteration cap removed or set >5 | GAP-05 | `test_iteration_cap_constant_is_bounded`, `test_max_correction_iterations_is_exactly_3` |
| AST check non-deterministic | GAP-05 | `test_repeated_call_same_input_same_output` |
| New un-allowlisted LLM validator call added | All | `test_no_new_llm_validator_calls` (guardian) |
| ML import added outside approved seam | All | `test_ml_import_count_does_not_grow` (guardian) |

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

