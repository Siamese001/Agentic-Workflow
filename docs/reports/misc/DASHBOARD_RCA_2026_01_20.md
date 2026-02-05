# Dashboard Root Cause Analysis (RCA)

**Date:** January 20, 2026
**Severity:** High
**Status:** Resolved with Guardrails Implemented

## Executive Summary

Multiple critical issues were discovered in the dashboard system that caused JavaScript errors, prevented proper rendering, and resulted in a bloated HTML file (2.7MB instead of ~500KB). All issues have been resolved and guardrails have been implemented to prevent recurrence.

---

## Issue 1: Bloated HTML File (2.7MB)

### Symptoms
- `autonomy_dashboard.html` grew from ~500KB to 2.7MB
- Multiple `</html>` tags found in file (4 occurrences)
- Browser reported "Identifier 'dashboardData' has already been declared"

### Root Cause
The regeneration script (`regenerate_dashboard_full.py`) used simple string `find()` to locate markers like `const dashboardData = [` and `];` for replacement. When the HTML already contained data, the script would:

1. Find `const dashboardData = [`
2. Find the NEXT `];` (which might be inside a nested array)
3. Replace only that portion, leaving the rest of the original data
4. Result: Original data remained, new data was inserted, creating duplicates

**Code that caused the issue:**
```python
# BROKEN: Simple find doesn't handle nested brackets
dd_start = content.find('const dashboardData = [')
dd_end = content.find('];', dd_start) + 2  # Finds FIRST ]; not MATCHING ];
```

### Fix Applied
Implemented bracket/brace counting to find the MATCHING closing delimiter:

```python
# FIXED: Count brackets to find matching close
bracket_count = 0
for i, char in enumerate(content[dd_start:], dd_start):
    if char == '[':
        bracket_count += 1
    elif char == ']':
        bracket_count -= 1
        if bracket_count == 0:
            dd_end = i + 1
            break
```

### Guardrail Implemented
Added corruption detection at the start of regeneration:

```python
html_end_count = content.count('</html>')
if html_end_count > 1:
    print(f"⚠️ WARNING: HTML file corrupted ({html_end_count} </html> tags)")
    first_html_end = content.find('</html>') + len('</html>')
    content = content[:first_html_end]  # Auto-truncate
```

---

## Issue 2: Duplicate JavaScript Declarations

### Symptoms
- Browser console: "Identifier 'dashboardData' has already been declared"
- Browser console: "Identifier 'recommendationsData' has already been declared"
- Tables not rendering properly

### Root Cause
The HTML file uses a fallback pattern for data loading:
```javascript
const dashboardData = window.dashboardData || [/* default data */];
```

The regeneration script was looking for `const dashboardData = [` but the actual pattern was `const dashboardData = window.dashboardData || [`. This caused:
1. Script couldn't find the marker
2. Script added NEW declaration instead of replacing
3. Result: Two declarations of the same variable

### Fix Applied
Handle both patterns:
```python
dd_start = content.find('const dashboardData = window.dashboardData || [')
if dd_start == -1:
    dd_start = content.find('const dashboardData = [')
```

### Guardrail Implemented
Added validation in test suite (`tests/dashboard/test_javascript.py`):
```python
def test_no_duplicate_dashboard_data(self, html_content):
    declarations = re.findall(r'const\s+dashboardData\s*=', html_content)
    assert len(declarations) <= 1, f"Multiple declarations: {len(declarations)}"
```

---

## Issue 3: StrategicRecommendationAgent Not Loading

### Symptoms
- Regeneration output: "StrategicRecommendationAgent failed: No module named 'agentic_core.L3_orchestration.strategic_recommendation'"
- 0 recommendations generated
- Empty recommendations section in dashboard

### Root Cause
Incorrect import path in regeneration script:
```python
# WRONG
from agentic_core.L3_orchestration.strategic_recommendation.StrategicRecommendationAgent import ...

# CORRECT
from agentic_core.L1_cognition.thought_engine.StrategicRecommendationAgent import ...
```

The agent was moved from L3 to L1 but the import path was never updated.

### Fix Applied
Updated import path to correct location.

### Guardrail Implemented
Added explicit ImportError handling with clear message:
```python
except ImportError as e:
    print(f"⚠️ StrategicRecommendationAgent import failed: {e}")
    return {"review": "Strategic analysis unavailable", "recommendations": []}
```

---

## Issue 4: Tests Checking HTML Instead of JS Files

### Symptoms
- Tests passed even when JS functions were missing
- False confidence in dashboard functionality

