"""Testing accelerator proxy - imports from actual location."""
# This file proxies to the actual adg_test_accelerator.py location
# to maintain unified import structure while keeping files in their original locations

import sys
from pathlib import Path

# Add parent of parent to path to reach tools/
tools_dir = Path(__file__).parent.parent.parent.parent
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

# Import and re-export everything from the actual location
from tools.adg_test_accelerator import (
    DEFAULT_MAX_DEPTH,
    DEFAULT_TOP_N,
    DEFAULT_WORKERS,
    MODULE_PREFIX,
    PROBLEM_FILE_DISPLAY_LIMIT,
    SYMBOL_PREFIX,
    ADGIndex,
    _is_production,
    _logger,
    _module_adg_to_path,
    _symbol_to_path,
    main,
)

__all__ = [
    "ADGIndex",
    "DEFAULT_MAX_DEPTH",
    "DEFAULT_TOP_N",
    "DEFAULT_WORKERS",
    "MODULE_PREFIX",
    "PROBLEM_FILE_DISPLAY_LIMIT",
    "SYMBOL_PREFIX",
    "_is_production",
    "_logger",
    "_module_adg_to_path",
    "_symbol_to_path",
    "main",
]
