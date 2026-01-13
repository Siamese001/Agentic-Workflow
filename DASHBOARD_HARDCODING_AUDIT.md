# Dashboard Hardcoding Audit - Findings & Remediation Plan

**Date**: 2026-01-13  
**Scope**: `generate_dashboard.py` end-to-end data pipeline review  
**Objective**: Identify all hardcoded values that should be calculated from agent discovery data

---

## Executive Summary

**Total Hardcoding Issues Found**: 5 critical instances  
**Data Available But Unused**: 2 fields (LOC, schema_strictness)  
**Data Not Collected**: 3 fields (metadata, criticality, used_pct)  
**Impact**: Dashboard shows inaccurate/placeholder data for 5 key metrics affecting ~20% of dashboard fields

---

## Findings

### 🔴 CRITICAL: Field Hardcoding Issues

#### Finding #1: Average LOC (Lines of Code)
**Location**: `generate_dashboard.py:341, 406`  
**Current Implementation**:
```python
"Avg LOC": 150,  # Placeholder
```

**Issue Severity**: HIGH  
**Impact**: Dashboard shows all territories with exactly 150 LOC, masking actual code size variations

**Data Availability**: ✅ AVAILABLE  
- Field exists in `agent_discovery_full.json` as `'loc'`
- All agents have LOC data (confirmed via discovery script)
- LOC range: varies by agent complexity

**Root Cause**: Legacy placeholder never replaced with actual calculation

**Recommendation**: CALCULATE from agent data
```python
# In compute_territory_metrics():
loc_sum = sum(a.get('loc', 0) for a in agents_list)
avg_loc = round(loc_sum / total, 1)

# In build_territory_row():
"Avg LOC": metrics["avg_loc"],
```

**Implementation Priority**: P0 - Data exists, trivial fix, high user value

---

#### Finding #2: Metadata %
**Location**: `generate_dashboard.py:344, 409`  
**Current Implementation**:
```python
"Metadata %": 100.0,
```

**Issue Severity**: HIGH  
**Impact**: Dashboard falsely reports 100% metadata coverage for all territories

**Data Availability**: ❌ NOT COLLECTED  
- Field does NOT exist in `agent_discovery_full.json`
- No metadata collection logic in discovery script
- Unclear definition of "metadata" in current context

**Root Cause**: Field added to dashboard schema without corresponding data collection

**Recommendation**: DEFINE then IMPLEMENT
1. **Define "Metadata"**: What constitutes metadata compliance?
   - Option A: Presence of module-level docstrings
   - Option B: Presence of class-level docstrings
   - Option C: Combination of docstring + `__version__` + `__author__`
   - Option D: Remove field if not architecturally significant

2. **If keeping field**: Add detection to `full_agent_discovery.py`
```python
def detect_metadata_compliance(file_source: str, class_node: ast.ClassDef) -> bool:
    """Detect if agent has proper metadata (docstrings, version, etc)."""
    has_module_doc = bool(ast.get_docstring(ast.parse(file_source)))
    has_class_doc = bool(ast.get_docstring(class_node))
    # Add to agent record: 'has_metadata': has_module_doc and has_class_doc
    return has_module_doc and has_class_doc
```

3. **Calculate in dashboard**:
```python
# In compute_territory_metrics():
metadata_count = sum(1 for a in agents_list if a.get('has_metadata', False))
metadata_pct = round(metadata_count / total * 100, 1)
```

**Implementation Priority**: P1 - Requires design decision + discovery script changes

---

#### Finding #3: Schema Strictness %
**Location**: `generate_dashboard.py:347, 412`  
**Current Implementation**:
```python
"Schema Strictness %": metrics["typed_pct"],
```

**Issue Severity**: MEDIUM  
**Impact**: Dashboard shows typing % twice (as both "Typed %" and "Schema Strictness %"), losing distinct signal

**Data Availability**: ✅ AVAILABLE  
- Field exists in `agent_discovery_full.json` as `'schema_strictness'`
- Calculated via `calculate_schema_strictness()` in discovery script
- **Currently mirrors typing coverage** (line 697: `return calculate_typing_coverage(class_node)`)

