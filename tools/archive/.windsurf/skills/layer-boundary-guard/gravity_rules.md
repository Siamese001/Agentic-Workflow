# Layer Gravity Rules

Canonical layer hierarchy and import permission table.
SSOT: `agentic_core/L4_state/utils/layer_gravity.py` (LAYER_ORDER, GRAVITY_RULES)

## Layer Hierarchy

| Layer | Numeric Rank | Purpose |
|-------|-------------|---------|
| L0 | 0 | Routing, entrypoints, path constants |
| L1 | 1 | Cognition, inference primitives |
| L2 | 2 | Execution, write gateway, audit |
| L3 | 3 | Orchestration, arbitration |
| L4 | 4 | State, blueprint, global bus |
| L5 | 5 | Safety enforcement plane |
| L6 | 6 | External integrations, adapters |

## Gravity Rules Table

| Source Layer | May Import From | FORBIDDEN |
|---|---|---|
| L0 | L0 only | L1, L2, L3, L4, L5, L6 |
| L1 | L0, L1 | L2, L3, L4, L5, L6 |
| L2 | L0, L1, L2 | L3, L4, L5, L6 |
| L3 | L0, L1, L2, L3 | L4, L5, L6 |
| L4 | L0, L1, L2, L3, L4 | L5, L6 |
| L5 | L0, L1, L2, L3, L4, L5 | L6 |
| L6 | L0–L6 (all) | — |
| apps_rg | agentic_core (any), apps_shared | apps_lic |
| apps_lic | agentic_core (any), apps_shared | apps_rg |
| apps_shared | agentic_core (any) | apps_rg, apps_lic |

## Violation Identification

Given a proposed import `from agentic_core.LM_* import X` inside `agentic_core.LN_*`:

```
1. Extract N from source path   → source_rank = N
2. Extract M from import path   → target_rank = M
3. IF target_rank > source_rank → GRAVITY VIOLATION — BLOCK
4. IF target_rank <= source_rank → ALLOWED — proceed
```

## Common Violation Examples

```python
# VIOLATION: L0 importing from L5
# File: agentic_core/L0_routing/engines/router.py
from agentic_core.L5_safety.enforcement.test_rigor_enforcer import TestRigorEnforcer
#                    ^^^ L5 > L0 → FORBIDDEN

# VIOLATION: L2 importing from L4
# File: agentic_core/L2_execution/audit/ledger.py
from agentic_core.L4_state.config.blueprint_config import BlueprintConfig
#                    ^^^ L4 > L2 → FORBIDDEN

# ALLOWED: L3 importing from L1
# File: agentic_core/L3_orchestration/arbitration/engine.py
from agentic_core.L1_cognition.engines.inference import InferenceEngine
#                    ^^^ L1 <= L3 → OK
```

## apps_* Additional Rules

- `apps_rg` and `apps_lic` MUST NOT import from each other (horizontal boundary)
- `apps_shared` is the only shared lateral dependency
- All `apps_*` may import from any `agentic_core` layer
