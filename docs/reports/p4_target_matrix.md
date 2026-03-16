# P4 Target Matrix

**Date**: 2026-03-15
**Denominator**: `modules_with_calls` = **3,011**

## Target Counts

| Metric | Formula | Target | Threshold |
|---|---|---:|---:|
| `snapshots_state` | modules_with_state × 1.00 | 3,011 | 100% |
| `writes_to` | modules_with_state × 1.00 | 3,011 | 100% |
| `records_execution_trace` | modules_with_state × 1.00 | 3,011 | 100% |
| `records_telemetry_event` | modules_with_state × 0.95 | 2,860 | 95% |
| `captures_evaluation_metric` | modules_with_state × 0.90 | 2,710 | 90% |
| `stores_embedding` | modules_with_state × 0.80 | 2,409 | 80% |
| `updates_meta_learning_state` | modules_with_state × 0.80 | 2,409 | 80% |
| `links_execution_to_snapshot` | modules_with_state × 1.00 | 3,011 | 100% |

## Achieved Counts

| Metric | Covered | Target | Status |
|---|---:|---:|---|
| `snapshots_state` | 3,011 | 3,011 | **PASS (100.0%)** |
| `writes_to` | 3,011 | 3,011 | **PASS (100.0%)** |
| `records_execution_trace` | 3,011 | 3,011 | **PASS (100.0%)** |
| `records_telemetry_event` | 3,011 | 2,860 | **PASS (100.0% > 95%)** |
| `captures_evaluation_metric` | 3,011 | 2,710 | **PASS (100.0% > 90%)** |
| `stores_embedding` | 3,011 | 2,409 | **PASS (100.0% > 80%)** |
| `updates_meta_learning_state` | 3,011 | 2,409 | **PASS (100.0% > 80%)** |
| `links_execution_to_snapshot` | 3,011 | 3,011 | **PASS (100.0%)** |

All thresholds exceeded.
