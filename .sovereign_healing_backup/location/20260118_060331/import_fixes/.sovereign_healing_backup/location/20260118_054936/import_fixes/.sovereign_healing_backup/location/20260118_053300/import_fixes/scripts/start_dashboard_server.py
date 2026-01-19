# Smart dashboard server launcher
# Checks if port 8000 is in use; starts server if not
# Run from project root or add as Windsurf task

import socket
import subprocess
import sys
import os
import signal
from pathlib import Path

# Import SSOT for dashboard directory - NO HARDCODING
from agentic_core.config.blueprint_sovereign.structure_blueprint_1 import DASHBOARD_DIR

REPORTS_DIR = Path(__file__).parent.parent / DASHBOARD_DIR
PORT = 8000

# Global process reference for signal handlers
server_process = None

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global server_process
    signal_name = signal.Signals(signum).name
    print(f"\n\n⚠️  Received {signal_name} signal - shutting down server...")
    if server_process:
        server_process.terminate()
        server_process.wait(timeout=5)
    print("✅ Server stopped gracefully.")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # Termination signal

if is_port_in_use(PORT):
    print(f"Dashboard already running → http://localhost:{PORT}/autonomy_dashboard.html")
else:
    print(f"Starting dashboard server on port {PORT}...")
    print("Press Ctrl+C to stop the server")
    os.chdir(REPORTS_DIR)
    try:
        server_process = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT)])
        server_process.wait()
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped gracefully.")
    finally:
        if server_process:
            server_process.terminate()
        print("🔒 Cleanup complete.")
