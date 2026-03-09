"""
Migrate missing names from monolithic structure_blueprint_config.py
into the modular structure_blueprint/ package.

Uses AST parsing to find line ranges, then extracts source text.
"""

from __future__ import annotations

import ast
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR, get_validated_project_root

ROOT = get_validated_project_root()
MONOLITH = ROOT / AGENTIC_CORE_DIR / "L5_safety" / "config" / "structure_blueprint_config.py"
MOD_DIR = ROOT / AGENTIC_CORE_DIR / "L5_safety" / "config" / "structure_blueprint"

# === TARGET MODULE ASSIGNMENTS ===
# Maps each missing name to the modular file it should live in.
ASSIGNMENTS: dict[str, str] = {
    # governance.py — operational configs
    "HEALING_CONFIG": "governance",
    "AGENT_RESILIENCE_CONFIG": "governance",
    "MISSION_CONFIG": "governance",
    "MCP_CAPABILITIES": "governance",
    "GRAVITY_CONFIG": "governance",
    "GRAVITY_SURGERY_ENABLED": "governance",
    "UPSTREAM_SOVEREIGN_ROOTS": "governance",
    "DOWNSTREAM_ROOTS": "governance",
    # ssot.py — project-level constants, whitelists, validation
    "VALIDATED_FILE_EXTENSIONS": "ssot",
    "NAMING_EXEMPT_FILES": "ssot",
    "NAMING_EXEMPT_DIRS": "ssot",
    "FORBIDDEN_PATTERNS": "ssot",
    "ROOT_PROTECTED_FILES": "ssot",
    "PROJECT_ROOT_WHITELIST": "ssot",
    "ROOT_ALLOWED_PATTERNS": "ssot",
    "SOVEREIGN_EXCLUDED_FOLDERS": "ssot",
    "FORBIDDEN_FOLDER_PATTERN": "ssot",
    "FORBIDDEN_ROOT_FOLDERS": "ssot",
    "TESTS_ROOT_FILE_WHITELIST": "ssot",
    "AUTONOMOUS_AGENT_WHITELIST": "ssot",
    "ALLOWED_DUPLICATE_FILENAMES": "ssot",
    "DISCOVERY_EXCLUDED_TERRITORIES": "ssot",
    "PYTHON_STDLIB_MODULES": "ssot",
    "ROOT_WHITELIST": "ssot",
    "GLOBAL_EXCLUDED_DIRS": "ssot",
    "SCOPE_SUMMARY_EXCLUSIONS": "ssot",
    "FLAT_DIRECTORIES": "ssot",
    "validate_flat_directory": "ssot",
    "safe_prefixed_filename": "ssot",
    "validate_no_duplicate_prefix": "ssot",
    "is_path_allowed": "ssot",
    "is_l4_approved": "ssot",
    "protected_folders": "ssot",
    "ignore_dirs": "ssot",
    "sovereign_ignored_folders": "ssot",
    # artifacts.py — routing maps, artifact validation, subfolder metadata
    "ARTIFACT_ROUTING_MAP": "artifacts",
    "validate_artifact_routing": "artifacts",
    "check_forbidden_signals": "artifacts",
    "DATA_SUBFOLDER_METADATA": "artifacts",
    "DOCS_SUBFOLDER_METADATA": "artifacts",
    "PROJECT_ROOT_SUBFOLDERS": "artifacts",
    "PROJECT_ROOT_METADATA": "artifacts",
    # semantics.py — AST signals, placement, registries
    "TEST_TYPE_SIGNALS": "semantics",
    "LEGACY_AST_SIGNALS": "semantics",
    "AST_PLACEMENT_SIGNALS": "semantics",
    "PLACEMENT_CONFIDENCE": "semantics",
    "L2_TO_L1_MAP": "semantics",
    "EXERCISER_REGISTRY": "semantics",
    "AGENT_REGISTRY": "semantics",
    "semantic_l2_registry": "semantics",
    "SEMANTIC_L2_REGISTRY": "semantics",
}

# Private names that must also be extracted (dependencies of public names)
PRIVATE_DEPS: dict[str, str] = {
    "_STATIC_ROOT_PROTECTED_FILES": "ssot",
    "_DYNAMIC_ROOT_PROTECTED_FILES": "ssot",
    "_semantic_templates": "semantics",
}


def find_top_level_nodes(source: str) -> dict[str, tuple[int, int]]:
    """AST-parse source and return {name: (start_line, end_line)} for all top-level definitions."""
    tree = ast.parse(source)
    result: dict[str, tuple[int, int]] = {}
    for node in ast.iter_child_nodes(tree):
        name = None
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    name = t.id
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            name = node.target.id
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name = node.name
        elif isinstance(node, ast.ClassDef):
            name = node.name
        if name:
            result[name] = (node.lineno, node.end_lineno)
    return result


def extract_lines(all_lines: list[str], start: int, end: int) -> str:
    """Extract source lines (1-indexed, inclusive)."""
    return "".join(all_lines[start - 1 : end])


def find_preceding_comments(all_lines: list[str], start_line: int) -> int:
    """Walk backward from start_line to include preceding comment/blank lines."""
    idx = start_line - 2  # 0-indexed, line before
    first_comment_line = start_line
    while idx >= 0:
        stripped = all_lines[idx].strip()
        if stripped.startswith("#") or stripped == "":
            first_comment_line = idx + 1  # 1-indexed
            idx -= 1
        else:
            break
    return first_comment_line


def main():
    source = MONOLITH.read_text(encoding="utf-8")
    all_lines = source.splitlines(True)  # keepends=True

    nodes = find_top_level_nodes(source)

    # Merge assignments
    all_targets = {**ASSIGNMENTS, **PRIVATE_DEPS}

    # Group by target module
    by_module: dict[str, list[tuple[str, int, int]]] = {}
    missing_names = []
    for name, module in all_targets.items():
        if name not in nodes:
            missing_names.append(name)
            continue
        start, end = nodes[name]
        # Include preceding comments
        comment_start = find_preceding_comments(all_lines, start)
        if module not in by_module:
            by_module[module] = []
        by_module[module].append((name, comment_start, end))

    if missing_names:
        print(f"WARNING: Names not found in monolith: {missing_names}")

    # Sort each module's names by line number
    for module in by_module:
        by_module[module].sort(key=lambda x: x[1])

    # Report what will be migrated
    for module, items in sorted(by_module.items()):
        total_lines = sum(end - start + 1 for _, start, end in items)
        names = [n for n, _, _ in items]
        print(f"\n{module}.py: {len(items)} names, ~{total_lines} lines")
        for n in names:
            print(f"  - {n}")

    # Extract code blocks
    for module, items in sorted(by_module.items()):
        blocks = []
        for name, start, end in items:
            block = extract_lines(all_lines, start, end)
            blocks.append(block)

        combined = "\n".join(blocks)
        output_file = ROOT / "data" / "freeze_reports" / f"_migrate_{module}.py.fragment"
        output_file.write_text(combined, encoding="utf-8")
        print(f"\nWrote {output_file} ({len(combined)} chars)")

    print("\n=== MIGRATION FRAGMENTS GENERATED ===")
    print("Review fragments in data/freeze_reports/_migrate_*.py.fragment")
    print("Then append each fragment to the corresponding modular file.")


if __name__ == "__main__":
    main()
