# SSOT Violations: Findings and Recommendations Report

**Date:** January 12, 2025  
**Scope:** Codebase-wide analysis for Single Source of Truth violations  
**Trigger:** Territory assignment dual-system discovered in dashboard generation

---

## Executive Summary

This report identifies **5 critical SSOT violations** in the codebase where multiple systems independently compute, assign, or categorize the same data, leading to inconsistency, unpredictable behavior, and maintenance burden. The territory assignment issue that triggered this analysis is representative of a broader architectural pattern where data derivation logic is duplicated across multiple components.

**Impact:** Medium-High  
**Effort to Fix:** Medium  
**Priority:** High (prevents future data inconsistencies)

---

## Violation 1: Territory Assignment (RESOLVED)

### **Status:** ✅ FIXED (January 12, 2025)

### Description
Agent territory assignments were computed in TWO independent systems:
1. **Discovery Script** (`full_agent_discovery.py`) - assigned simple territories ("L2", "L5")
2. **Dashboard Generator** (`generate_dashboard.py`) - re-mapped to detailed territories ("L2 Execution/Core")

### Evidence
- Discovery assigned `territory` field → saved to JSON
- Dashboard **ignored** that field → re-derived using different logic
- Result: Dashboard showed 292 agents (previous), discovery had 281 agents (actual)

### Root Cause
No architectural principle enforcing "compute once, use everywhere"

### Fix Applied
- Discovery script now assigns detailed territories as SSOT
- Dashboard generator uses `agent.get('territory')` directly
- Removed 90+ lines of re-mapping logic from dashboard

### Lesson Learned
**When data can be computed at ingestion time, do it there. Downstream consumers should NEVER re-derive.**

---

## Violation 2: Layer Inference Logic

### **Status:** ❌ ACTIVE VIOLATION

### Description
Layer assignment for agents is computed in **MULTIPLE LOCATIONS** with different logic:

**Location 1:** `full_agent_discovery.py` - `infer_layer()` function (lines 368-398)
```python
def infer_layer(py_file: Path) -> str:
    # Uses path-based detection
    if 'L0_maintenance' in str(py_file): return 'L0'
    if 'L1_cognition' in str(py_file): return 'L1'
    # ... etc
```

**Location 2:** `unified_validator.py` - `get_layer()` function
```python
def get_layer(file_path: str) -> Optional[str]:
    # Different path parsing logic
    parts = file_path.split('/')
    for part in parts:
        if part.startswith('L') and part[1].isdigit():
            return part[:2]
```

**Location 3:** `LocationAgent.py` - Territory validation logic
- Uses `SOVEREIGN_REGISTRY` to determine layer from path
- Different validation rules than discovery script

**Location 4:** `SemanticTerritoryMapperAgent.py` - Semantic layer mapping
- Uses embeddings and vector search to infer layer
- Completely different approach from path-based detection

### Impact
- Inconsistent layer assignments across tools
- Agents may be classified differently depending on which tool scans them
- Validation failures when tools disagree on layer

### Evidence
Found 107 matches for "infer_layer|get_layer|determine_layer" across 32 files

### Recommendation
**Create a single canonical layer inference function:**

```python
# agentic_core/config/blueprint_sovereign/layer_inference.py
def get_canonical_layer(file_path: Path) -> str:
    """
    SSOT for layer inference. All tools MUST use this function.
    Returns: 'L0', 'L1', ..., 'L6', 'Apps', 'utils', or 'Unknown'
    """
    # Single implementation used by:
    # - full_agent_discovery.py
    # - unified_validator.py
    # - LocationAgent.py
    # - All validation tools
```

**Migration Steps:**
1. Create canonical function in `structure_blueprint.py`
2. Update all 32 files to import and use it
3. Add test to ensure all tools use same layer logic
4. Remove duplicate implementations

---

## Violation 3: Agent Categorization Logic

### **Status:** ❌ ACTIVE VIOLATION

### Description
Agent categorization (for dashboard display, validation, etc.) is performed in **MULTIPLE SYSTEMS**:

