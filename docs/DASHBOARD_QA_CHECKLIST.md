# Dashboard QA Checklist

**MANDATORY**: Run ALL steps before committing any dashboard template or generator changes.

## Pre-Deployment QA Protocol

### 1. Template Syntax Validation

**File**: `agentic_core/L5_safety/validators/dashboard_template.html`

```bash
# Check for syntax errors
python -c "
import re
with open('agentic_core/L5_safety/validators/dashboard_template.html', 'r', encoding='utf-8') as f:
    content = f.read()
    # Check for unclosed tags
    if content.count('<div') != content.count('</div>'):
        print('ERROR: Mismatched div tags')
        exit(1)
    # Check for duplicate IDs
    ids = re.findall(r'id=[\"\\']([^\"\\'\s>]+)', content)
    if len(ids) != len(set(ids)):
        dupes = [x for x in ids if ids.count(x) > 1]
        print(f'ERROR: Duplicate IDs: {set(dupes)}')
        exit(1)
    print('✅ Template syntax valid')
"
```

**Expected**: No errors, all tags balanced, no duplicate IDs.

---

### 2. JavaScript Validation

**Check for**:
- No `undefined` variable references
- All `getElementById()` calls have matching HTML elements
- No conflicting timer/interval IDs
- Proper error handling in try-catch blocks

```bash
# Search for potential issues
grep -n "getElementById" agentic_core/L5_safety/validators/dashboard_template.html | while read line; do
    id=$(echo "$line" | grep -oP "getElementById\(['\"]\\K[^'\"]+")
    if ! grep -q "id=[\"']$id[\"']" agentic_core/L5_safety/validators/dashboard_template.html; then
        echo "⚠️  Missing element: $id (line: $line)"
    fi
done
```

**Expected**: All element IDs exist in HTML.

---

### 3. Regenerate Dashboard

```bash
cd C:\Git\Agentic-Workflow
python canon_validator_agentic_v2_thin.py --report
```

**Expected**:
- Exit code 0
- No Python exceptions
- Files generated:
  - `reports/autonomy_compliance_report.md`
  - `reports/autonomy_compliance_data.csv`
  - `reports/autonomy_dashboard.html`

---

### 4. Generated HTML Validation

**File**: `reports/autonomy_dashboard.html`

```bash
# Check file size (should be 400-600KB)
ls -lh reports/autonomy_dashboard.html

# Verify critical elements exist
python -c "
with open('reports/autonomy_dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()
    critical = [
        'healthScoreValue',
        'codeQualityScoreValue',
        'baseInheritanceValue',
        'execHealth',
        'execGap',
        'anomalyFlags',
        'refreshStatus',
        'REFRESH_INTERVAL_MS'
    ]
    missing = [e for e in critical if e not in html]
    if missing:
        print(f'❌ Missing elements: {missing}')
        exit(1)
    print('✅ All critical elements present')
"
```

**Expected**: File 400-600KB, all critical elements present.

---

### 5. Timer Configuration Audit

```bash
# Check refresh interval consistency
grep -n "REFRESH_INTERVAL_MS\|content=\"[0-9]\+\"\|30000\|setInterval\|setTimeout" reports/autonomy_dashboard.html
```

**Expected**:
- `REFRESH_INTERVAL_MS = 300000` (5 minutes)
- `<meta http-equiv="refresh" content="300">`
- NO hardcoded `30000` (except in stale buffer calculation)
- Single `setInterval` for refresh timer
- Single `setInterval` for countdown display

---

### 6. Browser Rendering Test

**Manual Steps**:

1. **Clear browser cache**: `Ctrl+Shift+Delete` → Clear cached images/files
2. **Open**: `C:\Git\Agentic-Workflow\reports\autonomy_dashboard.html`
3. **Open DevTools**: `F12` → Console tab

