import time
import os
import signal
import threading
import logging
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

# Configuration
CANARY_FILE_PATH = os.path.abspath("config/secrets_canary.txt")
TERMINATE_PID_PATH = "run/agent.pid" # Re-uses P5 PID file

logger = logging.getLogger("CanaryTrap")
logging.basicConfig(level=logging.INFO, format='%(asctime)s [CANARY] %(message)s')

class CanaryEventHandler(FileSystemEventHandler):
    """Handles filesystem events (read/write/delete) on the canary file."""
    
    def on_any_event(self, event: FileSystemEvent):
        """Called on any file event (created, deleted, modified, moved)."""
        # We are primarily interested in ACCESS or MODIFIED events on the canary file itself
        
        # NOTE: On Linux (inotify), ACCESS is often reliable for reads. 
        # On Windows/MacOS, we primarily rely on MODIFIED/CLOSED events.
        
        if os.path.abspath(event.src_path) == CANARY_FILE_PATH:
            # Check if this process initiated the event to avoid self-trap (optional)
            # This requires advanced process monitoring which we omit for the MVP.
            
            logger.critical(f"🚨 PROTOCOL 7 VIOLATION! Canary File accessed: {event.event_type}")
            
            # Initiate Emergency Shutdown
            CanaryMonitor.terminate_agent()
            
class CanaryMonitor:
    def __init__(self):
        self.observer = Observer()
        self.event_handler = CanaryEventHandler()
        self.target_dir = os.path.dirname(CANARY_FILE_PATH)
        
    def start(self):
        """Starts the filesystem monitoring thread."""
        if not os.path.exists(CANARY_FILE_PATH):
            logger.error(f"❌ Canary file not found at {CANARY_FILE_PATH}. Aborting monitor.")
            return

        logger.info(f"Setting up Canary Trap monitor on {self.target_dir}")
        self.observer.schedule(self.event_handler, self.target_dir, recursive=False)
        self.observer.start()
        logger.info("✅ Canary Monitor thread started.")
        
    def stop(self):
        """Stops the observer thread."""
        self.observer.stop()
        self.observer.join()
        logger.info("Canary Monitor stopped.")

    @staticmethod
    def terminate_agent():
        """Reads the agent PID and kills the process."""
        try:
            with open(TERMINATE_PID_PATH, 'r') as f:
                pid = int(f.read().strip())
        except (ValueError, FileNotFoundError):
            logger.error("❌ Cannot find agent PID for termination.")
            sys.exit(1) # Kill the monitor itself if it can't kill the agent
            
        logger.critical(f"🔥 EMERGENCY SHUTDOWN: Killing Agent PID {pid} to contain breach.")
        try:
            # Use SIGTERM on Windows, SIGKILL on Unix
            if sys.platform == "win32":
                os.kill(pid, signal.SIGTERM)
            else:
                os.kill(pid, signal.SIGKILL)
            logger.info("Agent process terminated.")
        except ProcessLookupError:
            logger.warning(f"PID {pid} not found (already dead).")
        except PermissionError:
            logger.error(f"❌ Permission denied to kill PID {pid}.")
            
        sys.exit(1) # Ensure the monitor also exits

def run_canary_monitor():
    monitor = CanaryMonitor()
    monitor.start()
    try:
        while monitor.observer.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        monitor.stop()

if __name__ == "__main__":
    # Note: Requires 'pip install watchdog'
    run_canary_monitor()
