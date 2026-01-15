# Browser Cache Fix Instructions

## Problem
Browser is showing old row order because JavaScript files are cached.

## Verified Correct
✅ `dashboard_data.js` - First row is "Sovereign Base Agent"
✅ `table-renderer.js` - Uses index map to preserve order
✅ Test 26 passes - Row order is correct in data files

## Solution: Clear Browser Cache

### Method 1: Hard Refresh (Recommended)
1. Open browser to `http://localhost:8765/autonomy_dashboard.html`
2. Press **Ctrl+Shift+R** (Windows/Linux) or **Cmd+Shift+R** (Mac)
3. Verify first row shows "Sovereign Base Agent"

### Method 2: Clear Cache via DevTools
1. Open DevTools (F12)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

### Method 3: Incognito/Private Mode
1. Open new incognito/private window
2. Navigate to `http://localhost:8765/autonomy_dashboard.html`
3. Should show correct order immediately

### Method 4: Restart Server with No Cache
```bash
# Stop current server
taskkill /F /IM python.exe

# Start with cache disabled
python -m http.server 8765 --directory agentic_core/L6_observability/dashboards
```

## Expected Row Order
1. Sovereign Base Agent
2. L6 Observability/Base Agent
3. L6 Observability/Infrastructure
4. L6 Observability/Metrics
5. L5 Safety/Base Agent
6. L5 Safety/Gravity
7. L5 Safety/Guardrails
8. L5 Safety/Red Teaming
9. L5 Safety/Validators
10. L4 State/Base Agent
11. L4 State/Core
12. L4 State/Infrastructure
13. L3 Orchestration/Base Agent
14. L3 Orchestration/Core
15. L2 Execution/Base Agent
16. L2 Execution/Core
17. L1 Cognition/Base Agent
18. L1 Cognition/Core
19. L0 Maintenance/Base Agent
20. L0 Maintenance/Core
21. Apps Rg
22. Apps Lic
23. Apps Shared
24. TOTAL

## Verification
Run: `python scripts/verify_row_order.py`
Should show: ✅ Row order is CORRECT!
