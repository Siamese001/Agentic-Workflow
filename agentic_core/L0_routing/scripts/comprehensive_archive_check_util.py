from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "comprehensive_archive_check_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "comprehensive_archive_check_util", "p0_governance")
_emit_snapshots_state("p0", "comprehensive_archive_check_util", "state_snapshot")

"Comprehensive check of ALL agents that might have been archived in entire chat history."
import os

from agentic_core.L0_routing.config import ARCHIVES_DIR
from agentic_core.L0_routing.config.path_constants import SOVEREIGN_EXCLUDED_FOLDERS

PROJECT_ROOT = Path("C:/Git/Agentic-Workflow")
l4_active = PROJECT_ROOT / "agentic_core/L4_state/memory/L4Agent.py"
archives_path = PROJECT_ROOT / ARCHIVES_DIR
l4_archived = []
if archives_path.exists():
    for root, dirs, files in os.walk(archives_path):
        dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
        if "L4Agent.py" in files:
            l4_archived.append(Path(root) / "L4Agent.py")
for _path in l4_archived:
    pass
archived_agents = []
if archives_path.exists():
    for root, dirs, files in os.walk(archives_path):
        dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
        if "identity_duplicates" in root:
            continue
        for file in files:
            if file.endswith("Agent.py"):
                rel_path = os.path.relpath(Path(root) / file, archives_path)
                archived_agents.append(rel_path)
by_subdir = {}
for agent in archived_agents:
    subdir = agent.split(os.sep)[0]
    if subdir not in by_subdir:
        by_subdir[subdir] = []
    by_subdir[subdir].append(agent)
for subdir in sorted(by_subdir.keys()):
    agents = by_subdir[subdir]
    for agent in sorted(agents)[:10]:
        pass
    if len(agents) > 10:
        pass
if l4_active.exists() and len(l4_archived) == 0:
    pass
