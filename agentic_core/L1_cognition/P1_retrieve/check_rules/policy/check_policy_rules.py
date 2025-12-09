"""
01_agentic_core/L1_cognition/P1_retrieve/check_rules/policy/check.py
AUTO-HARDENED BY ZERO-LOSS MERGE ENGINE
L5 CANONICAL — WINDSURF Ω — 2025-12-07
MERKLE-INTENDED: c238ebf6d2a9adac511fe76e5ae83560ae219101deb01787f647cf4aa5ab5e68
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


def main() -> int:
    """
    Main entry point for import checking.

    Returns:
        Exit code (0 if all imports succeed, 1 if any fail).
    """
    # Configure logger for standalone execution
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)

    successful, failed = check_imports()

    if failed:
        logger.error("Failed imports:")
        for name, error in failed.items():
            logger.error("  %s: %s", name, error)
        return 1

    logger.info("All imports successful")
    return 0


__all__ = ["check_imports", "main"]


if __name__ == "__main__":
    raise SystemExit(main())
