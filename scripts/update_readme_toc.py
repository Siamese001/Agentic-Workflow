# scripts/update_readme_toc.py
import sys
from pathlib import Path

readme = Path("README.md")
text = readme.read_text()

for f in sys.argv[1:]:
    rel = Path(f).relative_to(Path.cwd()).as_posix()
    if rel not in text:
        text += f"\n- `{rel}`"

readme.write_text(text)
