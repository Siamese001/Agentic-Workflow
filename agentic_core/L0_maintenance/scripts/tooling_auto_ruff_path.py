import logging

_logger = logging.getLogger(__name__)
# scripts/auto_ruff_path.py
import sys
import tomllib
from pathlib import Path

PYPROJECT = Path("pyproject.toml")
DATA = tomllib.loads(PYPROJECT.read_text())
PATHS = DATA.setdefault("tool", {}).setdefault("ruff", {}).setdefault("extend-include", [])

for f in sys.argv[1:]:
    REL = Path(f).relative_to(Path.cwd()).as_posix()
    if REL not in PATHS:
        PATHS.append(REL)
        PYPROJECT.write_text(tomllib.dumps(DATA))