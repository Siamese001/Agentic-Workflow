"""
Regenerate proper Python headers for all test files.
"""

from pathlib import Path

from agentic_core.L0_routing.config.path_constants import TESTS_DIR
from tqdm import tqdm

REPO_ROOT = Path(__file__).resolve().parents[2]


def regenerate_headers(project_root: Path):
    """Add proper Python headers to test files."""
    test_dir = project_root / TESTS_DIR / "unit"
    fixed_count = 0
    for test_file in tqdm(test_dir.rglob("*.py"), desc="Processing", unit="item"):
        if test_file.name in ("__init__.py", "conftest.py"):
            continue
        try:
            content = test_file.read_text(encoding="utf-8")
            if (
                not content.startswith('"""')
                and (not content.startswith("import"))
                and (not content.startswith("from"))
            ):
                class_name = test_file.stem.replace("test_", "")
                class_name = "".join(word.capitalize() for word in class_name.split("_"))
                header = f'"""\nTest file for {class_name}\n\nMECE Test Categories:\n- Initialization: Constructor and __post_init__ behavior\n- Core Methods: Primary business logic\n- Edge Cases: Boundary conditions and error handling\n- Type Boundaries: Input/output type validation\n\nValidation Points:\n- Acronym Protection: Using _to_smart_snake_case for all references\n- Suffix Hygiene: No stuttering patterns like AgentOrchestrator\n- Primary Class Focus: {class_name} only, secondaries mocked\n"""\n\n'
                lines = content.split("\n")
                cleaned_lines = []
                for line in tqdm(lines, desc="Processing", unit="item"):
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
                        and (not line.startswith("-"))
                        and (not line.startswith("Validation"))
                        and (not line.startswith("Test"))
                    ):
                        cleaned_lines.append(line)
                new_content = header + "\n".join(cleaned_lines)
                test_file.write_text(new_content, encoding="utf-8")
                fixed_count += 1
                print(f"Regenerated: {test_file.relative_to(project_root)}")
        except (
            UnicodeDecodeError,
            OSError,
        ):  # review: File operations with encoding need error-specific handling
            continue
    print(f"\nTotal files regenerated: {fixed_count}")


if __name__ == "__main__":
    project_root = REPO_ROOT
    regenerate_headers(project_root)
