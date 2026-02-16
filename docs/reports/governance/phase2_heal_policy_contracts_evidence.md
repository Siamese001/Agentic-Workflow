# Phase 2: Heal Escalation Policy Contracts Evidence

## Wave 2.1 — Pure Policy Types + Pure Decision Function

### Files Created
- agentic_core/L5_safety/types/heal_policy_types.py

### Import Smoke Test
```bash
python -c "from agentic_core.L5_safety.types.heal_policy_types import decide_reasoning_tier; print('ok')"
```

Output:
```
ok
```

### Module Characteristics
- Pure Python module using only stdlib (dataclasses, enum, typing)
- No imports from apps_*, routing, executors, model router, or agents
- Frozen dataclasses for immutability
- Deterministic decision logic with no randomness

---
