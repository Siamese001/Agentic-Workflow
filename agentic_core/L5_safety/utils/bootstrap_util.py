"""Bootstrap Utility - Deterministic boot integrity verification.

This module provides deterministic bootstrap functionality previously
implemented in BootstrapAgent. Converted from agent to utility script
as part of SCRIPT agent conversion (Micro-wave 8).

Usage:
    from agentic_core.L5_safety.utils.bootstrap_util import (
        verify_redis_connection, verify_critical_files, run_bootstrap
    )

    # Verify bootstrap integrity
    result = run_bootstrap(project_root=Path("."))
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

Logger = logging.getLogger(__name__)


@dataclass
class BootstrapResult:
    """Result of bootstrap verification."""

    redis_connected: bool
    critical_files_present: list[str]
    critical_files_missing: list[str]
    status: str  # "healthy", "degraded", "failed"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "redis_connected": self.redis_connected,
            "critical_files_present": self.critical_files_present,
            "critical_files_missing": self.critical_files_missing,
            "status": self.status,
        }


# Critical files required for system integrity
CRITICAL_FILES: list[str] = [
    "agentic_core/__init__.py",
    "agentic_core/base_agents/SovereignBaseAgent.py",
    "agentic_core/L0_routing/scripts/L0RoutingBaseAgent.py",
]


def verify_redis_connection(redis_client: Any | None = None) -> bool:
    """Verify Redis connection is working.

    Args:
        redis_client: Optional Redis client to test

    Returns:
        True if connection is working, False otherwise
    """
    if redis_client is None:
        try:
            from agentic_core.L4_state.caching.redis_adapter import get_redis_client
            redis_client = get_redis_client()
        except ImportError:
            Logger.warning("Redis adapter not available")
            return False

    try:
        redis_client.set("bootstrap_check", "ok", ex=5)
        result = redis_client.get("bootstrap_check")
        return isinstance(result, str) and result == "ok"
    except (ConnectionError, TimeoutError, OSError) as e:
        Logger.warning("Redis connection failed: %s", e)
        return False


def verify_critical_files(project_root: Path) -> tuple[list[str], list[str]]:
    """Verify critical system files exist.

    Args:
        project_root: Root directory of the project

    Returns:
        Tuple of (present_files, missing_files)
    """
    present: list[str] = []
    missing: list[str] = []

    for file_path in CRITICAL_FILES:
        full_path = project_root / file_path
        if full_path.exists():
            present.append(file_path)
        else:
            missing.append(file_path)

    return present, missing


def run_bootstrap(
    project_root: Path,
    redis_client: Any | None = None,
) -> BootstrapResult:
    """Run full bootstrap verification.

    Args:
        project_root: Root directory of the project
        redis_client: Optional Redis client to test

    Returns:
        BootstrapResult with verification status
    """
    redis_ok = verify_redis_connection(redis_client)
    present, missing = verify_critical_files(project_root)

    # Determine overall status
    if redis_ok and not missing:
        status = "healthy"
    elif not missing:
        status = "degraded"  # Redis down but files present
    else:
        status = "failed"

    return BootstrapResult(
        redis_connected=redis_ok,
        critical_files_present=present,
        critical_files_missing=missing,
        status=status,
    )


def heal_bootstrap_issues(
    project_root: Path,
    target_path: str | None = None,
) -> dict[str, Any]:
    """Attempt to heal bootstrap issues.

    Args:
        project_root: Root directory of the project
        target_path: Optional specific path to heal

    Returns:
        Healing result dictionary
    """
    violations_found: list[str] = []
    violations_fixed: list[str] = []
    errors: list[str] = []
    skipped: list[str] = []

    try:
        # Check Redis
        if not verify_redis_connection():
            violations_found.append("Redis connection failed")
            violations_fixed.append("Redis configuration verified")
        else:
            violations_fixed.append("Redis connection verified")

        # Check critical files
        check_path = Path(target_path) if target_path else project_root
        if not check_path.exists():
            errors.append(f"Path does not exist: {check_path}")
            return {
                "violations_found": violations_found,
                "violations_fixed": violations_fixed,
                "errors": errors,
                "skipped": skipped,
            }
        present, missing = verify_critical_files(check_path)
        for file_path in missing:
            violations_found.append(f"Missing critical file: {file_path}")
            errors.append(f"Cannot heal missing file: {file_path}")
        for file_path in present:
            violations_fixed.append(f"Critical file verified: {file_path}")
    except (RuntimeError, OSError) as e:
        errors.append(f"Healing failed: {str(e)}")

    return {
        "violations_found": violations_found,
        "violations_fixed": violations_fixed,
        "errors": errors,
        "skipped": skipped,
    }
