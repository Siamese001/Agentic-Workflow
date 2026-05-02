"""Dump each apps_qna plan's headings + first 3 lines."""
from pathlib import Path

plans = sorted(Path(".windsurf/plans").glob("apps-qna-*.md"))
for p in plans:
    src = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    print(f"=== {p.name} ===")
    # Show headings
    for line in src:
        if line.startswith("#"):
            print(f"  {line}")
    print()
