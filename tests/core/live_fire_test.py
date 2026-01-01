import logging
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import os
import signal
import subprocess
import sys
import time
from typing import Any, Optional
try:
    from resume_engine import generate_personalized_cover_letter
except ImportError:
    pass
from canary_monitor import CanaryMonitor, run_canary_monitor
logging.basicConfig(level=logging.INFO, format='%(asctime)s [MAIN] %(message)s', datefmt='%H:%M:%S')
logger: Any = logging.getLogger('Orchestrator')
WATCHDOG_PID: Optional[int] = None
CANARY_MONITOR_PID: Optional[int] = None

# Global declarations handled by type hints above

def start_canary_trap() -> Any:
    """Starts the P7 Canary Trap monitor in a background process."""
    global CANARY_MONITOR_PID
    logger.info('🚨 Bootstrapping Protocol 7 (Canary Trap)...')
    if not os.path.exists('canary_monitor.py'):
        logger.error('❌ canary_monitor.py not found! Aborting.')
        sys.exit(1)
    try:
        proc: Any = subprocess.Popen([sys.executable, 'canary_monitor.py'])
        CANARY_MONITOR_PID = proc.pid
        logger.info(f'✅ Canary Monitor active (PID: {CANARY_MONITOR_PID})')
        time.sleep(1)
    except Exception as e:
        logger.critical(f'Failed to start Canary Monitor: {e}')
        sys.exit(1)

def stop_canary_trap() -> Any:
    """Cleanup canary monitor process on exit."""
    if CANARY_MONITOR_PID:
        logger.info('Stopping Canary Monitor...')
        try:
            os.kill(CANARY_MONITOR_PID, signal.SIGTERM)
        except Exception as e:
            logger.warning(f'Error stopping canary trap: {e}')

def start_watchdog() -> Any:
    """Starts the P5 Dead Man's Switch as a background subprocess."""
    global WATCHDOG_PID
    logger.info('🛡️  Bootstrapping Protocol 5 (Watchdog)...')
    if not os.path.exists('watchdog_sidecar.py'):
        logger.error('❌ watchdog_sidecar.py not found! Aborting.')
        sys.exit(1)
    try:
        if sys.platform == 'win32':
            proc: Any = subprocess.Popen([sys.executable, 'watchdog_sidecar.py'], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            proc: Any = subprocess.Popen([sys.executable, 'watchdog_sidecar.py'])
        WATCHDOG_PID = proc.pid
        logger.info(f'✅ Watchdog active (PID: {WATCHDOG_PID})')
        time.sleep(1)
    except Exception as e:
        logger.critical(f'Failed to start Watchdog: {e}')
        sys.exit(1)

def stop_watchdog() -> Any:
    """Cleanup watchdog process on exit."""
    if WATCHDOG_PID:
        logger.info('Stopping Watchdog...')
        try:
            if sys.platform == 'win32':
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(WATCHDOG_PID)])
            else:
                os.kill(WATCHDOG_PID, signal.SIGTERM)
        except Exception as e:
            logger.warning(f'Error stopping watchdog: {e}')

def run_live_test(target_url: str, user_name: str) -> Any:
    """Executes the full Resume Generation Workflow."""
    logger.info(f'🚀 Starting Live Fire Test for target: {target_url}')
    mock_tools: Any = {'fetch': lambda url, max_length=None: f'Mock job description from {url}', 'search_nodes': lambda query: '{"entities": []}', 'search_records': lambda query, index, top_k, namespace: '[{"text": "Mock template"}]', 'write_file': lambda path, content: None, 'add_observations': lambda observations: None}
    result: Any = generate_personalized_cover_letter(target_url, user_name, 'output.txt', mock_tools, logger)
    status: Any = result.get('status')
    if status == 'success' or status == 'optimized':
        logger.info('✅ SUCCESS: Workflow completed without security violations.')
        logger.info(f"📂 Output saved to: {result.get('file_path', 'Unknown')}")
    elif status == 'FAILED':
        reason: Any = result.get('reason')
        details: Any = result.get('details')
        if reason == 'SECURITY_VIOLATION':
            logger.warning(f'🛡️  BLOCKED BY PROTOCOL 3 (FIREWALL): {details}')
        elif reason == 'HALLUCINATION_DETECTED':
            logger.warning(f'🛡️  BLOCKED BY PROTOCOL 4 (TRUTH ANCHOR): {details}')
        else:
            logger.error(f'❌ Workflow Failed: {reason} - {details}')
    else:
        logger.info(f'ℹ️  Workflow completed with status: {status}')

def signal_handler(sig: Any, frame: Any) -> Any:
    """Brief description of functionality and purpose."""
    logger.info('\nCaught interrupt. Shutting down...')
    stop_watchdog()
    sys.exit(0)
if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    start_canary_trap()
    start_watchdog()
    TEST_URL: Any = 'https://www.ycombinator.com/jobs/role/123-senior-engineer'
    USER_NAME: Any = 'Matthew Wallace'
    try:
        run_live_test(TEST_URL, USER_NAME)
    finally:
        stop_canary_trap()
        stop_watchdog()
