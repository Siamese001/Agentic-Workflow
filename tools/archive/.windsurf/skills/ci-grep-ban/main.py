#!/usr/bin/env python3
"""
Windsurf Skill: CI Grep Ban
Enforces ADG grep ban via existing CI script.
"""

import subprocess
import sys
from pathlib import Path

# guardian: allow-silent-swallower -- Exception handling for CI script execution
# guardian: allow-magic-configuration -- CI script path and argument configuration


def validate_files(files: list[str]) -> tuple[bool, str, str]:
    """Call existing CI script with files."""
    if not files:
        return True, "No files to check", ""

    # Convert to absolute paths if needed
    abs_files = []
    for f in files:
        path = Path(f)
        if not path.is_absolute():
            path = Path.cwd() / path
        abs_files.append(str(path))

    # Call the existing CI script
    cmd = ["python", "ops_scripts/ci/adg_grep_ban_gate.py"] + abs_files

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=Path.cwd(),
        )

        success = result.returncode == 0
        stdout = result.stdout or ""
        stderr = result.stderr or ""

        return success, stdout, stderr

    except subprocess.TimeoutExpired:
        return False, "", "Grep ban check timed out"
    except Exception as e:
        return False, "", f"Error running grep ban check: {e}"


def main():
    """Main entry point for the skill."""
    if len(sys.argv) < 2:
        print("Usage: python main.py <file1> [file2 ...]")
        print("Checks files for grep/rg violations using CI script")
        sys.exit(1)

    # Health check
    if len(sys.argv) == 2 and sys.argv[1] == "--health-check":
        print("[PASS] CI grep ban health check")
        sys.exit(0)

    files = sys.argv[1:]

    # Filter to Python files only (grep ban only applies to .py)
    py_files = []
    for f in files:
        if f.endswith('.py'):
            py_files.append(f)

    if not py_files:
        print("[INFO] No Python files to check")
        sys.exit(0)

    success, stdout, stderr = validate_files(py_files)

    if success:
        print("[PASS] Grep ban validation passed")
        if stdout:
            print(stdout)
        sys.exit(0)
    else:
        print("[FAIL] Grep ban validation failed")
        if stdout:
            print(stdout)
        if stderr:
            print(f"Errors: {stderr}")
        print("\n💡 Use ADG accelerators instead:")
        print("  Symbol search: python tools/adg/adg_redis_query.py search-nodes <term>")
        print("  File search:   python tools/adg/adg_redis_query.py search-files <term>")
        sys.exit(1)


if __name__ == "__main__":
    main()
