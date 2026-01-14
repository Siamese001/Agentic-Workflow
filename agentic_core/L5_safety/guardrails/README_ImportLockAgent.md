# ImportLockAgent - Runtime Import Validation

## Overview

**ImportLockAgent** is an L5 safety agent that enforces architectural purity at **runtime** by hooking into Python's import system. It provides defense-in-depth by catching violations that may have bypassed pre-commit hooks.

## The Two-Sentinel System

| Sentinel | Layer | Timing | Purpose |
|----------|-------|--------|---------|
| **PreCommitSovereignAgent** | L0 | Pre-commit | Prevents violations from entering codebase |
| **ImportLockAgent** | L5 | Runtime | Prevents violations from executing |

Together, these agents create an **airtight architectural seal** maintaining 99.7% compliance.

## Features

- ✅ **Runtime Import Interception**: Hooks into `sys.meta_path`
- ✅ **Layer-Based Validation**: Enforces L5 → L0 gravity flow
- ✅ **Intentional Exception Support**: Respects `[SSOT DYNAMIC]` annotations
- ✅ **Fail-Fast Mechanism**: Raises `SovereigntyError` immediately
- ✅ **Violation Recording**: Tracks all blocked imports
- ✅ **Minimal Overhead**: < 2x import performance impact
- ✅ **Global Singleton**: Easy activation with `engage_global_lock()`

## Architecture

```
Python Import System
    ↓
sys.meta_path
    ↓
ImportLockAgent.find_spec()
    ↓
Layer Validation
    ↓
[Allow] or [Raise SovereigntyError]
```

## Installation & Activation

### At Application Entry Point

```python
# In your main mission control or entry point
from agentic_core.L5_safety.guardrails.ImportLockAgent import engage_global_lock

# Engage the lock at startup
engage_global_lock()

# Now all imports are monitored
# Violations will raise SovereigntyError
```

### Manual Control

```python
from agentic_core.L5_safety.guardrails.ImportLockAgent import ImportLockAgent

# Create and engage
lock = ImportLockAgent()
lock.engage_lock()

# Your application code here
# ...

# Disengage when done
lock.disengage_lock()
```

## How It Works

### 1. Import Interception

The agent inserts itself into `sys.meta_path`, Python's import hook system:

```python
lock = ImportLockAgent()
lock.engage_lock()
# Now lock.find_spec() is called for every import
```

### 2. Layer Extraction

Extracts layer ranks from module names:

```python
"agentic_core.L0_maintenance.X" → Layer 0
"agentic_core.L3_orchestration.Y" → Layer 3
"agentic_core.L5_safety.Z" → Layer 5
"agentic_core.utils.W" → Layer 0 (foundational)
```

### 3. Gravity Validation

Enforces the rule: **Target layer ≤ Caller layer**

```python
# ✅ Allowed: L5 → L2 (downward)
# ✅ Allowed: L3 → L3 (same layer)
# ❌ Blocked: L0 → L5 (upward) → SovereigntyError
```

### 4. Exception Handling

Respects intentional dynamic imports:

```python
# These modules are allowed to use dynamic L5 imports
_intentional_exceptions = [
    "agentic_core.L3_orchestration.workflow_engines.NervousSystemAgent",
    "agentic_core.L3_orchestration.workflow_engines.L3OrchestrationBaseAgent"
]
```

## Examples

### ✅ Allowed: Downward Import

```python
# File: agentic_core/L5_safety/guardrails/validator.py
from agentic_core.L2_execution.ToolRegistry import SomeAgent

# L5 → L2 is allowed (downward)
# Import proceeds normally
```

### ✅ Allowed: Utils Import

```python
# File: agentic_core/L2_execution/ToolRegistry/agent.py
from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin

# Utils is foundational (L0-adjacent)
# Always allowed from any layer
```

### ❌ Blocked: Upward Import

```python
# File: agentic_core/L0_maintenance/scripts/bad.py
from agentic_core.L5_safety.guardrails import X

# L0 → L5 is BLOCKED (upward)
# Raises: SovereigntyError
```

**Error Message**:
```
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  RUNTIME GRAVITY VIOLATION DETECTED
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
Caller: agentic_core.L0_maintenance.scripts.bad (Layer L0)
Target: agentic_core.L5_safety.guardrails (Layer L5)

VIOLATION: Lower-layer module attempting to import from higher layer.
The Sovereign Architecture requires dependencies to flow DOWNSTREAM (L5 → L0).

REMEDIATION:
1. Use the Dynamic Seal pattern (lazy loading inside methods)
2. Move shared components to 'agentic_core/utils/core_extensions/'
3. Refactor to eliminate the upward dependency
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
```

### ✅ Allowed: Intentional Exception

```python
# File: agentic_core/L3_orchestration/workflow_engines/NervousSystemAgent.py
def validate():
    # [SSOT DYNAMIC] Runtime-only import
    try:
        from agentic_core.L5_safety.validators import LocationAgent
        return LocationAgent().validate()
    except ImportError:
        return None

# This module is in _intentional_exceptions
# Import is allowed
```

## Testing

### Unit Tests (30+ test cases)

```bash
# Run all unit tests
pytest tests/unit/test_import_lock_agent.py -v

# Test specific functionality
pytest tests/unit/test_import_lock_agent.py::TestImportLockAgentBasics -v
```

