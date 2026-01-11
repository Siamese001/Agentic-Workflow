#!/usr/bin/env python3
"""
Simple HTTP Server for Dashboard - No API routes
Serves autonomy_dashboard.html on http://localhost:8080/autonomy_dashboard.html
"""
import http.server
import socketserver
import os
from pathlib import Path

PORT = 8080

def main():
    """Start HTTP server."""
    dashboard_dir = Path(__file__).parent
    os.chdir(dashboard_dir)
    
    handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print("=" * 70)
        print("DASHBOARD HTTP SERVER")
        print("=" * 70)
        print(f"Serving at: http://localhost:{PORT}/autonomy_dashboard.html")
        print(f"Directory: {dashboard_dir}")
        print("\nPress Ctrl+C to stop")
        print("=" * 70)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServer stopped.")

if __name__ == "__main__":
    main()
