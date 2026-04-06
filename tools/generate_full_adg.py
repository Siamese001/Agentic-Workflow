"""Compatibility wrapper for ADG generation entrypoint.

Allows legacy invocation:
    python tools/generate_full_adg.py

Delegates to:
    tools/generate/generate_full_adg.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.generate.generate_full_adg import main


if __name__ == "__main__":
    main()
