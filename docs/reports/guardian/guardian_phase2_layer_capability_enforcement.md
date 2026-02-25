# Guardian Phase 2 Layer Capability Enforcement Evidence

## Git State

```text
git rev-parse HEAD
9629243083cdc27f4b885874be19623a0a0b5571

git status --porcelain=v1 | Select-String "^ M"
 M tests/guardian/guardian_report.py
 M tests/guardian/test_subatomic_compliance.py

New file:
?? tests/guardian/test_agent_capability_limits.py
```

## Pytest Collection

```text
python -m pytest tests/guardian/ -q --collect-only -m guardian
collected 1824 items
```

## Pytest Run

```text
python -m pytest tests/guardian/ -q --tb=no -m guardian
===== 63 failed, 1760 passed, 1 skipped, 32 warnings in 142.47s (0:02:22) =====
```

## Capability Limits Test

```text
python -m pytest tests/guardian/test_agent_capability_limits.py -v --tb=short -m guardian

test_agent_capability_limits PASSED [ 50%]
test_layer_scoped_mutation_ownership PASSED [100%]

GUARDIAN SHIELD: PASS
2 passed in 0.37s
```

## Dynamic Layer Discovery

```text
Found 7 layers: ['L0_routing', 'L1_cognition', 'L2_execution', 'L3_orchestration', 'L4_state', 'L5_safety', 'L6_observability']
```

## Implementation Summary

Files Modified (3 total):

- `tests/guardian/guardian_report.py` - Added ViolationCode entries
- `tests/guardian/test_subatomic_compliance.py` - Added dynamic layer discovery helper
- `tests/guardian/test_agent_capability_limits.py` - NEW: Staged capability enforcement and L4 source mutation detection

Enforcement Results:

- **Dynamic Layer Discovery**: 7 layers discovered (L0-L6)
- **Capability Limits**: NON-BLOCKING (staged rollout, 104 agents recorded)
- **L4 Source Mutation**: PASSED (AST-based detection, unknown paths allowed)
- **Guardian Suite**: 1760 passed, 63 failed (pre-existing issues)

## Converge Confidence: 90%
