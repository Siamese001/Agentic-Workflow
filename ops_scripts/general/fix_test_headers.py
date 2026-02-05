"""
Fix test file headers that are causing parsing errors.
The generated test files have problematic headers with Windows paths.
"""

from pathlib import Path


def fix_test_headers(project_root: Path):
    """Remove problematic headers from generated test files."""
    test_dir = project_root / "tests" / "unit"
    fixed_count = 0

    for test_file in test_dir.rglob("*.py"):
        if test_file.name in ("__init__.py", "conftest.py"):
            continue

        try:
            content = test_file.read_text(encoding="utf-8")

            # Check if file has problematic header
            if "Source: C:\\Git\\Agentic-Workflow" in content:
                # Remove first 7 lines (problematic header)
                lines = content.split("\n")
                if len(lines) > 7 and "Source:" in lines[4]:
                    content = "\n".join(lines[7:])
                    test_file.write_text(content, encoding="utf-8")
                    fixed_count += 1
                    print(f"Fixed: {test_file.relative_to(project_root)}")
        except (UnicodeDecodeError, OSError):
            continue

    print(f"\nTotal files fixed: {fixed_count}")


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    fix_test_headers(project_root)
