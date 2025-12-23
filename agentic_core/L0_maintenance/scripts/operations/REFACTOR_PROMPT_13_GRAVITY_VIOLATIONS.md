# Refactor Prompt: Fix 13 Gravity Violations

## Objective

Fix the 13 remaining gravity violations in `agentic_core` using proper architectural patterns. **Do not return empty changes.** All fixes must implement the prescribed patterns correctly.

---

## Critical Requirements

### ✅ DO:
- Use `TYPE_CHECKING` blocks for all cross-layer imports
- Implement lazy loading with `__getattr__` in package `__init__.py`
- Use string forward references in type hints
- Verify all methods exist before adding to `cleaning_crew`
- Maintain all existing functionality

### ❌ DO NOT:
- Return empty files or no-op changes
- Delete imports without replacement
- Remove functionality to "fix" circularity
- Skip the `TYPE_CHECKING` pattern
- Leave circular dependencies unresolved

---

## Fix 1: `agentic_core/__init__.py` - Implement Lazy Loading

**Problem**: Direct imports at package root cause circular dependency during initialization.

**Current Pattern** (WRONG):
```python
# agentic_core/__init__.py
from agentic_core.L1_cognition.canon_base_agent import SubAtomicAgent
from agentic_core.L4_state.validation_context import ValidationContext
# ... more direct imports
```

**Required Pattern** (CORRECT):
```python
# agentic_core/__init__.py
"""
Agentic Core Package
Lazy loading prevents circular imports during package initialization.
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Type hints only - not imported at runtime
    from agentic_core.L1_cognition.canon_base_agent import SubAtomicAgent
    from agentic_core.L4_state.validation_context import ValidationContext
    # ... other type-only imports

# Lazy loading using __getattr__
def __getattr__(name: str):
    """
    Lazy load modules and classes on first access.
    Prevents circular imports during package initialization.
    """
    if name == "SubAtomicAgent":
        from agentic_core.L1_cognition.canon_base_agent import SubAtomicAgent
        return SubAtomicAgent
    
    if name == "ValidationContext":
        from agentic_core.L4_state.validation_context import ValidationContext
        return ValidationContext
    
    if name == "ValidationProtocol":
        from agentic_core.L1_cognition.validation_protocol import ValidationProtocol
        return ValidationProtocol
    
    # Add other classes as needed
    # Pattern: Check name, import locally, return
    
    raise AttributeError(f"module 'agentic_core' has no attribute '{name}'")

# Optional: Define __all__ for explicit exports
__all__ = [
    "SubAtomicAgent",
    "ValidationContext",
    "ValidationProtocol",
    # ... other exports
]
```

**Why This Works**:
- No imports execute during `import agentic_core`
- Classes loaded only when accessed: `from agentic_core import SubAtomicAgent`
- Breaks circular dependency chain at package root
- Maintains full type safety with `TYPE_CHECKING`

---

## Fix 2: `inference_engine.py` - TYPE_CHECKING for SignalContext

**Problem**: `SignalContext` import creates circular dependency with signal processing modules.

**Current Pattern** (WRONG):
```python
# agentic_core/L1_cognition/inference/inference_engine.py
from agentic_core.L4_state.signal_context import SignalContext

@dataclass
class InferenceRequest:
    context: SignalContext
    query: str
```

**Required Pattern** (CORRECT):
```python
# agentic_core/L1_cognition/inference/inference_engine.py
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentic_core.L4_state.signal_context import SignalContext

@dataclass
class InferenceRequest:
    context: 'SignalContext'  # String forward reference
    query: str
```

**Why This Works**:
- `SignalContext` not imported at runtime
- Type checkers (mypy/pyright) still validate types
- String forward reference maintains type hints
- No circular dependency at runtime

**Additional Pattern** (if runtime access needed):
```python
def process_request(self, request: 'InferenceRequest') -> str:
    # Lazy import only when method is called
    from agentic_core.L4_state.signal_context import SignalContext
    
    # Now can use SignalContext at runtime
    if isinstance(request.context, SignalContext):
        # process...
```

---

## Fix 3: `canon_validator_agentic_v2.py` - Method Validation in Discovery

**Problem**: Agents without `execute` or `run` methods are added to `cleaning_crew`, causing runtime errors.

**Current Pattern** (WRONG):
```python
# canon_validator_agentic_v2.py - discover_agents()
for mod_name, cls_name, cls_ref in discovered:
    try:
        agent_instance = cls_ref(**kwargs)
        cleaning_crew.append(agent_instance)  # Added without checking
        print(f"     [+] Active: {cls_name}")
    except Exception as e:
        print(f"     [!] Failed to instantiate {cls_name}: {e}")
```

**Required Pattern** (CORRECT):
```python
# canon_validator_agentic_v2.py - discover_agents()
for mod_name, cls_name, cls_ref in discovered:
    try:
        agent_instance = cls_ref(**kwargs)
        
        # CRITICAL: Verify agent has callable method before adding
        has_execute = hasattr(agent_instance, 'execute') and callable(getattr(agent_instance, 'execute', None))
        has_run = hasattr(agent_instance, 'run') and callable(getattr(agent_instance, 'run', None))
        
        if has_execute or has_run:
            cleaning_crew.append(agent_instance)
            print(f"     [+] Active: {cls_name}")
        else:
            print(f"     [!] Skipped {cls_name}: No callable execute/run method")
            
    except Exception as e:
        print(f"     [!] Failed to instantiate {cls_name}: {e}")
```

