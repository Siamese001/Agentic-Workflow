"""ADG incremental update proxy - imports from actual location."""
# This file proxies to the actual adg_incremental_update.py location

import sys
from pathlib import Path

# Add parent of parent.parent to path to reach tools/
tools_dir = Path(__file__).parent.parent.parent.parent
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

# Re-export main function
from tools.adg_incremental_update import (
    ADGIncrementalUpdater,
    main,
    update_adg_for_files,
)

__all__ = [
    "ADGIncrementalUpdater",
    "main",
    "update_adg_for_files",
]