**Visual Checks**:
- [ ] Top section shows "🎯 Autonomy Readiness Overview"
- [ ] 3 KPI cards display with large percentages (not "--%" placeholders)
- [ ] Executive Summary box shows health percentage and gap text
- [ ] Anomaly flags section shows either warnings or "✅ Portfolio Balanced"
- [ ] Auto-refresh countdown shows "Xm Ys" format (e.g., "4m 59s")
- [ ] Countdown decrements smoothly every second
- [ ] No JavaScript errors in console
- [ ] All charts render (Risk Matrix, Base Inheritance table, etc.)

**Console Checks**:
```javascript
// Run in browser console
console.log('Health:', document.getElementById('healthScoreValue').textContent);
console.log('Code Quality:', document.getElementById('codeQualityScoreValue').textContent);
console.log('Base Inheritance:', document.getElementById('baseInheritanceValue').textContent);
console.log('Refresh Status:', document.getElementById('refreshStatus').textContent);
```

**Expected**: All elements return valid text (not null, not "---%").

---

### 7. Cross-Browser Compatibility

Test in:
- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari (if available)

**Expected**: Consistent rendering, no layout breaks.

---

### 8. Responsive Layout Test

**Resize browser window** to:
- [ ] 1920x1080 (desktop)
- [ ] 1366x768 (laptop)
- [ ] 768x1024 (tablet)

**Expected**: KPI grid adapts (3 columns → 2 columns → 1 column), no horizontal scroll.

---

### 9. Data Integrity Validation

```bash
# Verify CSV matches dashboard totals
python -c "
import csv
import json

# Read CSV
with open('reports/autonomy_compliance_data.csv', 'r') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    total_row = [r for r in rows if r['Territory'] == 'TOTAL'][0]

# Read dashboard HTML and extract embedded data
with open('reports/autonomy_dashboard.html', 'r') as f:
    html = f.read()
    # Extract dashboardData JSON
    start = html.find('const dashboardData = ') + len('const dashboardData = ')
    end = html.find(';', start)
    data_json = html[start:end]
    data = json.loads(data_json)
    html_total = [r for r in data if r['Territory'] == 'TOTAL'][0]

# Compare
if total_row['Total'] != str(html_total['Total']):
    print(f'❌ Total mismatch: CSV={total_row[\"Total\"]}, HTML={html_total[\"Total\"]}')
    exit(1)
print('✅ Data integrity verified')
"
```

**Expected**: CSV and embedded HTML data match.

---

### 10. Performance Check

**File size limits**:
- `autonomy_dashboard.html`: < 1MB
- `autonomy_compliance_data.csv`: < 100KB
- `autonomy_compliance_report.md`: < 500KB

```bash
du -h reports/autonomy_dashboard.html reports/autonomy_compliance_data.csv reports/autonomy_compliance_report.md
```

**Expected**: All files within limits.

---

## Regression Tests

### Test Case 1: Timer Countdown

1. Open dashboard
2. Note initial countdown (e.g., "4m 59s")
3. Wait 5 seconds
4. Verify countdown decreased by 5 seconds (e.g., "4m 54s")

**Expected**: Smooth countdown, no jumps to "29s" or other anomalies.

---

### Test Case 2: Anomaly Detection

**Scenario A: Missing Infrastructure**

Temporarily edit generator to exclude L5 infra agents, regenerate.

**Expected**: Red "🚨 Missing Infrastructure" card appears.

**Scenario B: L2 Disproportion**

Check current L2 agent count. If >30% of total, orange "⚠️ L2 Execution Disproportionately Large" card should appear.

**Expected**: Anomaly flags dynamically detect issues.

---

### Test Case 3: Manual Refresh Button

1. Click "🔄 Refresh Now" button
2. Verify page reloads with cache-busting query param (`?_ts=...`)

**Expected**: Immediate reload, timestamp updates.

---

### Test Case 4: Drill-Down Modals

1. Click any territory row in main table
2. Verify modal opens with agent list
3. Click agent file link
4. Verify VS Code opens (if configured)

**Expected**: All drill-downs functional.

---

## Automated QA Script

**File**: `scripts/dashboard_qa.py`

