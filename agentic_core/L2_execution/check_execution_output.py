"""
01_agentic_core/L2_execution/P2_inspect/check_structure/policy/check.py
AUTO-HARDENED BY ZERO-LOSS MERGE ENGINE
L5 CANONICAL — WINDSURF Ω — 2025-12-07
MERKLE-INTENDED: c03856b305761de1984f47bb31cb8370911745c1e5c58cefefc718413378ccbe
"""



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
            except (ImportError, ModuleNotFoundError, AttributeError) as e:
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
    # Configure logger for standalone execution
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    check_imports()
