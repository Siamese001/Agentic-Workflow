#!/usr/bin/env python3
"""
Simple HTTP server for autonomy dashboard with auto-refresh.
Serves dashboard on localhost:8000 with 30-second auto-refresh.
"""
import http.server
import socketserver
import os
from pathlib import Path

# Change to reports directory
reports_dir = Path(__file__).parent / "reports"
os.chdir(reports_dir)

PORT = 8000
Handler = http.server.SimpleHTTPRequestHandler

print(f"\n🚀 Starting Autonomy Dashboard Server...")
print(f"   → URL: http://localhost:{PORT}/autonomy_dashboard.html")
print(f"   → Auto-refresh: Every 30 seconds")
print(f"   → Serving from: {reports_dir}")
print(f"\n   Press Ctrl+C to stop the server\n")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped.")
