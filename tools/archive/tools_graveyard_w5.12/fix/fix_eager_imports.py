"""Bulk fix script for eager import violations in test files.

This script converts eager agentic_core imports to lazy fixtures.
Usage: python fix_eager_imports.py [--dry-run] [--file FILE]
"""

import argparse
import re
from pathlib import Path
from typing import Optional

# List of test files with eager imports to fix
TARGET_FILES = [
    "tests/architecture/test_wave2_phase2_3_prompt_taxonomy.py",
    "tests/e2e/test_ptc_full_lifecycle_e2e.py",
    "tests/e2e/test_ptc_aggressive_hardening.py",
    "tests/e2e/test_hitl_lifecycle_e2e.py",
    "tests/e2e/test_graphrag_hardened.py",
    "tests/e2e/test_graphrag_e2e.py",
    "tests/e2e/test_prompt_lifecycle_edge_cases_e2e.py",
    "tests/e2e/test_mcp_drift_e2e.py",
    "tests/e2e/test_code_validation_gates_e2e.py",
    "tests/e2e/test_cross_layer_integration_e2e.py",
    "tests/e2e/test_opentelemetry_integration_e2e.py",
    "tests/e2e/test_runtime_adg_l6_observability_e2e.py",
    "tests/integration/test_ptc_full_integration.py",
    "tests/integration/test_depth_violation_no_archive_invariant.py",
    "tests/integration/test_ci_adg_migration.py",
    "tests/integration/test_prompt_lifecycle_pipeline.py",
    "tests/integration/agentic_core/test_redis_l1_retrieval_gate_e2e.py",
    "tests/integration/test_wave4_simple_integration.py",
]


def create_lazy_fixture(import_stmt: str) -> str:
    """Convert an import statement to a lazy fixture function."""
    # Handle 'from X import Y' style
    if import_stmt.startswith("from "):
        # Extract module and imports
        match = re.match(r"from\s+(\S+)\s+import\s+\(([^)]+)\)", import_stmt, re.DOTALL)
        if match:
            module = match.group(1)
            names = [n.strip() for n in match.group(2).split(",") if n.strip()]
        else:
            match = re.match(r"from\s+(\S+)\s+import\s+(.+)", import_stmt)
            if match:
                module = match.group(1)
                names = [n.strip() for n in match.group(2).split(",")]
            else:
                return import_stmt  # Can't parse

        fixture_name = f"_fixture_{module.replace('.', '_')}"
        names_str = ", ".join(names)
        return f"""@pytest.fixture
def {fixture_name}():
    from {module} import {names_str}
    return type('Fixture', (), {{{", ".join(f'"{n}": {n}' for n in names)}}})"""

    return import_stmt


def fix_file(filepath: Path, dry_run: bool = False) -> tuple[int, Optional[str]]:
    """Fix eager imports in a single file.

    Returns:
        Tuple of (number of fixes made, new content or None if no changes)
    """
    content = filepath.read_text(encoding="utf-8")
    original = content

    # Find all eager agentic_core imports
    lines = content.split("\n")
    new_lines = []
    imports_to_fix = []
    i = 0
    fixes = 0

    while i < len(lines):
        line = lines[i]

        # Check for eager agentic_core import
        if re.match(r"^from\s+agentic_core|^import\s+agentic_core", line.strip()):
            # Collect multi-line imports
            import_lines = [line]
            while i + 1 < len(lines) and (
                lines[i + 1].strip().startswith("(")
                or (
                    import_lines[0].strip().endswith("(")
                    and not lines[i + 1].strip().startswith("from")
                    and not lines[i + 1].strip().startswith("import")
                )
            ):
                i += 1
                import_lines.append(lines[i])

            full_import = "\n".join(import_lines)
            imports_to_fix.append(full_import)
            fixes += 1
        else:
            new_lines.append(line)
        i += 1

    if not imports_to_fix:
        return 0, None

    # Generate fixture-based replacement
    fixture_code = ["# Lazy import fixtures to avoid collection-time errors"]

    for imp in imports_to_fix:
        fixture = create_lazy_fixture(imp)
        if fixture != imp:
            fixture_code.append(fixture)
            fixture_code.append("")

    # Insert fixtures after pytest import
    result_lines = []
    inserted = False
    for i, line in enumerate(new_lines):
        result_lines.append(line)
        if not inserted and line.strip() == "import pytest":
            result_lines.append("")
            result_lines.extend(fixture_code)
            inserted = True

    if not inserted:
        # Add pytest import and fixtures at top
        result_lines.insert(0, "import pytest")
        result_lines.insert(1, "")
        result_lines[2:2] = fixture_code

    new_content = "\n".join(result_lines)
    return fixes, new_content


def main():
    parser = argparse.ArgumentParser(description="Fix eager import violations")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument("--file", type=str, help="Fix specific file only")
    args = parser.parse_args()

    repo_root = Path("c:/Git/Agentic-Workflow")
    files_to_process = [args.file] if args.file else TARGET_FILES

    total_fixes = 0
    files_changed = 0

    for file_path in files_to_process:
        full_path = repo_root / file_path
        if not full_path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue

        fixes, new_content = fix_file(full_path, dry_run=args.dry_run)

        if fixes > 0:
            print(f"{'[DRY-RUN]' if args.dry_run else ''} {file_path}: {fixes} import(s) to fix")
            if not args.dry_run and new_content:
                full_path.write_text(new_content, encoding="utf-8")
                print("  ✅ Fixed and saved")
            total_fixes += fixes
            files_changed += 1
        else:
            print(f"  ℹ️  No eager imports found in {file_path}")

    print(f"\n{'=' * 50}")
    print(f"Summary: {total_fixes} imports fixed in {files_changed} files")
    if args.dry_run:
        print("Run without --dry-run to apply changes")


if __name__ == "__main__":
    main()
