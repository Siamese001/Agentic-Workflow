# Tiered Execution Flow - Test Guide

## Overview

The tiered execution flow implements a 4-tier mission structure in `canon_validator_agentic_v2_thin.py`:

- **Tier 1**: Structural Stabilization (Mandatory)
- **Tier 2**: Architectural Alignment (Mandatory)
- **Tier 3**: Deep Domain Healing (Discovery Roster)
- **Tier 4**: Final Safety Gate (AutonomyGuardian)

## Implementation Summary

### Changes Made

**File**: `canon_validator_agentic_v2_thin.py` (Lines 542-710)

**Key Features**:
1. **Tiered Agent Assembly**: Agents organized into 4 distinct tiers
2. **Stability Gate**: Mission aborts if Tier 1 violations persist in execute mode
3. **Roster Deduplication**: Mandatory agents filtered from Tier 3 discovery roster
4. **Execution Timeline**: All 4 tiers tracked with start/end timestamps in `runtime_state.json`
5. **Consolidated Reporting**: Results aggregated across all tiers

### Tier Structure

```python
# TIER 1: Structural Stabilization (MUST pass for mission to continue)
mandatory_structural = [
    ("LocationAgent", get_location_agent(project_root)),
    ("HierarchyAgent", get_hierarchy_agent(project_root)),
    ("NamingAgent", get_naming_agent(project_root)),
]

# TIER 2: Architectural Alignment
mandatory_architectural = [
    ("ImportAgent", get_import_agent(project_root)),
    ("GovernanceAgent", get_governance_agent_stub(project_root)),
]

# TIER 3: Deep Domain Healing (Discovery Roster)
# Built dynamically from build_healing_roster() with deduplication
discovery_roster = [a for a in full_roster if a[0] not in mandatory_names]

# TIER 4: Final Safety Gate
final_safety = [("AutonomyGuardian", get_autonomy_guardian(project_root))]
```

## Test Cases

### Quick Validation (Recommended First)

**Script**: `scripts/test_tiered_execution_quick.py`

**Run**:
```bash
python scripts/test_tiered_execution_quick.py
```

**Tests**:
1. ✅ Implementation Structure (15 checks)
2. ✅ Tier Structure (agent definitions)
3. ✅ Stability Gate (abort logic)
4. ✅ Execution Timeline (tracking)
5. ✅ Roster Deduplication (filtering)

**Expected Output**: 5/5 validations passed

---

### Test Case 1: Structural Abortion Verification

**Objective**: Verify mission aborts after Tier 1 if structural violations persist.

**Setup**:
1. Manually move a core agent (e.g., `NamingAgent.py`) to an illegal directory
2. Run validator with `--heal --execute-heal`

**Expected Behavior**:
- Tier 1 detects structural violation
- Mission prints: `[!] MISSION ABORTED: Repository filesystem is unstable.`
- Tier 3 agents are **NOT** invoked
- `runtime_state.json` shows only Tier 1 in `execution_timeline`

**Validation**:
```bash
# Move agent to illegal location
mkdir ILLEGAL_AGENT_LOCATION
mv agentic_core/utils/core_extensions/NamingAgent.py ILLEGAL_AGENT_LOCATION/

# Run validator
python canon_validator_agentic_v2_thin.py --heal --execute-heal

# Check runtime_state.json
cat runtime_state.json | grep -A 20 "execution_timeline"

# Restore agent
mv ILLEGAL_AGENT_LOCATION/NamingAgent.py agentic_core/utils/core_extensions/
rmdir ILLEGAL_AGENT_LOCATION
```

**Pass Criteria**:
- ✅ Mission aborted with clear error message
- ✅ Tier 3 not executed
- ✅ `runtime_state.json` shows Tier 1 with `success: false`

---

### Test Case 2: Roster Deduplication Check

**Objective**: Verify mandatory agents only appear in Tier 1/2, not Tier 3.

**Setup**:
1. Run validator in dry-run mode: `python canon_validator_agentic_v2_thin.py --heal`
2. Inspect `runtime_state.json`

**Expected Behavior**:
- `LocationAgent`, `HierarchyAgent`, `NamingAgent` appear only in Tier 1
- `ImportAgent`, `GovernanceAgent` appear only in Tier 2
- `AutonomyGuardian` appears only in Tier 4
- Tier 3 contains discovery roster agents, excluding mandatory agents

