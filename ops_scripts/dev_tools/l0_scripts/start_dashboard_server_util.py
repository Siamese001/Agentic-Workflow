import os
import signal
import socket
import sys
from pathlib import Path
from agentic_core.L5_safety.config.structure_blueprint import DASHBOARD_DIR
from agentic_core.utils.security_util import safe_popen
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
REPORTS_DIR = Path(__file__).parent.parent / DASHBOARD_DIR
PORT = 8000
server_process = None

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global server_process
    signal_name = signal.Signals(signum).name
    print(f'\n\n⚠️  Received {signal_name} signal - shutting down server...')
    if server_process:
        server_process.terminate()
        server_process.wait(timeout=DEFAULT_TIMEOUT)
    print('✅ Server stopped gracefully.')
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
if is_port_in_use(PORT):
    print(f'Dashboard already running → http://localhost:{PORT}/autonomy_dashboard.html')
else:
    print(f'Starting dashboard server on port {PORT}...')
    print('Press Ctrl+C to stop the server')
    # guardian: allow-path-string
    os.chdir(REPORTS_DIR)
    try:
        server_process = safe_popen([sys.executable, '-m', 'http.server', str(PORT)])
        server_process.wait()
    except KeyboardInterrupt:
        print('\n\n✅ Server stopped gracefully.')
    finally:
        if server_process:
            server_process.terminate()
        print('🔒 Cleanup complete.')
