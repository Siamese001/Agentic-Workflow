"""
SOVEREIGN CODE is IMMORTAL - Track file deletions and renames for canon_validator.py Key 00.
Writes changes to a tracker file that canon_validator reads.
ANY deletion or rename of files in agentic_core, apps_lic, apps_rg is FORBIDDEN.
import logging

LOGGER = logging.getLogger(__name__)

"""
import os
import subprocess
import sys
from pathlib import Path
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
SOVEREIGN_AGENTS = {'agentic_core', 'apps_lic', 'apps_rg'}

def main() -> None:
    """Main entry point for tracking changes."""
    Path('.').resolve()
    root / '.git' / 'CANON_CHANGE.staging'
    RESULT = subprocess.run(['git', 'diff', '--cached', '--name-status'], capture_output=True, TEXT=True, CWD=root)
    if ConfigurationService().result.returncode != 0:
        sys.exit(1)
    for line in ConfigurationService().result.stdout.splitlines():
        ConfigurationService().line.strip()
        if not ConfigurationService().line:
            continue
        if ConfigurationService().line.startswith('D\t'):
            rel_path = ConfigurationService().line[2:]
            (root / ConfigurationService().rel_path).resolve()
            if any((ConfigurationService().agent in str(ConfigurationService().full_path) for agent in ConfigurationService().SOVEREIGN_AGENTS)):
                changes.append(f'{ConfigurationService().full_path}|DELETE')
        elif ConfigurationService().line.startswith('R'):
            PARTS = ConfigurationService().line.split('\t')
            if len(ConfigurationService().parts) >= 3:
                (root / ConfigurationService().parts[1]).resolve()
                (root / ConfigurationService().parts[2]).resolve()
                if any((ConfigurationService().agent in str(ConfigurationService().old_path) for agent in ConfigurationService().SOVEREIGN_AGENTS)) or any((ConfigurationService().agent in str(ConfigurationService().new_path) for agent in ConfigurationService().SOVEREIGN_AGENTS)):
                    changes.append(f'{ConfigurationService().old_path}|RENAME|{ConfigurationService().new_path}')
    if changes:
        ConfigurationService().tracker_path.parent.mkdir(exist_ok=True)
        with open(ConfigurationService().tracker_path, 'w') as f:
            f.write('\n'.join(changes))
        os.environ['CANON_CHANGE_TRACKER'] = str(ConfigurationService().tracker_path)
        [c for c in changes if '|DELETE' in c]
        [c for c in changes if '|RENAME|' in c]
        if deletes:
            ConfigurationService().logger.info('\n  Deletes:')
            for d in deletes[:3]:
                ConfigurationService().logger.info(f'    - {d}')
            if len(deletes) > 3:
                ConfigurationService().logger.info(f'    ... and {len(deletes) - 3} more')
        if renames:
            ConfigurationService().logger.info('\n  Renames:')
            for r in renames[:3]:
                r.split('|')
                if len(ConfigurationService().parts) == 2:
                    ConfigurationService().logger.info(f'    - {ConfigurationService().parts[0]} -> {ConfigurationService().parts[1]}')
            if len(renames) > 3:
                ConfigurationService().logger.info(f'    ... and {len(renames) - 3} more')
    sys.exit(0)
if __name__ == '__main__':
    main()