# Dashboard Refresh Protocol - MANDATORY

## Overview
This protocol MUST be followed after ANY change to `agent_discovery_full.json` or `autonomy_dashboard.html`.

## Critical Requirements

### 1. **Run Complete E2E Test Suite**
```bash
python scripts/test_dashboard_end_to_end.py
```

**All 16 tests MUST pass:**
1. Agent Discovery Integrity
2. Dashboard HTML Exists
3. Dashboard Data Structure
4. Required Fields Present
5. Data Consistency
6. Table Rendering Elements
7. Drill-Down Agent Data Integrity
8. Base Agent Uniqueness
9. Orphaned Agents Check
10. Metric Consistency Check
11. L5 Safety MCP Requirement
12. Table 2 (Code Quality) Data Integrity
13. Footnote Accuracy Check
14. Dashboard Snapshot Regression Test
15. **Browser Cache & JavaScript Validation** ⭐ NEW
16. **File Freshness & Hash Verification** ⭐ NEW

### 2. **Browser Cache Verification** (Test 15)

**What it checks:**
- ✅ Cache-busting headers present (`Cache-Control`, `Pragma`, `Expires`)
- ✅ All critical JavaScript elements exist
- ✅ `Base Class Inherit %` field referenced in JavaScript rendering code

**Why it matters:**
- Browsers aggressively cache HTML files
- Without cache-busting headers, users see stale data
- JavaScript must reference the correct field names

### 3. **File Freshness Check** (Test 16)

**What it checks:**
- ✅ File modified within last 10 minutes
- ✅ File size reasonable (> 500KB)
- ✅ SHA256 hash for browser verification

**Why it matters:**
- Detects if dashboard generation actually updated the file
- Identifies web server caching issues
- Provides hash to verify browser loaded correct version

## Mandatory Browser Refresh Steps

### After Dashboard Generation:

1. **Save the file hash** (displayed in Test 16 output)
   ```
   SHA256: 48eb8a90230833b21179c90c7da1079530a95b1870eba96afe04ff6e2e879205
   ```

2. **Hard refresh browser** (DO NOT use normal refresh):
   - **Windows/Linux:** `Ctrl+Shift+R` or `Ctrl+F5`
   - **Mac:** `Cmd+Shift+R`

3. **If using web server:**
   ```bash
   # Stop server
   Ctrl+C
   
   # Restart with cache disabled
   http-server -c-1
   # or
   live-server --no-browser --port=8080
   ```

4. **Verify browser loaded correct version:**
   - Open browser DevTools (F12)
   - Go to Network tab
   - Hard refresh
   - Check `autonomy_dashboard.html` response headers
   - Verify file size matches Test 16 output

## Common Issues & Solutions

### Issue: Browser shows 0.0% for "Base Class Inherit %"

**Root Causes:**
1. Browser cached old HTML file
2. Web server caching enabled
3. Field name mismatch (JS expects different field than data provides)

**Solutions:**
1. ✅ **Hard refresh** (Ctrl+Shift+R)
2. ✅ **Clear browser cache** completely
3. ✅ **Restart web server** with caching disabled
4. ✅ **Verify Test 15B passes** (JavaScript elements present)
5. ✅ **Check file hash** matches between server and browser

### Issue: Test 16A fails (file is stale)

**Root Cause:**
Dashboard generation script didn't actually update the file

**Solutions:**
1. ✅ **Regenerate dashboard:**
   ```bash
   python agentic_core/L6_observability/dashboards/generate_dashboard.py
   ```
2. ✅ **Check file permissions** (can script write to file?)
3. ✅ **Verify no file locks** (close any editors with file open)

### Issue: Test 15B fails (missing JavaScript elements)

**Root Cause:**
Dashboard HTML template corrupted or field names changed

**Solutions:**
1. ✅ **Verify `row['Base Class Inherit %']` in HTML**
2. ✅ **Check dashboard generation** added field to data
3. ✅ **Verify REQUIRED_FIELDS** includes `"Base Class Inherit %"`

## Verification Checklist

Before considering dashboard update complete:

- [ ] All 16 e2e tests pass
- [ ] File hash saved from Test 16 output
- [ ] Browser hard refreshed (Ctrl+Shift+R)
- [ ] Web server restarted (if applicable)
- [ ] Browser DevTools confirms correct file loaded
- [ ] Visual inspection shows correct values (not 0.0%)
- [ ] "Base Class Inherit %" column displays 100.0%

## Automated Verification Script

Run this to verify browser state:
```bash
python scripts/verify_dashboard_browser_state.py
```

This script checks:
- File metadata and modification time
- Cache-busting headers
- Dashboard data validity
- JavaScript validation
- Provides browser refresh instructions

## Integration with CI/CD

### Pre-Deployment Checklist:
1. Run full e2e test suite
2. Verify all 16 tests pass
3. Save file hash to deployment log
4. Document browser refresh requirement in release notes

### Post-Deployment:
1. Verify production file hash matches deployment log
2. Test in clean browser (incognito/private mode)
3. Confirm no caching issues on CDN (if applicable)

## File Locations

- **E2E Test Suite:** `scripts/test_dashboard_end_to_end.py`
- **Browser Verification:** `scripts/verify_dashboard_browser_state.py`
- **Dashboard Generator:** `agentic_core/L6_observability/dashboards/generate_dashboard.py`
- **Dashboard HTML:** `agentic_core/L6_observability/dashboards/autonomy_dashboard.html`
- **Discovery Data:** `agent_discovery_full.json`

## Summary

**NEVER skip these steps:**
1. ✅ Run all 16 e2e tests
2. ✅ Save file hash
3. ✅ Hard refresh browser (Ctrl+Shift+R)
4. ✅ Restart web server with cache disabled
5. ✅ Verify browser loaded correct version

**Browser caching is the #1 cause of "dashboard not updating" issues.**
