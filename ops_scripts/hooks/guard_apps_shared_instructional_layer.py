"""
Guard against new imports of apps_shared.utils.instructional_layer

This hook prevents reintroduction of the deprecated apps_shared instructional_layer module.
It FAILS if any non-doc/non-artifact file introduces the string "apps_shared.utils.instructional_layer".
"""
import argparse
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)

_ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)


def check_forbidden_imports(repo_root: Path) -> int:
    """Check for forbidden imports of apps_shared instructional_layer."""
    forbidden_pattern = 'apps_shared.utils.instructional_layer'
    exclude_dirs = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS
    exclude_extensions = {'.md', '.json', '.txt', '.yml', '.yaml', '.toml'}
    violations = []
    for file_path in repo_root.rglob('*'):
        if not file_path.is_file():
            continue
        if any(exclude_dir in file_path.parts for exclude_dir in exclude_dirs):
            continue
        if file_path.suffix in exclude_extensions:
            continue
        if file_path.name == 'guard_apps_shared_instructional_layer.py':
            continue
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()
                if forbidden_pattern in content:
                    violations.append(str(file_path.relative_to(repo_root)))
        except (UnicodeDecodeError, PermissionError):    # guardian: Multiple exceptions (UnicodeDecodeError, PermissionError) need specific handling
            continue
    if violations:
        print('GUARD VIOLATION: Found forbidden imports of deprecated module')
        print(f'   Forbidden pattern: {forbidden_pattern}')
        print('   Violating files:')
        for violation in violations:
            print(f'     - {violation}')
        print('\n   To fix:')
        print('   1. Remove imports of apps_shared.utils.instructional_layer')
        print('   2. Use agentic_core.runtime.config.instructional_injections instead')
        print('   3. See migration guide in docs/rules/governance.md')
        return 1
    print('No forbidden apps_shared instructional_layer imports found')
    return 0

def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Guard against apps_shared instructional_layer imports')
    parser.add_argument('--repo-root', type=Path, default=Path.cwd(), help='Repository root path')
    args = parser.parse_args()
    return check_forbidden_imports(args.repo_root)
if __name__ == '__main__':
    sys.exit(main())