### Root Cause
Historical tests checked for function definitions in HTML (inline JS) instead of the modular JS files where functions actually live:
```python
# WRONG: Checked HTML
assert 'function renderTable' in html_content

# CORRECT: Check JS files
content = (dashboard_dir / "js/renderers/table-renderer.js").read_text()
assert 'function renderTerritorySummaryTable' in content
```

### Fix Applied
Updated `scripts/test_dashboard_e2e.py` to check JS files directly.

### Guardrail Implemented
New test class in `tests/dashboard/test_javascript.py`:
```python
class TestTableRenderer:
    @pytest.mark.parametrize("func_name", ["renderTerritorySummaryTable", "renderCodeQualityTable"])
    def test_required_function_exists(self, dashboard_dir, func_name):
        renderer_js = dashboard_dir / "js" / "renderers" / "table-renderer.js"
        content = renderer_js.read_text()
        assert f"function {func_name}" in content
```

---

## Issue 5: Playwright Visual Inspection Was Optional

### Symptoms
- Dashboard could have visual bugs that tests wouldn't catch
- "Optional" Playwright tests were often skipped
- No guaranteed visual validation before deployment

### Root Cause
Original e2e test had Playwright as optional:
```python
# WRONG: Optional
if playwright_available:
    run_playwright_tests()
else:
    print("Skipping Playwright (optional)")
```

### Fix Applied
Made Playwright mandatory with explicit failure:
```python
is_functional, error_msg = verify_playwright_functional()
if not is_functional:
    print(f"❌ PLAYWRIGHT NOT FUNCTIONAL: {error_msg}")
    return 0, 1, [f"MANDATORY: Playwright not functional"]
```

### Guardrail Implemented
`verify_playwright_functional()` checks both:
1. Module is installed (`from playwright.sync_api import sync_playwright`)
2. Browser can actually launch (`p.chromium.launch()`)

---

## Guardrails Summary

### 1. HTML Corruption Detection (regenerate_dashboard_full.py)
- Counts `</html>` tags before processing
- Auto-truncates if corruption detected
- Logs warning for investigation

### 2. Bracket Counting for JSON Replacement
- Uses proper bracket/brace counting instead of simple `find()`
- Handles nested structures correctly
- Prevents partial replacements

### 3. Pattern Flexibility
- Handles both `const x = [` and `const x = window.x || [` patterns
- Future-proofs against similar pattern variations

### 4. Duplicate Declaration Tests
- `test_no_duplicate_dashboard_data()`
- `test_no_duplicate_real_agent_data()`
- `test_no_duplicate_recommendations_data()`
- `test_single_html_closing_tag()`

### 5. HTML Size Validation
- `test_html_size_reasonable()` - fails if > 1MB
- Early warning for bloat issues

### 6. Mandatory Playwright
- `verify_playwright_functional()` - must pass before visual tests
- No "optional" visual inspection - it's required

### 7. JS File Validation (37 new tests)
- Syntax validation (balanced braces/brackets)
- Required function existence
- No debugger/alert statements
- Proper exports to window

---

## Prevention Checklist

Before any dashboard regeneration:
- [ ] Run `pytest tests/dashboard/test_javascript.py -v` to validate JS
- [ ] Check HTML file size (should be < 600KB)
- [ ] Verify single `</html>` tag in HTML

After regeneration:
- [ ] Run `python scripts/test_dashboard_e2e.py` (includes Playwright)
- [ ] Verify 0 JavaScript errors in browser console
- [ ] Check recommendations count > 0 (StrategicRecommendationAgent working)

---

## Files Modified for Guardrails

1. `agentic_core/L0_maintenance/scripts/regenerate_dashboard_full.py`
   - Corruption detection
   - Bracket counting
   - Pattern flexibility
   - Better error handling

2. `scripts/test_dashboard_e2e.py`
   - Mandatory Playwright
   - JS file checking (not HTML)
   - Proper test numbering

3. `tests/dashboard/test_javascript.py` (NEW)
   - 37 comprehensive JS tests
   - Duplicate declaration detection
   - HTML corruption detection

4. `tests/dashboard/test_ui_layout.py`
   - Updated for flexibility
   - Core functionality tests

---

## Lessons Learned

1. **Never use simple `find()` for JSON replacement** - Always count brackets/braces
2. **Test the actual files, not assumptions** - JS functions live in JS files, not HTML
3. **Make critical validations mandatory** - Optional tests get skipped
4. **Add size/count guardrails** - Catch bloat early
5. **Handle pattern variations** - Code evolves, patterns change
