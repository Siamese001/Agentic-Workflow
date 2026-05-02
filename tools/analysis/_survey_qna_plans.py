"""Survey apps_qna plans for status + deferred items."""
from pathlib import Path
import re

plans = sorted(Path(".windsurf/plans").glob("apps-qna-*.md"))
for p in plans:
    src = p.read_text(encoding="utf-8", errors="ignore")
    # find Status line
    m = re.search(r"\*\*Status:\*\*\s*(.+)", src)
    status = m.group(1).strip() if m else "UNKNOWN"
    # find DEFERRED_SCOPE
    deferred = re.findall(r"DEFERRED_SCOPE:[^\n]+", src)
    # find gap register bullets
    gaps = re.findall(r"## Gap Register[\s\S]*?(?=\n## |\Z)", src)
    # find sections headed "Out of scope" / "deferred"
    oos = re.findall(r"(?:## Out of Scope|## Deferred)[\s\S]*?(?=\n## |\Z)", src, re.IGNORECASE)
    print(f"=== {p.name} ===")
    print(f"  status: {status}")
    print(f"  size: {len(src)} bytes, {len(src.splitlines())} lines")
    if deferred:
        print(f"  DEFERRED_SCOPE markers: {len(deferred)}")
        for d in deferred[:3]:
            print(f"    - {d[:200]}")
    if oos:
        print(f"  Out-of-scope section ({len(oos[0])} chars)")
        for line in oos[0].splitlines()[:15]:
            print(f"    {line}")
    print()
