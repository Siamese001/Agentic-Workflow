# Layer Gravity Rules

## Rule Table

```
L0 → can import: L0 only
L1 → can import: L0, L1
L2 → can import: L0, L1, L2
L3 → can import: L0, L1, L2, L3
L4 → can import: L0, L1, L2, L3, L4
L5 → can import: L0, L1, L2, L3, L4, L5
L6 → can import: L0, L1, L2, L3, L4, L5, L6
apps_* → can import: agentic_core (any layer), apps_shared
```

**VIOLATION:** Any import where source layer N imports from layer M where M > N.

## Detection

- Layer determined from directory name: `agentic_core/L<N>_*/`
- Cross-layer validation via ADG edge type `IMPORTS`
- CI gate: `ops_scripts/ci/validate_import_dependencies.py`

## Common Violations

```python
# FORBIDDEN: L3 importing from L5
from agentic_core.L5_safety.config import some_config

# CORRECT: keep at same or lower layer
from agentic_core.L3_orchestration.config import some_config
```

## apps_* Rules

- `apps_*` packages may import from any `agentic_core` layer
- `apps_*` packages may import from `apps_shared`
- `apps_*` packages MUST NOT import from other `apps_*` packages
