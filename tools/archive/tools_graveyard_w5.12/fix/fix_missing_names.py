"""Fix missing NameErrors in agentic_core source files by adding imports."""

import ast
import os
import re

ROOT_DIR = r"C:\Git\Agentic-Workflow"

# Map of missing name -> (import_module, import_name)
FIXES = {
    "ROOT": ("pathlib", "Path", "ROOT = Path(__file__).resolve().parents[3]"),
    "GLOBAL_EXCLUDED_DIRS": (
        "agentic_core.L0_routing.config.path_constants",
        "SOVEREIGN_EXCLUDED_FOLDERS as GLOBAL_EXCLUDED_DIRS",
        None,
    ),
}

# Files with specific NameErrors to fix
NAMEERROR_FILES = {
    # ROOT errors — these files use ROOT = Path(...) pattern
    "agentic_core/L0_routing/utils/complexity_visitor_util.py": "ROOT",
    "agentic_core/L0_routing/utils/fix_mission_runner_util.py": "ROOT",
    "agentic_core/L0_routing/utils/fix_remaining_depth_util.py": "ROOT",
    "agentic_core/L0_routing/utils/force_annexation_util.py": "ROOT",
    "agentic_core/L0_routing/utils/gravity_audit_util.py": "ROOT",
    "agentic_core/L0_routing/utils/scorched_earth_merge_util.py": "ROOT",
    "agentic_core/L0_routing/utils/sovereign_alignment_v2_util.py": "ROOT",
    "agentic_core/L0_routing/utils/sovereign_convergence_util.py": "ROOT",
    "agentic_core/L0_routing/utils/trim_remaining_airlocks_util.py": "ROOT",
    "agentic_core/L5_safety/utils/forge_fortress_util.py": "ROOT",
    "agentic_core/L5_safety/utils/sovereign_lock_util.py": "ROOT",
}


def fix_root_in_file(filepath):
    """Add ROOT definition after imports if missing."""
    src = open(filepath, encoding="utf-8").read()
    if re.search(r"^ROOT\s*=", src, re.MULTILINE):
        return False  # Already defined

    # Check if pathlib.Path is imported
    has_path = "from pathlib import Path" in src or "import pathlib" in src

    # Find the right insertion point — after all imports
    lines = src.split("\n")
    last_import = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("from ") or stripped.startswith("import "):
            last_import = i
        # Also skip emit calls at module level
        if stripped.startswith("_emit_") or stripped.startswith("emit_"):
            last_import = i

    # Insert ROOT definition
    insert_lines = []
    if not has_path:
        insert_lines.append("from pathlib import Path")
    insert_lines.append("ROOT = Path(__file__).resolve().parents[3]")
    insert_lines.append("")

    lines.insert(last_import + 1, "\n".join(insert_lines))
    new_src = "\n".join(lines)

    # Verify syntax
    try:
        ast.parse(new_src)
    except SyntaxError as e:  # guardian: allow-silent-swallow - acceptable exception handling
        print(f"  SYNTAX ERROR in {filepath}: {e}")
        return False

    open(filepath, "w", encoding="utf-8").write(new_src)
    return True


def fix_global_excluded_dirs(filepath):
    """Add GLOBAL_EXCLUDED_DIRS definition."""
    src = open(filepath, encoding="utf-8").read()
    if "GLOBAL_EXCLUDED_DIRS" in src and "=" in src.split("GLOBAL_EXCLUDED_DIRS")[0].split("\n")[-1]:
        return False  # Already defined somewhere

    # Check what GLOBAL_EXCLUDED_DIRS is used for — it's usually a list of dirs to exclude
    # The easiest fix is to define it from SOVEREIGN_EXCLUDED_FOLDERS or as a constant
    lines = src.split("\n")
    last_import = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("from ") or stripped.startswith("import "):
            last_import = i
        if stripped.startswith("_emit_") or stripped.startswith("emit_"):
            last_import = i

    # Add the import
    insert = "from agentic_core.L0_routing.config.path_constants import SOVEREIGN_EXCLUDED_FOLDERS as GLOBAL_EXCLUDED_DIRS"
    lines.insert(last_import + 1, insert)
    new_src = "\n".join(lines)

    try:
        # guardian: allow-silent-swallow - acceptable exception handling
        ast.parse(new_src)
    except SyntaxError as e:
        print(f"  SYNTAX ERROR in {filepath}: {e}")
        return False

    open(filepath, "w", encoding="utf-8").write(new_src)
    return True


fixed = 0
for rel_path, error_name in NAMEERROR_FILES.items():
    filepath = os.path.join(ROOT_DIR, rel_path)
    if not os.path.exists(filepath):
        print(f"  SKIP (not found): {rel_path}")
        continue
    if error_name == "ROOT":
        if fix_root_in_file(filepath):
            print(f"  FIXED ROOT in {rel_path}")
            fixed += 1
        else:
            print(f"  SKIP (already has ROOT): {rel_path}")

# Fix GLOBAL_EXCLUDED_DIRS files
GED_FILES = [
    "agentic_core/config/core/constants_config.py",
    "agentic_core/config/core/non_conforming_agent_finder_config.py",
]
for rel_path in GED_FILES:
    filepath = os.path.join(ROOT_DIR, rel_path)
    if not os.path.exists(filepath):
        print(f"  SKIP (not found): {rel_path}")
        continue
    if fix_global_excluded_dirs(filepath):
        print(f"  FIXED GLOBAL_EXCLUDED_DIRS in {rel_path}")
        fixed += 1
    else:
        print(f"  SKIP: {rel_path}")

print(f"\nTotal fixed: {fixed}")
