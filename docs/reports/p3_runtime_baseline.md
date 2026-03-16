# P3 Runtime Baseline

**Date**: 2026-03-15
**ADG Before Wiring**: `adg_indexed_03152026_2218.sqlite`

## Baseline Counts (Pre-Wiring)

| Relation Type | Edges | Modules | Coverage | Status |
|---|---:|---:|---:|---|
| `calls` (denominator) | 65,761 | 3,011 | — | — |
| `orchestrates_workflow` | 74 | 48 | 1.59% | Exists (P1 visitor) |
| `dispatches_agent` | 0 | 0 | 0.00% | MISSING |
| `coordinates_agents` | 0 | 0 | 0.00% | MISSING |
| `records_workflow_lineage` | 0 | 0 | 0.00% | MISSING |
| `invokes_eval` | 543 | 129 | 4.28% | Exists (dynamic eval detector) |
| `dispatches_healing_run` | 1,229 | 1,169 | 38.82% | Exists (P0 emitter) |
| `records_healing_outcome` | 0 | 0 | 0.00% | MISSING |
| `escalates_failure` | 0 | 0 | 0.00% | MISSING |
| `records_execution_trace` | 6,568 | 3,011 | 100.00% | Already at 100% (P0) |

## Key Findings

- **4 dims already exist** in ADG with varying coverage
- **5 dims missing entirely** — need new infrastructure (schema frozensets, emitters, scanner visitor)
- `records_execution_trace` already at 100% from P0 hardening — no work needed
- `invokes_eval` is a code-safety edge (detects `eval()`/`exec()` calls), NOT an orchestration evaluation signal
  - Replaced with new `invokes_evaluation` P3 dim for orchestration evaluation coverage
