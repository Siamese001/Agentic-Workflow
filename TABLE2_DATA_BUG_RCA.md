# Table 2 Data Bug - Root Cause Analysis

**Date:** January 12, 2026  
**Issue:** Proper Base % shows 100.0% for many rows when actual agents have 0%  
**Severity:** 🔴 **CRITICAL - Data Integrity Violation**

---

## **Problem Statement**

Dashboard Table 2 (Code Quality) displays **Proper Base % = 100.0%** for territories where **0% of agents** have proper base class inheritance.

**Example:**
- Territory has 10 agents
- 0 agents have `proper_base_class=True`
- Expected: Proper Base % = 0.0%
- **Actual: Proper Base % = 100.0%** ❌

---

## **Root Cause Analysis**

### **Discovery Data Reality:**
```
Total agents: 284
Agents with proper_base_class=True: 88 (31.0%)
Agents with proper_base_class=False: 196 (69.0%)
```

**69% of agents are missing proper base class inheritance!**

### **Bug Location 1: TOTAL Row (Line 259)**

`@C:/Git/Agentic-Workflow/agentic_core/L6_observability/dashboards/generate_dashboard.py:259`

```python
"Proper Base %": 100.0,  # ❌ HARDCODED - WRONG!
```

**Should be:**
```python
"Proper Base %": metrics["proper_base_pct"],  # Calculated from actual data
```

### **Bug Location 2: Territory Aggregation (Line 300)**

`@C:/Git/Agentic-Workflow/agentic_core/L6_observability/dashboards/generate_dashboard.py:300`

```python
"Proper Base %": 100.0,  # ❌ HARDCODED - WRONG!
```

**Should be:**
```python
"Proper Base %": weighted_avg("Proper Base %"),  # From territory rows
```

### **Correct Calculation (Lines 390-391)**

The **per-agent calculation is correct**:
```python
base = 100.0 if agent.get('proper_base_class') else 0.0
base_values.append(base)
```

But this is **never aggregated** into territory metrics!

---

## **Why This Bug Exists**

1. **`compute_territory_metrics()` doesn't calculate `proper_base_pct`**
   - Line 387-391 collects `base_values` for per-agent data
   - But never computes `metrics["proper_base_pct"] = avg(base_values)`

2. **`build_territory_row()` hardcodes 100.0**
   - Line 259 assumes all agents have proper base class
   - Ignores actual data

3. **`build_total_row()` hardcodes 100.0**
   - Line 300 doesn't aggregate from territory rows
   - Ignores weighted average

---

## **Impact**

### **Data Integrity:**
- **100% of Table 2 "Proper Base %" data is WRONG**
- Dashboard shows false compliance
- Masks architectural debt (196 agents missing base inheritance)

### **Testing Gap:**
- E2E Test 12 only checks if fields exist and values are 0-100
- **Does NOT validate data accuracy**
- **Does NOT cross-check with agent_discovery_full.json**

---

## **The Fix**

### **Step 1: Add proper_base_pct to compute_territory_metrics()**

After line 391, add:
```python
# Calculate proper base percentage
proper_base_pct = (sum(base_values) / len(base_values)) if base_values else 0.0
```

Add to metrics dict:
```python
"proper_base_pct": proper_base_pct,
```

### **Step 2: Fix build_territory_row() line 259**

Change:
```python
"Proper Base %": 100.0,
```

To:
```python
"Proper Base %": metrics["proper_base_pct"],
```

### **Step 3: Fix build_total_row() line 300**

Change:
```python
"Proper Base %": 100.0,
```

To:
```python
"Proper Base %": weighted_avg("Proper Base %"),
```

---

## **Enhanced E2E Testing Required**

Current Test 12 is insufficient. Need to add:

### **Test 12A: Table 2 Data Accuracy**
```python
# Cross-validate dashboard data with agent_discovery_full.json
agents = json.load(open('agent_discovery_full.json'))
proper_base_true = [a for a in agents if a.get('proper_base_class', False)]
expected_pct = len(proper_base_true) / len(agents) * 100

dashboard_proper_base = total_row.get('Proper Base %', 0)
tolerance = 1.0  # Allow 1% variance

if abs(dashboard_proper_base - expected_pct) > tolerance:
    errors.append(f"Proper Base % mismatch: Expected {expected_pct:.1f}%, Got {dashboard_proper_base:.1f}%")
```

### **Test 12B: Territory-Level Validation**
```python
# Verify each territory's Proper Base % matches its agents
for territory_row in dashboard_data[1:]:  # Skip TOTAL
    territory_name = territory_row.get('Territory')
    territory_agents = [a for a in agents if a.get('territory') == territory_name]
    
    if territory_agents:
        proper_base_count = sum(1 for a in territory_agents if a.get('proper_base_class', False))
        expected_pct = (proper_base_count / len(territory_agents)) * 100
        actual_pct = territory_row.get('Proper Base %', 0)
        
        if abs(actual_pct - expected_pct) > tolerance:
            errors.append(f"{territory_name}: Expected {expected_pct:.1f}%, Got {actual_pct:.1f}%")
```

### **Test 12C: Schema Strictness Validation**
Same pattern for `Schema Strictness %` field.

---

## **Why Table 1 Testing is Better**

Table 1 tests (Tests 1-6) are rigorous because they:
1. **Cross-validate with source data** (agent_discovery_full.json)
2. **Check agent counts match**
3. **Verify percentages are calculated correctly**
4. **Validate data consistency across fields**

Table 2 tests (Test 12) only check:
1. Fields exist ✓
2. Values are 0-100 ✓
3. **NO data accuracy validation** ❌

---

## **Summary**

| Issue | Location | Current | Should Be |
|-------|----------|---------|-----------|
| Territory row | Line 259 | `100.0` (hardcoded) | `metrics["proper_base_pct"]` |
| TOTAL row | Line 300 | `100.0` (hardcoded) | `weighted_avg("Proper Base %")` |
| Metrics calc | Missing | N/A | Add `proper_base_pct` calculation |
| E2E tests | Test 12 | Existence only | Add accuracy validation |

**Expected Result After Fix:**
- TOTAL row: Proper Base % = **31.0%** (88/284 agents)
- Individual territories: Accurate percentages based on their agents
- E2E tests catch any future regressions

---

**Files to Modify:**
1. `agentic_core/L6_observability/dashboards/generate_dashboard.py` (3 changes)
2. `scripts/test_dashboard_end_to_end.py` (add Tests 12A, 12B, 12C)