**System 1:** `agent_categorizer.py` - Pattern-based categorization
```python
CATEGORY_PATTERNS = [
    {"name": "Validation & Compliance", "patterns": [r"Validator|Validation"]},
    {"name": "Self-Healing & Recovery", "patterns": [r"Healer|Healing"]},
    # ... 9 categories total
]
```

**System 2:** Dashboard generator - Implicit categorization by territory
- Groups agents by territory ("L5 Safety/Validators")
- Territory name implies category

**System 3:** Various validator agents - Role-based categorization
- `BaseClassEnforcerAgent` - categorizes by inheritance
- `HierarchyAgent` - categorizes by layer hierarchy
- Each uses different rules

### Impact
- Same agent may be categorized differently by different tools
- Dashboard categories don't match validation categories
- No single view of "what type of agent is this?"

### Evidence
- `agent_categorizer.py` has 9 hardcoded category patterns
- Found 52 matches for "categorize|classify" functions across 45 files
- Each tool implements own categorization logic

### Recommendation
**Establish agent categorization as a first-class field in discovery:**

```python
# In full_agent_discovery.py
agents.append({
    'class_name': node.name,
    'layer': layer,
    'territory': territory,
    'category': categorize_agent(node, bases, methods),  # NEW: SSOT
    # ... other fields
})

def categorize_agent(node, bases, methods) -> str:
    """
    SSOT for agent categorization.
    Returns: 'Validator', 'Healer', 'Guardian', 'Orchestrator', etc.
    """
    # Single canonical implementation
```

**Benefits:**
- Category computed once during discovery
- All tools use same category value
- Dashboard, validators, reports all consistent

---

## Violation 4: Health Score Calculation

### **Status:** ❌ ACTIVE VIOLATION

### Description
Health scores are calculated in **TWO DIFFERENT PLACES** with **DIFFERENT FORMULAS**:

**Location 1:** Dashboard generator - Weighted formula
```python
# generate_dashboard.py - compute_territory_metrics()
health = (
    heal_cap_pct * 0.30 +      # 30% weight
    invocation_pct * 0.10 +    # 10% weight
    test_pct * 0.25 +          # 25% weight
    observable_pct * 0.20 +    # 20% weight
    complexity_health * 0.15   # 15% weight
)
```

**Location 2:** E2E test validation - Simple average
```python
# test_dashboard_end_to_end.py - Test 5
expected_health = (heal + inv + test + obs + cc) / 5  # Equal weights
```

### Impact
- Dashboard shows health scores that don't match test expectations
- Test 5 consistently fails with "Health formula mismatch"
- Users see warnings like: "Expected: 85.6%, Actual: 89.2%"

### Evidence
From test output:
```
⚠️  WARNING: Health formula mismatch in L5 Safety/Base Class
   Expected: 92.2% (avg of 5 components)
   Actual: 94.2%
```

### Recommendation
**Create a canonical health calculation function:**

```python
# agentic_core/config/blueprint_sovereign/metrics.py
def calculate_health_score(
    heal_cap: float,
    invocation: float,
    test_coverage: float,
    observability: float,
    complexity_health: float
) -> float:
    """
    SSOT for health score calculation.
    
    Formula: Weighted average
    - Heal Capability: 30%
    - Invocation: 10%
    - Test Coverage: 25%
    - Observability: 20%
    - Complexity Health: 15%
    """
    return (
        heal_cap * 0.30 +
        invocation * 0.10 +
        test_coverage * 0.25 +
        observability * 0.20 +
        complexity_health * 0.15
    )
```

**Migration:**
- Import in `generate_dashboard.py`
- Import in `test_dashboard_end_to_end.py`
- Import in any other health calculation locations
- Remove duplicate implementations

---

## Violation 5: File Placement / Territory Validation

### **Status:** ❌ ACTIVE VIOLATION

### Description
File placement validation (determining if a file is in the correct location) is performed by **MULTIPLE AGENTS** with **OVERLAPPING LOGIC**:

**Agent 1:** `LocationAgent.py` (L5_safety/validators)
- Validates root folder whitelist
- Enforces depth per sovereign root
- Checks forbidden patterns

