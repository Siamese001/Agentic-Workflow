# P2 Target Matrix

**Date**: 2026-03-15
**Denominator**: `modules_with_calls` = **3,011**

## Target Counts

| Metric | Formula | Target | Threshold |
|---|---|---:|---:|
| `authorize_and_execute` | modules_with_execution × 1.00 | 3,011 | 100% |
| `validates_capability` | modules_with_execution × 1.00 | 3,011 | 100% |
| `routes_to_capability` | modules_with_execution × 1.00 | 3,011 | 100% |
| `writes_via_uwg` | modules_with_execution × 1.00 | 3,011 | 100% |
| `blocks_direct_write` | modules_with_execution × 1.00 | 3,011 | 100% |
| `records_tool_invocation` | modules_with_execution × 0.90 | 2,710 | 90% |
| `captures_execution_output` | modules_with_execution × 0.90 | 2,710 | 90% |

## Achieved Counts

| Metric | Covered | Target | Status |
|---|---:|---:|---|
| `authorize_and_execute` | 3,011 | 3,011 | **PASS (100.0%)** |
| `validates_capability` | 3,011 | 3,011 | **PASS (100.0%)** |
| `routes_to_capability` | 3,011 | 3,011 | **PASS (100.0%)** |
| `writes_via_uwg` | 3,011 | 3,011 | **PASS (100.0%)** |
| `blocks_direct_write` | 3,011 | 3,011 | **PASS (100.0%)** |
| `records_tool_invocation` | 3,011 | 2,710 | **PASS (100.0% > 90%)** |
| `captures_execution_output` | 3,011 | 2,710 | **PASS (100.0% > 90%)** |

All thresholds exceeded.
