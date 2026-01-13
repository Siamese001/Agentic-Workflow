# Autonomy Dashboard Usage Guide

## Opening the Dashboard (No Server Required)

The dashboard is a **fully self-contained HTML file** that works offline. All agent data is embedded directly in the HTML.

### Method 1: Direct File Open (Recommended)

**Windows:**
```bash
# Double-click the file in File Explorer, or:
start agentic_core/L6_observability/dashboards/autonomy_dashboard.html
```

**macOS:**
```bash
open agentic_core/L6_observability/dashboards/autonomy_dashboard.html
```

**Linux:**
```bash
xdg-open agentic_core/L6_observability/dashboards/autonomy_dashboard.html
```

**From VS Code:**
- Right-click `autonomy_dashboard.html` → "Open with Live Server" (if extension installed)
- Or right-click → "Reveal in File Explorer" → double-click

### Method 2: Python HTTP Server (Optional)

If you prefer using a local server:

```bash
# From project root
cd agentic_core/L6_observability/dashboards
python -m http.server 8080

# Then open: http://localhost:8080/autonomy_dashboard.html
```

---

## Features Available Offline

✅ **All data tables** - Territory summary, code quality metrics, agent details  
✅ **KPI boxes** - Total agents, health scores, compliance rates  
✅ **Drill-down views** - Click territories to see individual agents  
✅ **Search & filter** - Find agents by name, layer, or capability  
✅ **VS Code integration** - Click agent names to open in VS Code  

⚠️ **Charts require internet** - Plotly.js charts load from CDN  
- If offline, charts show simplified text-based metrics  
- All data is still accessible in tables  

---

## Troubleshooting

### Charts Not Loading

**Symptom:** Charts show "Charts require internet connection"

**Cause:** Plotly.js CDN is blocked or you're offline

**Solution:**
1. Connect to internet and refresh (Ctrl+Shift+R)
2. Or use tables - all data is available without charts

### Dashboard Shows Old Data

**Symptom:** Agent counts or metrics don't match latest discovery

**Solution:**
```bash
# Regenerate dashboard with latest data
python agentic_core/L6_observability/dashboards/generate_dashboard.py

# Hard refresh browser
# Windows/Linux: Ctrl+Shift+R
# macOS: Cmd+Shift+R
```

### 404 Error When Server Closes

**Symptom:** "Error response 404" when Windsurf/server stops

**Solution:** The dashboard doesn't need a server!
- Close the server
- Open the HTML file directly (Method 1 above)
- All data is embedded in the file

### VS Code Links Not Working

**Symptom:** Clicking agent names doesn't open files

**Cause:** Browser security blocks `vscode://` protocol

**Solution:**
1. Use a local server (Method 2) instead of file://
2. Or manually copy file paths and open in VS Code

---

## Updating Dashboard Data

The dashboard automatically embeds all data from `agent_discovery_full.json`.

**To update:**

```bash
# Step 1: Run discovery scan
python scripts/full_agent_discovery.py

# Step 2: Regenerate dashboard
python agentic_core/L6_observability/dashboards/generate_dashboard.py

# Step 3: Refresh browser (hard refresh)
# Windows/Linux: Ctrl+Shift+R
# macOS: Cmd+Shift+R
```

**Validation:**

```bash
# Run e2e tests to verify dashboard integrity
python scripts/test_dashboard_end_to_end.py
```

All 17 tests should pass before deployment.

---

## Dashboard Architecture

### Self-Contained Design

The dashboard is designed to work **without any server**:

1. **All data embedded** - `dashboardData` and `realAgentData` arrays in HTML
2. **No AJAX calls** - No fetch() or XMLHttpRequest to external files
3. **No relative paths** - All resources are absolute or inline
4. **CDN fallback** - Charts degrade gracefully if CDN unavailable

### Data Flow

```
agent_discovery_full.json
    ↓
generate_dashboard.py
    ↓
autonomy_dashboard.html (embedded data)
    ↓
Open directly in browser (file://)
```

### File Locations

```
C:/Git/Agentic-Workflow/
├── agent_discovery_full.json          # Source data
├── agentic_core/L6_observability/dashboards/
│   ├── autonomy_dashboard.html        # Self-contained dashboard
│   ├── generate_dashboard.py          # Generator script
│   └── DASHBOARD_USAGE.md            # This file
└── scripts/
    ├── full_agent_discovery.py        # Discovery scan
    └── test_dashboard_end_to_end.py   # Validation tests
```

---

## Best Practices

### For Development

1. **Always regenerate after discovery changes**
   ```bash
   python scripts/full_agent_discovery.py && \
   python agentic_core/L6_observability/dashboards/generate_dashboard.py
   ```

2. **Run tests before committing**
   ```bash
   python scripts/test_dashboard_end_to_end.py
   ```

3. **Hard refresh after regeneration**
   - Browsers cache aggressively
   - Always use Ctrl+Shift+R (or Cmd+Shift+R)

### For Deployment

1. **Dashboard is portable** - Copy `autonomy_dashboard.html` anywhere
2. **No dependencies** - Works on any machine with a browser
3. **Version control** - Commit dashboard with embedded data
4. **Offline ready** - Tables work without internet

### For Presentations

1. **Open before meeting** - Ensure charts load while online
2. **Use drill-down** - Click territories to show agent details
3. **Explain metrics** - Hover tooltips provide context
4. **Show trends** - Sparklines show metric evolution

---

## Technical Details

### Browser Compatibility

✅ Chrome/Edge 90+  
✅ Firefox 88+  
✅ Safari 14+  

### Security Considerations

- **No external data** - All data embedded at generation time
- **No user input** - Read-only dashboard
- **CSP compatible** - No inline event handlers (uses addEventListener)
- **VS Code protocol** - Requires user approval in browser

### Performance

- **File size:** ~2-3 MB with 268 agents
- **Load time:** <1 second on modern hardware
- **Memory:** ~50 MB in browser
- **Responsive:** Works on mobile/tablet

---

## Support

### Common Questions

**Q: Can I share the dashboard?**  
A: Yes! Just send the `autonomy_dashboard.html` file. It's self-contained.

**Q: Does it update automatically?**  
A: No. Run `generate_dashboard.py` to update with latest data.

**Q: Can I customize the dashboard?**  
A: Yes, but edit `generate_dashboard.py`, not the HTML directly. The HTML is regenerated each time.

**Q: Why do I need internet for charts?**  
A: Charts use Plotly.js from CDN. Tables work offline. We can embed Plotly.js if needed (adds ~3 MB).

### Getting Help

1. Check this guide first
2. Run e2e tests: `python scripts/test_dashboard_end_to_end.py`
3. Check browser console (F12) for errors
4. Verify `agent_discovery_full.json` exists and is valid

---

**Last Updated:** 2026-01-13  
**Dashboard Version:** Phase 3.3 (Self-Contained)  
**Agent Count:** 268 agents
