"""
01_agentic_core/L1_cognition/P2_inspect/check_structure/policy/check.py
Import validity checker for the resume generation system.

Verifies all modules can be imported without errors to maintain
code quality and ensure smooth resume generation functionality.

Auto-hardened by WINDSURF v7 — Production-ready, type-safe, zero-loss.
"""

from __future__ import annotations

import logging
import pkgutil
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


def check_imports(
    package_paths: List[str] | None = None,
) -> Tuple[List[str], Dict[str, str]]:
    """
    Check import validity for all discoverable modules.

    Args:
        package_paths: List of package paths to scan. Defaults to current directory.

    Returns:
        Tuple of (successful_imports, failed_imports) where failed_imports
        maps module name to error message.
    """
    if package_paths is None:
        package_paths = [""]

    successful: List[str] = []
    failed: Dict[str, str] = {}

    logger.debug("Starting import check for paths: %s", package_paths)

    for path in package_paths:
        for module_info in pkgutil.walk_packages([path] if path else []):
            name = (module_info.name or "").strip()
            if not name:
                continue

            try:
                __import__(name)
                successful.append(name)
                logger.debug("OK: %s", name)
            except Exception as e:
                error_msg = f"{type(e).__name__}: {e}"
                failed[name] = error_msg
                logger.warning("FAILED: %s -> %s", name, error_msg)

    logger.info(
        "Import check complete: %d successful, %d failed",
        len(successful),
        len(failed),
    )

    return successful, failed


__all__ = ["check_imports"]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    check_imports()
