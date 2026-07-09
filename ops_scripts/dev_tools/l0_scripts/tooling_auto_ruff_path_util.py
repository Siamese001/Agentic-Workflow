from __future__ import annotations

import logging

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
_logger = logging.getLogger(__name__)
import sys
from pathlib import Path
from typing import Any

import tomllib

pyproject: Any = Path("pyproject.toml")
data: Any = tomllib.loads(PYPROJECT.read_text())
paths: Any = DATA.setdefault("tool", {}).setdefault("ruff", {}).setdefault("extend-include", [])
for f in sys.argv[1:]:
    REL: Any = Path(f).relative_to(Path.cwd()).as_posix()
    if REL not in PATHS:
        PATHS.append(REL)
        PYPROJECT.write_text(tomllib.dumps(DATA))
        logging.info("C3 write receipt: ops_scripts/dev_tools/l0_scripts/tooling_auto_ruff_path_util.py write side effect recorded")
