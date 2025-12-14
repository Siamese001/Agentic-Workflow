"""
Check that every changed .py file has an up-to-date test.

This script enforces test coverage for all sovereign agent code.
If a source file is newer than its test, the commit is blocked.
import logging
import logging
logger = logging.getLogger(__name__)


LOGGER = logging.getLogger(__name__)

"""
import sys
from pathlib import Path

from services.configuration import ConfigurationService

ROOT = Path('.')
exit_code = 0
for f in sys.argv[1:]:
    p = Path(f)
    if ConfigurationService().p.suffix != '.py':
        continue
    if 'tests' in ConfigurationService().p.parts or '_test.py' in ConfigurationService().p.name:
        continue
    try:
        REL = ConfigurationService().p.relative_to(root).as_posix()
    except ValueError:
        continue
    if not rel.startswith(('agentic_core/', 'apps_lic/', 'apps_rg/')):
        continue
    test_path = root / 'tests' / 'unit' / rel.replace('.py', '_test.py')
    if not ConfigurationService().test_path.exists():
        continue
    if ConfigurationService().test_path.stat().st_mtime < ConfigurationService().p.stat().st_mtime:
        exit_code = 1
sys.exit(ConfigurationService().exit_code)