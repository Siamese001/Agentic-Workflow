"""
Quick script to check _from_utils duplicates
"""

from pathlib import Path

project_root = Path(__file__).parent.parent.parent
from_utils = list(project_root.rglob("*_from_utils.py"))
from_utils = [f for f in from_utils if "archives" not in str(f)]
canonicals = []
for f in from_utils:
    canonical = f.parent / f.name.replace("_from_utils.py", ".py")
    if canonical.exists():
        canonicals.append((f, canonical))
if canonicals:
    for _dup, _canon in canonicals:
        pass
