# Dashboard Server - Graceful Shutdown Implementation

## Overview
All dashboard server scripts now support graceful shutdown with proper signal handling, preventing orphaned processes and port conflicts.

## Enhanced Scripts

### 1. `serve_dashboard.py` (Port 8765)
**Primary dashboard server with browser auto-launch**

**Features:**
- ✅ SIGINT (Ctrl+C) handler
- ✅ SIGTERM handler for process termination
- ✅ Port conflict detection (Windows error 10048)
- ✅ Socket reuse enabled (`allow_reuse_address`)
- ✅ Graceful cleanup in finally block
- ✅ Global server reference for signal handlers

**Usage:**
```bash
python scripts/serve_dashboard.py
# Press Ctrl+C to stop gracefully
```

**Shutdown Behavior:**
- Displays signal name (SIGINT/SIGTERM)
- Calls `httpd.shutdown()` to stop server loop
- Cleans up resources
- Exits with status 0

---

### 2. `start_dashboard_server.py` (Port 8000)
**Smart launcher with port availability check**

**Features:**
- ✅ SIGINT (Ctrl+C) handler
- ✅ SIGTERM handler
- ✅ Subprocess management with proper termination
- ✅ Port-in-use detection before starting
- ✅ 5-second timeout for graceful subprocess shutdown

**Usage:**
```bash
python scripts/start_dashboard_server.py
# Press Ctrl+C to stop gracefully
```

**Shutdown Behavior:**
- Terminates subprocess with `process.terminate()`
- Waits up to 5 seconds for clean exit
- Displays graceful shutdown message

---

### 3. `dashboard_live_server.py` (Port 8000)
**Live reload server with file watching**

**Features:**
- ✅ SIGINT (Ctrl+C) handler
- ✅ SIGTERM handler
- ✅ Auto-regeneration on file changes
- ✅ Browser auto-reload via livereload
- ✅ Graceful cleanup in finally block

**Usage:**
```bash
python scripts/dashboard_live_server.py
# Press Ctrl+C to stop gracefully
```

**Shutdown Behavior:**
- Stops livereload server
- Displays graceful shutdown message
- Cleanup confirmation

---

## Technical Implementation

### Signal Handler Pattern
```python
import signal
import sys

# Global server reference
httpd_server = None

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global httpd_server
    signal_name = signal.Signals(signum).name
    print(f"\n\n⚠️  Received {signal_name} signal - shutting down gracefully...")
    if httpd_server:
        httpd_server.shutdown()
    sys.exit(0)

# Register handlers
signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # Termination
```

### Try-Finally Pattern
```python
try:
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd_server = httpd
        httpd.allow_reuse_address = True
        httpd.serve_forever()
except KeyboardInterrupt:
    print("\n\n✅ Server stopped gracefully.")
finally:
    httpd_server = None
    print("🔒 Cleanup complete.")
```

---

## Benefits

### Before Enhancement
❌ Orphaned processes on Ctrl+C
❌ Port conflicts requiring manual cleanup
❌ No graceful shutdown feedback
❌ Resource leaks

### After Enhancement
✅ Clean process termination
✅ Port immediately available after stop
✅ Clear shutdown status messages
✅ Proper resource cleanup
✅ Socket reuse enabled
✅ Error handling for port conflicts

---

## Testing

### Test Graceful Shutdown
```bash
# Start server
python scripts/serve_dashboard.py

# In another terminal, send SIGTERM (or press Ctrl+C in original terminal)
# Windows: Use Task Manager or taskkill
# Linux/Mac: kill -TERM <pid>

# Verify:
# 1. Server displays "Received SIGINT/SIGTERM signal"
# 2. Server displays "Server stopped gracefully"
# 3. Port is immediately available
# 4. No orphaned processes remain
```

### Test Port Conflict Handling
```bash
# Start first server
python scripts/serve_dashboard.py

# Try starting second server (should fail gracefully)
python scripts/serve_dashboard.py
# Expected: "❌ Error: Port 8765 is already in use!"
```

---

## Troubleshooting

### Port Still in Use After Shutdown
```bash
# Windows - Find process using port
netstat -ano | findstr :8765

# Kill specific process
taskkill /PID <pid> /F
```

### Server Won't Stop
- Check for multiple Python processes
- Use Task Manager to force-kill if needed
- Verify signal handlers are registered before `serve_forever()`

---

## Integration with legacy editor Tasks

All servers can now be safely used in legacy editor tasks with automatic cleanup:

```json
{
  "name": "Serve Dashboard",
  "command": "python scripts/serve_dashboard.py",
  "type": "process",
  "isBackground": true
}
```

The task can be stopped cleanly via legacy editor's task manager without leaving orphaned processes.

---

## SSOT Enforcement

**Dashboard Directory SSOT:**
All dashboard-related scripts MUST use the centralized constant from `structure_blueprint.py`:

```python
from agentic_core.config.blueprint_sovereign.structure_blueprint import DASHBOARD_DIR, get_validated_project_root

# Correct usage
project_root = get_validated_project_root()
dashboard_path = project_root / DASHBOARD_DIR / "autonomy_dashboard.html"

# WRONG - Never hardcode paths
dashboard_path = Path("C:/Git/Agentic-Workflow/agentic_core/L6_observability/dashboards/autonomy_dashboard.html")
```

**SSOT Location:** `agentic_core/config/blueprint_sovereign/structure_blueprint.py`
```python
DASHBOARD_DIR: str = "agentic_core/L6_observability/dashboards"
```

**Validation:**
Run `scripts/validate_dashboard_ssot.py` to detect hardcoded paths:
```bash
python scripts/validate_dashboard_ssot.py
```

**Automatic Fix:**
Use `scripts/fix_dashboard_hardcoding.py` to bulk-fix violations:
```bash
python scripts/fix_dashboard_hardcoding.py
```

---

## Maintenance Notes

**When adding new server scripts:**
1. Import `signal` and `sys`
2. Create global server reference
3. Define `signal_handler()` function
4. Register SIGINT and SIGTERM handlers
5. Use try-finally for cleanup
6. Enable `allow_reuse_address` for TCP servers
7. Add port conflict detection
8. **ALWAYS use DASHBOARD_DIR from structure_blueprint.py - NO HARDCODING**

**Testing checklist:**
- [ ] Ctrl+C stops server gracefully
- [ ] Port is immediately available after stop
- [ ] No orphaned processes remain
- [ ] Error messages are clear
- [ ] Cleanup runs in all exit paths
- [ ] Uses DASHBOARD_DIR SSOT (no hardcoded paths)
- [ ] Passes `validate_dashboard_ssot.py` check
