from pathlib import Path

"Comprehensive check of ALL agents that might have been archived in entire chat history."
import os

from agentic_core.L0_routing.config import ARCHIVES_DIR
from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS

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