**Validation**:
```bash
# Run validator
python canon_validator_agentic_v2_thin.py --heal

# Check execution timeline
python -c "
import json
with open('runtime_state.json') as f:
    state = json.load(f)
    for tier in state['execution_timeline']:
        print(f\"Tier {tier['tier']}: {tier['agents']}\")
"
```

**Pass Criteria**:
- ✅ No duplicate agents across tiers
- ✅ Mandatory agents filtered from Tier 3
- ✅ All 4 tiers have distinct agent lists

---

### Test Case 3: Execution Timeline Integrity

**Objective**: Verify `runtime_state.json` records all 4 tiers with timestamps.

**Setup**:
1. Run validator in dry-run mode: `python canon_validator_agentic_v2_thin.py --heal`
2. Inspect `runtime_state.json`

**Expected Behavior**:
- `execution_timeline` array contains 4 objects (one per tier)
- Each tier has: `tier`, `name`, `start`, `end`, `agents`, `fixes`, `violations`, `success`
- Timestamps are valid ISO format
- `end` timestamp is after `start` timestamp

**Validation**:
```bash
# Run validator
python canon_validator_agentic_v2_thin.py --heal

# Validate timeline structure
python -c "
import json
from datetime import datetime

with open('runtime_state.json') as f:
    state = json.load(f)
    timeline = state['execution_timeline']

    print(f'Tiers recorded: {len(timeline)}')

    for tier in timeline:
        start = datetime.fromisoformat(tier['start'])
        end = datetime.fromisoformat(tier['end'])
        duration = (end - start).total_seconds()

        print(f\"Tier {tier['tier']} ({tier['name']}): {duration:.2f}s, {len(tier['agents'])} agents\")
"
```

**Pass Criteria**:
- ✅ Exactly 4 tiers recorded
- ✅ All required fields present
- ✅ Valid ISO timestamps
- ✅ End time after start time

---

### Test Case 4: Stability Gate Passthrough

**Objective**: Verify clean repository passes all tiers without abortion.

**Setup**:
1. Ensure repository is in clean state (no structural violations)
2. Run validator in execute mode: `python canon_validator_agentic_v2_thin.py --heal --execute-heal`

**Expected Behavior**:
- Tier 1 completes with 0 violations
- Mission continues to Tier 2, 3, and 4
- No abortion message
- All 4 tiers complete successfully

**Validation**:
```bash
# Run validator
python canon_validator_agentic_v2_thin.py --heal --execute-heal

# Check for abortion
if grep -q "MISSION ABORTED" output.log; then
    echo "❌ Mission aborted unexpectedly"
else
    echo "✅ Mission completed all tiers"
fi

# Verify Tier 1 violations
python -c "
import json
with open('runtime_state.json') as f:
    state = json.load(f)
    tier1 = next(t for t in state['execution_timeline'] if t['tier'] == 1)
    print(f\"Tier 1 violations: {tier1['violations']}\")
    print(f\"Tier 1 success: {tier1['success']}\")
"
```

**Pass Criteria**:
- ✅ No abortion message
- ✅ Tier 1 violations = 0
- ✅ All 4 tiers executed
- ✅ Mission completed successfully

---

### Test Case 5: Tier 4 Reporting Accuracy

**Objective**: Verify AutonomyGuardian in Tier 4 reports violations from Tier 3.

**Setup**:
1. Run validator in dry-run mode: `python canon_validator_agentic_v2_thin.py --heal`
2. Inspect `runtime_state.json` and console output

**Expected Behavior**:
- Tier 4 contains `AutonomyGuardian`
- Tier 4 reports violations found in Tier 3
- Final compliance report includes all tier results

**Validation**:
```bash
# Run validator
python canon_validator_agentic_v2_thin.py --heal

# Check Tier 4 structure
python -c "
import json
with open('runtime_state.json') as f:
    state = json.load(f)
    tier3 = next(t for t in state['execution_timeline'] if t['tier'] == 3)
    tier4 = next(t for t in state['execution_timeline'] if t['tier'] == 4)

    print(f\"Tier 3 violations: {tier3['violations']}\")
    print(f\"Tier 4 violations: {tier4['violations']}\")
    print(f\"Tier 4 agents: {tier4['agents']}\")

    if 'AutonomyGuardian' in tier4['agents']:
        print('✅ AutonomyGuardian present in Tier 4')
    else:
        print('❌ AutonomyGuardian missing from Tier 4')
"
```

