import mimetypes
import os
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
from pathlib import Path
try:
    from waitress import serve
except ImportError as _err:
    raise ImportError("waitress is required for this module. Install with: pip install -e '.[infra]'") from _err
# guardian: allow-path-string
os.chdir('C:\\Git\\Agentic-Workflow\\agentic_core\\L6_observability\\dashboards')

class StaticFileApp:
    """Simple WSGI app to serve static files"""

    def __init__(self, directory):
        self.directory = directory

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '/')
        if path == '/':
            path = '/autonomy_dashboard.html'
        filepath = Path(self.directory) / path.lstrip('/')
        # guardian: allow-path-string
        filepath = os.path.abspath(filepath)
        # guardian: allow-path-string
        if not filepath.startswith(os.path.abspath(self.directory)):
            start_response('403 Forbidden', [('Content-Type', 'text/plain')])
            return [b'Forbidden']
        # guardian: allow-path-string
        if os.path.isfile(filepath):
            mimetype, _ = mimetypes.guess_type(filepath)
            if mimetype is None:
                mimetype = 'application/octet-stream'
            if filepath.endswith('.js'):
                mimetype = 'application/javascript'
            elif filepath.endswith('.css'):
                mimetype = 'text/css'
            elif filepath.endswith('.html'):
                mimetype = 'text/html'
            try:
                with open(filepath, 'rb') as f:
                    data = f.read()
                start_response('200 OK', [('Content-Type', mimetype), ('Content-Length', str(len(data))), ('cache-Control', 'no-cache, no-store, must-revalidate'), ('Pragma', 'no-cache'), ('Expires', '0')])
                return [data]
            # guardian: allow-silent-swallow
            except Exception as e:
                start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
                return [f'Error reading file: {e}'.encode()]
        else:
            start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return [b'File not found']
app = StaticFileApp('C:\\Git\\Agentic-Workflow\\agentic_core\\L6_observability\\dashboards')
print('Serving at port 8765', flush=True)
serve(app, host='0.0.0.0', port=8765, threads=6)
