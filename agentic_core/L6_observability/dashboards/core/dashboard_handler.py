"""
Simple HTTP Server for Dashboard
Serves autonomy_dashboard.html on http://localhost:8080/autonomy_dashboard.html
"""
import http.server
import os
import socketserver
from pathlib import Path
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
PORT = 8080

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to serve from dashboard directory with strong no-cache headers."""

    def __init__(self, *args, **kwargs):
        dashboard_dir = Path(__file__).parent
        # guardian: allow-path-string
        os.chdir(dashboard_dir)
        super().__init__(*args, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def main():
    """Start HTTP server."""
    dashboard_dir = Path(__file__).parent
    # guardian: allow-path-string
    os.chdir(dashboard_dir)
    with socketserver.TCPServer(('', PORT), DashboardHandler) as httpd:
        print('=' * 70)
        print('DASHBOARD HTTP SERVER')
        print('=' * 70)
        print(f'Serving dashboard at: http://localhost:{PORT}/autonomy_dashboard.html')
        print(f'Directory: {dashboard_dir}')
        print('\nPress Ctrl+C to stop server')
        print('=' * 70)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\n\nServer stopped.')
if __name__ == '__main__':
    main()
