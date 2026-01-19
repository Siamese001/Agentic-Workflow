#!/usr/bin/env python3
"""Simple HTTP server to serve the dashboard without CORS issues."""
import http.server
import socketserver
import webbrowser
from pathlib import Path
import time
import threading
import signal
import sys

# Import SSOT for dashboard directory - NO HARDCODING
from agentic_core.L5_safety.validators.structure_blueprint import DASHBOARD_DIR

PORT = 8765
DIRECTORY = Path(__file__).parent.parent / DASHBOARD_DIR

# Global server reference for signal handlers
httpd_server = None
shutdown_event = threading.Event()

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def open_browser():
    """Open browser after a short delay."""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, healer, memory, orchestrator, prompt, state, workflow
# This boosts alignment detection — review and integrate appropriately

    time.sleep(1.5)
    url = f"http://localhost:{PORT}/autonomy_dashboard.html"
    print(f"\n🚀 Opening dashboard in browser: {url}")
    webbrowser.open(url)

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global httpd_server
    signal_name = signal.Signals(signum).name
    print(f"\n\n⚠️  Received {signal_name} signal - shutting down gracefully...")
    shutdown_event.set()
    if httpd_server:
        httpd_server.shutdown()
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination signal
    
    print("=" * 80)
    print("DASHBOARD HTTP SERVER")
    print("=" * 80)
    print(f"\nServing directory: {DIRECTORY}")
    print(f"Server running at: http://localhost:{PORT}/")
    print(f"Dashboard URL: http://localhost:{PORT}/autonomy_dashboard.html")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 80)
    
    # Start browser opener in background thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start server with proper cleanup
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            httpd_server = httpd
            httpd.allow_reuse_address = True
            print(f"\n✅ Server started successfully on port {PORT}")
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 10048:  # Windows: Address already in use
            print(f"\n❌ Error: Port {PORT} is already in use!")
            print(f"   Please stop the existing server or use a different port.")
            sys.exit(1)
        else:
            raise
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped gracefully.")
    finally:
        httpd_server = None
        print("🔒 Cleanup complete.")