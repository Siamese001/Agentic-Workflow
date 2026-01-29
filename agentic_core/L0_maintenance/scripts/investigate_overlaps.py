import hashlib
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
GROUPS = {
    "Location": ["LocationAgent.py", "LocationValidatorAgent.py", "LocationHealerAgent.py"],
    "Hierarchy": ["HierarchyAgent.py", "HierarchyValidatorAgent.py"],
    "Import": ["ImportAgent.py", "ImportLockAgent.py"],
    "Strategic": ["StrategicRecommendationAgent.py", "StrategicPlannerAgent.py"],
}


def get_file_hash(path: Path):
    """TODO: Add documentation for get_file_hash."""
    if not path.exists():
        return None
    return hashlib.md5(path.read_bytes()).hexdigest()


def investigate():
    """TODO: Add documentation for investigate."""
    for group_name, filenames in GROUPS.items():
        found_files = []
        for root, _, files in os.walk(PROJECT_ROOT / "agentic_core"):
            for f in files:
                if f in filenames:
                    found_files.append(Path(root) / f)
        if not found_files:
            continue
        for f_path in found_files:
            f_hash = get_file_hash(f_path)
            rel_path = f_path.relative_to(PROJECT_ROOT)
        hashes = [get_file_hash(p) for p in found_files]
        unique_hashes = set(hashes)
        if len(unique_hashes) < len(hashes):
            pass


if __name__ == "__main__":
    investigate()
