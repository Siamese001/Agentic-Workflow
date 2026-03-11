import mimetypes
import os

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

try:
    from waitress import serve
except ImportError as _err:
    raise ImportError(
        "waitress is required for this module. Install with: pip install -e '.[infra]'",
    ) from _err

os.chdir(
    r"C:\Git\Agentic-Workflow\agentic_core\L6_observability\dashboards",
)  # guardian: allow-path_fragility


class StaticFileApp:
    """Simple WSGI app to serve static files"""

    def __init__(self, directory):
        self.directory = directory

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "/")
        if path == "/":
            path = "/autonomy_dashboard.html"

        # Remove leading slash and resolve path
        filepath = os.path.join(self.directory, path.lstrip("/"))  # guardian: allow-path_fragility

        # Security: prevent directory traversal
        filepath = os.path.abspath(filepath)  # guardian: allow-path_fragility
        if not filepath.startswith(os.path.abspath(self.directory)):  # guardian: allow-path_fragility
            start_response("403 Forbidden", [("Content-Type", "text/plain")])
            return [b"Forbidden"]

        # Serve file if it exists
        if os.path.isfile(filepath):  # guardian: allow-path_fragility
            mimetype, _ = mimetypes.guess_type(filepath)
            if mimetype is None:
                mimetype = "application/octet-stream"

            # Override MIME types for common dashboard files
            if filepath.endswith(".js"):
                mimetype = "application/javascript"
            elif filepath.endswith(".css"):
                mimetype = "text/css"
            elif filepath.endswith(".html"):
                mimetype = "text/html"

            try:
                with open(filepath, "rb") as f:
                    data = f.read()
                start_response(
                    "200 OK",
                    [
                        ("Content-Type", mimetype),
                        ("Content-Length", str(len(data))),
                        ("cache-Control", "no-cache, no-store, must-revalidate"),
                        ("Pragma", "no-cache"),
                        ("Expires", "0"),
                    ],
                )
                return [data]
            except Exception as e:  # guardian: allow-silent_swallower
                start_response("500 Internal Server Error", [("Content-Type", "text/plain")])
                return [f"Error reading file: {e}".encode()]
        else:
            start_response("404 Not Found", [("Content-Type", "text/plain")])
            return [b"File not found"]


app = StaticFileApp(r"C:\Git\Agentic-Workflow\agentic_core\L6_observability\dashboards")
print("Serving at port 8765", flush=True)
serve(app, host="0.0.0.0", port=8765, threads=6)
