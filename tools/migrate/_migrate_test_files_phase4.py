"""Phase 4: Batch migrate all test files from SOVEREIGN_TERRITORIES to new API."""

import re
from pathlib import Path

ROOT = Path(r"c:\Git\Agentic-Workflow")

# Test files that need migration (from ADG analysis)
TEST_FILES = [
    "tests/integration/agentic_core/L5_safety/reasoning/test_tests_support_phantom_subdirs.py",
    "tests/architecture/test_contracts_fixture_placement.py",
    "tests/integration/agentic_core/L5_safety/reasoning/test_hierarchy_agent_phantom_dir_edge_cases.py",
    "tests/architecture/test_hierarchy_agent_invariants.py",
    "tests/architecture/test_phantom_folder_regression.py",
    "tests/guardian/test_structure_blueprint_hardened.py",
    "tests/integration/test_depth_violation_no_archive_invariant.py",
    "tests/unit/agentic_core/L5_safety/reasoning/test_constants_quarantine_invariant.py",
    "tests/unit/agentic_core/L5_safety/validators/test_global_candidate_vacuum.py",
    "tests/unit_min_deps/test_leaf_domain_contract.py",
]

# Migration patterns
PATTERNS = [
    # Pattern 1: Direct import from __init__
    (
        r"from agentic_core\.L5_safety\.config\.structure_blueprint import \(\s*SOVEREIGN_TERRITORIES,",
        r"from agentic_core.L5_safety.config.structure_blueprint import (\n    get_all_territories,",
    ),
    # Pattern 2: Direct import from __init__ (single line)
    (
        r"from agentic_core\.L5_safety\.config\.structure_blueprint import SOVEREIGN_TERRITORIES",
        r"from agentic_core.L5_safety.config.structure_blueprint import get_all_territories",
    ),
    # Pattern 3: Import from _constants
    (
        r"from agentic_core\.L5_safety\.config\.structure_blueprint\._constants import \(\s*SOVEREIGN_TERRITORIES,",
        r"from agentic_core.L5_safety.config.structure_blueprint.territories import (\n    get_all_territories,",
    ),
    # Pattern 4: Import from structure_blueprint_config
    (
        r"from agentic_core\.L5_safety\.config\.structure_blueprint_config import SOVEREIGN_TERRITORIES",
        r"from agentic_core.L5_safety.config.structure_blueprint import get_all_territories",
    ),
    # Pattern 5: Usage - SOVEREIGN_TERRITORIES.get(
    (
        r"SOVEREIGN_TERRITORIES\.get\(",
        r"get_all_territories().get(",
    ),
    # Pattern 6: Usage - SOVEREIGN_TERRITORIES\[
    (
        r"SOVEREIGN_TERRITORIES\[",
        r"get_all_territories()[",
    ),
    # Pattern 7: Usage - in SOVEREIGN_TERRITORIES
    (
        r"in SOVEREIGN_TERRITORIES",
        r"in get_all_territories()",
    ),
    # Pattern 8: Usage - SOVEREIGN_TERRITORIES.items()
    (
        r"SOVEREIGN_TERRITORIES\.items\(\)",
        r"get_all_territories().items()",
    ),
    # Pattern 9: Docstring/comment references (informational only)
    (
        r'SOVEREIGN_TERRITORIES\["',
        r'territory_definitions["',
    ),
]


def migrate_file(file_path: Path) -> tuple[bool, int]:
    """Migrate a single test file. Returns (changed, replacement_count)."""
    if not file_path.exists():
        print(f"  ⚠️  File not found: {file_path}")
        return False, 0

    content = file_path.read_text(encoding="utf-8")
    original_content = content
    replacements = 0

    for pattern, replacement in PATTERNS:
        new_content, count = re.subn(pattern, replacement, content)
        if count > 0:
            content = new_content
            replacements += count

    if content != original_content:
        file_path.write_text(content, encoding="utf-8")
        return True, replacements

    return False, 0


def main():
    print("=" * 80)
    print("Phase 4: Test File Migration")
    print("=" * 80)
    print()

    migrated = []
    unchanged = []
    not_found = []

    for rel_path in TEST_FILES:
        file_path = ROOT / rel_path
        print(f"Processing: {rel_path}")

        if not file_path.exists():
            print("  ❌ NOT FOUND")
            not_found.append(rel_path)
            continue

        changed, count = migrate_file(file_path)

        if changed:
            print(f"  ✅ MIGRATED ({count} replacements)")
            migrated.append((rel_path, count))
        else:
            print("  ⏭️  NO CHANGES NEEDED")
            unchanged.append(rel_path)

    print()
    print("=" * 80)
    print("Migration Summary")
    print("=" * 80)
    print(f"Migrated:  {len(migrated)} files")
    print(f"Unchanged: {len(unchanged)} files")
    print(f"Not found: {len(not_found)} files")
    print()

    if migrated:
        print("Migrated files:")
        for path, count in migrated:
            print(f"  - {path} ({count} replacements)")

    if not_found:
        print()
        print("Not found files:")
        for path in not_found:
            print(f"  - {path}")

    print()
    print("=" * 80)
    print(f"Phase 4 {'COMPLETE' if not not_found else 'COMPLETE WITH WARNINGS'}")
    print("=" * 80)


if __name__ == "__main__":
    main()
