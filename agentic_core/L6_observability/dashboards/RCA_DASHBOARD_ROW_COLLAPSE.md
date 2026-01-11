# RCA: Dashboard Row Collapse & Health Score Investigation

**Date:** 2026-01-10  
**Status:** ✅ RESOLVED

---

## Executive Summary

Investigated why dashboard rows were collapsing from expected 29 rows to fewer, and analyzed health score calculation formula. Implemented comprehensive guardrails to prevent future deviations.

---

## Root Cause Analysis

### Issue 1: Row Collapse

**Symptom:** Dashboard was generating fewer than 29 rows (TOTAL + 28 territories)

**Root Cause:**
- Generator only created rows for territories that had agents
- Territories with 0 agents were skipped entirely
- This violated the frozen wireframe requirement of exactly 29 rows

**Location:** `generate_dashboard.py` lines 340-373

**Fix Applied:**
```python
# Now creates empty rows for territories with no agents
if territory_name in territories and len(territories[territory_name]) > 0:
    # Territory has agents - compute real metrics
    ...
else:
    # Territory has no agents - create empty row to maintain wireframe
    empty_metrics = {...}
    row = self.build_territory_row(territory_name, empty_metrics, ...)
    rows.append(row)
```

**Result:** Dashboard now ALWAYS generates exactly 29 rows

---

### Issue 2: Health Score Formula Mismatch

**Symptom:** Health Breakdown showed 5 components but Health calculation only used 3

**Original Formula (INCORRECT):**
```python
# Line 241 (old)
health = round((test_pct + heal_inv_pct + obs_pct) / 3, 1)
```

**Health Breakdown String:**
```
"Heal:{heal_cap}+Inv:{heal_inv}+Test:{test}+Obs:{obs}+CC:{complexity}"
```

**Mismatch:**
- Breakdown showed: Heal Cap %, Heal Invocation %, Test %, Observable %, Complexity Health (5 components)
- Formula used: Test %, Heal Invocation %, Observable % (3 components only)
- Missing: Heal Cap %, Complexity Health

**Fix Applied:**
```python
# Line 242 (new)
# Health is weighted average of 5 components as shown in Health Breakdown
health = round((heal_cap_pct + heal_inv_pct + test_pct + obs_pct + complexity_health) / 5, 1)
```

**Impact:**
- Health score changed from 82.3% → 77.0% (more accurate)
- Now properly includes all 5 components shown in breakdown
- Formula matches the displayed breakdown string

---

### Issue 3: TOTAL Row Calculation with L6 Observability

**Investigation:** Are L6 Observability rows included in TOTAL calculation?

**Findings:**
- L6 Observability has 4 territories: Metrics, Telemetry, Tracing, Compliance
- All 4 territories currently have 0 agents (empty rows)
- TOTAL calculation uses weighted average: `sum(territory_health * territory_agents) / total_agents`
- Empty territories (0 agents) contribute 0 to the weighted sum
- **Conclusion:** L6 rows ARE included in calculation, but have no impact when empty

**Verification:**
```
Manual calculation: 77.0%
Dashboard value: 77.0%
Match: ✅ YES
```

**TOTAL row calculation is CORRECT**

---

## Guardrails Implemented

### GUARDRAIL 1: Row Count Enforcement
```python
# Enforce exactly 29 rows (TOTAL + 28 territories)
expected_row_count = len(TERRITORY_ORDER) + 1
if len(data) != expected_row_count:
    print("❌ GUARDRAIL VIOLATION: Row count mismatch")
    return False
```

**Prevents:** Row collapse, missing territories, extra rows

---

### GUARDRAIL 2: TOTAL Row Position
```python
# TOTAL row must be first
if data[0].get("Territory") != "TOTAL":
    print("❌ GUARDRAIL VIOLATION: TOTAL row must be first")
    return False
```

**Prevents:** TOTAL row appearing in wrong position

---

### GUARDRAIL 3: Required Fields
```python
# All rows must have all required fields
for i, row in enumerate(data):
    missing_fields = [f for f in REQUIRED_FIELDS if f not in row]
    if missing_fields:
        print(f"❌ GUARDRAIL VIOLATION: Row {i} missing fields: {missing_fields}")
        return False
```

**Prevents:** Missing fields, incomplete rows

---

### GUARDRAIL 4: Territory Order
```python
# Territory order must match FIXED structure exactly
for i, row in enumerate(territory_rows):
    expected = TERRITORY_ORDER[i]
    actual = row.get("Territory")
    if actual != expected:
        print("❌ GUARDRAIL VIOLATION: Territory order mismatch")
        return False
```

**Prevents:** Territory order deviation, scrambled wireframe

---

### GUARDRAIL 5: Health Formula Consistency
```python
# Verify health formula consistency
for row in data[1:]:
    if row.get('Total', 0) > 0:
        expected_health = round((heal_cap + heal_inv + test + obs + complexity) / 5, 1)
        if abs(health - expected_health) > 0.2:
            print("⚠️  WARNING: Health formula mismatch")
```

**Prevents:** Health calculation drift, formula inconsistency

---

## Current Dashboard State

**Rows:** 29 (✅ CORRECT)
- 1 TOTAL row
- 28 territory rows (18 non-empty, 10 empty)

**Empty Territories:**
- L4 State/Specialized
- L3 Orchestration/Infrastructure
- L3 Orchestration/Specialized
- L2 Execution/Specialized
- L1 Cognition/Specialized
- L0 Maintenance/Infrastructure
- L6_Observability/Metrics
- L6_Observability/Telemetry
- L6_Observability/Tracing
- L6_Observability/Compliance

**Health Score:** 77.0%
- Formula: (Heal Cap + Heal Inv + Test + Obs + Complexity Health) / 5
- Components: 100 + 85 + 62 + 100 + 38 = 385 / 5 = 77.0%
- ✅ Matches Health Breakdown string

**TOTAL Calculation:** ✅ CORRECT
- Weighted average by agent count
- L6 rows included but have no impact (0 agents)

---

## Testing

All 6 tests passing:
1. ✅ Wireframe Consistency - 29 rows with all required fields
2. ✅ Territory Order - 28 detailed territories validated
3. ✅ Data Consistency - 291 agents, 100.0% heal cap
4. ✅ Field Types - All correct
5. ✅ Regeneration Stability - Always produces 29 rows
6. ✅ HTML Rendering Elements - All present

---

## Prevention Measures

1. **Generator always creates 29 rows** - Empty rows for missing territories
2. **5 strict guardrails** - Validate row count, order, fields, and health formula
3. **Test suite validates frozen wireframe** - Prevents any deviation
4. **Documentation updated** - README.md reflects frozen 29-row structure

---

## Lessons Learned

1. **Wireframe must be frozen** - Never skip rows, even if empty
2. **Formula must match display** - Health breakdown must reflect actual calculation
3. **Guardrails are essential** - Prevent silent failures and drift
4. **Weighted averages work correctly** - Empty rows (0 agents) don't break TOTAL calculation
5. **Testing is mandatory** - All 6 tests must pass before commit

---

## Files Modified

- `generate_dashboard.py` - Fixed health formula, added guardrails, always create 29 rows
- `test_dashboard.py` - Validates frozen 29-row wireframe
- `README.md` - Documents frozen structure
- `autonomy_dashboard.html` - Regenerated with correct health scores

---

## Status: ✅ RESOLVED

All issues identified and fixed. Guardrails in place to prevent recurrence.
