# Territory Structure Inconsistencies: Findings and Recommendations

**Date**: January 5, 2026  
**Analysis Scope**: L0-L5 Layer Territory Reporting in Autonomy Dashboard  
**Status**: Critical Inconsistencies Identified

---

## Executive Summary

Analysis of the autonomy dashboard reveals **significant structural inconsistencies** in how L1-L5 layers are reported. The most critical issue is that **Base Class territories only appear for L1 and L2**, despite base class agents existing in L3, L4, and L5 codebases. Additionally, subterritory naming and categorization patterns are inconsistent across layers.

---

## Critical Findings

### 1. **Base Class Territory Inconsistency** [SEVERITY: HIGH]

**Issue**: Base Class agents exist in L1-L5 but only L1 and L2 have dedicated "Base Class" territories in the dashboard.

**Evidence**:
- **L1 Cognition/Base Class**: 1 agent (`L1CognitionBaseAgent.py`) ✅ Reported
- **L2 Execution/Base Class**: 1 agent (`L2ExecutionBaseAgent.py`) ✅ Reported
- **L3 Orchestration**: Has `OrchestrationBaseAgent.py` ❌ NOT reported as separate territory
- **L4 State**: Has `StateBaseAgent.py` ❌ NOT reported as separate territory
- **L5 Safety**: Has `SafetyBaseAgent.py` ❌ NOT reported as separate territory

**Root Cause**: The L3, L4, and L5 base class agents are **not being discovered** by the agent discovery system (`agent_discovery_full.json`). They exist in the codebase but are not being classified as agents, likely because:
1. They may be abstract base classes without concrete implementations
2. The discovery system may be filtering them out
3. They may not match the agent detection criteria

