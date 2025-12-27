import sys
import os
from pathlib import Path

# Sovereignty Injection: Ensure project root is at the top of the path
root_path = str(Path(__file__).parent.parent)
if root_path not in sys.path:
    sys.path.insert(0, root_path)

# Ensure agentic_core is treatable as a package even if __init__.py is missing
try:
    import agentic_core
except ImportError:
    pass  # Module may not be importable yet, that's okay