**Agent 2:** `TerritoryHealerAgent.py` (L3_orchestration/workflow_engines)
- Detects intra-territory strays
- Uses key-specific stray signals
- Suggests territory moves

**Agent 3:** `SemanticTerritoryMapperAgent.py` (L3_orchestration/workflow_engines)
- Maps files to semantic territories using embeddings
- Uses vector similarity search
- Different confidence thresholds

**Agent 4:** `HierarchyAgent.py` (L5_safety/guardrails)
- Validates layer hierarchy
- Enforces import restrictions
- Checks territory alignment

### Impact
- Four different agents can give four different answers about file placement
- Conflicting suggestions for where to move files
- No single authority on "is this file in the right place?"

### Evidence
- `LocationAgent` uses `SOVEREIGN_REGISTRY` for validation
- `TerritoryHealerAgent` uses `key_stray_signals` dictionary
- `SemanticTerritoryMapperAgent` uses `TERRITORY_EXAMPLES` and embeddings
- Each has different thresholds and rules

### Recommendation
**Establish a hierarchy of validation:**

```python
# Proposed architecture:
# 1. LocationAgent (L5) - Structural validation (MUST pass)
#    - Root folder whitelist
#    - Depth enforcement
#    - Forbidden patterns
#
# 2. TerritoryHealerAgent (L3) - Semantic validation (SHOULD pass)
#    - Delegates to SemanticTerritoryMapperAgent for suggestions
#    - Uses LocationAgent rules as constraints
#
# 3. SemanticTerritoryMapperAgent (L3) - Advisory only
#    - Provides suggestions, doesn't enforce
#    - Used by TerritoryHealerAgent
```

**Key principle:** Lower layers (L5) define hard rules, higher layers (L3) provide suggestions within those constraints.

**Refactor:**
1. `LocationAgent` becomes SSOT for structural rules
2. `TerritoryHealerAgent` delegates to `LocationAgent` for validation
3. `SemanticTerritoryMapperAgent` provides suggestions only
4. Remove duplicate validation logic

---

## Common Patterns Across Violations

### Pattern 1: "Compute Everywhere"
Multiple systems independently compute the same value from raw data instead of computing once and sharing.

**Example:** Layer inference computed in 4+ places from file paths

### Pattern 2: "Different Formulas"
Same conceptual metric calculated with different formulas in different locations.

**Example:** Health score uses weighted average in dashboard, simple average in tests

### Pattern 3: "Overlapping Responsibilities"
Multiple agents/tools claim authority over the same domain without clear hierarchy.

**Example:** 4 agents validate file placement with different rules

### Pattern 4: "Implicit vs Explicit"
Some systems store computed values explicitly, others derive implicitly from context.

**Example:** Territory stored in JSON but dashboard re-derives from path

---

## Architectural Recommendations

### Recommendation 1: Establish "Compute Once" Principle

**Rule:** If data can be computed during ingestion/discovery, compute it there and store it. Downstream consumers should NEVER re-compute.

**Application:**
- Agent discovery computes: layer, territory, category, base class status
- Dashboard/validators/reports consume those values directly
- No re-derivation allowed

### Recommendation 2: Create Canonical Metrics Module

**File:** `agentic_core/config/blueprint_sovereign/canonical_metrics.py`

**Contents:**
```python
def get_layer(file_path: Path) -> str:
    """SSOT for layer inference"""
    
def categorize_agent(class_node, bases, methods) -> str:
    """SSOT for agent categorization"""
    
def calculate_health_score(...) -> float:
    """SSOT for health calculation"""
    
def calculate_code_quality_score(...) -> float:
    """SSOT for code quality calculation"""
```

**Enforcement:**
- Add pre-commit hook to detect duplicate implementations
- Add test that scans for "def.*health|def.*layer|def.*categorize" and ensures only one implementation exists

### Recommendation 3: Validation Hierarchy

