# Consolidated Layer Base Classes

## Overview

Each layer has **ONE** base class that provides **ALL** standard capabilities:

| Base | Layer | Capabilities |
|------|-------|--------------|
| `L0Agent` | Maintenance | HealerMixin + MCPHardenedMixin + L0DelegationTestingMixin |
| `L1Agent` | Cognition | HealerMixin + MCPHardenedMixin + self-tests |
| `L2Agent` | Execution | HealerMixin + MCPHardenedMixin + SubatomicTestingMixin |
| `L3Agent` | Orchestration | HealerMixin + MCPHardenedMixin + L3SubatomicTestingMixin |
| `L4Agent` | State | HealerMixin + MCPHardenedMixin + L4SubatomicTestingMixin |
| `L5Agent` | Safety | HealerMixin + MCPHardenedMixin + self-tests |

## Usage

```python
from agentic_core.bases import L3Agent

class MyOrchestratorAgent(L3Agent):
    name: str = "MyOrchestratorAgent"
    
    def heal_repository(self, dry_run: bool = True) -> dict:
        # Your healing logic
        return {"healed": 0}
    
    async def orchestrate(self, task: dict) -> dict:
        # Your orchestration logic
        return {"status": "success"}
```

## Guaranteed Capabilities

When you inherit from a layer base, you automatically get:

### 1. Self-Healing (`heal_repository`)
```python
def heal_repository(self, dry_run: bool = True) -> dict:
    # Provided by HealerMixin
```

### 2. Hardened MCP Operations (`_hardened_call`)
```python
async def _hardened_call(self, operation: str, call_func: Callable, *args, **kwargs) -> Any:
    # Exponential backoff retry
    # Timeout enforcement
    # CRITIQUE emission on failure
```

### 3. Subatomic Testing (`_run_self_tests`)
```python
def _run_self_tests(self) -> dict:
    # Layer-specific testing
    # Delegation to TestSovereigntyAgent on failure
```

## Migration Guide

### Before (Inconsistent)
```python
class MyAgent(CanonBaseAgent, MCPHardenedMixin, HealerMixin, SubatomicTestingMixin):
    pass  # Which capabilities does this have? Unclear.
```

### After (Consolidated)
```python
class MyAgent(L2Agent):
    pass  # Guaranteed: healing, MCP, testing
```

## Why This Design?

1. **Zero Ambiguity**: Every L3 agent has MCP, healing, testing
2. **Simple Imports**: `from agentic_core.bases import L3Agent`
3. **Easy Auditing**: Check inheritance = know capabilities
4. **Reduced Errors**: Can't forget to add MCPHardenedMixin

## Layer-Specific Notes

### L0 (Maintenance)
- Runs at boot time
- Delegates testing to higher layers (stability)
- Uses `L0DelegationTestingMixin`

### L5 (Safety)
- IS the validator layer
- Does NOT delegate to TestSovereigntyAgent (it IS the validator)
- Self-validates internally
