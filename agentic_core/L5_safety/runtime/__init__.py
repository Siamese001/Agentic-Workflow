"""
Runtime Safety Module - Operational Layer Protection.

Landmine #8 & #9 Prevention: Environment Corruption and Zombie Processes.

This module provides:
- ProcessGuard: Singleton for tracking and cleaning up spawned processes
- safe_run: Secure subprocess wrapper with command validation
"""

from agentic_core.L5_safety.runtime.process_guard import ProcessGuard, SecurityViolation
from agentic_core.L5_safety.runtime.safe_subprocess import safe_run

__all__ = ["ProcessGuard", "SecurityViolation", "safe_run"]