**Why This Works**:
- Only agents with callable methods added to crew
- Prevents "no method" runtime errors
- Protocols and Contexts properly excluded
- Clear logging of skipped components

---

## Additional Fixes for Remaining 10 Violations

### Pattern A: Cross-Layer Imports in L3 Orchestration

**Files**: `nervous_system.py`, `mission_runner.py`, `canon_scheduler.py`

**Fix**:
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentic_core.L1_cognition.sovereign_cognitive_plane import create_sovereign_cognitive_plane
    from agentic_core.L2_execution.sovereign_action_plane import create_sovereign_action_plane
    from agentic_core.L4_state.checkpointing import VerifiableCheckpointManager
    from agentic_core.L5_safety.safety_layer import create_l5_safety_layer

# Use string forward references in type hints
def __init__(self, cognitive_plane: 'ICognitivePlane', ...):
    # Lazy import in methods where actually used
    from agentic_core.L1_cognition.sovereign_cognitive_plane import create_sovereign_cognitive_plane
    self.brain = cognitive_plane or create_sovereign_cognitive_plane()
```

### Pattern B: Runtime Files Cross-Layer Imports

**Files**: `subatomic_hop.py`, `subatomic_hop_l5.py`, `subatomic_hop_l5_integrated.py`

**Fix**:
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentic_core.L2_execution.mcp_manager import MCPConnectionManager
    from agentic_core.L5_safety.governor import CostGovernor
    # ... all other cross-layer imports

# Use string forward references
def __init__(self, role: str, config: Dict) -> None:
    # Lazy import in __init__ where needed
    from agentic_core.L2_execution.mcp_manager import MCPConnectionManager
    from agentic_core.L5_safety.governor import CostGovernor
    
    self.mcp = MCPConnectionManager(config['mcp_mappings'])
    self.governor = CostGovernor(limit_usd=config.get('max_cost', 5.0))
```

### Pattern C: Same-Layer Circular Imports

**Files**: `safety_layer.py`, `checkpointing.py`

**Fix**:
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentic_core.L5_safety.governor import create_cost_governor
    from agentic_core.L5_safety.overseer import create_overseer

# Lazy import in factory functions
def create_l5_safety_layer(cost_limit_usd: float = 5.0):
    from agentic_core.L5_safety.governor import create_cost_governor
    from agentic_core.L5_safety.overseer import create_overseer
    
    return L5SafetyLayer(
        governor=create_cost_governor(cost_limit_usd),
        overseer=create_overseer()
    )
```

---

## Verification Checklist

After applying all fixes, verify:

### ✅ Import Test
```python
# Should work without circular import errors
import agentic_core
from agentic_core import SubAtomicAgent, ValidationContext
```

### ✅ Gravity Scanner
```bash
python scripts/operations/fix_gravity_violations.py
# Expected: 0 violations
```

### ✅ Discovery Probe
```bash
python scripts/operations/canon_key_discovery_probe.py
# Expected: All modules canonical
```

### ✅ Canon Validator
```bash
python canon_validator_agentic_v2.py --target agentic_core
# Expected: 
# - 12+ agents discovered
# - No "no method" warnings
# - 50/50 key convergence
```

---

## Summary of 13 Fixes

1. **`agentic_core/__init__.py`** - Lazy loading with `__getattr__`
2. **`inference_engine.py`** - TYPE_CHECKING for SignalContext
3. **`canon_validator_agentic_v2.py`** - Method validation before adding to crew
4. **`nervous_system.py`** - TYPE_CHECKING for L1-L5 imports
5. **`mission_runner.py`** - TYPE_CHECKING for cross-layer imports
6. **`canon_scheduler.py`** - TYPE_CHECKING for intervention_server
7. **`subatomic_hop.py`** - TYPE_CHECKING for all layer imports
8. **`subatomic_hop_l5.py`** - TYPE_CHECKING for L2/L4/L5 imports
9. **`subatomic_hop_l5_integrated.py`** - TYPE_CHECKING for safety imports
10. **`safety_layer.py`** - TYPE_CHECKING for same-layer imports
11. **`checkpointing.py`** - TYPE_CHECKING for storage imports
12. **`canon_base_agent.py`** - Already fixed (ValidationProtocol pattern)
13. **Discovery modules** - TYPE_CHECKING for internal imports

---

## Expected Outcome

```
======================================================================
GRAVITY VIOLATIONS RESOLVED: 13/13
======================================================================

✅ agentic_core/__init__.py - Lazy loading implemented
✅ inference_engine.py - TYPE_CHECKING applied
✅ canon_validator_agentic_v2.py - Method validation added
✅ All cross-layer imports - TYPE_CHECKING blocks
✅ All type hints - String forward references
✅ Zero circular dependencies - Verified
✅ 50-key system - Operational

ARCHITECTURAL STATUS:
  ✓ Package initialization: SAFE
  ✓ Type safety: MAINTAINED
  ✓ Runtime imports: LAZY
  ✓ Discovery: VALIDATED
  ✓ Circular dependencies: ELIMINATED

======================================================================
```

---

**Date**: December 22, 2025  
**Priority**: CRITICAL  
**Approach**: Surgical refactoring with proven patterns  
**Validation**: Multi-stage verification required
