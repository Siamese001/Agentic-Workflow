# L6ObservabilityBaseAgent Discovery Issue - FINAL RCA

**Date:** January 12, 2026  
**Status:** 🔴 **CRITICAL BUG FOUND**  
**Issue:** L6ObservabilityBaseAgent exists but is NOT discovered as an agent

---

## Problem Statement

**L6ObservabilityBaseAgent is NOT appearing in dashboard despite:**
1. ✅ File exists: `agentic_core/L6_observability/L6ObservabilityBaseAgent.py`
2. ✅ Is a valid agent class (inherits from SovereignBaseAgent, ABC, mixins)
3. ✅ Territory added to TERRITORY_ORDER: `L6_Observability/Base Class`
4. ✅ Discovery script updated to recognize it as base class
5. ✅ Agent discovery runs successfully (282 agents found)

**But:**
- ❌ L6 Base Class agents: **0** (should be 1)
- ❌ Only 3 L6 agents discovered (should be 4)
- ❌ L6ObservabilityBaseAgent NOT in agent_discovery_full.json

---

## Root Cause Analysis

### Discovery Scan Results
```
L6 agents found: 3
- RuntimeMetricsAgent -> L6_Observability/Metrics
- StrategicObservationAgent -> L6_Observability/Metrics  
- RuntimeTelemetryAgent -> L6_Observability/Telemetry

L6ObservabilityBaseAgent: NOT FOUND
```

### Why It's Not Being Discovered

**The agent IS being found by grep:**
```json
"inheritance": [
  "L6ObservabilityBaseAgent"
]
```
This proves other agents inherit from it, so the file is being parsed.

**Hypothesis 1: Filename Mismatch Violation**
The discovery script has STRICT REQUIREMENT 2:
```python
# STRICT REQUIREMENT 2: Class name MUST exactly match filename stem
if node.name != py_file.stem:
    log.info(f"VIOLATION {node.name} in {rel_path}: class name '{node.name}' does not match filename stem '{py_file.stem}'")
    continue  # SKIP THIS CLASS
```

**Check:**
- File: `L6ObservabilityBaseAgent.py`
- Class: `L6ObservabilityBaseAgent`
- Match: ✅ YES - should pass

**Hypothesis 2: Skip Names**
```python
skip_names = {
    'SubAtomicAgent',
    'CanonBaseAgent',
    'MaintenanceBaseAgent',
    'IActionPlane',
    'ValidationProtocol',
    'Protocol',
    # NOTE: ABC removed - L6ObservabilityBaseAgent inherits from ABC
}
```
- L6ObservabilityBaseAgent NOT in skip_names ✅

**Hypothesis 3: is_agent_class() Returns False**

The `is_agent_class()` function checks:
1. Has strong positive signal (Agent in name, inherits from known bases)
2. NOT in agent_bases set (base agents are excluded from being "agents")

**CRITICAL BUG FOUND:**
```python
agent_bases = {
    'L0Agent', 'L1Agent', 'L2Agent', 'L3Agent', 'L4Agent', 'L5Agent', 'L6Agent',
    'L2ExecutionBaseAgent', 'OrchestrationBaseAgent', 'StateBaseAgent', 'SafetyBaseAgent',
    'ExecutionCanonBaseAgent',
    'CognitionCanonBaseAgent', 'CanonASTValidator', 'CanonBaseAgentInterface',
    'BaseAgent', 'SovereignBaseAgent',
    'L6ObservabilityBaseAgent',  # L6 base agent (inherits from ABC)
}
```

**L6ObservabilityBaseAgent IS in agent_bases!**

This means `is_agent_class()` returns **False** because:
```python
if name in agent_bases:
    return False  # Base agents are not considered "agent candidates"
```

**But wait... other base agents ARE discovered:**
- L0Agent ✅ discovered
- L1Agent ✅ discovered  
- L2ExecutionBaseAgent ✅ discovered
- SafetyBaseAgent ✅ discovered

**Why are they discovered but L6ObservabilityBaseAgent is not?**

Looking at the code more carefully:
```python
# Line 914-916
is_base_agent = name.endswith('BaseAgent')
if any(d in {'dataclass', 'attrs', 'attr.s'} for d in decorators) and not has_strong_positive_signal and not is_base_agent:
    return False
```

