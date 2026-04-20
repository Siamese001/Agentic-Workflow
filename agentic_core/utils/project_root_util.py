"""Dynamic project root resolution utility."""

import os
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR


def _validated_root(candidate: Path | None) -> Path | None:
    if candidate is None:
        return None
    try:
        resolved = candidate.expanduser().resolve(strict=True)
    except (OSError, RuntimeError):  # guardian: allow-return-none-swallow -- path resolution: non-fatal, caller falls back to None
        return None
    if (resolved / ".git").is_dir() and (resolved / AGENTIC_CORE_DIR).is_dir():
        return resolved
    return None


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
    current = (start_path or Path(__file__).resolve()).expanduser().resolve()
    if current.is_file():
        current = current.parent
    while current != current.parent:
        validated = _validated_root(current)
        if validated is not None:
            return validated
        current = current.parent
    # guardian: allow-global-mutation
    env_root = _validated_root(Path(os.environ["PROJECT_ROOT"])) if "PROJECT_ROOT" in os.environ else None
    if env_root is not None:
        return env_root
    raise RuntimeError(
        f"Could not find project root starting from {start_path}. Ensure you're in a git repository.",
    )


def get_project_root_safe(start_path: Path | None = None) -> Path:
    """
    Get project root with fallback to known location if .git not found.
    Used only for test files where .git might not be available.
    """
    try:
        return get_project_root(start_path)
    except RuntimeError:  # guardian: allow-silent-swallow - acceptable exception handling
        current = (start_path or Path(__file__).resolve()).expanduser().resolve()
        if current.is_file():
            current = current.parent
        while current != current.parent:
            validated = _validated_root(current)
            if validated is not None:
                return validated
            if (current / AGENTIC_CORE_DIR).is_dir():
                return current
            current = current.parent
        known_roots = [Path.cwd() / "Agentic-Workflow", Path.home() / "Git" / "Agentic-Workflow"]
        for root in known_roots:
            validated = _validated_root(root)
            if validated is not None:
                return validated
            if root.exists() and (root / AGENTIC_CORE_DIR).is_dir():
                return root.resolve()
        raise RuntimeError("Could not determine project root")


PROJECT_ROOT = get_project_root_safe()
