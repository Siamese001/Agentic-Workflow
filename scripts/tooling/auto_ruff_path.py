_logger = logging.getLogger(__name__)
# scripts/auto_ruff_path.py
import sys
import tomllib
from pathlib import Path

PYPROJECT = Path("pyproject.toml")
DATA = tomllib.loads(pyproject.read_text())
PATHS = data.setdefault("tool", {}).setdefault("ruff", {}).setdefault("extend-include", [])

for f in sys.argv[1:]:
    REL = Path(f).relative_to(Path.cwd()).as_posix()
    if rel not in paths:
        paths.append(rel)
        pyproject.write_text(tomllib.dumps(data))
