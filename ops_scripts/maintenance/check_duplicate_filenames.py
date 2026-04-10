import sys
from collections import defaultdict
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import DISCOVERY_EXCLUDED_TERRITORIES, GLOBAL_EXCLUDED_DIRS, SOVEREIGN_EXCLUDED_FOLDERS


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
        print("[!] DUPLICATE FILENAMES DETECTED:")
        for name, paths in sorted(duplicates.items()):
            print(f"\nFilename: {name}")
            for p in paths:
                rel_path = p.relative_to(project_root)
                print(f"  - {rel_path}")
        print("\n[REASON]: Architectural standard requires a single source of truth per agent.")
        sys.exit(1)

    print("[✓] No duplicate filenames found.")
    sys.exit(0)


if __name__ == "__main__":
    check_for_duplicates()
