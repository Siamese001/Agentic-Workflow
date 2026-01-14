# Dashboard Data Validation Framework

## Overview

Comprehensive data validation framework that ensures dashboard data quality before generation. Integrated into the dashboard E2E pipeline to catch architectural and data issues early.

---

## Critical Finding: Multiple Base Agents Per Layer

### Current State (❌ BLOCKER)

**5 layers have duplicate base agents:**

| Layer | Canonical | Duplicates | Status |
|-------|-----------|------------|--------|
| L1 | L1CognitionBaseAgent 👑 | L1CognitionBaseAgent 🔴 | ❌ 2 base agents |
| L2 | L2Agent 👑 | L2ExecutionBaseAgent 🔴, SovereignBaseAgent 🔴 | ❌ 3 base agents |
| L3 | L3Agent 👑 | L3OrchestrationBaseAgent 🔴 | ❌ 2 base agents |
| L4 | L4Agent 👑 | L4StateBaseAgent 🔴 | ❌ 2 base agents |
| L5 | L5Agent 👑 | L5SafetyBaseAgent 🔴 | ❌ 2 base agents |
| L6 | None | None | ⚠️  No base agent |

**Impact:**
- Causes inheritance confusion
- Violates single source of truth principle
- Creates architectural ambiguity
- May lead to inconsistent behavior

**Recommendation:**
Keep canonical (L1CognitionBaseAgent, L2Agent, etc.), deprecate duplicates

---

## Validation Scripts

### 1. `validate_base_agents.py`
**Purpose:** Ensures each layer has exactly 1 canonical base agent

**Checks:**
- Base agent count per layer (must be 0 or 1)
- Canonical naming (L0MaintenanceBaseAgent, L1CognitionBaseAgent, etc.)
- Path consistency (base_class directories)

**Usage:**
```bash
python scripts/validate_base_agents.py
```

**Output:**
- Per-layer base agent inventory
- Duplicate detection with paths
- Recommendations for fixes

### 2. `validate_dashboard_data.py`
**Purpose:** Comprehensive data validation with 7 checks

**Validation Categories:**

1. **Base Agent Uniqueness** ⚠️ CRITICAL
   - Each layer: exactly 1 base agent
   - Status: ❌ 5 layers have duplicates

2. **Layer Consistency**
   - Agents in correct layer directories
   - Status: ⚠️  4 mismatches

3. **Path Integrity**
   - No duplicate file paths
   - Status: ✅ 292 unique paths

4. **Metric Sanity**
   - Percentages: 0-100 range
   - Complexity: reasonable values (<100)
   - LOC: reasonable values
   - Status: ❌ 10 anomalies (high complexity agents)

5. **Inheritance Patterns**
   - No circular dependencies
   - Proper base class usage
   - Status: ✅ Patterns look good

6. **Naming Conventions**
   - Ends with "Agent"
   - PascalCase
   - No underscores
   - Status: ✅ All agents comply

7. **Data Completeness**
   - Required fields present
   - Status: ✅ All 292 agents complete

**Usage:**
```bash
python scripts/validate_dashboard_data.py
```

---

## Integration into E2E Pipeline

### Step 0: Data Validation (NEW)

Added to `dashboard_e2e_pipeline_fast.py`:

```python
def step0_validate_data(self) -> bool:
    """Validate data quality before processing."""
    # Run base agent validation
    # Run comprehensive validation
    # Block pipeline if critical issues found
```

**Behavior:**
- ❌ **BLOCKS** pipeline if multiple base agents detected
- ⚠️  **WARNS** for non-critical issues (continues pipeline)
- ✅ **PASSES** if all checks pass

**Example Output:**
```
STEP 0: Validating dashboard data quality...
   ❌ Base agent validation failed:
   
   ⚠️  CRITICAL: Multiple base agents detected per layer
   This causes inheritance confusion and must be fixed manually

❌ PIPELINE BLOCKED: Critical data validation failures
   Fix base agent duplicates before continuing
   Run: python scripts/validate_base_agents.py
```

---

## Test Suite Integration

### Test 8: Base Agent Uniqueness (NEW)

Added to `test_dashboard_end_to_end.py`:

**Validates:**
- Each layer has 0-1 base agents
- No duplicate base classes
- Canonical naming patterns

**Behavior:**
- ❌ **FAILS** if any layer has >1 base agent
- Shows critical alert with fix commands
- Blocks deployment

**Example Output:**
```
──────────────────────────────────────────────────────────────────────
Running: Base Agent Uniqueness (Critical)
──────────────────────────────────────────────────────────────────────
❌ Test 8 FAILED: L1 has 2 base agents: ['L1CognitionBaseAgent', 'L1CognitionBaseAgent']
❌ Test 8 FAILED: L2 has 3 base agents: ['L2Agent', 'L2ExecutionBaseAgent', 'SovereignBaseAgent']

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
CRITICAL: Multiple base agents detected
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
This causes inheritance confusion. Run:
  python scripts/validate_base_agents.py
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
```

---

## Current Validation Results

### Summary

| Category | Status | Count | Details |
|----------|--------|-------|---------|
| Base Agent Duplicates | ❌ ERROR | 5 | L1-L5 have 2-3 base agents each |
| High Complexity | ❌ ERROR | 5 | Agents with CC > 100 |
| Layer Mismatches | ⚠️  WARNING | 4 | Agents in wrong directories |
| Low LOC Agents | ⚠️  WARNING | 5 | Healing agents < 10 LOC |
| Path Integrity | ✅ PASS | 292 | All paths unique |
| Naming Conventions | ✅ PASS | 292 | All comply |
| Data Completeness | ✅ PASS | 292 | All fields present |

