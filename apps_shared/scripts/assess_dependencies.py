import argparse
from typing import Any

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""Brief description of functionality and purpose."""

"Brief description of functionality and purpose."
import json
import os
import sys


def get_active_files(entry_points: Any, root_dir: Any) -> Any:
    """
    Traces imports starting from entry_points to find all 'active' files.
    """
    finder: Any = ModuleFinder(path=[root_dir] + sys.path)
    for script in entry_points:
        finder.run_script(script)
    active_files: Any = set()
    abs_root: Any = os.path.abspath(root_dir)
    for _name, mod in finder.modules.items():
        if mod.__file__:
            abs_path: Any = os.path.abspath(mod.__file__)
            if abs_path.startswith(abs_root):
                rel_path: Any = os.path.relpath(abs_path, abs_root)
                active_files.add(rel_path)
    for ep in entry_points:
        rel_ep: Any = os.path.relpath(os.path.abspath(ep), abs_root)
        active_files.add(rel_ep)
    return sorted(active_files)


def main() -> Any:
    """Brief description of functionality and purpose."""
    parser: Any = argparse.ArgumentParser()
    parser.add_argument(
        "--entry-points",
        nargs="+",
        required=True,
        help="Main script(s) that trigger the application (e.g., canon_validator_v2_agentic.py)",
    )
    parser.add_argument(
        "--root-dir",
        type=str,
        default="/app",
        help="Root directory of the project",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="active_manifest.json",
        help="Output file to store the list of active files",
    )
    args: Any = parser.parse_args()
    active_files: Any = get_active_files(args.entry_points, args.root_dir)
    with open(args.output, "w") as f:
        json.dump(active_files, f, indent=2)


if __name__ == "__main__":
    main()
