# RCA: Why Existing Tests Didn't Catch Health/Code Quality Bug

## The Bug

**File:** `js/renderers/table-renderer.js`
- **Line 247:** `const healthColor = getWorstCaseColor(row['Code Quality Score'] || 0);`
- **Line 292:** Displayed `row['Code Quality Score']` instead of `row['Health']`

**Impact:** Table 1 "Health" column showed Code Quality Score (97.7%) instead of actual Health (78.5%)

---

## Why Existing Tests Didn't Catch It

### 1. **E2E Tests Only Validate Data Files, Not Rendered Output**

**Current Test Coverage:**
- ✅ `test_dashboard_end_to_end.py` validates `dashboard_data.js` contains correct values
- ✅ Verifies Health = 78.5 and Code Quality Score = 97.7 in the **data file**
- ❌ **Does NOT validate what's actually rendered in the browser**

**The Gap:**
```python
# Current test (test_dashboard_end_to_end.py):
total_row = next((r for r in dashboard_data if r['Territory'] == 'TOTAL'), None)
assert total_row['Health'] == 78.5  # ✅ Passes (data is correct)
assert total_row['Code Quality Score'] == 97.7  # ✅ Passes (data is correct)

# Missing test:
# Verify the HTML/JS actually DISPLAYS row['Health'] in the Health column
# Not row['Code Quality Score']
```

**Root Cause:** Tests validate **data integrity** but not **rendering integrity**.

---

### 2. **No JavaScript Execution in Python Tests**

**Current Approach:**
- Python-based E2E tests parse HTML/JS as **text files**
- Extract `dashboardData` JSON and validate values
- **Never execute JavaScript** to see what's actually rendered

**The Gap:**
```python
# Current test extracts data from JS:
data_match = re.search(r'const dashboardData = (\[.*?\]);', html_content, re.DOTALL)
dashboard_data = json.loads(data_match.group(1))

# But doesn't verify the JS code that USES this data:
# ❌ No check that renderTerritorySummaryTable() uses row['Health']
# ❌ No check that it doesn't accidentally use row['Code Quality Score']
```

**Root Cause:** Tests assume if data is correct, rendering is correct.

---

### 3. **Playwright Visual Tests Don't Validate Column Values**

**Current Playwright Tests:**
- ✅ Verify tables exist
- ✅ Verify scrollbars work
- ✅ Take screenshots
- ❌ **Don't extract and validate cell values**

**The Gap:**
```python
# Current Playwright test:
page.wait_for_selector('#kpiGrid')  # ✅ Table exists

# Missing:
# health_cell = page.locator('tr:has-text("TOTAL") td:nth-child(8)').text_content()
# assert health_cell == "78.5%"  # Would have caught the bug
```

**Root Cause:** Visual tests verify **structure** but not **content accuracy**.

---

### 4. **No Column-to-Data Mapping Validation**

**Current Tests:**
- Validate data file has correct values
- Validate HTML has table headers
- **Don't validate that column N displays field X**

**The Gap:**
```
Table 1 Header:    | Territory | Total | Heal Cap % | ... | Health |
Expected Data:     | TOTAL     | 265   | 100.0      | ... | 78.5   |
Actual Rendered:   | TOTAL     | 265   | 100.0      | ... | 97.7   | ❌

No test validates: "Column 8 should display row['Health'], not row['Code Quality Score']"
```

**Root Cause:** No explicit column-to-field mapping validation.

---

### 5. **Test 20B (Health Score Weighted Average) Only Checks Data File**

**Current Test 20B:**
```python
# Verifies dashboard_data.js has correct health calculation
expected_health = calc_health_score(heal_cap, invocation, test, 50.0, complexity, is_l0=False)
actual_health = total_row.get(COL_HEALTH, 0)
assert abs(actual_health - expected_health) < 0.5  # ✅ Passes
```

**The Gap:**
- Validates the **data file** has correct health score
- Doesn't validate the **browser** displays that health score
- Bug was in **rendering**, not calculation

**Root Cause:** Test validates data generation, not data presentation.

---

## Testing Gaps Summary

| Test Type | What It Validates | What It Misses |
|-----------|-------------------|----------------|
| E2E Python Tests | Data file correctness | Browser rendering |
| Playwright Visual | Table structure exists | Cell value accuracy |
| SSOT Enforcement | Calculation formulas | JS uses correct fields |
| Health Score Test | Weighted average calc | Displayed in correct column |

---

## Recommended Additional Testing

### **Test 1: Column Value Extraction (Playwright)**

**Purpose:** Validate rendered cell values match data file

```python
def test_table1_health_column_accuracy(page):
    """Verify Table 1 Health column displays row['Health'], not Code Quality Score."""
    page.goto('http://localhost:8765/autonomy_dashboard.html')
    page.wait_for_selector('#kpiGrid')
    
    # Extract TOTAL row Health value from rendered table
    health_cell = page.locator('table:has-text("Territory Summary") tr:has-text("TOTAL") td:nth-last-child(1)').text_content()
    health_value = float(health_cell.strip().replace('%', ''))
    
    # Load expected value from data file
    with open('data/dashboard_data.js') as f:
        data = parse_dashboard_data(f.read())
        expected_health = data[0]['Health']  # TOTAL row
        expected_quality = data[0]['Code Quality Score']
    
    # Verify Health column shows Health, not Code Quality
    assert abs(health_value - expected_health) < 0.1, \
        f"Health column shows {health_value}, expected {expected_health}"
    assert abs(health_value - expected_quality) > 1.0, \
        f"Health column shows Code Quality Score ({expected_quality})!"
```

