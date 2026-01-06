#!/usr/bin/env python3
"""Simple HTTP server to serve the dashboard without CORS issues."""
import http.server
import socketserver
import webbrowser
from pathlib import Path
import time
import threading

PORT = 8765
DIRECTORY = Path(__file__).parent.parent / "reports"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def open_browser():
    """Open browser after a short delay."""
    time.sleep(1.5)
    url = f"http://localhost:{PORT}/autonomy_dashboard.html"
    print(f"\n🚀 Opening dashboard in browser: {url}")
    webbrowser.open(url)

if __name__ == "__main__":
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
    
    # Start server
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServer stopped.")
