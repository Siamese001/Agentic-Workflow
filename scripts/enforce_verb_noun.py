# scripts/enforce_verb_noun.py
import re
import shutil
import sys
from pathlib import Path

for f in sys.argv[1:]:
    p = Path(f)
    if re.match(r"^[a-z]+_[a-z_]+\.py$", p.name):
        continue
    if p.parent.name.startswith("L2_"):
        new = p.parent / f"invoke_{p.stem}.py"
    else:
        new = p.parent / f"retrieve_{p.stem}.py"
    shutil.move(p, new)
    print(f"Renamed {p.name} → {new.name}")
