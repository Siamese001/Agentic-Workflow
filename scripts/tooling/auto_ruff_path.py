logger = logging.getLogger(__name__)
# scripts/auto_ruff_path.py
import logging
import sys
import tomllib
from pathlib import Path

pyproject = Path("pyproject.toml")
data = tomllib.loads(pyproject.read_text())
paths = data.setdefault("tool", {}).setdefault("ruff", {}).setdefault("extend-include", [])

for f in sys.argv[1:]:
    rel = Path(f).relative_to(Path.cwd()).as_posix()
    if rel not in paths:
        paths.append(rel)
        pyproject.write_text(tomllib.dumps(data))
