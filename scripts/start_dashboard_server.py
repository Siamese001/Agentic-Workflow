# Smart dashboard server launcher
# Checks if port 8000 is in use; starts server if not
# Run from project root or add as Windsurf task

import socket
import subprocess
import sys
import os
from pathlib import Path

REPORTS_DIR = Path(__file__).parent.parent / "reports"
PORT = 8000

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

if is_port_in_use(PORT):
    print(f"Dashboard already running → http://localhost:{PORT}/autonomy_dashboard.html")
else:
    print(f"Starting dashboard server on port {PORT}...")
    os.chdir(REPORTS_DIR)
    subprocess.run([sys.executable, "-m", "http.server", str(PORT)])
