import sys
from pathlib import Path


def check_for_duplicates():
    """Scans for identical filenames across different directories."""
    project_root = Path(__file__).parent.parent.parent
    file_map = defaultdict(list)
    exclude = {".git", "archives", "__pycache__", "venv", "node_modules", ".venv", "env"}
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
