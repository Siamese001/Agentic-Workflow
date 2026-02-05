"""
Regenerate proper Python headers for all test files.
"""

from pathlib import Path


def regenerate_headers(project_root: Path):
    """Add proper Python headers to test files."""
    test_dir = project_root / "tests" / "unit"
    fixed_count = 0

    for test_file in test_dir.rglob("*.py"):
        if test_file.name in ("__init__.py", "conftest.py"):
            continue

        try:
            content = test_file.read_text(encoding="utf-8")

            # Check if file starts with Python docstring or imports
            if (
                not content.startswith('"""')
                and not content.startswith("import")
                and not content.startswith("from")
            ):
                # Extract class name from filename
                class_name = test_file.stem.replace("test_", "")
                class_name = "".join(word.capitalize() for word in class_name.split("_"))

                # Add proper header
                header = f'''"""
Test file for {class_name}

MECE Test Categories:
- Initialization: Constructor and __post_init__ behavior
- Core Methods: Primary business logic
- Edge Cases: Boundary conditions and error handling
- Type Boundaries: Input/output type validation

Validation Points:
- Acronym Protection: Using _to_smart_snake_case for all references
- Suffix Hygiene: No stuttering patterns like AgentOrchestrator
- Primary Class Focus: {class_name} only, secondaries mocked
"""

'''

                # Remove any leading non-Python content
                lines = content.split("\n")
                cleaned_lines = []
                for line in lines:
                    if (
                        line.strip().startswith("import")
                        or line.strip().startswith("from")
                        or line.strip().startswith("class")
                        or line.strip().startswith("def")
                        or line.strip().startswith("@")
                    ):
                        cleaned_lines.append(line)
                    elif (
                        line.strip()
                        and not line.startswith("-")
                        and not line.startswith("Validation")
                        and not line.startswith("Test")
                    ):
                        # This might be actual code, keep it
                        cleaned_lines.append(line)

                new_content = header + "\n".join(cleaned_lines)
                test_file.write_text(new_content, encoding="utf-8")
                fixed_count += 1
                print(f"Regenerated: {test_file.relative_to(project_root)}")

        except (UnicodeDecodeError, OSError):
            continue

    print(f"\nTotal files regenerated: {fixed_count}")


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    regenerate_headers(project_root)
