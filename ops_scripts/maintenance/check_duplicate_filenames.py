import sys
from collections import defaultdict
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
    get_validated_project_root,
)


PROJECT_ROOT = get_validated_project_root()
EXCLUDED_PARTS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES


def find_duplicates(project_root: Path) -> dict[str, list[Path]]:
    file_map: dict[str, list[Path]] = defaultdict(list)
    for path in sorted(project_root.rglob("*.py")):
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        file_map[path.name].append(path)
    return {name: paths for name, paths in file_map.items() if len(paths) > 1}


def main() -> int:
    duplicates = find_duplicates(PROJECT_ROOT)
    if duplicates:
        print("[!] DUPLICATE FILENAMES DETECTED:")
        for name, paths in sorted(duplicates.items()):
            print(f"\nFilename: {name}")
            for path in paths:
                print(f"  - {path.relative_to(PROJECT_ROOT)}")
        print("\n[REASON]: Architectural standard requires a single source of truth per agent.")
        return 1

    print("[✓] No duplicate filenames found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