**Impact**:
- Inconsistent reporting makes it difficult to track base class compliance across all layers
- L3-L5 base class agents are invisible in autonomy metrics
- Cannot apply uniform target policies to base classes across all layers
- Misleading representation of architecture (suggests L3-L5 don't have base classes)

---

### 2. **Subterritory Distribution Inconsistencies** [SEVERITY: MEDIUM]

**Issue**: Common subterritories (Core, Infrastructure, Specialized) appear in some layers but not others without clear architectural justification.

#### 2.1 Core Subterritory
- **Present in**: L0, L1, L2, L3, L4
- **Missing in**: L5
- **L5 has instead**: Gravity, Guardrails, Red Teaming, Validators

**Analysis**: L5 uses domain-specific categories rather than generic "Core". This is architecturally justified but creates inconsistency.

#### 2.2 Infrastructure Subterritory
- **Present in**: L0, L1, L2, L3, L4
- **Missing in**: L5

**Analysis**: L5 Safety layer may not need infrastructure agents, but this should be explicitly documented.

#### 2.3 Specialized Subterritory
- **Present in**: L1, L2, L3, L4
- **Missing in**: L0, L5

**Analysis**: 
- L0 (Maintenance) may not have specialized agents by design
- L5 uses domain-specific categories instead

---

### 3. **Naming Inconsistencies** [SEVERITY: LOW]

**Issue**: Abbreviated vs full names used inconsistently.

**Examples**:
- "Infrastructure" (full) vs "Infrast" (abbreviated) - both appear in dashboard
- "Specialized" vs "Special" - inconsistent usage
- "Base Cl" (abbreviated) vs "Base Class" (full)

**Impact**: Makes filtering and analysis more difficult; reduces dashboard professionalism.

---

## Current Territory Structure by Layer

```
L5 Safety (4 territories):
  ├── Gravity (1 agent)
  ├── Guardrails (1 agent)
  ├── Red Teaming (1 agent)
  └── Validators (1 agent)

L4 State (3 territories):
  ├── Core (2 agents)
  ├── Infrastructure (3 agents)
  └── Specialized (5 agents)

L3 Orchestration (3 territories):
  ├── Core (40 agents)
  ├── Infrastructure (2 agents)
  └── Specialized (5 agents)

L2 Execution (4 territories):
  ├── Base Class (1 agent) ✅
  ├── Core (69 agents)
  ├── Infrastructure (2 agents)
  └── Specialized (4 agents)

L1 Cognition (4 territories):
  ├── Base Class (1 agent) ✅
  ├── Core (14 agents)
  ├── Infrastructure (8 agents)
  └── Specialized (3 agents)

L0 Maintenance (2 territories):
  ├── Core (6 agents)
  └── Infrastructure (3 agents)
```

---

## Recommendations

### Option A: Add Base Class Territories for L3-L5 [RECOMMENDED]

**Approach**: Ensure L3, L4, and L5 base class agents are discovered and reported as separate territories.

**Actions Required**:
1. **Fix Agent Discovery**: Investigate why `OrchestrationBaseAgent`, `StateBaseAgent`, and `SafetyBaseAgent` are not being discovered
   - Check if they're marked as abstract and excluded
   - Verify they match agent detection criteria
   - Update discovery logic if needed

2. **Add Base Class Territories**:
   - L3 Orchestration/Base Class (1 agent)
   - L4 State/Base Class (1 agent)
   - L5 Safety/Base Class (1 agent)

3. **Update Target Configuration**: Ensure `autonomy_targets.py` applies consistent base class targets (invocation=N/A) to all layers

**Benefits**:
- ✅ Consistent reporting across all layers
- ✅ Complete visibility into base class compliance
- ✅ Easier to apply uniform policies
- ✅ Accurate architectural representation

**Risks**:
- May require changes to agent discovery system
- Could affect agent count metrics

---

### Option B: Bundle Base Classes into Core [ALTERNATIVE]

**Approach**: Remove separate Base Class territories and bundle base class agents into Core subterritory.

**Actions Required**:
1. Reclassify L1CognitionBaseAgent → L1 Cognition/Core
2. Reclassify L2ExecutionBaseAgent → L2 Execution/Core
3. Update territory classification logic

**Benefits**:
- ✅ Simpler territory structure
- ✅ No need to fix discovery system

**Drawbacks**:
- ❌ Loses visibility into base class compliance
- ❌ Cannot apply special target policies to base classes
- ❌ Mixes abstract base classes with concrete implementations

**Verdict**: NOT RECOMMENDED - Base classes have special characteristics (invocation=N/A, observability=N/A) that justify separate tracking.

---

### Option C: Document L5 as Exception [PARTIAL SOLUTION]

**Approach**: Accept that L5 uses domain-specific categories and document this as intentional architectural difference.

**Actions Required**:
1. Add L3 Orchestration/Base Class
2. Add L4 State/Base Class
3. Document that L5 Safety uses domain-specific categories (Gravity, Guardrails, etc.) instead of generic Core/Infrastructure/Specialized

**Benefits**:
- ✅ Acknowledges L5's unique role
- ✅ Still fixes L3-L4 inconsistency

**Drawbacks**:
- ⚠️ Partial solution - doesn't address L5 base class visibility

---

## Additional Recommendations

### 1. Standardize Naming
- Use full names consistently: "Infrastructure" not "Infrast", "Base Class" not "Base Cl"
- Update dashboard template to display full names
- Add abbreviation mapping for backward compatibility

### 2. Document Territory Classification Rules
Create `docs/territory_classification.md` with:
- Clear rules for when to create Core vs Specialized vs Infrastructure
- Explanation of L5's domain-specific categories
- Base class classification criteria

### 3. Add Territory Structure Tests
Extend `comprehensive_dashboard_tests.py` with:
- Test that all L1-L5 layers have consistent subterritory structure (or documented exceptions)
- Test that base class agents are discovered and reported
- Test for naming consistency

---

## Implementation Priority

### Phase 1: Critical Fixes (Immediate)
1. ✅ Fix agent discovery to include L3-L5 base class agents
2. ✅ Add Base Class territories for L3, L4, L5
3. ✅ Update target configuration for new territories

### Phase 2: Consistency Improvements (Short-term)
1. Standardize naming (Infrastructure, Base Class, etc.)
2. Add territory structure validation tests
3. Document classification rules

### Phase 3: Documentation (Medium-term)
1. Create territory classification guide
2. Add architectural decision records (ADRs) for L5's unique structure
3. Update dashboard user guide

---

## Conclusion

The **recommended approach is Option A**: Add Base Class territories for L3-L5 to achieve full consistency. This requires fixing the agent discovery system but provides the most accurate and maintainable representation of the architecture.

The current inconsistency is not just cosmetic - it affects:
- Target policy application
- Compliance tracking
- Architectural visibility
- Dashboard usability

**Next Steps**:
1. Investigate why L3-L5 base class agents are not being discovered
2. Fix discovery logic or agent classification
3. Regenerate dashboard with complete Base Class territories
4. Add validation tests to prevent regression
