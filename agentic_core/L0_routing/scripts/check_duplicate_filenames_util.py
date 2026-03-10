import sys
from collections import defaultdict
from pathlib import Path

from agentic_core.L5_safety.config.structure_blueprint.ssot import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)


def check_for_duplicates():
    """Scans for identical filenames across different directories."""
    project_root = Path(__file__).parent.parent.parent
    file_map = defaultdict(list)
    exclude = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES
    for path in project_root.rglob("*.py"):
        if any(ex in path.parts for ex in exclude):
            continue
        file_map[path.name].append(path)
    duplicates = {name: paths for name, paths in file_map.items() if len(paths) > 1}
    if duplicates:
        for _name, paths in sorted(duplicates.items()):
            for p in paths:
                p.relative_to(project_root)
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    check_for_duplicates()