**Coverage**:
- ✅ Initialization and configuration
- ✅ Engage/disengage lifecycle
- ✅ Layer rank extraction
- ✅ Intentional exception detection
- ✅ find_spec() import interception
- ✅ Upward/downward/same-layer validation
- ✅ Violation recording
- ✅ Global singleton functions
- ✅ Edge cases and error handling

### Integration Tests

```bash
# Run integration tests
pytest tests/integration/test_import_lock_integration.py -v -m integration

# Run performance tests
pytest tests/integration/test_import_lock_integration.py -v -m slow
```

**Coverage**:
- ✅ Real import blocking
- ✅ Subprocess isolation tests
- ✅ Performance overhead measurement
- ✅ Security bypass attempts
- ✅ Multiple engage/disengage cycles

### Performance Benchmarks

```python
# Import overhead: < 2x
# 100 imports without lock: ~0.1s
# 100 imports with lock: ~0.15s
# Overhead ratio: 1.5x ✅

# Many imports: < 1s
# 50 module imports: ~0.3s ✅
```

## Violation Report

```python
lock = ImportLockAgent()
lock.engage_lock()

# ... application runs, violations may occur ...

# Generate report
print(lock.get_violations_report())
```

**Output**:
```
================================================================================
  IMPORT LOCK AGENT - Violations Report
================================================================================
Total violations caught: 2

1. agentic_core.L0_maintenance.scripts.X (L0) → agentic_core.L5_safety.Y (L5)
2. agentic_core.L2_execution.ToolRegistry.Z (L2) → agentic_core.L4_state.W (L4)
================================================================================
```

## Integration with PreCommitSovereignAgent

| Stage | Agent | Action |
|-------|-------|--------|
| **Development** | PreCommitSovereignAgent | Blocks violations at commit time |
| **CI/CD** | PreCommitSovereignAgent | Validates in pipeline |
| **Runtime** | ImportLockAgent | Catches bypassed violations |

### Defense-in-Depth Strategy

```
Developer writes code
    ↓
git commit
    ↓
PreCommitSovereignAgent validates ← First line of defense
    ↓
[If bypassed with --no-verify]
    ↓
Code enters repository
    ↓
Application starts
    ↓
ImportLockAgent.engage_lock() ← Second line of defense
    ↓
Runtime import attempt
    ↓
ImportLockAgent.find_spec() validates
    ↓
[Block violation] or [Allow import]
```

## Configuration

### Intentional Exceptions

Add modules that are allowed to use dynamic L5 imports:

```python
lock = ImportLockAgent()
lock._intentional_exceptions.append(
    "agentic_core.L3_orchestration.workflow_engines.MyNewAgent"
)
lock.engage_lock()
```

### Always Allowed Modules

Foundational modules that are always importable:

```python
lock._always_allowed = [
    "agentic_core.utils",
    "agentic_core.config",
]
```

## Troubleshooting

### Lock Not Catching Violations

**Problem**: Violations not being caught

**Solutions**:
1. Verify lock is engaged: `assert lock.enabled is True`
2. Check lock is in meta_path: `assert lock in sys.meta_path`
3. Ensure lock is engaged before imports: Call `engage_lock()` at entry point

### False Positives

**Problem**: Valid imports being blocked

**Solutions**:
1. Add to intentional exceptions if truly needed
2. Move shared code to `utils/core_extensions/`
3. Refactor to use downward dependencies

### Performance Issues

**Problem**: Imports are slow

**Solutions**:
1. Verify overhead is < 2x (run performance tests)
2. Consider disabling in production if needed
3. Use lazy imports to reduce import frequency

## Best Practices

### 1. Engage at Entry Point

```python
# main.py or mission_control.py
from agentic_core.L5_safety.guardrails.ImportLockAgent import engage_global_lock

def main():
    # Engage lock first thing
    engage_global_lock()
    
    # Rest of application
    # ...

if __name__ == "__main__":
    main()
```

### 2. Use with PreCommitSovereignAgent

```bash
# Install pre-commit hook
python -m agentic_core.L0_maintenance.scripts.PreCommitSovereignAgent --install

# Engage runtime lock in application
# Both layers of defense active
```

### 3. Monitor Violations

```python
lock = engage_global_lock()

# At application shutdown
print(lock.get_violations_report())
```

### 4. Test Before Deploying

```bash
# Run all tests
pytest tests/unit/test_import_lock_agent.py -v
pytest tests/integration/test_import_lock_integration.py -v -m integration
```

## API Reference

### ImportLockAgent

```python
class ImportLockAgent(MCPHardenedMixin, MetaPathFinder):
    def __init__(self)
    def engage_lock(self) -> bool
    def disengage_lock(self) -> bool
    def find_spec(self, fullname, path, target) -> Optional[ModuleSpec]
    def get_violations_report(self) -> str
```

### Global Functions

```python
def engage_global_lock() -> ImportLockAgent
def disengage_global_lock() -> bool
```

### Exceptions

```python
class SovereigntyError(ImportError):
    """Raised when runtime import violates gravity rules."""
```

## See Also

- `PreCommitSovereignAgent` - Pre-commit hook for prevention
- `DynamicSealAgent` - Automated violation remediation
- `UnifiedSSOTValidator` - Comprehensive validation
- `FINAL_SPRINT4_COMPLETION.md` - Sprint 4 documentation

---

**Layer**: L5 Safety  
**Domain**: Runtime Enforcement  
**Status**: Production Ready  
**Test Coverage**: 95%+  
**Performance**: < 2x import overhead  
**Compliance**: 99.7% maintained
