#!/usr/bin/env python3
"""
P5 Dead Man's Switch Watchdog for Agentic Workflow
Monitors agent processes for rapid action bursts and kills if needed
"""

import logging
import os
import signal
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from functools import wraps
from threading import Lock, Thread

# Configure logging
logger = logging.getLogger(__name__)


class DeadManSwitch:
    """
    Dead Man's Switch that monitors agent actions.
    Kills process if rapid burst detected.
    """

    def __init__(self, max_actions: int = 10, time_window: int = 300):
        """
        Initialize Dead Man's Switch.

        Args:
            max_actions: Maximum allowed actions in time window
            time_window: Time window in seconds (default 5 minutes)
        """
        self.max_actions = max_actions
        self.time_window = time_window
        self.action_counts = defaultdict(deque)
        self.lock = Lock()
        self.monitoring = False
        self.monitor_thread = None

    def track_action(self, agent_name: str, action_type: str):
        """
        Track an action for monitoring.

        Args:
            agent_name: Name of the agent
            action_type: Type of action being tracked
        """
        with self.lock:
            now = datetime.now()
            action_key = f"{agent_name}:{action_type}"

            # Add current action timestamp
            self.action_counts[action_key].append(now)

            # Remove old actions outside time window
            cutoff = now - timedelta(seconds=self.time_window)
            while (self.action_counts[action_key] and
                   self.action_counts[action_key][0] < cutoff):
                self.action_counts[action_key].popleft()

            # Check if threshold exceeded
            if len(self.action_counts[action_key]) > self.max_actions:
                logger.critical(f"P5_KILL_TRIGGER: {agent_name} exceeded {self.max_actions} {action_type} actions in {self.time_window}s")
                self.kill_agent(agent_name)

    def kill_agent(self, agent_name: str):
        """
        Kill the agent process.

        Args:
            agent_name: Name of the agent to kill
        """
        logger.critical(f"P5_KILL_AGENT: Terminating agent {agent_name}")
        os.kill(os.getpid(), signal.SIGTERM)

    def start_monitoring(self):
        """Start background monitoring thread."""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("P5_MONITOR_START: Dead Man's Switch monitoring active")

    def stop_monitoring(self):
        """Stop background monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
            logger.info("P5_MONITOR_STOP: Dead Man's Switch monitoring stopped")

    def _monitor_loop(self):
        """Background monitoring loop."""
        while self.monitoring:
            time.sleep(60)  # Check every minute
            with self.lock:
                # Clean up old entries
                now = datetime.now()
                cutoff = now - timedelta(seconds=self.time_window)

                for action_key in list(self.action_counts.keys()):
                    while (self.action_counts[action_key] and
                           self.action_counts[action_key][0] < cutoff):
                        self.action_counts[action_key].popleft()

                    # Remove empty entries
                    if not self.action_counts[action_key]:
                        del self.action_counts[action_key]


# Global Dead Man's Switch instance
_dead_man_switch = None


def get_dead_man_switch() -> DeadManSwitch:
    """Get global Dead Man's Switch instance."""
    global _dead_man_switch
    if _dead_man_switch is None:
        _dead_man_switch = DeadManSwitch()
        _dead_man_switch.start_monitoring()
    return _dead_man_switch


def watchdog(max_actions: int = 10, time_window: int = 300):
    """
    Decorator to add P5 watchdog monitoring to functions.

    Args:
        max_actions: Maximum allowed actions in time window
        time_window: Time window in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get agent name from function or class
            agent_name = getattr(wrapper, '_agent_name', func.__name__)
            action_type = getattr(wrapper, '_action_type', func.__name__)

            # Track action before execution
            get_dead_man_switch().track_action(agent_name, action_type)

            # Execute function
            return func(*args, **kwargs)

        # Set metadata for decorator
        wrapper._watchdog_max_actions = max_actions
        wrapper._watchdog_time_window = time_window

        return wrapper
    return decorator


def track_action(agent_name: str, action_type: str):
    """
    Track an action manually (for non-decorated functions).

    Args:
        agent_name: Name of the agent
        action_type: Type of action
    """
    get_dead_man_switch().track_action(agent_name, action_type)


# Initialize global instance on import
get_dead_man_switch()