**What It Catches:** Rendering bugs where wrong field is displayed

---

### **Test 2: Column-to-Field Mapping Validation**

**Purpose:** Verify each column displays the correct data field

```python
def test_table1_column_mapping():
    """Verify Table 1 columns display correct data fields."""
    
    column_mappings = [
        (1, 'Territory'),
        (2, 'Total'),
        (3, 'Heal Cap %'),
        (4, 'Invocation %'),
        (5, 'MCP Hardened %'),
        (6, 'Test %'),
        (7, 'Complexity Health %'),
        (8, 'Health'),  # ← This is what caught the bug
    ]
    
    # Parse JS rendering code
    with open('js/renderers/table-renderer.js') as f:
        js_code = f.read()
    
    # Verify each column renders the correct field
    for col_num, field_name in column_mappings:
        # Check that column N uses row[field_name]
        pattern = rf"<td[^>]*>.*?row\['{field_name}'\].*?</td>"
        assert re.search(pattern, js_code, re.DOTALL), \
            f"Column {col_num} doesn't render row['{field_name}']"
```

**What It Catches:** Copy-paste errors where column uses wrong field

---

### **Test 3: Cross-Table Value Uniqueness**

**Purpose:** Verify Table 1 and Table 2 don't show identical values

```python
def test_health_vs_code_quality_different():
    """Verify Health and Code Quality Score are different values."""
    
    # Load dashboard data
    with open('data/dashboard_data.js') as f:
        data = parse_dashboard_data(f.read())
    
    for row in data:
        health = row.get('Health')
        code_quality = row.get('Code Quality Score')
        
        if health is not None and code_quality is not None:
            # They should be different (unless by coincidence)
            if abs(health - code_quality) < 0.1:
                # If they're the same, verify it's intentional
                # (e.g., both happen to be 100.0)
                assert health == 100.0 and code_quality == 100.0, \
                    f"{row['Territory']}: Health ({health}) suspiciously equals Code Quality ({code_quality})"
```

**What It Catches:** Rendering bugs where same value appears in multiple columns

---

### **Test 4: JavaScript Static Analysis**

**Purpose:** Detect copy-paste errors in JS rendering code

```python
def test_js_rendering_no_field_confusion():
    """Verify JS doesn't use wrong fields in table rendering."""
    
    with open('js/renderers/table-renderer.js') as f:
        js_code = f.read()
    
    # Find renderTerritorySummaryTable function
    table1_start = js_code.find('function renderTerritorySummaryTable')
    table1_end = js_code.find('function renderCodeQualityTable', table1_start)
    table1_code = js_code[table1_start:table1_end]
    
    # Table 1 should NOT reference Code Quality Score
    assert "row['Code Quality Score']" not in table1_code, \
        "Table 1 rendering uses 'Code Quality Score' field (should use 'Health')"
    
    # Table 1 MUST reference Health
    assert "row['Health']" in table1_code, \
        "Table 1 rendering doesn't use 'Health' field"
```

**What It Catches:** Wrong field references in rendering code

---

### **Test 5: End-to-End Rendered Value Validation (Playwright)**

**Purpose:** Full integration test of data → rendering → display

```python
def test_e2e_rendered_values_match_data(page):
    """Verify all rendered table values match dashboard_data.js."""
    
    page.goto('http://localhost:8765/autonomy_dashboard.html')
    page.wait_for_selector('#kpiGrid')
    
    # Load expected data
    with open('data/dashboard_data.js') as f:
        expected_data = parse_dashboard_data(f.read())
        total_row = next(r for r in expected_data if r['Territory'] == 'TOTAL')
    
    # Extract rendered values from Table 1
    rendered_values = {
        'Health': extract_cell_value(page, 'table:has-text("Territory Summary")', 'TOTAL', 8),
        'Complexity Health %': extract_cell_value(page, 'table:has-text("Territory Summary")', 'TOTAL', 7),
        'Test %': extract_cell_value(page, 'table:has-text("Territory Summary")', 'TOTAL', 6),
    }
    
    # Verify rendered values match data file
    for field, rendered_value in rendered_values.items():
        expected_value = total_row[field]
        assert abs(rendered_value - expected_value) < 0.1, \
            f"{field}: rendered {rendered_value}, expected {expected_value}"
```

**What It Catches:** Any mismatch between data file and rendered output

---

## Implementation Priority

### **High Priority (Implement Immediately)**

1. **Test 1: Column Value Extraction (Playwright)** ← Would have caught this bug
2. **Test 4: JavaScript Static Analysis** ← Fast, catches copy-paste errors
3. **Test 3: Cross-Table Value Uniqueness** ← Catches suspicious duplicates

### **Medium Priority**

4. **Test 2: Column-to-Field Mapping Validation** ← Comprehensive but complex
5. **Test 5: E2E Rendered Value Validation** ← Full integration test

---

## Root Cause Summary

**Why tests didn't catch it:**
1. ❌ Tests validate **data files**, not **rendered output**
2. ❌ No JavaScript execution in Python tests
3. ❌ Playwright tests check **structure**, not **content**
4. ❌ No column-to-field mapping validation
5. ❌ Assumed correct data = correct rendering

**Fix:**
- Add Playwright tests that extract and validate cell values
- Add JS static analysis to detect field confusion
- Add cross-table uniqueness checks
- Test the **full path**: data → JS → rendering → browser display