**Root Cause**: 
1. Discovery script calculates `schema_strictness` but just duplicates `typed_pct`
2. Dashboard generator ignores the `schema_strictness` field and uses `typed_pct` instead

**Recommendation**: USE ACTUAL FIELD
```python
# In compute_territory_metrics():
schema_sum = sum(a.get('schema_strictness', 0) for a in agents_list)
schema_pct = round(schema_sum / total, 1)

# Add to metrics dict:
"schema_pct": schema_pct

# In build_territory_row():
"Schema Strictness %": metrics["schema_pct"],  # NOT typed_pct
```

**Future Enhancement**: Improve `calculate_schema_strictness()` in discovery script to:
- Penalize use of `Any` type
- Require Pydantic models for state
- Enforce strict type checking flags

**Implementation Priority**: P0 - Data exists, trivial fix

---

#### Finding #4: Criticality
**Location**: `generate_dashboard.py:350, 415`  
**Current Implementation**:
```python
"Criticality": 75,
```

**Issue Severity**: HIGH  
**Impact**: All territories show identical criticality (75), eliminating prioritization signal

**Data Availability**: ❌ NOT COLLECTED  
- Field does NOT exist in `agent_discovery_full.json`
- No criticality scoring in discovery script

**Root Cause**: Field added to dashboard without data collection strategy

**Recommendation**: DEFINE then CALCULATE

**Option A: Layer-Based Criticality (Recommended)**
```python
# In build_territory_row():
LAYER_CRITICALITY = {
    'L5': 100,  # Safety - critical
    'L4': 85,   # State - high
    'L3': 75,   # Orchestration - medium-high
    'L2': 60,   # Execution - medium
    'L1': 50,   # Cognition - medium-low
    'L0': 40,   # Maintenance - low
    'L6': 30,   # Observability - support
    'Base': 95, # Foundation - very high
    'Apps': 70  # Applications - medium-high
}

def calculate_criticality(territory_name: str) -> int:
    """Calculate criticality based on architectural layer."""
    for layer, score in LAYER_CRITICALITY.items():
        if layer in territory_name:
            return score
    return 50  # Default
```

**Option B: Usage-Based Criticality (Advanced)**
Requires new discovery logic to track import frequency:
```python
# In full_agent_discovery.py - add import graph analysis
def calculate_agent_criticality(agent_class: str, import_graph: Dict) -> int:
    """Higher criticality for agents imported by many others."""
    import_count = len(import_graph.get(agent_class, []))
    # Map import count to 0-100 scale
    return min(100, import_count * 5)
```

**Implementation Priority**: P1 - Requires architecture decision

---

#### Finding #5: Used %
**Location**: `generate_dashboard.py:354, 419`  
**Current Implementation**:
```python
"Used %": 95.0,
```

**Issue Severity**: HIGH  
**Impact**: False signal that 95% of agents are "used" when actual usage is unknown

**Data Availability**: ❌ NOT COLLECTED  
- Field does NOT exist in `agent_discovery_full.json`
- No usage tracking in codebase

**Root Cause**: Aspirational field added without implementation

**Recommendation**: DEFINE then TRACK

**Option A: Import-Based Usage (Recommended)**
```python
# In full_agent_discovery.py - add import graph
def build_import_graph(all_agents: List[Dict]) -> Dict[str, Set[str]]:
    """Track which agents are imported by other Python files."""
    import_graph = defaultdict(set)
    
    for file_path in all_python_files:
        source = read_file(file_path)
        imports = extract_imports(source)
        for imp in imports:
            if imp in agent_class_names:
                import_graph[imp].add(file_path)
    
    return import_graph

# Mark agent as "used" if imported anywhere
agent['is_used'] = agent['class_name'] in import_graph
```

**Option B: Instantiation-Based Usage (Advanced)**
Requires runtime analysis:
```python
# Add instrumentation to SovereignBaseAgent.__init__
# Log all agent instantiations to usage_tracker.json
# Aggregate in discovery script
```

