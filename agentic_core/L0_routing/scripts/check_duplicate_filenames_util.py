import sys
from collections import defaultdict
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "check_duplicate_filenames_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "check_duplicate_filenames_util", "p0_governance")
_emit_snapshots_state("p0", "check_duplicate_filenames_util", "state_snapshot")


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
