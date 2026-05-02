"""Find DEFERRED_SCOPE markers across all plan files + scan qna/underwriting source."""
from pathlib import Path
import re

plans = Path(".windsurf/plans")
print("=== DEFERRED_SCOPE markers in plan files ===")
for p in sorted(plans.glob("*.md")):
    src = p.read_text(encoding="utf-8", errors="ignore")
    for m in re.finditer(r"DEFERRED_SCOPE:[^\n]+", src):
        print(f"  {p.name}: {m.group()[:200]}")

print()
print("=== Plan status + target app ===")
for p in sorted(plans.glob("*.md")):
    src = p.read_text(encoding="utf-8", errors="ignore")
    lines = src.splitlines()
    # Extract plan title + status
    title = lines[0] if lines else ""
    status_m = re.search(r"\*\*Status:\*\*\s*(.+)", src)
    status = status_m.group(1).strip() if status_m else "?"
    if any(k in src.lower() for k in ("apps_qna", "apps_underwriting")):
        print(f"  {p.name}")
        print(f"    title: {title}")
        print(f"    status: {status}")

print()
print("=== apps_qna deferred/TODO markers in source ===")
qna = Path("apps_qna")
for py in sorted(qna.rglob("*.py")):
    if "__pycache__" in str(py): continue
    try:
        src = py.read_text(encoding="utf-8")
    except Exception:
        continue
    for i, line in enumerate(src.splitlines(), 1):
        if re.search(r"\b(TODO|FIXME|XXX|DEFERRED|NotImplementedError|raise NotImplementedError)\b", line):
            print(f"  {py}:{i}: {line.strip()[:150]}")
