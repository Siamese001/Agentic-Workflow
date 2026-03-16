# P4 Runtime Baseline

**Date**: 2026-03-15
**ADG Before Wiring**: `adg_indexed_03152026_2236.sqlite`

## Baseline Counts (Pre-Wiring)

| Relation Type | Edges | Modules | Coverage | Status |
|---|---:|---:|---:|---|
| `calls` (denominator) | 89,862 | 3,011 | — | — |
| `snapshots_state` | 3,020 | 3,011 | 100.00% | Already at 100% (P0) |
| `writes_to` | 12,273 | 3,011 | 100.00% | Already at 100% |
| `records_execution_trace` | 6,568 | 3,011 | 100.00% | Already at 100% (P0) |
| `records_telemetry_event` | 0 | 0 | 0.00% | MISSING |
| `captures_evaluation_metric` | 0 | 0 | 0.00% | MISSING |
| `stores_embedding` | 14 | 9 | 0.30% | Exists (low coverage) |
| `updates_meta_learning_state` | 0 | 0 | 0.00% | MISSING |
| `links_execution_to_snapshot` | 0 | 0 | 0.00% | MISSING |

## Key Findings

- **3 dims already at 100%** from prior hardening — no work needed
- **1 dim exists at 0.30%** (`stores_embedding`) — needs full wiring
- **4 dims missing entirely** — need new infrastructure (schema frozensets, emitters, scanner visitor)
