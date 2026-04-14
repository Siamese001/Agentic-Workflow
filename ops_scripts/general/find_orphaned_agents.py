"""
Find Orphaned Agents - Agents flagged for consolidation but never deleted.

Scans the consolidation reports and checks if flagged agents still exist
in the active codebase (not in archives).
"""

import argparse
import json
import os
import re
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import ARCHIVES_DIR
from tqdm import tqdm

FLAGGED_AGENTS = [
    "BareExceptValidatorAgent.py",
    "DangerousBuiltinsValidatorAgent.py",
    "DebuggerValidatorAgent.py",
    "EmptyExceptValidatorAgent.py",
    "EvalExecValidatorAgent.py",
    "AutonomousCheckpointManagerAgent.py",
    "AutonomousStateGuardianAgent.py",
    "CheckpointManagerAgent.py",
    "L4Agent.py",
    "ManifestManagerAgent.py",
    "MemoryManagerAgent.py",
    "BaseClassEnforcerAgent.py",
    "HygieneGuardianAgent.py",
    "HygieneValidatorAgent.py",
    "PatternEnforcerAgent.py",
    "TypeHintEnforcementAgent.py",
]


def _resolve_project_root(explicit_root: str | None = None) -> Path:
    if explicit_root:
        return Path(explicit_root).expanduser().resolve()
    env_root = os.getenv("AGENTIC_WORKFLOW_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists():
            return candidate
    return Path.cwd().resolve()


def find_orphaned_agents(project_root: Path):
    """Find agents that were flagged but still exist in active codebase."""
    orphaned = []
    for agent_file in tqdm(FLAGGED_AGENTS, desc="Processing", unit="item"):
        for path in tqdm(project_root.rglob(agent_file), desc="Processing", unit="item"):
            if any(skip in str(path) for skip in [ARCHIVES_DIR, ".sovereign_healing_backup", "__pycache__"]):
                continue
            is_used = check_if_used(project_root, path, agent_file)
            orphaned.append(
                {
                    "file": agent_file,
                    "path": str(path.relative_to(project_root)),
                    "absolute_path": str(path),
                    "is_used": is_used,
                    "action": "KEEP" if is_used else "DELETE",
                }
            )
    return orphaned


def check_if_used(project_root: Path, file_path: Path, agent_file: str) -> bool:
    """Check if agent is actually used (imported or inherited from)."""
    agent_class = agent_file.replace(".py", "")
    import_pattern = f"from.*{agent_class} import|import.*{agent_class}"
    inheritance_pattern = f"class.*\\({agent_class}\\)"
    for py_file in tqdm(PROJECT_ROOT.rglob("*.py"), desc="Processing", unit="item"):
        if any(skip in str(py_file) for skip in [ARCHIVES_DIR, ".sovereign_healing_backup", "__pycache__"]):
            continue
        if py_file == file_path:
            continue
        try:
            content = py_file.read_text(encoding="utf-8", errors="replace")
            if import_pattern.search(content) or inheritance_pattern.search(content):
                return True
        # guardian: allow-silent-swallow
        except Exception:
            continue
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find archived agents that still exist in active territories."
    )
    parser.add_argument("--project-root", help="Override repo root resolution.")
    args = parser.parse_args()
    PROJECT_ROOT = _resolve_project_root(args.project_root)

    print("=" * 80)
    print("ORPHANED AGENT SCAN")
    print("=" * 80)
    print()
    orphaned = find_orphaned_agents(PROJECT_ROOT)
    if not orphaned:
        print("✅ No orphaned agents found - all flagged agents have been removed.")
    else:
        print(f"Found {len(orphaned)} agents flagged for consolidation:\n")
        to_delete = [a for a in orphaned if a["action"] == "DELETE"]
        to_keep = [a for a in orphaned if a["action"] == "KEEP"]
        if to_delete:
            print(f"🗑️  {len(to_delete)} ORPHANED (safe to delete):")
            for agent in to_delete:
                print(f"  - {agent['file']}")
                print(f"    Path: {agent['path']}")
                print(f"    Used: {agent['is_used']}")
                print()
        if to_keep:
            print(f"⚠️  {len(to_keep)} STILL IN USE (do not delete):")
            for agent in to_keep:
                print(f"  - {agent['file']}")
                print(f"    Path: {agent['path']}")
                print()
        results_file = PROJECT_ROOT / "orphaned_agents_report.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(orphaned, f, indent=2)
        print(f"\n📄 Full report saved to: {results_file}")
