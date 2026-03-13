"""conftest for apps_exec tests — ensures repo root is on sys.path."""

import sys
from pathlib import Path

_ROOT = str(Path(__file__).parent.parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
