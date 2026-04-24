#!/usr/bin/env python3
"""
Windsurf Skill: CI Schema Validation
Validates ADG schema field names via CI script.
"""

import subprocess
import sys
from pathlib import Path

# guardian: allow-silent-swallower -- Exception handling for CI script execution
# guardian: allow-magic-configuration -- CI script path and argument configuration


def validate_schema_fields(file_path: str) -> tuple[bool, str, str]:
    """Call existing CI script to validate ADG schema field names."""
    path = Path(file_path)

    # Convert to absolute path if needed
    if not path.is_absolute():
        path = Path.cwd() / path

    # Only check files in ops_scripts/ or tools/ directories
    if not (
        str(path).startswith(str(Path.cwd() / "ops_scripts"))
        or str(path).startswith(str(Path.cwd() / "tools"))
    ):
        return True, "File not in schema validation scope", ""

    # Call the existing CI script
    cmd = ["python", "ops_scripts/ci/check_adg_schema_field_names.py", str(path)]

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
        return False, "", "Schema validation timed out"
    except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
        return False, "", f"Error running schema validation: {e}"


def main():
    """Main entry point for the skill."""
    if len(sys.argv) != 2:
        print("Usage: python main.py <file>")
        print("Validates ADG schema field names in the specified file")
        sys.exit(1)

    # Health check
    if len(sys.argv) == 2 and sys.argv[1] == "--health-check":
        print("[PASS] CI schema validation health check")
        sys.exit(0)

    file_path = sys.argv[1]

    # Check if file exists
    if not Path(file_path).exists():
        print(f"[ERROR] File not found: {file_path}")
        sys.exit(1)

    success, stdout, stderr = validate_schema_fields(file_path)

    if success:
        print("[PASS] Schema validation passed")
        if stdout:
            print(stdout)
        sys.exit(0)
    else:
        print("[FAIL] Schema validation failed")
        if stdout:
            print(stdout)
        if stderr:
            print(f"Errors: {stderr}")
        print("\n💡 ADG schema field name requirements:")
        print("  1. Use canonical field names per §16.2")
        print("  2. entityType → entity_type")
        print("  3. entityName → name")
        print("  4. import_edges → imports")
        print("  5. call_edges → calls")
        print("  6. test_edges → tests")
        sys.exit(1)


if __name__ == "__main__":
    main()