### Critical Issues (Must Fix)

**1. Duplicate Base Agents (5 layers)**
```
L1: L1CognitionBaseAgent (canonical) + L1CognitionBaseAgent (duplicate)
L2: L2Agent (canonical) + L2ExecutionBaseAgent + SovereignBaseAgent (duplicates)
L3: L3Agent (canonical) + L3OrchestrationBaseAgent (duplicate)
L4: L4Agent (canonical) + L4StateBaseAgent (duplicate)
L5: L5Agent (canonical) + L5SafetyBaseAgent (duplicate)
```

**2. High Complexity Agents (5 agents)**
```
ComplianceOrchestratorAgent: CC=179
CodeDeduplicationAgent: CC=153
FilesystemSSOTReconcilerAgent: CC=114
GovernanceAgent: CC=110
NervousSystemAgent: CC=105
```

### Warnings (Should Review)

**1. Layer Mismatches (4 agents)**
```
CognitiveContractValidatorAgent: in schemas but tagged L1
NamingAgent: in utils but tagged L2
PromptRegistryAgent: in prompt_governance but tagged L2
SovereignBaseAgent: in base_agents but tagged L2
```

**2. Suspiciously Low LOC (5 agents)**
```
SemanticMapperAgent: 7 LOC
DocEnforcerAgent: 8 LOC
NamingEnforcerAgent: 8 LOC
TypeEnforcerAgent: 8 LOC
OmniContextAgent: 9 LOC
```

---

## Recommended Actions

### Immediate (Blocking)

1. **Fix Duplicate Base Agents**
   ```bash
   # Review duplicates
   python scripts/validate_base_agents.py
   
   # Manually deprecate or consolidate:
   # - L1CognitionBaseAgent → use L1CognitionBaseAgent
   # - L2ExecutionBaseAgent → use L2Agent
   # - SovereignBaseAgent → use L2Agent or move to correct layer
   # - L3OrchestrationBaseAgent → use L3Agent
   # - L4StateBaseAgent → use L4Agent
   # - L5SafetyBaseAgent → use L5Agent
   ```

2. **Create L6ObservabilityBaseAgent**
   - Currently missing
   - Should be canonical base for L6 layer

### Short-term (High Priority)

3. **Refactor High Complexity Agents**
   - ComplianceOrchestratorAgent (CC=179)
   - CodeDeduplicationAgent (CC=153)
   - Target: CC < 50 for maintainability

4. **Fix Layer Mismatches**
   - Move agents to correct layer directories
   - Or update layer tags to match paths

### Medium-term (Improvements)

5. **Review Low LOC Agents**
   - Verify these are intentionally minimal
   - Consider if they should be utility functions instead

6. **Add Auto-Fix Capability**
   - Implement `--fix` flag in validation scripts
   - Auto-deprecate duplicate base agents
   - Auto-consolidate references

---

## Pipeline Workflow

```
┌─────────────────────────────────────────────┐
│ Step 0: Data Validation (NEW)              │
│ ├─ Base Agent Uniqueness Check             │
│ ├─ Comprehensive Data Validation (7 checks)│
│ └─ Block if critical failures               │
└──────────────┬──────────────────────────────┘
               │ ✅ PASS
               ▼
┌─────────────────────────────────────────────┐
│ Step 1: Fix Heal Invocation                │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│ Step 1.5: Fix MCP Hardening                │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│ Step 2: Update Discovery Metadata          │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│ Step 3: Regenerate Dashboard                │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│ Step 4: Run Tests (including Test 8)       │
└──────────────┬──────────────────────────────┘
               │ ✅ ALL 8 TESTS PASS
               ▼
┌─────────────────────────────────────────────┐
│ Step 5: Visual Confirmation                 │
└─────────────────────────────────────────────┘
```

---

## Files Created

| File | Purpose |
|------|---------|
| `scripts/validate_base_agents.py` | Base agent uniqueness validation |
| `scripts/validate_dashboard_data.py` | Comprehensive 7-check validation |
| `README_DATA_VALIDATION.md` | This documentation |

## Files Modified

| File | Changes |
|------|---------|
| `scripts/dashboard_e2e_pipeline_fast.py` | Added Step 0: Data Validation |
| `scripts/test_dashboard_end_to_end.py` | Added Test 8: Base Agent Uniqueness |

---

## Success Criteria

✅ **Validation Framework Complete:**
- 2 validation scripts created
- 8 validation checks implemented
- Integrated into E2E pipeline
- Test 8 added to test suite

❌ **Data Quality (Blocked):**
- 5 layers have duplicate base agents
- Must fix before dashboard can be considered production-ready

---

## Next Steps

1. **Manual Fix Required:** Resolve duplicate base agents (blocking)
2. **Run Pipeline:** `python scripts/dashboard_e2e_pipeline_fast.py`
3. **Verify Tests:** All 8 tests must pass
4. **Deploy:** Dashboard ready after validation passes

---

## Commands Reference

```bash
# Run base agent validation
python scripts/validate_base_agents.py

# Run comprehensive validation
python scripts/validate_dashboard_data.py

# Run full E2E pipeline with validation
python scripts/dashboard_e2e_pipeline_fast.py

# Run test suite (8 tests)
python scripts/test_dashboard_end_to_end.py
```

---

**Status:** ⚠️  **VALIDATION FRAMEWORK COMPLETE - AWAITING MANUAL FIXES**

The validation framework is fully operational and successfully catching critical architectural issues. The pipeline will block until base agent duplicates are resolved.