```python
#!/usr/bin/env python3
"""
Automated Dashboard QA Validation
Run before committing dashboard changes.
"""
import sys
import re
from pathlib import Path

def validate_template():
    """Check template syntax."""
    template = Path('agentic_core/L5_safety/validators/dashboard_template.html')
    content = template.read_text(encoding='utf-8')

    # Check balanced tags
    if content.count('<div') != content.count('</div>'):
        print('❌ Mismatched div tags')
        return False

    # Check duplicate IDs
    ids = re.findall(r'id=["\']([^"\'\s>]+)', content)
    if len(ids) != len(set(ids)):
        dupes = [x for x in ids if ids.count(x) > 1]
        print(f'❌ Duplicate IDs: {set(dupes)}')
        return False

    print('✅ Template syntax valid')
    return True

def validate_generated():
    """Check generated dashboard."""
    dashboard = Path('reports/autonomy_dashboard.html')
    if not dashboard.exists():
        print('❌ Dashboard not generated')
        return False

    content = dashboard.read_text(encoding='utf-8')

    # Check critical elements
    critical = [
        'healthScoreValue',
        'codeQualityScoreValue',
        'baseInheritanceValue',
        'execHealth',
        'execGap',
        'anomalyFlags',
        'refreshStatus',
        'REFRESH_INTERVAL_MS'
    ]
    missing = [e for e in critical if e not in content]
    if missing:
        print(f'❌ Missing elements: {missing}')
        return False

    # Check refresh interval
    if 'REFRESH_INTERVAL_MS = 300000' not in content:
        print('❌ Incorrect refresh interval')
        return False

    # Check for old 30-second timer
    if re.search(r'setInterval.*30000.*forceReload', content):
        print('❌ Old 30-second timer still present')
        return False

    print('✅ Generated dashboard valid')
    return True

if __name__ == '__main__':
    print('Running Dashboard QA...\n')

    checks = [
        validate_template(),
        validate_generated()
    ]

    if all(checks):
        print('\n✅ All QA checks passed')
        sys.exit(0)
    else:
        print('\n❌ QA checks failed')
        sys.exit(1)
```

**Usage**:
```bash
python scripts/dashboard_qa.py
```

---

## Pre-Commit Checklist

Before committing dashboard changes:

- [ ] Run `python scripts/dashboard_qa.py` (must pass)
- [ ] Regenerate dashboard: `python canon_validator_agentic_v2_thin.py --report`
- [ ] Open `reports/autonomy_dashboard.html` in browser
- [ ] Verify all 3 KPIs display correctly
- [ ] Verify countdown timer shows "Xm Ys" format and decrements smoothly
- [ ] Check browser console for errors (should be none)
- [ ] Test manual refresh button
- [ ] Test at least one drill-down modal
- [ ] Clear cache and reload to verify no stale content

**Only commit if ALL checks pass.**

---

## Known Issues & Workarounds

### Issue: Browser Cache Showing Old Dashboard

**Symptom**: Dashboard shows old layout or "30s" countdown despite regeneration.

**Fix**: Hard refresh with `Ctrl+Shift+R` or `Ctrl+F5`, or open in Incognito mode.

---

### Issue: Countdown Jumps to "29s"

**Symptom**: Timer starts at "5m 0s" then jumps to "0m 29s" on next tick.

**Root Cause**: Multiple conflicting timer systems updating same element.

**Fix**: Ensure only ONE `setInterval` updates `refreshStatus` element. Check for duplicate timer code in template.

---

### Issue: KPIs Show "---%"

**Symptom**: Large KPI cards display placeholder "--%" instead of actual percentages.

**Root Cause**: JavaScript population logic not running or `totalRow` undefined.

**Fix**:
1. Check browser console for errors
2. Verify `dashboardData` is embedded in HTML
3. Ensure `loadData()` function executes on page load

---

## Maintenance Notes

**Template Location**: `agentic_core/L5_safety/validators/dashboard_template.html`

**Generator**: `agentic_core/L5_safety/validators/AutonomyGuardianAgent.py`
- Method: `_generate_self_contained_dashboard()`
- Line: ~2858

**Output**: `reports/autonomy_dashboard.html`

**Update Frequency**: Dashboard regenerates on every `--report` run.

**Version Control**: Always commit template + generated output together to maintain consistency.
