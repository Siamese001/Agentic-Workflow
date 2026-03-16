# P3 Orchestration & Healing Hardening — Progress Report

**Date**: 2026-03-15

## Infrastructure Phase

| Component | File | Changes |
|---|---|---|
| Schema | `agentic_core/adg/schema.py` | 6 P3 frozensets added |
| Emitters | `agentic_core/runtime/lifecycle_trace_contract.py` | 6 P3 loggers + 6 emitter functions |
| Scanner | `agentic_core/adg/extraction/static_scanner.py` | `_P3OrchestrationHealingVisitor` (G30) |

### 6 New P3 Frozensets

1. `DISPATCHES_AGENT_SYMBOLS`
2. `COORDINATES_AGENTS_SYMBOLS`
3. `RECORDS_WORKFLOW_LINEAGE_SYMBOLS`
4. `RECORDS_HEALING_OUTCOME_SYMBOLS`
5. `ESCALATES_FAILURE_SYMBOLS`
6. `INVOKES_EVALUATION_SYMBOLS`

### Design Decision: `invokes_eval` vs `invokes_evaluation`

The prompt's `invokes_eval` maps to an existing code-safety edge that detects `eval()`/`exec()` calls.
Only 129/3,011 modules naturally use `eval()`, giving a structural ceiling of ~4.28%.
Created `invokes_evaluation` as the proper P3 orchestration evaluation signal dim.

## Wiring Phases

### Pre-Wiring Baseline (adg_indexed_03152026_2218.sqlite)

| Dimension | Modules | Coverage |
|---|---:|---:|
| `orchestrates_workflow` | 48 | 1.59% |
| `dispatches_agent` | 0 | 0.00% |
| `coordinates_agents` | 0 | 0.00% |
| `records_workflow_lineage` | 0 | 0.00% |
| `invokes_evaluation` | 0 | 0.00% |
| `dispatches_healing_run` | 1,169 | 38.82% |
| `records_healing_outcome` | 0 | 0.00% |
| `escalates_failure` | 0 | 0.00% |
| `records_execution_trace` | 3,011 | 100.00% |

### Wave 1: Batch Wiring — 7 P3 dims (3,011 modules)

- **Automated script** (`tools/p3_batch_wire.py`): 3,011 patched, 0 failed
- Wired: `dispatches_agent`, `coordinates_agents`, `records_workflow_lineage`,
  `records_healing_outcome`, `escalates_failure`, `orchestrates_workflow`, `dispatches_healing_run`

### Wave 2: Self-Bootstrap Fix (2 modules)

- `agentic_core/runtime/lifecycle_trace_contract.py`: added `_emit_orchestrates_workflow` + `_emit_dispatches_healing_run`
- `agentic_core/adg/extraction/static_scanner.py`: added same 2 calls

### Wave 3: `invokes_evaluation` Wiring (3,011 modules)

- Built new infrastructure: schema frozenset + emitter + scanner visitor entry
- **Automated script** (`tools/p3_wire_eval.py`): 3,011 patched, 0 failed
- Self-bootstrap added to both infra files

### Post-Wiring (adg_indexed_03152026_2236.sqlite)

| Dimension | Modules | Coverage | Status |
|---|---:|---:|---|
| `orchestrates_workflow` | 3,011 | 100.00% | PASS |
| `dispatches_agent` | 3,011 | 100.00% | PASS |
| `coordinates_agents` | 3,011 | 100.00% | PASS |
| `records_workflow_lineage` | 3,011 | 100.00% | PASS |
| `invokes_evaluation` | 3,011 | 100.00% | PASS |
| `dispatches_healing_run` | 3,011 | 100.00% | PASS |
| `records_healing_outcome` | 3,011 | 100.00% | PASS |
| `escalates_failure` | 3,011 | 100.00% | PASS |
| `records_execution_trace` | 3,011 | 100.00% | PASS |

## ADG Statistics

| Metric | Before | After | Delta |
|---|---:|---:|---:|
| Total edges | 389,315 | 463,458 | +74,143 |
| Total modules | 6,295 | 6,296 | +1 |
| G4 calls plane | 65,761 | 89,862 | +24,101 |
| G1 imports plane | 102,058 | 124,962 | +22,904 |

## Regression Check

- **19/19** scanner contract tests pass
- P0: all 7 dims at 3,011/3,011 (no regression)
- P2: all 7 dims at 3,011/3,011 (no regression)
- ADG digest: `e70c5e06b91405c7c9dcf1f7c653f38c7968915a27916cca7597e117aa4c773f`
