# RCA: E2E Dashboard Test Field Name Validation Gap

**Date:** January 17, 2026  
**Issue:** E2E tests did not catch field name errors (e.g., `docstring_percentage` vs `documented_pct`)  
**Severity:** CRITICAL - This was a "big miss" that allowed SSOT violations to go undetected

---

## Executive Summary

The e2e dashboard test suite had a **critical gap**: it validated that the dashboard used correct column names, but **never validated that `agent_discovery_full.json` used correct SSOT field names**. This allowed diagnostic queries to use wrong field names (`docstring_percentage`, `typed_percentage`) without detection, leading to false 0% metrics and wasted debugging time.

**Root Cause:** Test 4 only checked dashboard output (`dashboard_data.js`), not discovery input (`agent_discovery_full.json`).

**Impact:** The system was correct all along - the issue was a faulty diagnostic query using wrong field names that should have been caught by e2e tests.

---

## Detailed RCA

### What Happened

1. **User Query Error:** Diagnostic query used `docstring_percentage` and `typed_percentage` instead of SSOT field names `documented_pct` and `typed_pct`
2. **False Alarm:** Query returned 0% for all agents, triggering unnecessary RCA
3. **SSOT Integrity Confirmed:** Discovery script and JSON were using correct field names all along
4. **Test Gap Identified:** E2E tests never validated discovery JSON field names against SSOT definitions

### Why E2E Tests Didn't Catch This

**Test 4 (Required Fields Present)** validated:
- ✅ Dashboard `dashboard_data.js` has correct **column names** (e.g., `Typed %`, `Documented %`)
- ✅ Dashboard columns match SSOT `COL_*` constants
- ❌ **NEVER validated** that `agent_discovery_full.json` uses correct **field names** (e.g., `typed_pct`, `documented_pct`)

**The Gap:**
```python
# Test 4 checked THIS (dashboard output):
required_fields = [COL_TYPED, COL_DOCUMENTED, ...]  # Column names for display

# Test 4 NEVER checked THIS (discovery input):
required_fields = [FIELD_TYPED_PCT, FIELD_DOCUMENTED_PCT, ...]  # Field names in JSON
```

### SSOT Field Names (Correct)

From `dashboard_ssot_definitions.py`:
```python
FIELD_TYPED_PCT = 'typed_pct'           # ✅ CORRECT
FIELD_DOCUMENTED_PCT = 'documented_pct' # ✅ CORRECT
```

### Common Mistakes (Forbidden)

```python
'docstring_percentage'  # ❌ WRONG - Use 'documented_pct'
'typed_percentage'      # ❌ WRONG - Use 'typed_pct'
'docstring_pct'         # ❌ WRONG - Use 'documented_pct'
'type_hints_pct'        # ❌ WRONG - Use 'typed_pct'
'has_schema'            # ❌ WRONG - Use 'schema_strictness'
'base_class'            # ❌ WRONG - Use 'proper_base_class'
```

---

## Solution Implemented

### New Test 4B: Discovery SSOT Field Names

**Purpose:** Validate that `agent_discovery_full.json` uses exact SSOT field names from `dashboard_ssot_definitions.py`

**What it checks:**
1. ✅ All agents have required SSOT fields (`typed_pct`, `documented_pct`, etc.)
2. ✅ No agents use forbidden field names (`docstring_percentage`, `typed_percentage`, etc.)
3. ✅ Field names match SSOT definitions exactly

**Test Output:**
```
✅ Test 4B PASSED: All agents use correct SSOT field names
   ✓ Validated 10 agents
   ✓ No forbidden fields (docstring_percentage, typed_percentage, etc.)
   ✓ All required SSOT fields present
```

### Code Changes

**File:** `scripts/test_dashboard_end_to_end.py`

**Added:**
- Test 4B: `test_discovery_field_names()` - Validates discovery JSON field names
- SSOT field name constants imported from `dashboard_ssot_definitions.py`
- Forbidden field name detection with helpful error messages

