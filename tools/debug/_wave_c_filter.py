"""Filter Wave C dead-module candidates: exclude those re-exported via parent __init__.py."""
from __future__ import annotations

import pathlib
import re
from collections import Counter, defaultdict

targets = pathlib.Path("artifacts/adg/wave_c_targets.txt").read_text().splitlines()
by_dir: dict[str, list[str]] = defaultdict(list)
for t in targets:
    by_dir[str(pathlib.Path(t).parent).replace("\\", "/")].append(t)

truly_dead: list[str] = []
excluded: list[str] = []
for d, files in by_dir.items():
    init = pathlib.Path(d) / "__init__.py"
    if not init.exists():
        truly_dead.extend(files)
        continue
    txt = init.read_text(encoding="utf-8", errors="replace")
    dotted = d.replace("/", ".")
    for f in files:
        stem = pathlib.Path(f).stem
        patterns = [
            rf"\bfrom\s+\.{re.escape(stem)}\b",
            rf"\bfrom\s+{re.escape(dotted)}\.{re.escape(stem)}\b",
            rf"\.{re.escape(stem)}\s+import",
        ]
        if any(re.search(p, txt) for p in patterns):
            excluded.append(f)
        else:
            truly_dead.append(f)

print(f"TRULY DEAD: {len(truly_dead)}")
print(f"EXCLUDED (parent __init__.py re-exports): {len(excluded)}")
bydir = Counter(str(pathlib.Path(d).parent).replace("\\", "/") for d in truly_dead)
for k, v in sorted(bydir.items(), key=lambda x: -x[1]):
    print(f"  {v:3d}  {k}")

pathlib.Path("artifacts/adg/wave_c_targets.txt").write_text(
    "\n".join(truly_dead) + "\n", encoding="utf-8"
)
print("rewrote artifacts/adg/wave_c_targets.txt")
