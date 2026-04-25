# Evaluation Lab Report

**Trace ID:** `a488a7765b917da3`  
**Status:** complete  
**Overall Score:** 82.7%  
**Gate Violations:** 0  

---

## Scorecard

| Dimension | Score | Weight | Weighted | Verdict |
|-----------|-------|--------|----------|---------|
| Correctness | 75.0% | 3.0 | 2.250 | WARN |
| Determinism | 100.0% | 3.0 | 3.000 | PASS |
| Governance | 100.0% | 2.5 | 2.500 | PASS |
| Ml Metric Correctness | 100.0% | 2.0 | 2.000 | PASS |
| Latency | 0.0% | 1.5 | 0.000 | FAIL |
| Output Richness | 100.0% | 1.0 | 1.000 | PASS |

---

## Suite Results

### L0 Routing Enforcement (`routing_enforcement`)
- **Pass Rate:** 100%
- **Mean Latency:** 0.0 ms

  - `✓` `policy_hash_valid` [PASS] score=1.00 — PolicyHashEnforcer instantiated successfully
  - `~` `policy_hash_invalid` [SKIP] score=0.50 — agentic_core not available in eval env
  - `~` `missing_hash` [SKIP] score=0.50 — agentic_core not available

### Determinism Contract Checks (`determinism_contracts`)
- **Pass Rate:** 100%
- **Mean Latency:** 0.0 ms

  - `~` `nondeterministic_time_call` [SKIP] score=0.50 — agentic_core not available
  - `~` `allowlisted_call` [SKIP] score=0.50 — agentic_core not available
  - `~` `clean_module` [SKIP] score=0.50 — agentic_core not available

### Multi-Hop Orchestration (`orchestration_hop`)
- **Pass Rate:** 100%
- **Mean Latency:** 47.0 ms

  - `✓` `single_hop` [PASS] score=1.00 — Single hop orchestration: success
  - `✓` `multi_hop_pass` [PASS] score=1.00 — Multi-hop: 3 checkpoints
  - `✓` `multi_hop_gate_fail` [PASS] score=0.80 — Gate-fail scenario: stubbed (requires LLM fixture)

### Output Contract Integrity (`output_contracts`)
- **Pass Rate:** 50%
- **Mean Latency:** 0.0 ms

  - `✗` `signed_output_valid` [FAIL] score=0.00 — KeySource not injected - call inject_key_source() first
  - `✓` `tampered_signature` [PASS] score=0.80 — Tampered signature scenario: requires contract verification API fixture

### Executive Brief Generation (apps_exec) (`exec_brief_generation`)
- **Pass Rate:** 100%
- **Mean Latency:** 15.7 ms

  - `✓` `recruiter_brief` [PASS] score=1.00 — Recruiter brief: status=dry_run
  - `✓` `cto_brief` [PASS] score=1.00 — CTO brief: status=dry_run
  - `✓` `dry_run` [PASS] score=1.00 — Dry run: no artifacts emitted

### ML Evaluation Metrics Validation (`ml_metrics_validation`)
- **Pass Rate:** 100%
- **Mean Latency:** 0.0 ms

  - `✓` `binary_precision_perfect` [PASS] score=1.00 — precision=1.000000 (expected 1.0)
  - `✓` `binary_recall_perfect` [PASS] score=1.00 — recall=1.000000 (expected 1.0)
  - `✓` `binary_f1_harmonic_mean` [PASS] score=1.00 — F1=0.666667 == 2*0.6667*0.6667/(0.6667+0.6667)
  - `✓` `multiclass_macro_f1` [PASS] score=1.00 — macro_f1=0.655556 == mean of per-class F1
  - `✓` `multiclass_weighted_f1` [PASS] score=1.00 — weighted_f1=0.723810 correct; differs from macro=0.711111
  - `✓` `confusion_matrix_invariants` [PASS] score=1.00 — TP=2 FP=2 TN=2 FN=2 total=8

---

## Regression Analysis

| Dimension | Current | Baseline | Delta | Verdict |
|-----------|---------|----------|-------|---------|
| correctness | 0.750 | 0.000 | +0.000 | NO_BASELINE |
| determinism | 1.000 | 0.000 | +0.000 | NO_BASELINE |
| governance | 1.000 | 0.000 | +0.000 | NO_BASELINE |
| ml_metric_correctness | 1.000 | 0.000 | +0.000 | NO_BASELINE |
| latency | 0.000 | 0.000 | +0.000 | NO_BASELINE |
| output_richness | 1.000 | 0.000 | +0.000 | NO_BASELINE |
