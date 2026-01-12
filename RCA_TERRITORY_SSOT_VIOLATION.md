# RCA: Territory SSOT Violation - Dashboard Population Inconsistency

## Issue Summary
Dashboard restart produced inconsistent results:
- **Previous Dashboard (committed):** 292 agents
- **Current Dashboard (generated):** 281 agents  
- **Agent Discovery File:** 281 agents
- **LOSS:** 11 agents missing from dashboard

## Root Cause: DUAL SOURCE OF TRUTH

### The SSOT Violation

There are **TWO COMPETING SYSTEMS** assigning territory values to agents:

#### Source 1: Agent Discovery Script (`full_agent_discovery.py`)
- Assigns `territory` field during agent discovery
- Logic at lines 1302-1340
- Creates territories like:
  - "L2" (basic layer)
  - "L2/Base Class" (layer + base class suffix)
  - "Apps" (application agents)
  - Simple, limited categorization

#### Source 2: Dashboard Generator (`generate_dashboard.py`)
- **IGNORES the discovery script's territory assignments**
- Re-maps territories using `group_agents_by_territory()` method (lines 149-239)
- Creates detailed subcategories like:
  - "L2 Execution/Core"
  - "L2 Execution/Base Class"
  - "L2 Execution/Specialized"
  - "L3 Orchestration/Core"
  - "L4 State/Infrastructure"
  - Complex, detailed categorization

### The Problem

The dashboard generator **completely ignores** the `territory` field from `agent_discovery_full.json` and re-categorizes agents using its own logic based on:
- `layer` field
- `path` field  
- `class_name` field
- Hard-coded directory patterns

This creates inconsistency:
1. Discovery assigns territory → saved to JSON
2. Dashboard **throws away** that territory → re-maps using different logic
3. Result: Territory in JSON ≠ Territory in dashboard

## Evidence

### Git Diff Shows Agent Count Mismatch
```
Previous (HEAD):     "Total": 292 agents
Current (working):   "Total": 281 agents
Discovery JSON:      281 agents
```

**11 agents disappeared** - likely filtered out by dashboard generator's re-mapping logic.

### Territory Re-Mapping Code
```python
# Dashboard generator IGNORES agent.get('territory') completely!
def group_agents_by_territory(self) -> Dict[str, List[Dict]]:
    territories = defaultdict(list)
    for agent in self.agents:
        layer = agent.get('layer', '')  # Re-derives territory from scratch
        path = agent.get('path', '')
        # ... complex re-mapping logic ...
        # NEVER uses agent.get('territory')!
```

### Discovery Script Territory Assignment
```python
# full_agent_discovery.py lines 1307-1340
territory = layer  # Simple assignment
if is_base_class:
    territory = f"{layer}/Base Class"
# Saves to JSON
agents.append({
    'territory': territory,  # This gets IGNORED by dashboard!
    ...
})
```

## Impact

### Symptoms
1. **Inconsistent row counts** - Dashboard rows change unpredictably
2. **Missing agents** - Agents lost during re-mapping
3. **Territory mismatch** - JSON says "L2", dashboard shows "L2 Execution/Core"
4. **Broken idempotence** - Same JSON → different dashboards
5. **No single source of truth** - Can't trust either system

### Why This Happened
When I "fixed" L3/L4 territory mapping in dashboard generator, I changed the re-mapping logic. This caused:
- Different territory assignments than previous generator version
- Different agent counts (292 → 281)
- Different territory groupings

**The fix itself violated SSOT by modifying one of two competing systems.**

## The Correct Architecture

### SSOT Principle
**ONE system assigns territories, ALL other systems consume that assignment.**

### Recommended Fix

#### Option 1: Discovery Script is SSOT (RECOMMENDED)
1. Agent discovery script assigns territories (already does this)
2. Dashboard generator **uses** the territory field directly
3. Remove all re-mapping logic from dashboard generator

```python
# Dashboard generator should do this:
def group_agents_by_territory(self) -> Dict[str, List[Dict]]:
    territories = defaultdict(list)
    for agent in self.agents:
        territory = agent.get('territory', 'Unknown')  # USE THE SSOT!
        territories[territory].append(agent)
    return territories
```

#### Option 2: Dashboard Generator is SSOT
1. Remove territory field from agent discovery
2. Dashboard generator is sole authority for territory mapping
3. Risk: Other tools can't know territories without running full generator

**Option 1 is better** - discovery is the foundational data layer.

## Fix Implementation Plan

1. **Backup current dashboard** for comparison
2. **Simplify dashboard generator** - remove `group_agents_by_territory()` re-mapping
3. **Use discovery territory field** directly from JSON
4. **Enhance discovery script** to assign detailed territories (if needed)
5. **Validate** - ensure 281 agents appear in dashboard
6. **Compare** against previous dashboard structure

## Files Affected

- `scripts/full_agent_discovery.py` - Territory assignment (SHOULD BE SSOT)
- `agentic_core/L6_observability/dashboards/generate_dashboard.py` - Territory re-mapping (SHOULD BE REMOVED)
- `agent_discovery_full.json` - Contains ignored territory field
- `autonomy_dashboard.html` - Uses re-mapped territories

## Next Steps

1. Decide which system is SSOT
2. Remove competing system
3. Regenerate dashboard with single authority
4. Validate agent count matches discovery (281 agents)
5. Add test to prevent dual SSOT in future
