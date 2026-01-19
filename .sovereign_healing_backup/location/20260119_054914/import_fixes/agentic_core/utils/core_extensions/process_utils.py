from __future__ import annotations
"""
Process Management Utilities

Cluster: Process registration and action logging for Watchdog monitoring
Lines: 418-444 from core_utils.py
"""
import logging
import os
import time
from typing import Any
from agentic_core.utils.file_utils import safe_read_file, safe_write_file

def register_process(pid_file_path: str='run/agent.pid') -> Any:
    """Writes the current process ID to the PID file."""
    try:
        os.makedirs(os.path.dirname(pid_file_path), exist_ok=True)
        with open(pid_file_path, 'w') as f:
            f.write(str(os.getpid()))
        logging.info(f'Process registered. PID: {os.getpid()}')
    except Exception as e:
        logging.error(f'Failed to register PID: {e}')

def log_action(action_name: str, details: str, log_file: str='logs/agent_actions.log') -> Any:
    """
    Logs an operational action for the Watchdog to see.
    Keyword 'ACTION_EXECUTED' is mandatory for the trigger.
    """
    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        timestamp: Any = time.strftime('%Y-%m-%d %H:%M:%S')
        with open(log_file, 'a') as f:
            f.write(f'[{timestamp}] ACTION_EXECUTED: {action_name} - {details}\n')
    except Exception as e:
        logging.error(f'Failed to log action: {e}')
