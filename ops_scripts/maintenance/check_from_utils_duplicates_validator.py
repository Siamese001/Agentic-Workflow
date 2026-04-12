"""
Quick script to check _from_utils duplicates
"""

from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)

project_root = Path(__file__).parent.parent.parent
from_utils = list(project_root.rglob("*_from_utils.py"))
from_utils = [f for f in from_utils if ARCHIVES_DIR not in str(f)]
print(f"Total _from_utils files: {len(from_utils)}")
canonicals = []
for f in from_utils:
    canonical = f.parent / f.name.replace("_from_utils.py", ".py")
    if canonical.exists():
        canonicals.append((f, canonical))
print(f"Files with canonical versions: {len(canonicals)}")
if canonicals:
    print("\nDuplicates found:")
    for dup, canon in canonicals:
        print(f"  {dup.relative_to(project_root)} -> {canon.relative_to(project_root)}")