**Establish clear hierarchy:**
1. **L5 Agents** - Define hard rules (MUST pass)
2. **L3 Agents** - Orchestrate and suggest (SHOULD pass)
3. **L2 Agents** - Execute suggestions (MAY execute)

**Example:**
- `LocationAgent` (L5) defines "file MUST be in whitelisted root"
- `TerritoryHealerAgent` (L3) suggests "file SHOULD move to better territory"
- File mover (L2) executes the move

### Recommendation 4: Explicit Field Storage

**Rule:** Computed values should be stored as explicit fields, not derived on-the-fly.

**Before (implicit):**
```python
# Dashboard derives territory from path
territory = derive_territory_from_path(agent['path'])
```

**After (explicit):**
```python
# Discovery stores territory explicitly
agents.append({'territory': territory, ...})
# Dashboard uses stored value
territory = agent['territory']
```

### Recommendation 5: SSOT Documentation

**Create:** `SSOT_REGISTRY.md` documenting the canonical source for each data type

**Format:**
```markdown
| Data Type | SSOT Location | Consumers | Notes |
|-----------|---------------|-----------|-------|
| Layer | full_agent_discovery.py:infer_layer() | Dashboard, validators, tests | Path-based |
| Territory | full_agent_discovery.py:assign_territory() | Dashboard, reports | Detailed subcategories |
| Health Score | canonical_metrics.py:calculate_health() | Dashboard, tests | Weighted formula |
```

---

## Implementation Priority

### High Priority (Fix Immediately)
1. **Health Score Calculation** - Causing test failures, user confusion
2. **Layer Inference** - Core to all categorization logic

### Medium Priority (Fix This Sprint)
3. **Agent Categorization** - Affects dashboard display, validation
4. **File Placement Validation** - Multiple agents with conflicting logic

### Low Priority (Technical Debt)
5. **Territory Assignment** - Already fixed, document as example

---

## Testing Strategy

### Test 1: SSOT Enforcement Test
```python
def test_no_duplicate_implementations():
    """Ensure only ONE implementation of each canonical function exists."""
    # Scan codebase for duplicate function names
    # Fail if multiple implementations found
```

### Test 2: Consistency Test
```python
def test_all_tools_use_canonical_functions():
    """Ensure all tools import from canonical locations."""
    # Check that no tool has local implementation
    # Verify all imports come from canonical_metrics.py
```

### Test 3: Formula Validation Test
```python
def test_health_score_matches_spec():
    """Verify health score formula matches documented weights."""
    # Test with known inputs
    # Verify output matches expected weighted average
```

---

## Estimated Effort

| Violation | Analysis | Implementation | Testing | Total |
|-----------|----------|----------------|---------|-------|
| Layer Inference | 2h | 4h | 2h | 8h |
| Agent Categorization | 2h | 6h | 2h | 10h |
| Health Score | 1h | 2h | 1h | 4h |
| File Placement | 4h | 8h | 4h | 16h |
| **TOTAL** | **9h** | **20h** | **9h** | **38h** |

**Timeline:** 1 sprint (2 weeks) with 1 developer

---

## Success Metrics

1. **Zero duplicate implementations** - Codebase scan shows only one implementation per canonical function
2. **All tests pass** - No health formula mismatches, no layer inference conflicts
3. **Consistent categorization** - Same agent shows same category across all tools
4. **Single source of truth** - SSOT_REGISTRY.md documents canonical source for all computed data

---

## Conclusion

The territory assignment SSOT violation was not an isolated incident but part of a broader architectural pattern where data derivation logic is duplicated across components. By establishing canonical functions, enforcing "compute once" principles, and documenting SSOT locations, we can eliminate these violations and prevent future inconsistencies.

**Next Steps:**
1. Review this report with team
2. Prioritize violations (recommend: Health Score → Layer Inference → Agent Categorization)
3. Create implementation tickets
4. Establish SSOT enforcement in CI/CD pipeline

---

**Report prepared by:** Cascade AI  
**Review status:** Draft - Awaiting team review  
**Related documents:** 
- `RCA_TERRITORY_SSOT_VIOLATION.md`
- `RCA_FIXES_SUMMARY.md`
