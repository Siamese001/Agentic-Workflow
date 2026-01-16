# Dashboard Startup Guide

## ⚠️ CRITICAL: Always Restart Server & Clear Cache

**MANDATORY STEPS** before viewing dashboard changes:

1. **Stop existing server**: Press `Ctrl+C` in the terminal running the dashboard server
2. **Restart server**: See Step 2 below
3. **Clear browser cache**: See Step 1 below

**Why?** Browsers aggressively cache JavaScript files. Without clearing cache, you'll see OLD versions of the dashboard even after code changes.

---

## Quick Start - See Live Runtime Changes

### Step 1: Clear Browser Cache (MANDATORY)

**Option A - Hard Refresh (Fastest)**
- **Windows/Linux**: Press `Ctrl + Shift + R`  
- **Mac**: Press `Cmd + Shift + R`

**Option B - Incognito/Private Mode (Guaranteed Fresh)**
- Open new incognito/private window
- Navigate to dashboard URL

**Option C - Clear Cache Completely (Most Thorough)**
- Chrome/Edge: Settings → Privacy → Clear browsing data → Cached images and files
- Firefox: Settings → Privacy → Clear Data → Cached Web Content

### Step 2: Start the API Server

The Live Runtime tab needs the API server to provide real-time data:

```bash
python scripts/start_runtime_api.py
```

You should see:
```
======================================================================
RUNTIME API SERVER
======================================================================
Host: 0.0.0.0
Port: 8081
======================================================================

API Endpoints:
  Health:              http://localhost:8081/api/health
  Runtime State:       http://localhost:8081/api/runtime/state
  Meta-Learning Stats: http://localhost:8081/api/meta-learning/statistics
  ...
```

### Step 3: Start the Dashboard Server

```bash
python -m http.server 8765 --directory agentic_core/L6_observability/dashboards
```

### Step 4: Access Dashboard

Open: `http://localhost:8765/autonomy_dashboard.html#runtime`

### Step 5: Generate Live Data (Optional)

To see the dashboard populate with real data, run the canon validator:

```bash
python canon_validator_agentic_v2_thin.py --heal
```

## What You Should See

The **Live Runtime** tab now has 4 new sections:

### 🧠 Meta-Learning Activity
- **Meta-Learning Statistics**: Total experiences, patterns extracted
- **Strategy Weights**: CoT, ToT, ReAct, Reflection weights (bar chart)
- **Experience Stream**: Recent learning experiences with reward colors
- **Pattern Timeline**: Extracted patterns over time

### 💾 Redis Cache Activity
- **Operation Statistics**: GET/SET/DELETE counts, hit rate
- **Recent Operations**: Last 20 cache operations with hit/miss indicators

### 🔍 Pinecone Vector Operations
- **Vector Storage Statistics**: Vectors stored, avg similarity
- **Recent Queries**: Last 10 similarity searches with scores

### ⚡ Agent Execution Flow
- **Layer Progression**: Visual flow diagram (L6 → L0)
- **Execution Summary**: Success rates, timing stats
- **Execution Timeline**: Individual agent execution durations

## Troubleshooting

### "I still don't see the new sections"

1. **Check browser console** (F12 → Console tab)
   - Look for JavaScript errors
   - Look for 404 errors loading JS/CSS files

2. **Verify files exist**:
   ```bash
   ls agentic_core/L6_observability/dashboards/js/components/
   ls agentic_core/L6_observability/dashboards/css/
   ```
   
   Should show:
   - `meta-learning-panel.js`
   - `redis-monitor.js`
   - `pinecone-monitor.js`
   - `execution-flow.js`
   - `meta-learning.css`

3. **Check API server is running**:
   ```bash
   curl http://localhost:8081/api/health
   ```
   
   Should return: `{"status":"healthy","version":"1.0.0"}`

4. **Clear browser cache completely**:
   - Chrome: Settings → Privacy → Clear browsing data → Cached images and files
   - Firefox: Settings → Privacy → Clear Data → Cached Web Content
   - Edge: Settings → Privacy → Clear browsing data → Cached images and files

### "The sections are there but show no data"

1. **Check API server is running** (see above)

2. **Check runtime_state.json exists**:
   ```bash
   cat runtime_state.json
   ```

3. **Run canon validator to generate data**:
   ```bash
   python canon_validator_agentic_v2_thin.py --heal
   ```

4. **Check browser console for API errors**:
   - Should see polling requests every 2 seconds
   - Should NOT see CORS errors or 404s

### "I see errors in the console"

Common errors and fixes:

- **"Failed to fetch"**: API server not running → Start it with `python scripts/start_runtime_api.py`
- **"404 Not Found"**: File path issue → Hard refresh browser
- **"CORS error"**: Wrong port → Ensure dashboard is on 8765, API on 8081
- **"Undefined is not a function"**: Cached JS → Clear cache and hard refresh

## Verification Checklist

- [ ] API server running on port 8081
- [ ] Dashboard server running on port 8765
- [ ] Browser hard refreshed (Ctrl+Shift+R)
- [ ] Opened `http://localhost:8765/autonomy_dashboard.html#runtime`
- [ ] Can see 4 new sections in Live Runtime tab
- [ ] Browser console shows no errors
- [ ] API health check returns `{"status":"healthy"}`

## Files to Check

If you want to verify the implementation manually:

```bash
# HTML structure
cat agentic_core/L6_observability/dashboards/autonomy_dashboard.html | grep -A 5 "Meta-Learning Activity"

# JavaScript components
ls -lh agentic_core/L6_observability/dashboards/js/components/

# CSS styling
cat agentic_core/L6_observability/dashboards/css/meta-learning.css | head -20

# API endpoints
curl http://localhost:8081/api/meta-learning/statistics
curl http://localhost:8081/api/redis/stats
curl http://localhost:8081/api/pinecone/stats
```

## Need More Help?

See the full documentation:
- User Guide: `docs/DASHBOARD_META_LEARNING_GUIDE.md`
- Developer API: `docs/META_LEARNING_TELEMETRY_API.md`
