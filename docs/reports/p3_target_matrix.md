# P3 Target Matrix

**Date**: 2026-03-15
**Denominator**: `modules_with_calls` = **3,011**

## Target Counts

| Metric | Formula | Target | Threshold |
|---|---|---:|---:|
| `orchestrates_workflow` | modules_with_orchestration × 1.00 | 3,011 | 100% |
| `dispatches_agent` | modules_with_orchestration × 1.00 | 3,011 | 100% |
| `coordinates_agents` | modules_with_orchestration × 1.00 | 3,011 | 100% |
| `records_workflow_lineage` | modules_with_orchestration × 1.00 | 3,011 | 100% |
| `invokes_evaluation` | modules_with_orchestration × 0.90 | 2,710 | 90% |
| `dispatches_healing_run` | modules_with_orchestration × 0.90 | 2,710 | 90% |
| `records_healing_outcome` | modules_with_orchestration × 0.90 | 2,710 | 90% |
| `escalates_failure` | modules_with_orchestration × 0.80 | 2,409 | 80% |
| `records_execution_trace` | modules_with_orchestration × 0.90 | 2,710 | 90% |

## Achieved Counts

| Metric | Covered | Target | Status |
|---|---:|---:|---|
| `orchestrates_workflow` | 3,011 | 3,011 | **PASS (100.0%)** |
| `dispatches_agent` | 3,011 | 3,011 | **PASS (100.0%)** |
| `coordinates_agents` | 3,011 | 3,011 | **PASS (100.0%)** |
| `records_workflow_lineage` | 3,011 | 3,011 | **PASS (100.0%)** |
| `invokes_evaluation` | 3,011 | 2,710 | **PASS (100.0% > 90%)** |
| `dispatches_healing_run` | 3,011 | 2,710 | **PASS (100.0% > 90%)** |
| `records_healing_outcome` | 3,011 | 2,710 | **PASS (100.0% > 90%)** |
| `escalates_failure` | 3,011 | 2,409 | **PASS (100.0% > 80%)** |
| `records_execution_trace` | 3,011 | 2,710 | **PASS (100.0% > 90%)** |

All thresholds exceeded.
