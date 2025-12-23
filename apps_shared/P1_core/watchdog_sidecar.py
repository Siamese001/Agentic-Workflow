from typing import Any, Optional, Protocol, Dict, List

import logging
import os
import signal
import time
from typing import List

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [WATCHDOG] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("Watchdog")

class DeadManSwitch:
    def __init__(self, log_file: str, pid_file: str, max_actions: int = 5, window_seconds: int = 60):
        self.log_file = log_file
        self.pid_file = pid_file
        self.max_actions = max_actions
        self.window_seconds = window_seconds
        self.action_timestamps: List[float] = []

    def get_target_pid(self) -> int:
        """Reads the PID of the agent from the lock file."""
        if not os.path.exists(self.pid_file):
            return None
        try:
            with open(self.pid_file, 'r') as f:
                return int(f.read().strip())
        except (ValueError, FileNotFoundError):
            return None

    def kill_agent(self, pid: int):
        """Terminates the agent process immediately."""
        logger.critical(f"[ALERT] RUNAWAY DETECTED! Killing PID {pid}...")
        try:
            # Cross-platform process termination
            if os.name == 'nt':  # Windows
                os.kill(pid, signal.SIGTERM)
            else:  # Unix/Linux
                os.kill(pid, signal.SIGKILL)
            logger.info(f"[OK] PID {pid} successfully terminated.")

            # Optional: Send Alert (Email/Slack)
            # send_alert("Agent killed due to spam loop.")

        except ProcessLookupError:
            logger.warning(f"PID {pid} not found (already dead?).")
        except PermissionError:
            logger.error(f"[X] Permission denied killing PID {pid}.")

    def monitor(self):
        """Main loop: Tails the log file and counts actions."""
        logger.info(f"Monitoring {self.log_file} (Threshold: {self.max_actions} actions / {self.window_seconds}s)...")

        # Ensure log file exists
        if not os.path.exists(self.log_file):
            open(self.log_file, 'a').close()

        with open(self.log_file, 'r') as f:
            # Seek to end of file to ignore past history
            f.seek(0, os.SEEK_END)

            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.1) # efficient polling
                    continue

                # Check for "ACTION" keyword (Protocol convention)
                if "ACTION_EXECUTED" in line:
                    now = time.time()
                    self.action_timestamps.append(now)
                    logger.debug(f"Action detected at {now}")

                    # Prune old timestamps
                    self.action_timestamps = [t for t in self.action_timestamps if now - t <= self.window_seconds]

                    count = len(self.action_timestamps)
                    logger.info(f"Activity Level: {count}/{self.max_actions} in last {self.window_seconds}s")

                    if count > self.max_actions:
                        pid = self.get_target_pid()
                        if pid:
                            self.kill_agent(pid)
                            break # Stop monitoring after kill
                        else:
                            logger.error("Runaway detected but PID file missing/invalid!")

if __name__ == "__main__":
    # Default Config
    LOG_PATH = "logs/agent_actions.log"
    PID_PATH = "run/agent.pid"

    # Ensure directories exist
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(PID_PATH), exist_ok=True)

    watchdog = DeadManSwitch(LOG_PATH, PID_PATH)
    try:
        watchdog.monitor()
    except KeyboardInterrupt:
        logger.info("Watchdog stopped by user.")

