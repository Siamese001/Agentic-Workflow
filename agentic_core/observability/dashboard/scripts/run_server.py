"""
Unified Dashboard Server Runner - Sovereign CLI (L6 Observability)
Consolidates: serve_dashboard.py, start_dashboard_server.py, dashboard_live_server.py
"""
import subprocess
import sys
from pathlib import Path

def run_sovereign_server(port: int = 8000):
    """Launch the Phase 3 Unified FastAPI Server."""
    project_root = Path(__file__).parent.parent.parent.parent.parent
    server_path = project_root / "agentic_core" / "observability" / "dashboard" / "server"
    
    print(f"🚀 Launching Sovereign Dashboard Server on port {port}...")
    print(f"📍 Root: {project_root}")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", str(port), "--reload"],
            cwd=str(server_path),
            check=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Server halted by guardian.")
    except Exception as e:
        print(f"❌ Server Crash: {e}")
        sys.exit(1)

if __name__ == "__main__":
    port_arg = 8000
    if len(sys.argv) > 1:
        try:
            port_arg = int(sys.argv[1])
        except ValueError:
            pass
    run_sovereign_server(port_arg)
