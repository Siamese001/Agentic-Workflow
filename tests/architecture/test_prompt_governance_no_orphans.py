"""
Deterministic invariant test: No orphan prompt governance files.
Ensures every prompt/template file under data/prompt_governance/** is referenced by at least one integration surface.
"""

import ast
from pathlib import Path

import pytest


def test_no_orphan_prompt_governance_files() -> None:
    """Invariant: Every prompt/template file must be referenced by apps_lic or apps_rg engines."""

    # A. Inventory - enumerate all prompt/template files
    repo_root = Path(__file__).parent.parent.parent
    prompt_governance_dir = repo_root / "data" / "prompt_governance"

    if not prompt_governance_dir.exists():
        pytest.skip(f"Prompt governance directory not found: {prompt_governance_dir}")

    # Find all .yaml, .yml, and .md files
    prompt_files = []
    for ext in [".yaml", ".yml", ".md"]:
        prompt_files.extend(prompt_governance_dir.rglob(f"*{ext}"))

    # Normalize to POSIX-style relative paths from repo root
    normalized_files = []
    for file_path in prompt_files:
        rel_path = file_path.relative_to(repo_root)
        posix_path = str(rel_path).replace("\\", "/")
        normalized_files.append(posix_path)

    # Sort for deterministic ordering
    normalized_files.sort()

    if not normalized_files:
        pytest.skip("No prompt/template files found in data/prompt_governance/**")

    # B. Reference scan - collect all string literals from engine files
    referenced_basenames = set()
    referenced_filenames = set()
    referenced_shared_paths = set()

    # Scan apps_lic engines
    apps_lic_engines = repo_root / "apps_lic" / "engines"
    if apps_lic_engines.exists():
        _scan_engine_directory(
            apps_lic_engines, referenced_basenames, referenced_filenames, referenced_shared_paths
        )

    # Scan apps_rg engines
    apps_rg_engines = repo_root / "apps_rg" / "engines"
    if apps_rg_engines.exists():
        _scan_engine_directory(
            apps_rg_engines, referenced_basenames, referenced_filenames, referenced_shared_paths
        )

    # C. Assertion - every file must have at least one reference
    orphan_files = []

    for file_path in normalized_files:
        file_obj = Path(file_path)
        basename = file_obj.stem  # filename without extension
        filename = file_obj.name  # full filename with extension

        is_referenced = False

        # Check basename reference
        if basename in referenced_basenames:
            is_referenced = True

        # Check full filename reference
        if filename in referenced_filenames:
            is_referenced = True

        # Check shared path reference for markdown templates
        if file_path.endswith(".md") and "shared/" in file_path:
            shared_segment = file_path.split("shared/")[-1]  # e.g., "connection_request.md"
            if f"shared/{shared_segment}" in referenced_shared_paths:
                is_referenced = True

        if not is_referenced:
            orphan_files.append(file_path)

    # Sort orphan files for deterministic output
    orphan_files.sort()

    if orphan_files:
        # Print detailed failure information
        print("\n=== ORPHAN PROMPT GOVERNANCE FILES ===")
        for orphan in orphan_files:
            print(f"  {orphan}")

        print("\n=== REMEDIATION HINT ===")
        print("Add a reference to one of the orphan files in:")
        print("  - apps_lic/engines/**/*.py")
        print("  - apps_rg/engines/**/*.py")
        print("\nReference can be:")
        print("  - Basename in quotes: e.g., 'k11_shadow_audit'")
        print("  - Full filename in quotes: e.g., 'connection_request.md'")
        print("  - Shared path in quotes: e.g., 'shared/connection_request.md'")

        pytest.fail(f"Found {len(orphan_files)} orphan prompt governance files (see output above)")

    # Success - all files are referenced
    print(f"✓ All {len(normalized_files)} prompt governance files are referenced")


def _scan_engine_directory(
    engine_dir: Path,
    referenced_basenames: set[str],
    referenced_filenames: set[str],
    referenced_shared_paths: set[str],
) -> None:
    """Scan Python files in engine directory for string literals."""

    for py_file in engine_dir.rglob("*.py"):
        if not py_file.is_file():
            continue

        try:
            with open(py_file, encoding="utf-8") as f:
                content = f.read()

            # Parse AST and extract string constants
            tree = ast.parse(content, filename=str(py_file))

            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    string_value = node.value

                    # Add to reference sets (avoid empty strings)
                    if string_value.strip():
                        referenced_basenames.add(string_value)
                        referenced_filenames.add(string_value)

                        # Also add potential shared paths
                        if "shared/" in string_value:
                            referenced_shared_paths.add(string_value)

        except (SyntaxError, UnicodeDecodeError, OSError):
            # Skip files that can't be parsed - they won't provide references anyway
            continue


if __name__ == "__main__":
    # Allow running as script for manual testing
    import pytest

    pytest.main([__file__, "-v"])
