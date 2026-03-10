"""
file: ops_scripts/governance/intelligence_sentry.py
description: |
    [MASTER ALIGNMENT AGENT]
    1. Indexes Source Tree (agentic_core L0-L6) to build an Address Map.
    2. Recursively finds 'test_*.py' files anywhere in the project.
    3. Moves them to tests/unit/{mirrored_path}.
    4. Rewrites imports from 'from agentic_core' or 'from core' to 'from agentic_core'.
"""

#!/usr/bin/env python3
"""Intelligence sentry for monitoring project health."""

import shutil
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from agentic_core.utils.project_root_util import get_project_root
from agentic_core.L0_routing.config.path_constants import (
    ARCHIVES_DIR,
    OPS_SCRIPTS_DIR,
)

PROJECT_ROOT = get_project_root()
SOURCE_ROOTS = [AGENTIC_CORE_DIR, APPS_RG_DIR, APPS_LIC_DIR]
TEST_UNIT_ROOT = PROJECT_ROOT / TESTS_UNIT_DIR


def build_source_map():
    print("🧠 Indexing Source Tree (L0-L6)...")
    source_index = {}
    for root in SOURCE_ROOTS:
        path = PROJECT_ROOT / root
        if not path.exists():
            continue
        for file in path.rglob("*.py"):
            if file.name == "__init__.py":
                continue
            # Map filename stem to its relative parent directory
            source_index[file.stem] = file.parent.relative_to(PROJECT_ROOT)
    return source_index


def fix_imports(file_path):
    content = file_path.read_text(encoding="utf-8")
    original = content
    # Regex 1: Remove 'src.' prefix
    content = re.sub(r"from src\.agentic_core", r"from agentic_core", content)
    # Regex 2: Fix legacy 'core.' to 'agentic_core.'
    content = re.sub(r"from core\.", r"from agentic_core.", content)
    # Regex 3: Fix relative depth (..utils -> ...utils) if file moved deeper
    # This is handled by ensuring 'pythonpath = .' in pytest.ini
    if content != original:
        file_path.write_text(content, encoding="utf-8")
        return True
    return False


def execute_sentry():
    source_map = build_source_map()
    print("🚀 Scanning for misplaced test files...")

    # Find all test files NOT already in tests/ directory
    all_tests = [
        f
        for f in PROJECT_ROOT.rglob("test_*.py")
        if "/tests/" not in str(f.as_posix())
        and OPS_SCRIPTS_DIR not in str(f.as_posix())
        and ARCHIVES_DIR not in str(f.as_posix())
    ]

    moved = 0
    for test_file in all_tests:
        target_stem = test_file.stem.replace("test_", "")

        # Strategy 1: Try to find matching source file
        if target_stem in source_map:
            dest_dir = TEST_UNIT_ROOT / source_map[target_stem]
        else:
            # Strategy 2: Mirror the directory structure
            relative_path = test_file.parent.relative_to(PROJECT_ROOT)
            dest_dir = TEST_UNIT_ROOT / relative_path

        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / test_file.name

        shutil.move(str(test_file), str(dest_path))
        fix_imports(dest_path)
        print(f"  [MIRRORED] {test_file.name} -> {dest_dir.relative_to(TEST_UNIT_ROOT)}")
        moved += 1

    print(f"✅ Sentry Complete. Mirrored {moved} files and patched imports.")


if __name__ == "__main__":
    execute_sentry()