**Option C: Remove Field (Pragmatic)**
If usage tracking is not architecturally critical, remove field from schema:
```python
# Remove "Used %" from REQUIRED_FIELDS
# Remove from build_territory_row() and build_total_row()
# Update dashboard HTML to hide this column
```

**Implementation Priority**: P2 - Lower impact, requires significant effort

---

## Secondary Issues

### Issue #6: Invocation % Duplication
**Location**: `generate_dashboard.py:335, 400`  
```python
"Heal Invocation %": metrics["heal_inv_pct"],
"Invocation %": metrics["heal_inv_pct"],  # Same value!
```

**Impact**: Two fields showing identical data, wasting dashboard space

**Recommendation**: 
- Keep "Heal Invocation %" (more descriptive)
- Remove "Invocation %" or repurpose for different metric
- Update REQUIRED_FIELDS accordingly

---

### Issue #7: Base Class Inherit % Duplication  
**Location**: `generate_dashboard.py:346, 411`
```python
"Proper Base %": metrics["proper_base_pct"],
"Base Class Inherit %": metrics["proper_base_pct"],  # Alias!
```

**Impact**: Duplicate field for JavaScript rendering compatibility

**Recommendation**: Keep alias for backward compatibility, but document clearly

---

## Implementation Roadmap

### Phase 1: Quick Wins (P0 - 1-2 hours)
1. ✅ **Fix Avg LOC** - Use existing `loc` field from agent data
2. ✅ **Fix Schema Strictness %** - Use existing `schema_strictness` field
3. ✅ **Document duplications** - Add comments explaining Invocation % and Base Class Inherit % aliases

**Code Changes**:
```python
# In compute_territory_metrics():
loc_sum = sum(a.get('loc', 0) for a in agents_list)
avg_loc = round(loc_sum / total, 1)

schema_sum = sum(a.get('schema_strictness', 0) for a in agents_list)
schema_pct = round(schema_sum / total, 1)

return {
    # ... existing fields ...
    "avg_loc": avg_loc,
    "schema_pct": schema_pct,
}

# In build_territory_row():
"Avg LOC": metrics["avg_loc"],
"Schema Strictness %": metrics["schema_pct"],
```

**Validation**: Run e2e tests, verify LOC shows real variations across territories

---

### Phase 2: Architecture Decisions (P1 - Design meeting required)
1. **Define Metadata %** - What does metadata compliance mean?
2. **Define Criticality** - Layer-based vs usage-based scoring?
3. **Define Used %** - Import-based vs instantiation-based vs remove?

**Action Items**:
- [ ] Schedule architecture review meeting
- [ ] Document metric definitions in `DASHBOARD_METRICS_SPEC.md`
- [ ] Get stakeholder approval on definitions

---

### Phase 3: Data Collection Enhancement (P1 - 4-6 hours)
1. **Implement Metadata Detection** (if keeping field)
   - Add `detect_metadata_compliance()` to `full_agent_discovery.py`
   - Update agent schema to include `has_metadata` field
   - Regenerate `agent_discovery_full.json`

2. **Implement Criticality Calculation**
   - Add layer-based criticality lookup
   - OR implement import graph analysis for usage-based scoring

3. **Implement Usage Tracking** (if keeping field)
   - Build import graph in discovery script
   - Mark agents as used/unused
   - OR remove field from schema

**Code Changes**: See detailed recommendations under each finding above

**Validation**: 
- Run full discovery scan
- Verify new fields present in JSON
- Run e2e tests
- Visual inspection of dashboard

---

### Phase 4: Schema Cleanup (P2 - Optional)
1. Remove or repurpose duplicate "Invocation %" field
2. Improve `calculate_schema_strictness()` to check for `Any` usage
3. Add field descriptions to dashboard HTML tooltips

---

## Testing Requirements

