from pathlib import Path

"""Comprehensive check of ALL agents that might have been archived in entire chat history."""
import os

PROJECT_ROOT = Path("C:/Git/Agentic-Workflow")
l4_active = PROJECT_ROOT / "agentic_core/L4_state/validation_context/L4Agent.py"
archives_path = PROJECT_ROOT / "archives"
l4_archived = []
if archives_path.exists():
    for root, _dirs, files in os.walk(archives_path):
        if ".sovereign_healing_backup" in root:
            continue
        if "L4Agent.py" in files:
            l4_archived.append(os.path.join(root, "L4Agent.py"))
for _path in l4_archived:
    pass
archived_agents = []
if archives_path.exists():
    for root, _dirs, files in os.walk(archives_path):
        if ".sovereign_healing_backup" in root:
            continue
        if "healing_backups" in root:
            continue
        if "identity_duplicates" in root:
            continue
        for file in files:
            if file.endswith("Agent.py"):
                rel_path = os.path.relpath(os.path.join(root, file), archives_path)
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
