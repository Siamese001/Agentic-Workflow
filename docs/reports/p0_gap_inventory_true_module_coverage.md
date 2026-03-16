# P0 Gap Inventory — True Module-Level Coverage

**Date**: 2026-03-15
**ADG SQLite**: `adg_indexed_03152026_2154.sqlite`
**Denominator**: `modules_with_calls` = **3011**

## Coverage by Dimension

| Dimension | Covered | Missing | Coverage |
|---|---:|---:|---:|
| `records_execution_trace` | 3005 | 6 | 99.8% |
| `applies_guardrail` | 3004 | 7 | 99.77% |
| `reads_policy_state` | 3008 | 3 | 99.9% |
| `emits_replay_key` | 3004 | 7 | 99.77% |
| `emits_determinism_digest` | 3004 | 7 | 99.77% |
| `signs_execution_trace` | 3005 | 6 | 99.8% |
| `snapshots_state` | 3004 | 7 | 99.77% |

## Overlap Analysis

**Unique modules missing any P0 dimension**: 8

### Distribution by gap count

| Gaps | Module Count |
|---:|---:|
| 7 | 3 |
| 6 | 3 |
| 2 | 2 |

### Modules missing 4+ dimensions (highest priority)

- `tests/guardian/conftest.py` — missing 7: applies_guardrail, emits_determinism_digest, emits_replay_key, reads_policy_state, records_execution_trace, signs_execution_trace, snapshots_state
- `tests/sovereign_hardening/conftest.py` — missing 7: applies_guardrail, emits_determinism_digest, emits_replay_key, reads_policy_state, records_execution_trace, signs_execution_trace, snapshots_state
- `tests/unit_min_deps/conftest.py` — missing 7: applies_guardrail, emits_determinism_digest, emits_replay_key, reads_policy_state, records_execution_trace, signs_execution_trace, snapshots_state
- `agentic_core/L0_routing/config/ssot_tier_constants.py` — missing 6: applies_guardrail, emits_determinism_digest, emits_replay_key, records_execution_trace, signs_execution_trace, snapshots_state
- `agentic_core/L5_safety/config/structure_blueprint/_constants.py` — missing 6: applies_guardrail, emits_determinism_digest, emits_replay_key, records_execution_trace, signs_execution_trace, snapshots_state
- `agentic_core/L5_safety/config/structure_blueprint_config.py` — missing 6: applies_guardrail, emits_determinism_digest, emits_replay_key, records_execution_trace, signs_execution_trace, snapshots_state

### Modules missing 2-3 dimensions

- `agentic_core/runtime/lifecycle_trace_contract.py` — missing 2: applies_guardrail, snapshots_state
- `agentic_core/L0_routing/config/path_constants.py` — missing 2: emits_determinism_digest, emits_replay_key

### Single-gap modules by dimension
