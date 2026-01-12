# RCA: Base Class Discovery Issues

## Issue 1: Base Class Rows Show >1 Agent

### Symptom
Test 8 in E2E suite reports multiple base agents per layer:
```
Test 8 FAILED: L1 has 2 base agents: ['L1Agent', 'L1CognitionBaseAgent']
Test 8 FAILED: L2 has 3 base agents: ['L2Agent', 'L2ExecutionBaseAgent', 'SovereignBaseAgent']
Test 8 FAILED: L3 has 2 base agents: ['L3Agent', 'OrchestrationBaseAgent']
Test 8 FAILED: L4 has 2 base agents: ['L4Agent', 'StateBaseAgent']
Test 8 FAILED: L5 has 2 base agents: ['L5Agent', 'SafetyBaseAgent']
```

### Root Cause
**Discovery script is correctly finding multiple base classes per layer, but Test 8 expects exactly 1.**

The issue is NOT with discovery - it's with the **test expectation**. Multiple base classes exist:
- **L1:** `L1Agent` (canonical) + `L1CognitionBaseAgent` (layer-specific)
- **L2:** `L2Agent` (canonical) + `L2ExecutionBaseAgent` (layer-specific) + `SovereignBaseAgent` (cross-layer)
- **L3:** `L3Agent` (canonical) + `OrchestrationBaseAgent` (layer-specific)
- **L4:** `L4Agent` (canonical) + `StateBaseAgent` (layer-specific)
- **L5:** `L5Agent` (canonical) + `SafetyBaseAgent` (layer-specific)

### Analysis
1. **Canonical base agents:** `L0Agent`, `L1Agent`, `L2Agent`, etc. (simple naming)
2. **Layer-specific base agents:** `L1CognitionBaseAgent`, `L2ExecutionBaseAgent`, etc. (descriptive naming)
3. **Cross-layer base:** `SovereignBaseAgent` (used across multiple layers)

**This is NOT a bug** - it's architectural reality. Multiple base classes serve different purposes:
- Canonical bases: Simple inheritance
- Layer-specific bases: Domain-specific functionality
- Sovereign base: Cross-cutting concerns

### Territory Assignment Issue
**Problem:** Base class agents are NOT being assigned to "Base Class" territories.

**Evidence:**
```bash
python -c "import json; data=json.load(open('agent_discovery_full.json')); 
base_class_rows=[a for a in data if 'Base Class' in a.get('territory','')]; 
print(f'Base Class territory agents: {len(base_class_rows)}')"
# Output: Base Class territory agents: 0
```

**Expected:** Base agents should be in territories like:
- `L1 Cognition/Base Class`
- `L2 Execution/Base Class`
- `L3 Orchestration/Base Class`
- etc.

**Actual:** Base agents are being grouped with regular agents in their layer territories.

---

## Issue 2: L6ObservabilityBaseAgent Not Discovered

### Symptom
L6 base class `L6ObservabilityBaseAgent` is not appearing in `agent_discovery_full.json`.

### Root Cause
**The `@dataclass` decorator is causing exclusion.**

**Evidence from discovery script (line 936-938):**
```python
# Conditional negative: dataclass/attrs only disqualifies absent strong positive
if any(d in {'dataclass', 'attrs', 'attr.s'} for d in decorators) and not has_strong_positive_signal:
    return False
```

**L6ObservabilityBaseAgent definition (line 72):**
```python
@dataclass
class L6ObservabilityBaseAgent(SovereignBaseAgent, MCPHardenedMixin, ...):
```

**Why it's excluded:**
1. Class has `@dataclass` decorator
2. Class name ends with "Agent" but is a **base class**
3. May not have "strong positive signal" (healing methods, etc.)
4. Discovery script excludes dataclasses without strong positive signals

**This is a BUG** - base classes should be discovered regardless of dataclass decorator.

---

## Root Cause Summary

### Issue 1: Multiple Base Agents Per Layer
- **NOT A BUG:** Multiple base classes legitimately exist per layer
- **REAL ISSUE:** Territory assignment logic doesn't create "Base Class" sub-territories
- **IMPACT:** Test 8 fails because it expects exactly 1 base agent per layer

### Issue 2: L6 Base Class Missing
- **BUG:** `@dataclass` decorator causes exclusion of L6ObservabilityBaseAgent
- **REAL ISSUE:** Discovery script's dataclass exclusion logic is too aggressive
- **IMPACT:** L6 base class not discovered, no "L6 Observability/Base Class" territory

---

## Fixes Required

### Fix 1: Update Test 8 Logic
**Current:** Expects exactly 1 base agent per layer
**Fixed:** Allow multiple base agents, verify they're all in "Base Class" territories

### Fix 2: Fix Territory Assignment for Base Classes
**Current:** Base classes assigned to regular layer territories
**Fixed:** Detect base classes and assign to "{Layer}/Base Class" territories

### Fix 3: Fix Dataclass Exclusion Logic
**Current:** Excludes dataclasses without strong positive signals
**Fixed:** Never exclude classes ending with "BaseAgent" regardless of decorators

### Fix 4: Add Guardrails
1. **Test:** Verify all base agents are in "Base Class" territories
2. **Test:** Verify L6ObservabilityBaseAgent is discovered
3. **Validation:** Ensure dataclass base agents are never excluded
4. **Documentation:** Clarify multiple base agents per layer is expected

---

## Implementation Plan

1. ✅ **RCA Complete:** Identified both root causes
2. **Fix discovery script:** Update dataclass exclusion logic
3. **Fix territory assignment:** Create "Base Class" sub-territories
4. **Update Test 8:** Accept multiple base agents per layer
5. **Add guardrails:** Prevent regression
6. **Test fixes:** Run full E2E suite
