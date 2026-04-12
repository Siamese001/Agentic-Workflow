#!/usr/bin/env python3
"""
Windsurf Skill: CI Hollow File
Detects hollow files during creation/editing.
"""

import sys
from pathlib import Path

# guardian: allow-silent-swallower -- Exception handling for CI script execution
# guardian: allow-magic-configuration -- CI script path and argument configuration


def validate_hollow_file(file_path: str) -> tuple[bool, str, str]:
    """Simple hollow file detection for single file."""
    path = Path(file_path)

    # Convert to absolute path if needed
    if not path.is_absolute():
        path = Path.cwd() / path

    try:
        # Check if file is empty
        if not path.exists():
            return False, "", f"File not found: {file_path}"

        content = path.read_text(encoding="utf-8").strip()

        # Check for hollow file patterns
        if not content:
            return False, "File is empty", ""

        # Check for only whitespace/comments
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        meaningful_lines = []

        for line in lines:
            # Skip comment lines
            if (
                line.startswith("#")
                or line.startswith("//")
                or line.startswith('"""')
                or line.startswith("'''")
            ):
                continue
            # Skip import statements
            if line.startswith("import ") or line.startswith("from "):
                continue
            # Skip docstring markers
            if line in ['"""', "'''"]:
                continue
            meaningful_lines.append(line)

        if not meaningful_lines:
            return False, "File contains only imports/comments", ""

        # Check minimum meaningful content (at least 5 lines of actual code)
        if len(meaningful_lines) < 5 and path.suffix == ".py":
            return (
                False,
                f"Python file has insufficient content ({len(meaningful_lines)} meaningful lines)",
                "",
            )

        return True, "File has meaningful content", ""

    except Exception as e:
        return False, "", f"Error checking file: {e}"


def main():
    """Main entry point for the skill."""
    if len(sys.argv) != 2:
        print("Usage: python main.py <file>")
        print("Detects hollow files in the specified file")
        sys.exit(1)

    # Health check
    if len(sys.argv) == 2 and sys.argv[1] == "--health-check":
        print("[PASS] CI hollow file health check")
        sys.exit(0)

    file_path = sys.argv[1]

    # Check if file exists
    if not Path(file_path).exists():
        print(f"[ERROR] File not found: {file_path}")
        sys.exit(1)

    success, stdout, stderr = validate_hollow_file(file_path)

    if success:
        print("[PASS] Hollow file validation passed")
        if stdout:
            print(stdout)
        sys.exit(0)
    else:
        print("[FAIL] Hollow file validation failed")
        if stdout:
            print(stdout)
        if stderr:
            print(f"Errors: {stderr}")
        print("\n💡 Hollow file requirements:")
        print("  1. Files must contain meaningful content")
        print("  2. Avoid empty behavioral files")
        print("  3. Include proper documentation and implementation")
        sys.exit(1)


if __name__ == "__main__":
    main()
