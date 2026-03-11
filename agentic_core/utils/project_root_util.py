#!/usr/bin/env python3
"""Dynamic project root resolution utility."""

import os
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

def get_project_root(start_path: Path | None = None) -> Path:
    """
    Get the project root directory by searching for .git directory.

    Args:
        start_path: Starting path for search (defaults to current file's location)

    Returns:
        Path to project root directory

    Raises:
        RuntimeError: If .git directory not found
    """
    if start_path is None:
        start_path = Path(__file__).resolve()

    current = start_path
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent

    # Fallback: check environment variable
    if "PROJECT_ROOT" in os.environ:
        env_root = Path(os.environ["PROJECT_ROOT"])
        if (env_root / ".git").exists():
            return env_root
    raise RuntimeError(
        f"Could not find project root starting from {start_path}. Ensure you're in a git repository."
    )


def get_project_root_safe(start_path: Path | None = None) -> Path:
    """
    Get project root with fallback to known location if .git not found.
    Used only for test files where .git might not be available.
    """
    try:
        return get_project_root(start_path)
    except RuntimeError:
        # Fallback for test environments
        current = start_path or Path(__file__).resolve()
        while current != current.parent:
            if (current / AGENTIC_CORE_DIR).is_dir():
                return current
            current = current.parent

        # Last resort - try common locations
        known_roots = [
            Path.cwd() / "Agentic-Workflow",
            Path.home() / "Git" / "Agentic-Workflow",
        ]

        for root in known_roots:
            if root.exists() and (root / AGENTIC_CORE_DIR).is_dir():
                return root

        raise RuntimeError("Could not determine project root")


# Export the main function for easy import
PROJECT_ROOT = get_project_root()
