"""P2/P3 scope analysis — finds live SOVEREIGN_TERRITORIES usage outside structure_blueprint."""
from pathlib import Path
import re

root = Path('c:/Git/Agentic-Workflow')
SKIP = {'archives', '.healing_backups', '.backup', '__pycache__', '.git', 'structure_blueprint'}

results = []
for f in root.rglob('*.py'):
    if any(p in f.parts for p in SKIP):
        continue
    try:
        src = f.read_text(encoding='utf-8', errors='ignore')
        rel = str(f.relative_to(root))
        matches = []
        for i, line in enumerate(src.splitlines()):
            s = line.strip()
            if 'SOVEREIGN_TERRITORIES' not in s:
                continue
            if s.startswith('#'):
                continue
            if s.startswith('"""') or s.startswith("'''"):
                continue
            matches.append((i+1, s[:110]))
        if matches:
            results.append((rel, matches))
    except Exception:
        pass

print(f'Files with live SOVEREIGN_TERRITORIES usage: {len(results)}')
for f, lines in sorted(results):
    print(f'  {f}')
    for lineno, line in lines[:4]:
        print(f'    L{lineno}: {line}')