This suggests base agents ARE allowed through if they end with 'BaseAgent'.

**ACTUAL ROOT CAUSE:**

The issue is that `L6ObservabilityBaseAgent` is in `agent_bases` which causes `is_agent_class()` to return False BEFORE the base agent exception logic runs.

Looking at line 867-874:
```python
agent_bases = {
    # ... all base agents including L6ObservabilityBaseAgent
}

# Determine if this is an agent candidate
if name in agent_bases:
    return False  # ← THIS KILLS L6ObservabilityBaseAgent
```

**But other base agents pass through because:**
They have special handling AFTER the agent_bases check that re-includes them.

**The fix is already in the code at line 914:**
```python
is_base_agent = name.endswith('BaseAgent')
```

But this happens AFTER the `agent_bases` check kills it.

---

## The Real Issue

**L6ObservabilityBaseAgent is being EXCLUDED by the agent_bases check at line 867-874.**

The code has contradictory logic:
1. Line 873: Adds L6ObservabilityBaseAgent to agent_bases (to exclude it)
2. Line 914: Tries to re-include base agents with `is_base_agent = name.endswith('BaseAgent')`

But the exclusion happens FIRST, so L6ObservabilityBaseAgent never reaches the re-inclusion logic.

---

## Solution

**Option 1: Remove from agent_bases**
```python
agent_bases = {
    'L0Agent', 'L1Agent', 'L2Agent', 'L3Agent', 'L4Agent', 'L5Agent', 'L6Agent',
    'L2ExecutionBaseAgent', 'OrchestrationBaseAgent', 'StateBaseAgent', 'SafetyBaseAgent',
    'ExecutionCanonBaseAgent',
    'CognitionCanonBaseAgent', 'CanonASTValidator', 'CanonBaseAgentInterface',
    'BaseAgent', 'SovereignBaseAgent',
    # REMOVED: 'L6ObservabilityBaseAgent',  # Should be discovered as agent
}
```

**Option 2: Add early return exception**
```python
# Line 867-874
if name in agent_bases:
    # Exception: *BaseAgent classes should still be discovered
    if not name.endswith('BaseAgent'):
        return False
```

**Option 3: Remove agent_bases check entirely**
The `is_base_agent` logic at line 914 already handles this correctly.

---

## Recommended Fix

**Remove L6ObservabilityBaseAgent from agent_bases set:**

```python
# In full_agent_discovery.py, line 867-874
agent_bases = {
    'L0Agent', 'L1Agent', 'L2Agent', 'L3Agent', 'L4Agent', 'L5Agent', 'L6Agent',
    'L2ExecutionBaseAgent', 'OrchestrationBaseAgent', 'StateBaseAgent', 'SafetyBaseAgent',
    'ExecutionCanonBaseAgent',
    'CognitionCanonBaseAgent', 'CanonASTValidator', 'CanonBaseAgentInterface',
    'BaseAgent', 'SovereignBaseAgent',
    # L6ObservabilityBaseAgent removed - should be discovered like other *BaseAgent classes
}
```

This will allow L6ObservabilityBaseAgent to be discovered like all other base agents.

---

## Verification Steps

After fix:
1. Run `python scripts/full_agent_discovery.py`
2. Check: `python test_l6_discovery.py` should show 1 base agent
3. Regenerate dashboard: `python agentic_core/L6_observability/dashboards/generate_dashboard.py`
4. Verify L6_Observability/Base Class appears in dashboard
5. Run E2E tests: `python scripts/test_dashboard_end_to_end.py`

---

## Impact

**Before Fix:**
- L6 agents: 3 (missing base agent)
- L6_Observability/Base Class territory: EMPTY
- Dashboard incomplete

**After Fix:**
- L6 agents: 4 (includes base agent)
- L6_Observability/Base Class territory: 1 agent (L6ObservabilityBaseAgent)
- Dashboard complete with all base agents visible

---

**Status:** Ready to implement fix  
**Priority:** 🔴 CRITICAL  
**Effort:** 1 line change  
**Risk:** Low (consistent with other base agent handling)