### Pre-Implementation Tests
```bash
# Verify current agent data fields
python -c "import json; d=json.load(open('agent_discovery_full.json')); print(list(d[0].keys()))"

# Check LOC data availability
python -c "import json; d=json.load(open('agent_discovery_full.json')); print('LOC data:', sum(1 for a in d if 'loc' in a), '/', len(d))"

# Check schema_strictness availability  
python -c "import json; d=json.load(open('agent_discovery_full.json')); print('Schema data:', sum(1 for a in d if 'schema_strictness' in a), '/', len(d))"
```

### Post-Implementation Tests
```bash
# Regenerate dashboard with fixes
python agentic_core/L6_observability/dashboards/generate_dashboard.py

# Run e2e tests
python scripts/test_dashboard_end_to_end.py

# Verify LOC variations (should NOT all be 150)
python -c "import json; d=json.load(open('agent_discovery_full.json')); from collections import Counter; print('LOC distribution:', Counter(a.get('loc') for a in d[:20]))"
```

### Validation Checklist
- [ ] All territories show different Avg LOC values
- [ ] Schema Strictness % differs from Typed % for some agents
- [ ] Metadata % shows actual coverage (if implemented)
- [ ] Criticality varies by layer/territory
- [ ] Used % reflects actual usage patterns (if implemented)
- [ ] All 17 e2e tests pass
- [ ] Dashboard visually inspected for data integrity

---

## Risk Analysis

### Low Risk Changes (Phase 1)
- Using existing LOC data - **zero risk**
- Using existing schema_strictness data - **zero risk**
- Both fields already collected, just need to wire them up

### Medium Risk Changes (Phase 3)
- Adding new detection logic to discovery script
- Risk: Could introduce parsing errors or slow down scan
- Mitigation: Extensive testing, performance benchmarking

### High Risk Changes
- Removing fields from schema (breaks backward compatibility)
- Changing health formula weights
- Mitigation: Don't do this without stakeholder approval

---

## Success Metrics

### Quantitative
- ✅ 0 hardcoded numeric values in `build_territory_row()` (excluding constants like layer priority)
- ✅ 100% of agent data fields used if they exist in discovery JSON
- ✅ All e2e tests passing after changes
- ✅ Dashboard generation time < 10 seconds (performance baseline)

### Qualitative  
- ✅ Dashboard shows **real variations** in LOC across territories
- ✅ No duplicate metrics showing identical values
- ✅ All metrics have clear definitions documented
- ✅ Users can trust dashboard data for decision-making

---

## Appendix A: Current vs Proposed Data Flow

### Current Flow (BROKEN)
```
agent_discovery_full.json (has 'loc') 
    ↓
generate_dashboard.py (ignores 'loc', uses hardcoded 150)
    ↓
autonomy_dashboard.html (shows 150 for all territories)
```

### Proposed Flow (FIXED)
```
agent_discovery_full.json (has 'loc': 347) 
    ↓
generate_dashboard.py (calculates avg_loc from agent data)
    ↓
autonomy_dashboard.html (shows real avg: 247)
```

---

## Appendix B: Fields Requiring Upstream Changes

| Field | Exists in Discovery? | Action Required |
|-------|---------------------|-----------------|
| LOC | ✅ Yes | Use existing data |
| Schema Strictness | ✅ Yes | Use existing data |
| Metadata % | ❌ No | Add detection to discovery script |
| Criticality | ❌ No | Add scoring logic (layer-based recommended) |
| Used % | ❌ No | Add import tracking OR remove field |

---

## Conclusion

**Immediate Action Required**: Implement Phase 1 (LOC and Schema Strictness fixes)  
**Strategic Decision Required**: Define Metadata, Criticality, and Used % metrics  
**Long-term Goal**: Zero hardcoded values, all metrics calculated from real agent data

**Estimated Total Effort**: 
- Phase 1: 2 hours
- Phase 2: 2 hours (meetings + documentation)  
- Phase 3: 6 hours (implementation + testing)
- **Total: ~10 hours** for complete remediation

**ROI**: High - Dashboard becomes trusted source of truth for agent health metrics
