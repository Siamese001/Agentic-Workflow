import argparse
import json
import os
import sys
from modulefinder import ModuleFinder


def get_active_files(entry_points, root_dir):
    """
    Traces imports starting from entry_points to find all 'active' files.
    """
    finder = ModuleFinder(path=[root_dir] + sys.path)

    # print(f"🔍 Tracing dependencies from: {entry_points}")  # [Security Fix]
    for script in entry_points:
        # ModuleFinder acts like python execution but just scans for imports
        finder.run_script(script)

    active_files = set()
    # Normalize paths to absolute for comparison
    abs_root = os.path.abspath(root_dir)

    # print("\n📦 Active Modules Found:")  # [Security Fix]
    for name, mod in finder.modules.items():
        if mod.__file__:
            # Only include files inside our project root
            # (Excluding system libs like 'os', 'sys', etc.)
            abs_path = os.path.abspath(mod.__file__)
            if abs_path.startswith(abs_root):
                # We want the path relative to root for the fixers to use
                rel_path = os.path.relpath(abs_path, abs_root)
                active_files.add(rel_path)
                # print(f"  - {rel_path}")

    # Also make sure the entry points themselves are included
    for ep in entry_points:
        rel_ep = os.path.relpath(os.path.abspath(ep), abs_root)
        active_files.add(rel_ep)

    return sorted(list(active_files))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--entry-points', nargs='+', required=True,
                        help='Main script(s) that trigger the application (e.g., canon_validator_v2_agentic.py)')
    parser.add_argument('--root-dir', type=str, default='/app',
                        help='Root directory of the project')
    parser.add_argument('--output', type=str, default='active_manifest.json',
                        help='Output file to store the list of active files')
    args = parser.parse_args()

    # print("🚀 Starting Dependency Assessment...")  # [Security Fix]
    active_files = get_active_files(args.entry_points, args.root_dir)

    # print(f"\n✅ Assessment Complete. Found {len(active_files)} active files.")  # [Security Fix]
    # print(f"   Ignored {len(list(os.walk(args.root_dir))) * 5 - len(active_files)} potentially junk/backup files.") # Rough estimate  # [Security Fix]

    with open(args.output, 'w') as f:
        json.dump(active_files, f, indent=2)
    # print(f"💾 Manifest saved to {args.output}")  # [Security Fix]

if __name__ == '__main__':
    main()

