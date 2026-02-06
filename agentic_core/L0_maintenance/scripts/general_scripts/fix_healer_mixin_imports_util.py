"""
Script to fix all incorrect healer_mixin import paths.

Changes:
    from agentic_core.base_agents.healer_mixin import healer_mixin
to:
    from agentic_core.base_agents.healer_mixin import healer_mixin
"""


def fix_healer_mixin_imports(project_root: Path):
    """Fix all healer_mixin imports in the codebase."""

    old_import = "from agentic_core.base_agents.healer_mixin import"
    new_import = "from agentic_core.base_agents.healer_mixin import"

    fixed_count = 0

    # Search all Python files
    for py_file in project_root.rglob("*.py"):
        # Skip archives and backups
        if any(
            skip in str(py_file) for skip in ["archives", ".sovereign_healing_backup", "__pycache__", ".venv"]
        ):
            continue

        try:
            content = py_file.read_text(encoding="utf-8")

            if old_import in content:
                new_content = content.replace(old_import, new_import)
                py_file.write_text(new_content, encoding="utf-8")
                print(f"Fixed: {py_file.relative_to(project_root)}")
                fixed_count += 1
        except Exception as e:
            print(f"Error processing {py_file}: {e}")

    print(f"\nTotal files fixed: {fixed_count}")


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    fix_healer_mixin_imports(project_root)
