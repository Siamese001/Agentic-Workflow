# P0 Micro-Wave Priority Plan

**Date**: 2026-03-15
**Denominator**: `modules_with_calls` = **3,011**
**Total unique gap modules**: 8

## Wave 1 (Final — all 8 modules)

Only 8 modules have gaps — fits in a single micro-wave (< 15 limit).

### Priority Tier 1: Missing 7 dims (all P0)

| Module | Missing |
|---|---|
| `tests/guardian/conftest.py` | all 7 |
| `tests/sovereign_hardening/conftest.py` | all 7 |
| `tests/unit_min_deps/conftest.py` | all 7 |

### Priority Tier 2: Missing 6 dims

| Module | Missing |
|---|---|
| `agentic_core/L0_routing/config/ssot_tier_constants.py` | applies_guardrail, emits_determinism_digest, emits_replay_key, records_execution_trace, signs_execution_trace, snapshots_state |
| `agentic_core/L5_safety/config/structure_blueprint/_constants.py` | applies_guardrail, emits_determinism_digest, emits_replay_key, records_execution_trace, signs_execution_trace, snapshots_state |
| `agentic_core/L5_safety/config/structure_blueprint_config.py` | applies_guardrail, emits_determinism_digest, emits_replay_key, records_execution_trace, signs_execution_trace, snapshots_state |

### Priority Tier 3: Missing 2 dims

| Module | Missing |
|---|---|
| `agentic_core/runtime/lifecycle_trace_contract.py` | applies_guardrail, snapshots_state |
| `agentic_core/L0_routing/config/path_constants.py` | emits_determinism_digest, emits_replay_key |

## Blast Efficiency

- Wiring all 8 modules closes all 43 dimension-gaps across 7 P0 dimensions
- 3 modules × 7 gaps = 21 gaps closed (Tier 1)
- 3 modules × 6 gaps = 18 gaps closed (Tier 2)
- 2 modules × 2 gaps = 4 gaps closed (Tier 3)
