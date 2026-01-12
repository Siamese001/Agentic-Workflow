# Dashboard Footnote Maintenance

## Overview

Footnotes in the dashboard provide detailed explanations of metrics and formulas. They must be kept synchronized with actual calculation logic to prevent user confusion.

---

## Current Footnotes

### Table 1 (Territory Summary)

**1. Health**
```
Gospel-weighted composite score (0-100): 
  Heal Capability (30%) + 
  Invocation (10%) + 
  Test Coverage (25%) + 
  Observability (20%) + 
  Complexity Health (15%)

Prioritizes autonomy and testing over complexity.
L5 security violation = 0%.
```

**Formula Location:** `generate_dashboard.py` lines 283-290

**2. Heal Capability %**
```
Percentage of agents with self-healing capability (has_healing=True).
Core autonomy metric.
```

**3. Test Coverage %**
```
Percentage of agents with test files.
Primary defense against regression.
```

**4. Observability %**
```
Percentage of agents with MCP logging/observability.
Prevents "Ghost Agents".
```

**5. Complexity Health**
```
Inverted cyclomatic complexity: 100 - (Avg CC * 2).
Lower complexity = higher health.
```

### Table 2 (Code Quality)

**1. Code Quality Score**
```
Simple average: (Typed % + Documented %) / 2
Overall code hygiene and documentation quality.
```

**Formula Location:** `generate_dashboard.py` line 274

**2. Typed %**
```
Percentage of code with type hints.
Enables static analysis and IDE support.
```

**3. Documented %**
```
Percentage of code with docstrings.
Improves maintainability and onboarding.
```

**4. Schema Strictness %**
```
Currently mirrors Typed % (placeholder).
Future: Pydantic/schema validation coverage.
```

---

## Recently Updated Footnotes

### ✅ Fixed: Code Quality Score (Jan 2026)

**Old (Stale):**
```
Weighted composite: Typed (35%) + Schema (30%) + Metadata (15%) + Documented (20%)
```

**New (Accurate):**
```
Simple average: (Typed % + Documented %) / 2
```

**Why:** Formula was simplified but footnote wasn't updated, causing confusion.

---

### ✅ Fixed: Health Score (Jan 2026)

**Old (Stale):**
```
Average of five key metrics: Heal Capability %, Heal Invocation %, 
Test Coverage %, Observability %, and Complexity Health.
```

**New (Accurate):**
```
Gospel-weighted composite: Heal Capability (30%) + Invocation (10%) + 
Test Coverage (25%) + Observability (20%) + Complexity Health (15%).
L5 security violation = 0%.
```

**Why:** Switched from even weighting (20% each) to Gospel-weighted formula.

---

## Validation Process

### Test 13: Footnote Accuracy

**Location:** `test_dashboard_end_to_end.py`

**Checks:**
1. Health footnote mentions "Gospel-weighted" or "30%"
2. Code Quality Score footnote shows simple average, not old weighted formula
3. No stale percentage patterns (35%, 30%, 15% from old formula)

**Usage:**
```bash
python scripts/test_dashboard_end_to_end.py
```

**Expected Output:**
```
──────────────────────────────────────────────────────────────────────
Running: Footnote Accuracy Check
──────────────────────────────────────────────────────────────────────
   ✅ Health footnote updated to weighted formula
   ✅ Code Quality Score footnote updated to simple average
✅ Test 13 PASSED: All footnotes accurate and up-to-date
```

---

## Maintenance Checklist

When changing a formula in `generate_dashboard.py`:

- [ ] **1. Update the calculation code**
- [ ] **2. Update the Health Breakdown display** (if applicable)
- [ ] **3. Find the corresponding footnote in `autonomy_dashboard.html`**
- [ ] **4. Update the footnote text to match new formula**
- [ ] **5. Update Test 13 validation** (if new formula pattern)
- [ ] **6. Run E2E test suite** to verify footnote accuracy
- [ ] **7. Document the change** in this file

---

## Common Footnote Locations

**In `autonomy_dashboard.html`:**

```html
<!-- Metric Definitions Section -->
<div class="metric-definitions">
    <h3>📊 Metric Definitions</h3>
    <div class="definitions-grid">
        <div class="definition-item">
            <strong>Health:</strong> Gospel-weighted composite...
        </div>
        <div class="definition-item">
            <strong>Code Quality Score:</strong> Simple average...
        </div>
    </div>
</div>
```

