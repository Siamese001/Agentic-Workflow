# execute-ssot Observability Hardening Plan
# Concern: 6 root-cause gaps in execute_ssot --heal diagnostics
# Target: 3 high-signal outputs with prove-it evidence for all concerns

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

Files modified (declare before any edit):
- `agentic_core/L0_routing/scripts/execute_ssot.py`
  - Add `_collect_llm_call_trace()` data collection helper
  - Add `_collect_blocker_scan()` data collection helper
  - Add `_write_heal_run_complete()` replacing `_write_mandatory_json_output()`
  - Add `_write_failure_forensics()` new file writer
  - Add `_print_executive_summary()` new terminal output
  - Update call site at line 6568-6580

New test file:
- `tests/unit/agentic_core/L0_routing/scripts/test_execute_ssot_observability.py`

Evidence file:
- `docs/reports/plans/execute-ssot-observability-hardening-evidence.md`

## Root-Cause Concerns Addressed

| # | Concern | Prove-It Mechanism |
|---|---------|-------------------|
| 1 | Not running all agents | AST discovery hash + execution log hash + coverage ratio |
| 2 | Heal blocked by flags/debt | Flag check timestamp + stack trace hash + blocker taxonomy |
| 3 | Agents not running as intended | Subphase proof hash per phase + gate decision hash |
| 4 | LLM API calls not happening | Request hash + response hash + HTTP status + request_id |
| 5 | Low signal confidence scores | Calibration error per tier + prediction/outcome hashes |
| 6 | Meta-learning not improving | Previous run hash + success_rate_delta + t-test significance |

## Output Artifacts (3 total)

### Output 1: heal_run_complete.json
Path: `logs/compliance_reports/heal_run_complete.json`
Replaces: `heal_run_output.json`
Sections:
- meta (run_id, git_commit, timestamp)
- coverage (expected/executed/skipped agents with proof hashes)
- routing (LLM call trace, calibration, blocked calls)
- learning (run comparison, pattern reuse, strategy evolution)
- healing_actions (existing + subphase proof hashes)
- blockers (taxonomy + stack traces)
- executive_summary (10 gate criteria pass/fail)

### Output 2: diagnostic_heatmap.txt (console)
Replaces: _print_healing_heatmap + _print_meta_learning_summary
Sections:
- COVERAGE ANALYSIS with proof hashes
- ROUTING EFFECTIVENESS with LLM call proof
- HEALING HEATMAP table
- META-LEARNING EFFECTIVENESS with run comparison
- CRITICAL ISSUES list

### Output 3: failure_forensics.json
Path: `logs/compliance_reports/failure_forensics.json`
New file - detailed drill-down for failures
Sections:
- failed_agents (subphase breakdown + gate decision proof)
- blocked_agents (flag check + stack trace + last successful run)
- misrouted_agents (confidence calculation + routing proof + calibration)

### Executive Summary Table (console, mandatory last output)
Called after all three file writes
10 gate criteria rows, PASS/FAIL binary, VERDICT line

## Wave Breakdown

### Wave 1: Prove-It Data Collection Layer
Scope: execute_ssot.py only
- Add `_collect_llm_call_trace(state_mgr, decision_engine)` — extracts LLM proof from healing_actions
- Add `_collect_blocker_scan(state_mgr)` — extracts blocked agent records with timestamps
- Add `_build_coverage_proof(state_mgr, expected_agents)` — coverage ratio + hashes
- Add `_build_calibration_proof(state_mgr, decision_engine)` — per-tier calibration error
- No output changes yet; only data plumbing
Tests: unit tests for each collector with null/empty/malformed inputs

### Wave 2: heal_run_complete.json
Scope: execute_ssot.py only
- Implement `_write_heal_run_complete()` using Wave 1 collectors
- Keeps backward-compat `heal_run_output.json` stub for one wave (symlink not needed, just write both)
- Remove `_write_mandatory_json_output()` after Wave 2 tests pass
Tests: schema contract tests, proof field presence, hash determinism

### Wave 3: failure_forensics.json
Scope: execute_ssot.py only
- Implement `_write_failure_forensics()` using Wave 1 collectors
- Writes only when there are failures/blocks/misroutes
Tests: empty case (no failures), partial case, full case with all three categories

### Wave 4: Executive Summary Table
Scope: execute_ssot.py only
- Implement `_print_executive_summary()` with 10 gate criteria
- Call at line 6581 after _write_heal_run_complete
- Replaces separate _print_healing_heatmap + _print_meta_learning_summary calls at 6568-6569
  (those functions remain but are absorbed into diagnostic_heatmap section of executive summary)
Tests: gate threshold boundary tests, PASS/FAIL logic, empty-state defense

### Wave 5: Full Suite + Evidence
- Run `python -m pytest -q --color=no`
- Collect collected/executed counts
- Write evidence file with BRANCH_INVENTORY, ROBUSTNESS_MATRIX, DEFECT_MODEL

## Acceptance Criteria (per wave)

Each wave: `python -m pytest -q --color=no` exits 0
Wave 5 final: collected == executed count, evidence file complete

## BRANCH_INVENTORY (declared upfront)

| File | Function | Branch | Expected Outcome | Test |
|------|----------|--------|-----------------|------|
| execute_ssot.py | _collect_llm_call_trace | healing_actions empty | returns [] | test_llm_trace_empty_actions |
| execute_ssot.py | _collect_llm_call_trace | action missing routing_tier | defaults DETERMINISTIC | test_llm_trace_missing_tier |
| execute_ssot.py | _collect_llm_call_trace | http_status != 200 | blocked_call entry | test_llm_trace_blocked_call |
| execute_ssot.py | _collect_blocker_scan | no blocked agents | returns [] | test_blocker_scan_empty |
| execute_ssot.py | _collect_blocker_scan | feature_flag blocker | blocker_type=feature_flag | test_blocker_scan_flag |
| execute_ssot.py | _build_coverage_proof | all agents executed | coverage_ratio=1.0 | test_coverage_full |
| execute_ssot.py | _build_coverage_proof | skipped agents present | ratio < 1.0 | test_coverage_partial |
| execute_ssot.py | _build_calibration_proof | no decisions | returns empty dict | test_calibration_no_decisions |
| execute_ssot.py | _build_calibration_proof | tier with 0 actual | calibration_error computed | test_calibration_zero_actual |
| execute_ssot.py | _write_heal_run_complete | write succeeds | file at expected path | test_heal_run_complete_written |
| execute_ssot.py | _write_heal_run_complete | write fails (OSError) | logs error, no crash | test_heal_run_complete_write_fail |
| execute_ssot.py | _write_failure_forensics | no failures | file not written | test_forensics_no_failures |
| execute_ssot.py | _write_failure_forensics | failed agents present | file written with entries | test_forensics_with_failures |
| execute_ssot.py | _print_executive_summary | all gates pass | VERDICT: PASS | test_summary_all_pass |
| execute_ssot.py | _print_executive_summary | any gate fails | VERDICT: FAIL | test_summary_any_fail |
| execute_ssot.py | _print_executive_summary | coverage < 0.90 threshold | gate FAIL | test_summary_coverage_fail |
| execute_ssot.py | _print_executive_summary | coverage >= 0.90 | gate PASS | test_summary_coverage_pass |
| execute_ssot.py | _print_executive_summary | llm_rate < 0.80 | gate FAIL | test_summary_llm_rate_fail |
| execute_ssot.py | _print_executive_summary | calibration_error > 0.15 | gate FAIL | test_summary_calib_fail |

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

