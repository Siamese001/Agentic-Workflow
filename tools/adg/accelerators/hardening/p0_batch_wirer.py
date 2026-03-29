"""P0 batch wirer proxy - imports from actual location."""
# This file proxies to the actual p0_batch_wirer.py location

import sys
from pathlib import Path

# Add parent of parent.parent to path to reach tools/
tools_dir = Path(__file__).parent.parent.parent.parent
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

# Re-export main function
from tools.p0_batch_wirer import (
    DIMENSION_CONFIG,
    PROJECT_ROOT,
    main,
)

__all__ = [
    "DIMENSION_CONFIG",
    "PROJECT_ROOT",
    "main",
]