**Search Pattern:**
```bash
# Find all footnotes
Select-String -Path "autonomy_dashboard.html" -Pattern "<strong>.*:</strong>" -Context 0,2

# Find specific metric footnote
Select-String -Path "autonomy_dashboard.html" -Pattern "strong>Health" -Context 0,3
```

---

## Stale Footnote Detection

### Red Flags

1. **Percentage weights that don't match code**
   - Example: Footnote says "30%" but code uses 0.25

2. **Formula descriptions that don't match implementation**
   - Example: "Weighted composite" but code uses simple average

3. **Missing new features**
   - Example: L5 zero-multiplier not mentioned in Health footnote

4. **Outdated terminology**
   - Example: "Equal weight" when now using Gospel-weighted

### Automated Detection

Test 13 checks for:
- Stale patterns: `35%.*Schema.*30%`, `Typed.*35%`, `Metadata.*15%`
- Missing patterns: `Gospel-weighted`, `30%`, `Simple average`
- Inconsistent formulas: Cross-reference with `generate_dashboard.py`

---

## Formula Reference

### Current Formulas (Jan 2026)

| Metric | Formula | Location |
|--------|---------|----------|
| **Health** | `(heal*0.30 + inv*0.10 + test*0.25 + obs*0.20 + cc*0.15)` | `generate_dashboard.py:283-290` |
| **Code Quality** | `(typed + documented) / 2` | `generate_dashboard.py:274` |
| **Complexity Health** | `max(0, 100 - (avg_cc * 2))` | `generate_dashboard.py:273` |
| **Heal Cap %** | `(agents_with_healing / total) * 100` | `generate_dashboard.py:260` |
| **Test %** | `(agents_with_tests / total) * 100` | `generate_dashboard.py:262` |

---

## Integration with E2E Pipeline

### Dashboard E2E Pipeline

```
Step 0: Data Validation
Step 1-2: Fix code issues
Step 3: Regenerate Dashboard
  ├─ Updates formulas
  └─ ⚠️ Footnotes may become stale
Step 4: Run Tests (13 total)
  ├─ Tests 1-12: Data validation
  └─ Test 13: Footnote accuracy ⭐
Step 5: Visual Confirmation
```

**If Test 13 fails:**
1. Identify which footnote is stale
2. Update footnote in `autonomy_dashboard.html`
3. Re-run Test 13 to verify
4. Commit both formula change AND footnote update together

---

## Best Practices

### DO:
✅ Update footnotes immediately when changing formulas
✅ Use exact percentages from code (e.g., 30%, not "about 30%")
✅ Mention special cases (e.g., L5 zero-multiplier)
✅ Keep factory analogies consistent with formula intent
✅ Run Test 13 after any formula change

### DON'T:
❌ Leave footnotes with old formula descriptions
❌ Use vague terms like "weighted" without specifying weights
❌ Forget to update Health Breakdown display format
❌ Skip Test 13 validation
❌ Commit formula changes without footnote updates

---

## Future Enhancements

1. **Auto-generate footnotes from code**
   - Parse formulas from `generate_dashboard.py`
   - Generate footnote text automatically
   - Eliminate manual sync issues

2. **Footnote version tracking**
   - Add `data-formula-version` attribute
   - Track when formula last changed
   - Flag stale footnotes automatically

3. **Formula documentation in code**
   - Add docstrings with formula explanations
   - Use same text in code and footnotes
   - Single source of truth

---

## Commands

```bash
# Find all footnotes in dashboard
Select-String -Path "agentic_core/L6_observability/dashboards/autonomy_dashboard.html" -Pattern "<strong>.*:</strong>" -Context 0,2

# Validate footnote accuracy
python scripts/test_dashboard_end_to_end.py

# Regenerate dashboard (may require footnote updates)
python agentic_core/L6_observability/dashboards/generate_dashboard.py

# Run full pipeline
python scripts/dashboard_e2e_pipeline_fast.py
```

---

**Status:** ✅ **FOOTNOTES UPDATED AND VALIDATED**

All footnotes now accurately reflect current formulas. Test 13 ensures ongoing accuracy as part of E2E validation.