**Pass Criteria**:
- ✅ Tier 4 contains `AutonomyGuardian`
- ✅ Tier 4 reports violations
- ✅ Final report aggregates all tier results

---

## Automated Test Suite

**Full Test Suite**: `scripts/test_tiered_execution_flow.py`

**Run**:
```bash
python scripts/test_tiered_execution_flow.py
```

**Note**: This suite runs all 5 test cases automatically but may take 10-15 minutes due to full validator execution.

**Quick Validation** (recommended for CI/CD):
```bash
python scripts/test_tiered_execution_quick.py
```

## Runtime State Structure

After running the validator, `runtime_state.json` contains:

```json
{
  "status": "idle",
  "start_time": "2026-01-18T16:48:00.123456",
  "agents_order": ["LocationAgent", "HierarchyAgent", ...],
  "total_agents": 215,
  "completed_agents": [...],
  "events": [...],
  "execution_timeline": [
    {
      "tier": 1,
      "name": "Structural Stabilization",
      "start": "2026-01-18T16:48:01.123456",
      "end": "2026-01-18T16:48:15.123456",
      "agents": ["LocationAgent", "HierarchyAgent", "NamingAgent"],
      "fixes": 0,
      "violations": 0,
      "success": true
    },
    {
      "tier": 2,
      "name": "Architectural Alignment",
      "start": "2026-01-18T16:48:15.234567",
      "end": "2026-01-18T16:48:30.234567",
      "agents": ["ImportAgent", "GovernanceAgent"],
      "fixes": 0,
      "violations": 0,
      "success": true
    },
    {
      "tier": 3,
      "name": "Deep Domain Healing",
      "start": "2026-01-18T16:48:30.345678",
      "end": "2026-01-18T16:52:00.345678",
      "agents": ["Agent1", "Agent2", ...],
      "fixes": 5,
      "violations": 2,
      "success": true
    },
    {
      "tier": 4,
      "name": "Final Safety Gate",
      "start": "2026-01-18T16:52:00.456789",
      "end": "2026-01-18T16:52:10.456789",
      "agents": ["AutonomyGuardian"],
      "fixes": 0,
      "violations": 2,
      "success": true
    }
  ]
}
```

## Troubleshooting

### Mission Aborts Unexpectedly

**Symptom**: Mission aborts even in clean repository

**Diagnosis**:
```bash
# Check Tier 1 violations
python -c "
import json
with open('runtime_state.json') as f:
    state = json.load(f)
    tier1 = next(t for t in state['execution_timeline'] if t['tier'] == 1)
    print(f\"Tier 1 violations: {tier1['violations']}\")
    print(f\"Tier 1 agents: {tier1['agents']}\")
"
```

**Solution**: Fix structural violations reported by LocationAgent, HierarchyAgent, or NamingAgent

### Duplicate Agents in Tier 3

**Symptom**: Mandatory agents appear in both Tier 1/2 and Tier 3

**Diagnosis**:
```bash
# Check for duplicates
python -c "
import json
with open('runtime_state.json') as f:
    state = json.load(f)
    tier1 = set(next(t for t in state['execution_timeline'] if t['tier'] == 1)['agents'])
    tier2 = set(next(t for t in state['execution_timeline'] if t['tier'] == 2)['agents'])
    tier3 = set(next(t for t in state['execution_timeline'] if t['tier'] == 3)['agents'])
    tier4 = set(next(t for t in state['execution_timeline'] if t['tier'] == 4)['agents'])

    mandatory = tier1 | tier2 | tier4
    duplicates = mandatory & tier3

    if duplicates:
        print(f\"❌ Duplicates found: {duplicates}\")
    else:
        print(f\"✅ No duplicates\")
"
```

**Solution**: Verify roster deduplication logic in lines 587-591 of `canon_validator_agentic_v2_thin.py`

### Missing Execution Timeline

**Symptom**: `runtime_state.json` missing `execution_timeline` field

**Diagnosis**: Check if validator completed successfully

**Solution**: Ensure validator runs to completion without exceptions

## Summary

The tiered execution flow provides:

1. **Structural Stability**: Tier 1 ensures filesystem integrity before proceeding
2. **Architectural Alignment**: Tier 2 validates import structure and governance
3. **Deep Domain Healing**: Tier 3 runs discovery-based healing agents
4. **Final Safety Gate**: Tier 4 performs comprehensive compliance check

All test cases validate these guarantees and ensure the implementation is correct.
