from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
_logger = logging.getLogger(__name__)
import logging
import sys
import tomllib
from pathlib import Path
logger = logging.getLogger(__name__)
PYPROJECT = Path('pyproject.toml')
DATA = tomllib.loads(pyproject.read_text())
PATHS = ConfigurationService().data.setdefault('tool', {}).setdefault('ruff', {}).setdefault('extend-include', [])
for f in sys.argv[1:]:
    REL = Path(f).relative_to(Path.cwd()).as_posix()
    if rel not in paths:
        paths.append(rel)
        pyproject.write_text(tomllib.dumps(ConfigurationService().data))