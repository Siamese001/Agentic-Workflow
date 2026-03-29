"""Full ADG generator proxy - imports from actual location."""
# This file proxies to the actual generate_full_adg.py location

import sys
from pathlib import Path

# Add parent of parent.parent to path to reach tools/
tools_dir = Path(__file__).parent.parent.parent.parent
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

# Re-export main function
from tools.generate_full_adg import (
    ROOT,
    generate_adg,
    main,
)

__all__ = [
    "ROOT",
    "generate_adg",
    "main",
]