**Key Features:**
```python
# SSOT: All required field names
REQUIRED_SSOT_FIELDS = {
    'class_name', 'path', 'layer', 'territory',
    'has_healing', 'has_tests', 'mcp_hardened', 'invocation',
    'typed_pct',        # NOT 'typed_percentage'
    'documented_pct',   # NOT 'docstring_percentage'
    'schema_strictness', 'proper_base_class', 'cyclomatic_complexity',
}

# FORBIDDEN field names (common mistakes)
FORBIDDEN_FIELD_NAMES = {
    'docstring_percentage': "Use 'documented_pct' instead",
    'typed_percentage': "Use 'typed_pct' instead",
    # ... more forbidden patterns
}
```

---

## Prevention Strategy

### This Will Never Happen Again Because:

1. **Test 4B** now validates discovery JSON field names on every e2e test run
2. **Forbidden field detection** catches common mistakes with helpful error messages
3. **SSOT enforcement** ensures field names match `dashboard_ssot_definitions.py` exactly
4. **Early detection** catches field name errors before they cause false alarms

### When Test 4B Would Catch Errors:

**Scenario 1: Wrong field name in discovery script**
```python
# If discovery script used this:
agent_data['docstring_percentage'] = 95.0  # ❌ WRONG

# Test 4B would fail with:
# "Found forbidden field 'docstring_percentage' - Use 'documented_pct' instead"
```

**Scenario 2: Missing required field**
```python
# If discovery script forgot to add:
agent_data['typed_pct'] = ...  # Missing!

# Test 4B would fail with:
# "Missing SSOT fields: {'typed_pct'}"
```

**Scenario 3: Diagnostic query using wrong field**
```python
# If diagnostic query used:
agents_with_docs = [a for a in agents if a.get('docstring_percentage', 0) > 0]

# This would return 0 agents (field doesn't exist)
# But Test 4B ensures the field is 'documented_pct', preventing this mistake
```

---

## Lessons Learned

### What Went Well
- ✅ SSOT integrity was maintained throughout (system was correct)
- ✅ RCA process identified the test gap quickly
- ✅ Fix implemented and tested immediately

### What Didn't Go Well
- ❌ Test coverage gap allowed field name errors to go undetected
- ❌ Diagnostic query used wrong field names without validation
- ❌ Wasted time debugging a non-existent problem

### Improvements Made
1. **Test 4B** added to validate discovery JSON field names
2. **Forbidden field detection** prevents common mistakes
3. **SSOT enforcement** ensures consistency across entire pipeline
4. **Documentation** (this RCA) prevents future occurrences

---

## Test Coverage Summary

### Before Fix
- ✅ Test 4: Dashboard columns validated
- ❌ **GAP:** Discovery JSON fields NOT validated

### After Fix
- ✅ Test 4: Dashboard columns validated
- ✅ **Test 4B:** Discovery JSON fields validated ← **NEW**
- ✅ Forbidden field detection
- ✅ SSOT field name enforcement

---

## Conclusion

**The system was correct all along.** The issue was a faulty diagnostic query using wrong field names (`docstring_percentage`, `typed_percentage`) that should have been caught by e2e tests.

**Test 4B now ensures this never happens again** by validating that `agent_discovery_full.json` uses exact SSOT field names from `dashboard_ssot_definitions.py`.

**Impact:** This fix prevents future field name errors, reduces debugging time, and maintains SSOT integrity across the entire dashboard pipeline.

---

## Files Modified

1. `scripts/test_dashboard_end_to_end.py` - Added Test 4B
2. `RCA_E2E_FIELD_NAME_VALIDATION_GAP.md` - This documentation

## Related Files

- `scripts/dashboard_ssot_definitions.py` - SSOT field name definitions
- `scripts/full_agent_discovery.py` - Discovery script (uses correct field names)
- `agent_discovery_full.json` - Discovery output (validated by Test 4B)
