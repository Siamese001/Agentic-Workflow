"""Dump each apps_qna plan's Out-of-Scope + Gap Register sections verbatim."""
from pathlib import Path
import re

plans = sorted(Path(".windsurf/plans").glob("apps-qna-*.md"))
for p in plans:
    src = p.read_text(encoding="utf-8", errors="ignore")
    # Out-of-scope section
    oos_m = re.search(
        r"## (?:Out[-\s]of[-\s]Scope|Out of Scope)[^\n]*\n([\s\S]*?)(?=\n## |\Z)",
        src,
        re.IGNORECASE,
    )
    gap_m = re.search(
        r"## Gap Register[^\n]*\n([\s\S]*?)(?=\n## |\Z)", src, re.IGNORECASE
    )
    print(f"=== {p.name} ===")
    if oos_m:
        print("  -- Out-of-Scope --")
        for line in oos_m.group(1).splitlines()[:30]:
            if line.strip():
                print(f"    {line}")
    if gap_m:
        print("  -- Gap Register --")
        for line in gap_m.group(1).splitlines()[:15]:
            if line.strip():
                print(f"    {line}")
    print()
