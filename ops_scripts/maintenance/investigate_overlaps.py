"""Investigate overlapping file stems and target-name collisions."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import get_validated_project_root


PROJECT_ROOT = get_validated_project_root()


def find_stem_overlaps(root: Path) -> dict[str, list[Path]]:
    by_stem: dict[str, list[Path]] = defaultdict(list)
    for path in sorted(root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        by_stem[path.stem].append(path)
    return {stem: paths for stem, paths in by_stem.items() if len(paths) > 1}


def main(limit: int = 100) -> int:
    overlaps = find_stem_overlaps(PROJECT_ROOT)
    print(f"Overlapping Python stems: {len(overlaps)}")
    for index, (stem, paths) in enumerate(sorted(overlaps.items()), start=1):
        if index > limit:
            break
        print(f"\n{stem}")
        for path in paths:
            print(f"- {path.relative_to(PROJECT_ROOT)}")
    if len(overlaps) > limit:
        print(f"\n... truncated {len(overlaps) - limit} additional overlap groups")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Investigate overlapping Python file stems.")
    parser.add_argument("--limit", type=int, default=100, help="Maximum overlap groups to print.")
    raise SystemExit(main(limit=parser.parse_args().limit))
