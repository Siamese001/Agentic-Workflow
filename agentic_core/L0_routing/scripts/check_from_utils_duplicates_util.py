"""
Quick script to check _from_utils duplicates
"""

from pathlib import Path

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

project_root = Path(__file__).parent.parent.parent
from_utils = list(project_root.rglob("*_from_utils.py"))
from_utils = [f for f in from_utils if ARCHIVES_DIR not in str(f)]
canonicals = []
for f in from_utils:
    canonical = f.parent / f.name.replace("_from_utils.py", ".py")
    if canonical.exists():
        canonicals.append((f, canonical))
if canonicals:
    for _dup, _canon in canonicals:
        pass
