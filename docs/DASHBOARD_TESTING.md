# Dashboard Testing & Validation

## Overview

All dashboard updates are now **test-driven** with mandatory unit test validation. Dashboard generation is **blocked** if any tests fail.

## Test Suite

**Location**: `tests/test_dashboard_generation.py`

**Total Tests**: 12 comprehensive validation checks

### Test Coverage

#### 1. Template Structure Tests (Tests 1-2)
- ✅ Template file exists at correct location
- ✅ All required DOM elements present (11 elements)

#### 2. Data Injection Tests (Test 3)
- ✅ Data injection placeholders exist:
  - `dashboardData`
  - `recommendationsData`
  - `lastUpdatedStr`
  - `gaugeData`

#### 3. JavaScript Function Tests (Tests 4-5)
- ✅ All 11 required render functions defined
- ✅ `loadData()` is called on page load

#### 4. Critical Bug Prevention (Test 6)
- ✅ **Gauge rendering functions NOT called** (prevents JavaScript errors)
- ✅ Validates `renderHealthGauge()` and `renderComplianceGauge()` are not in `loadData()`

#### 5. External Dependencies (Test 7)
- ✅ Plotly.js CDN included

#### 6. Configuration Tests (Test 8)
- ✅ Auto-refresh set to 30 seconds

#### 7. Navigation Tests (Test 9)
- ✅ All 6 tabs present (Executive, Territory, Risk, Compliance, Recommendations, Interview)

#### 8. Generated Output Tests (Tests 10-11)
- ✅ Data successfully injected (not empty arrays)
- ✅ Valid JSON structure
- ✅ TOTAL row exists with required fields

#### 9. Styling Tests (Test 12)
- ✅ All CSS variables defined (9 variables)

## Running Tests

### Manual Test Execution
```bash
# Run tests directly
python tests/test_dashboard_generation.py

# Expected output: "Ran 12 tests in X.XXXs - OK"
```

### Automatic Test Execution
```bash
# Tests run automatically before dashboard generation
python gen_dashboard.py

# Output:
# 🧪 Running dashboard unit tests (mandatory)...
# ============================================================
# test_01_template_exists ... ok
# test_02_template_has_required_elements ... ok
# ... (all 12 tests)
# ============================================================
# ✅ ALL DASHBOARD TESTS PASSED
# ============================================================
# 📊 Generating autonomy compliance report and dashboard...
```

## Test Failure Behavior

If **any test fails**, dashboard generation is **blocked**:

```
❌ DASHBOARD TESTS FAILED
============================================================
⛔ Dashboard generation BLOCKED - tests must pass first.
   Fix the failing tests and try again.
```

**Exit code**: 1 (failure)

## Test-Driven Development Workflow

### 1. Making Template Changes

```bash
# 1. Edit template
vim agentic_core/L5_safety/validators/dashboard_template.html

# 2. Run tests to verify changes don't break anything
python tests/test_dashboard_generation.py

# 3. If tests pass, generate dashboard
python gen_dashboard.py
```

### 2. Adding New Features

```bash
# 1. Add test for new feature first (TDD)
vim tests/test_dashboard_generation.py

# 2. Implement feature in template
vim agentic_core/L5_safety/validators/dashboard_template.html

# 3. Run tests until they pass
python tests/test_dashboard_generation.py

# 4. Generate dashboard
python gen_dashboard.py
```

### 3. Bug Fixes

```bash
# 1. Add regression test for the bug
vim tests/test_dashboard_generation.py

# 2. Fix the bug in template
vim agentic_core/L5_safety/validators/dashboard_template.html

# 3. Verify test now passes
python tests/test_dashboard_generation.py

# 4. Generate dashboard
python gen_dashboard.py
```

## Critical Tests (Prevent Known Issues)

### Test 6: No Gauge Rendering
**Purpose**: Prevents the bug where `renderHealthGauge()` and `renderComplianceGauge()` were called but the DOM elements didn't exist, causing JavaScript errors that prevented the entire dashboard from populating.

**What it checks**:
- `renderHealthGauge(` NOT in `loadData()` function
- `renderComplianceGauge(` NOT in `loadData()` function

**Why it matters**: This was the root cause of the "nothing populated" issue. This test ensures it never happens again.

### Test 10: Data Injection Validation
**Purpose**: Ensures data is actually injected into the dashboard (not empty arrays).

**What it checks**:
- `const dashboardData = [];` should NOT exist in generated file
- `const recommendationsData = [];` should NOT exist in generated file

**Why it matters**: Empty data arrays mean the dashboard loads but shows no content.

### Test 11: Valid JSON Structure
**Purpose**: Ensures injected data is valid JSON and has required structure.

**What it checks**:
- JSON parses without errors
- TOTAL row exists
- Required fields present (Total, Health, Invocation %, Test %, Avg CC, Risk)

**Why it matters**: Invalid JSON causes JavaScript errors; missing fields cause rendering failures.

## Adding New Tests

To add a new test to the suite:

```python
def test_13_your_new_test(self):
    """Test 13: Description of what this test validates."""
    self.assertIsNotNone(self.template_content, "Template content not loaded")

    # Your test logic here
    self.assertIn(
        'expected_content',
        self.template_content,
        "Error message if test fails"
    )
```

**Test naming convention**: `test_XX_descriptive_name` where XX is the test number (01-99)

## Test Maintenance

### When to Update Tests

1. **Adding new DOM elements**: Update `test_02_template_has_required_elements`
2. **Adding new JavaScript functions**: Update `test_04_template_has_required_functions`
3. **Adding new tabs**: Update `test_09_template_has_all_tabs`
4. **Adding new CSS variables**: Update `test_12_template_css_variables_defined`
5. **Changing data structure**: Update `test_11_generated_dashboard_has_valid_json`

### Test Philosophy

- **Fail fast**: Tests should catch errors before dashboard generation
- **Comprehensive**: Cover template structure, data injection, and generated output
- **Regression prevention**: Add tests for every bug found
- **Self-documenting**: Test names and docstrings explain what's being validated

## Integration with CI/CD

The test suite can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Dashboard Tests
  run: python tests/test_dashboard_generation.py

- name: Generate Dashboard (only if tests pass)
  run: python gen_dashboard.py
```

## Benefits

✅ **Prevents regressions**: Bugs can't be reintroduced
✅ **Fast feedback**: Catch errors in seconds, not minutes
✅ **Documentation**: Tests document expected behavior
✅ **Confidence**: Safe to refactor knowing tests will catch breaks
✅ **Quality gate**: Dashboard generation only succeeds with valid templates

## Summary

- **12 comprehensive tests** validate template structure, data injection, and generated output
- **Mandatory execution** before every dashboard generation
- **Blocks generation** if any test fails
- **Prevents known bugs** (gauge rendering, empty data, invalid JSON)
- **Test-driven workflow** ensures quality and prevents regressions

**Bottom line**: Dashboard updates are now **test-driven and validated** - no more "nothing populated" issues.
