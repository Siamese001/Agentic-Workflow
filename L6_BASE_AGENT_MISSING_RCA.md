# L6 Base Agent Missing from Dashboard - Root Cause Analysis

**Date:** January 12, 2025  
**Issue:** L6ObservabilityBaseAgent not appearing in dashboard despite existing in codebase  
**Status:** ⚠️ INVESTIGATION IN PROGRESS

---

## Problem Statement

User reported that L6 base agent is not shown in the dashboard, despite:
- L0-L5 base agents all appearing correctly (1 per layer)
- L6ObservabilityBaseAgent.py file exists in `agentic_core/L6_observability/`
- Class definition exists and is properly structured

---

## Investigation Steps

### 1. Verified File Exists ✅
**Location:** `C:/Git/Agentic-Workflow/agentic_core/L6_observability/L6ObservabilityBaseAgent.py`

**Class Definition:**
```python
@dataclass
class L6ObservabilityBaseAgent(SovereignBaseAgent, MCPHardenedMixin, SubatomicTestingMixin, RedisCacheMixin, PineconeVectorMixin, ABC):
    """Base class for L6 Observability agents - The Skeptical Analysts."""
```

### 2. Checked Discovery JSON ❌
**Result:** L6ObservabilityBaseAgent NOT found in `agent_discovery_full.json`

**Command:**
```bash
grep "L6ObservabilityBaseAgent" agent_discovery_full.json
# No results
```

### 3. Identified Root Cause #1: ABC in skip_names ✅ FIXED
**Issue:** Discovery script was skipping classes named "ABC"

**Fix Applied:**
```python
# OLD:
skip_names = {
    'SubAtomicAgent', 'CanonBaseAgent', 'MaintenanceBaseAgent',
    'IActionPlane', 'ValidationProtocol', 'Protocol', 'ABC'
}

# NEW:
skip_names = {
    'SubAtomicAgent', 'CanonBaseAgent', 'MaintenanceBaseAgent',
    'IActionPlane', 'ValidationProtocol', 'Protocol',
    # NOTE: ABC removed - L6ObservabilityBaseAgent inherits from ABC
}
```

### 4. Added L6 Base Class Territory Logic ✅ FIXED
**Issue:** Discovery had no territory assignment for L6 base classes

**Fix Applied:**
```python
# L6 Observability detailed territories
elif layer == 'L6':
    if is_base_class:
        territory = "L6_Observability/Base Class"  # ADDED
    elif 'metrics' in path_str or 'Metric' in node.name:
        territory = "L6_Observability/Metrics"
    # ... other territories
```

### 5. Re-ran Discovery ✅
**Command:** `python scripts/full_agent_discovery.py`

**Result:** Still 281 agents (no change)

**L6 agents found:** 2 (PerformanceAnalystAgent, RuntimeTelemetryAgent)

**L6ObservabilityBaseAgent:** ❌ STILL NOT DISCOVERED

---

## Current Hypothesis

**L6ObservabilityBaseAgent is being filtered out by discovery logic despite fixes.**

Possible causes:
1. **Filename/Class mismatch** - Discovery requires exact match (CHECKED: Match is correct)
2. **ABC inheritance issue** - Even though ABC removed from skip_names, inheritance chain may cause issues
3. **Agent detection logic** - May not recognize it as an agent due to:
   - Abstract base class (ABC)
   - No concrete methods
   - Dataclass decorator interaction
4. **File encoding issue** - Unicode error when trying to parse file
5. **Hidden filter** - Another filter in discovery logic blocking base agents

---

## Evidence

### File Structure
```
agentic_core/L6_observability/
├── L6ObservabilityBaseAgent.py  ← Contains L6ObservabilityBaseAgent class
├── agents/
│   ├── PerformanceAnalystAgent.py  ← Discovered ✅
│   └── RuntimeTelemetryAgent.py    ← Discovered ✅
```

### Class Inheritance Chain
```
L6ObservabilityBaseAgent
├── SovereignBaseAgent
├── MCPHardenedMixin
├── SubatomicTestingMixin
├── RedisCacheMixin
├── PineconeVectorMixin
└── ABC  ← Abstract Base Class
```

### Discovery Logs
- No mention of L6ObservabilityBaseAgent in discovery output
- No VIOLATION messages for this class
- Silently filtered out

---

## Next Steps

1. **Add debug logging** to discovery script to trace why L6ObservabilityBaseAgent is filtered
2. **Check if ABC inheritance** causes `has_strong_positive_signal` to fail
3. **Verify agent_bases set** includes L6ObservabilityBaseAgent
4. **Test with simpler L6 base agent** without ABC to isolate issue
5. **Check if @dataclass decorator** with ABC causes issues

---

## Workaround Options

### Option 1: Create L6Agent.py (Simple Base)
Create a simpler L6 base agent without ABC:
```python
@dataclass
class L6Agent(HealerMixin, MCPHardenedMixin):
    """Simple L6 base agent without ABC."""
    name: str = "L6Agent"
    layer: str = "L6"
```

### Option 2: Rename L6ObservabilityBaseAgent
Rename to match L0-L5 pattern:
- L0MaintenanceBaseAgent, L1CognitionBaseAgent → L6Agent
- Keep L6ObservabilityBaseAgent as alias

### Option 3: Force Include in Discovery
Add L6ObservabilityBaseAgent to agent_bases set:
```python
agent_bases = {
    'SubAtomicAgent', 'CanonBaseAgent', 'MaintenanceBaseAgent',
    'L3OrchestrationBaseAgent', 'L4StateBaseAgent', 'L5SafetyBaseAgent',
    'L6ObservabilityBaseAgent',  # FORCE INCLUDE
    'SovereignBaseAgent',
}
```

---

## Impact

**Current State:**
- Dashboard shows 6 base agents (L0-L5) ✅
- L6 layer has no base agent shown ❌
- Test 8 passes (1 base agent per layer for L0-L5)
- L6 not tested in Test 8

**User Expectation:**
- Dashboard should show 7 base agents (L0-L6)
- L6_Observability/Base Class territory should exist
- Consistent with L0-L5 pattern

---

## Status

**Issue:** ⚠️ PARTIALLY RESOLVED
- ABC filter removed ✅
- L6 territory logic added ✅
- Discovery still not finding L6ObservabilityBaseAgent ❌

**Root Cause:** UNKNOWN - Requires deeper investigation into discovery filtering logic

**Recommendation:** Implement Option 3 (Force Include) as immediate fix while investigating root cause

---

**Report prepared by:** Cascade AI  
**Status:** IN PROGRESS  
**Next Action:** Add L6ObservabilityBaseAgent to agent_bases set and regenerate
