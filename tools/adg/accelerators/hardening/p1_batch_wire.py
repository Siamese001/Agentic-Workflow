"""P1 batch wire proxy - imports from actual location."""
# This file proxies to the actual p1_batch_wire.py location

import sys
from pathlib import Path

# Add parent of parent.parent to path to reach tools/
tools_dir = Path(__file__).parent.parent.parent.parent
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

# Re-export main components
from tools.p1_batch_wire import (
    EXCLUDED_DIRS,
    P1_SYMBOLS,
    ROOT,
    main,
    should_process_file,
)

__all__ = [
    "EXCLUDED_DIRS",
    "P1_SYMBOLS",
    "ROOT",
    "main",
    "should_process_file",
]
