#!/usr/bin/env python3
"""
Simple HTTP Server for Dashboard
Serves autonomy_dashboard.html on http://localhost:8080/autonomy_dashboard.html
"""
import http.server
import socketserver
import os
from pathlib import Path

PORT = 8080

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to serve from dashboard directory with strong no-cache headers."""
    
    def __init__(self, *args, **kwargs):
        # Set directory to dashboard location
        dashboard_dir = Path(__file__).parent
        os.chdir(dashboard_dir)
        super().__init__(*args, **kwargs)
    
    def end_headers(self):
        # Add CORS headers for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        
        # Strong no-cache headers to prevent browser caching issues
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        
        super().end_headers()

def main():
    """Start HTTP server."""
    dashboard_dir = Path(__file__).parent
    os.chdir(dashboard_dir)
    
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        print("=" * 70)
        print("DASHBOARD HTTP SERVER")
        print("=" * 70)
        print(f"Serving dashboard at: http://localhost:{PORT}/autonomy_dashboard.html")
        print(f"Directory: {dashboard_dir}")
        print("\nPress Ctrl+C to stop server")
        print("=" * 70)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServer stopped.")

if __name__ == "__main__":
    main()
