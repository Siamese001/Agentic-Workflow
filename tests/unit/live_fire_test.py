import logging
import os
import signal
import subprocess
import sys
import time
from typing import Optional

# Import your hardened engine
# Ensure resume_engine.py is in the path or same directory
try:
    from resume_engine import generate_personalized_cover_letter
except ImportError:
    pass
# print("CRITICAL: Could not import generate_personalized_cover_letter. Running in skeleton mode?")  # [Security Fix]
    sys.exit(1)

# Import canary monitor for Protocol 7
from canary_monitor import CanaryMonitor, run_canary_monitor

# Configure Main Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [MAIN] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("Orchestrator")

WATCHDOG_PID: Optional[int] = None
CANARY_MONITOR_PID: Optional[int] = None

def start_canary_trap():
    """Starts the P7 Canary Trap monitor in a background process."""
    global CANARY_MONITOR_PID
    logger.info("🚨 Bootstrapping Protocol 7 (Canary Trap)...")

    if not os.path.exists("canary_monitor.py"):
        logger.error("❌ canary_monitor.py not found! Aborting.")
        sys.exit(1)

    try:
        # Launch run_canary_monitor script in background
        proc = subprocess.Popen([sys.executable, "canary_monitor.py"])
        CANARY_MONITOR_PID = proc.pid
        logger.info(f"✅ Canary Monitor active (PID: {CANARY_MONITOR_PID})")
        time.sleep(1) # Warmup
    except Exception as e:
logger.critical(f"Failed to start Canary Monitor: {e}")
        sys.exit(1)

def stop_canary_trap():
    """Cleanup canary monitor process on exit."""
    if CANARY_MONITOR_PID:
        logger.info("Stopping Canary Monitor...")
        try:
            # Use SIGTERM for graceful shutdown
            os.kill(CANARY_MONITOR_PID, signal.SIGTERM)
        except Exception as e:
logger.warning(f"Error stopping canary trap: {e}")

def start_watchdog():
    """Starts the P5 Dead Man's Switch as a background subprocess."""
    global WATCHDOG_PID
    logger.info("🛡️  Bootstrapping Protocol 5 (Watchdog)...")

    # Check if watchdog script exists
    if not os.path.exists("watchdog_sidecar.py"):
        logger.error("❌ watchdog_sidecar.py not found! Aborting.")
        sys.exit(1)

    # Launch in background
    # using preexec_fn=os.setsid to ensure we can kill the whole group if needed (Unix)
    # On Windows, creationflags=subprocess.CREATE_NEW_CONSOLE could be used
    try:
        if sys.platform == "win32":
            proc = subprocess.Popen([sys.executable, "watchdog_sidecar.py"],
                                    creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            proc = subprocess.Popen([sys.executable, "watchdog_sidecar.py"])

        WATCHDOG_PID = proc.pid
        logger.info(f"✅ Watchdog active (PID: {WATCHDOG_PID})")
        time.sleep(1) # Warmup
    except Exception as e:
logger.critical(f"Failed to start Watchdog: {e}")
        sys.exit(1)

def stop_watchdog():
    """Cleanup watchdog process on exit."""
    if WATCHDOG_PID:
        logger.info("Stopping Watchdog...")
        try:
            if sys.platform == "win32":
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(WATCHDOG_PID)])
            else:
                os.kill(WATCHDOG_PID, signal.SIGTERM)
        except Exception as e:
logger.warning(f"Error stopping watchdog: {e}")

def run_live_test(target_url: str, user_name: str):
    """Executes the full Resume Generation Workflow."""
    logger.info(f"🚀 Starting Live Fire Test for target: {target_url}")

    # Mock tools for testing
    mock_tools = {
        'fetch': lambda url, max_length=None: f"Mock job description from {url}",
        'search_nodes': lambda query: '{"entities": []}',
        'search_records': lambda query, index, top_k, namespace: '[{"text": "Mock template"}]',
        'write_file': lambda path, content: None,
        'add_observations': lambda observations: None
    }

    # 1. Trigger the Generation (Protocols 3 & 4 run inside this call)
    # Note: resume_engine.py should have P3 (Firewall) and P4 (Fact Checker) integrated.
    result = generate_personalized_cover_letter(target_url, user_name, "output.txt", mock_tools, logger)

    # 2. Analyze Result
    status = result.get("status")

    if status == "success" or status == "optimized":
        logger.info("✅ SUCCESS: Workflow completed without security violations.")
        logger.info(f"📂 Output saved to: {result.get('file_path', 'Unknown')}")
    elif status == "FAILED":
        reason = result.get("reason")
        details = result.get("details")

        if reason == "SECURITY_VIOLATION":
            logger.warning(f"🛡️  BLOCKED BY PROTOCOL 3 (FIREWALL): {details}")
        elif reason == "HALLUCINATION_DETECTED":
            logger.warning(f"🛡️  BLOCKED BY PROTOCOL 4 (TRUTH ANCHOR): {details}")
        else:
            logger.error(f"❌ Workflow Failed: {reason} - {details}")
    else:
        logger.info(f"ℹ️  Workflow completed with status: {status}")

def signal_handler(sig, frame):
    logger.info("\nCaught interrupt. Shutting down...")
    stop_watchdog()
    sys.exit(0)

if __name__ == "__main__":
    # Register cleanup
    signal.signal(signal.SIGINT, signal_handler)

    # 1. Start Immune System - P7 is the highest priority defense
    start_canary_trap()
    start_watchdog() # P5 runs after P7

    # 2. Define Test Inputs
    # Real URL for realism (though our mock fetcher might just use the string)
    TEST_URL = "https://www.ycombinator.com/jobs/role/123-senior-engineer"
    USER_NAME = "Matthew Wallace"

    try:
        run_live_test(TEST_URL, USER_NAME)
    finally:
        # Ensure cleanup runs even if code crashes
        stop_canary_trap()
        stop_watchdog()

