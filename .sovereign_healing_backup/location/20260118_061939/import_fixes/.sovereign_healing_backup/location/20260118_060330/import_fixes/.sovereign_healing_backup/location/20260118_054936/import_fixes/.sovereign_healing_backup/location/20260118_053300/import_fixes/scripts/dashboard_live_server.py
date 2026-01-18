# Dashboard Live Reload Server
# Location: scripts/dashboard_live_server.py
# Purpose: Serves L6_observability/dashboards/ directory with automatic browser reload on file changes
# Features:
# - Uses livereload (pip install livereload)
# - Watches autonomy_dashboard.html + any included assets
# - Auto-reloads browser tab when dashboard regenerates
# - Runs on http://localhost:8000
# - Windsurf task integration ready
# SSOT: agentic_core/L6_observability/dashboards/

from livereload import Server
from pathlib import Path
import os
import subprocess
import sys
import signal

# Import SSOT for dashboard directory - NO HARDCODING
from agentic_core.config.blueprint_sovereign.structure_blueprint import DASHBOARD_DIR

# Project root (adjust if script location changes)
PROJECT_ROOT = Path(__file__).parent.parent
GEN_SCRIPT = PROJECT_ROOT / "agentic_core" / "L5_safety" / "validators" / "AutonomyGuardianAgent.py"

def regenerate_dashboard():
    """Trigger dashboard regeneration."""
    print("\n🔄 Source files changed → Regenerating autonomy_dashboard.html...")
    try:
        result = subprocess.run(
            [sys.executable, "-c", 
             "from pathlib import Path; from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent; "
             "agent = AutonomyGuardianAgent(project_root=Path('.')); agent.generate_compliance_report()"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        if result.returncode == 0:
            print("   ✅ Dashboard regenerated successfully")
        else:
            print(f"   ❌ Regeneration failed:\n{result.stderr}")
    except Exception as e:
        print(f"   ❌ Error running dashboard generation: {e}")

REPORTS_DIR = PROJECT_ROOT / DASHBOARD_DIR
PORT = 8000

# Global server reference for signal handlers
live_server = None

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    signal_name = signal.Signals(signum).name
    print(f"\n\n⚠️  Received {signal_name} signal - shutting down live server...")
    print("✅ Server stopped gracefully.")
    sys.exit(0)

# Register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # Termination signal

# Ensure we're in reports directory
os.chdir(REPORTS_DIR)

server = Server()
live_server = server

# Watch main dashboard HTML + common asset patterns
server.watch("autonomy_dashboard.html")
server.watch("*.css")
server.watch("*.js")
server.watch("assets/*")

# Regenerate dashboard when canonical discovery JSON changes
server.watch(str(PROJECT_ROOT / "agent_discovery_full.json"), func=regenerate_dashboard, delay=1)

# Auto-regeneration - watch agent source code
# Triggers dashboard regeneration when any .py file in agentic_core/ changes
# Live reload then auto-refreshes browser on new HTML
server.watch(str(PROJECT_ROOT / "agentic_core" / "**" / "*.py"), func=regenerate_dashboard, delay=1)

# Serve on port 8000
print(f"🚀 Dashboard live server starting → http://localhost:{PORT}/autonomy_dashboard.html")
print("   Live reload enabled - browser auto-refreshes on regeneration")
print("   Auto-regeneration enabled - watches agentic_core/ for code changes")
print("   Press Ctrl+C to stop the server")
try:
    server.serve(port=PORT, host="localhost")
except KeyboardInterrupt:
    print("\n\n✅ Server stopped gracefully.")
finally:
    print("🔒 Cleanup complete.")
