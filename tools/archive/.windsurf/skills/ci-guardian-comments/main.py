#!/usr/bin/env python3
"""
Windsurf Skill: CI Guardian Comments
Validates guardian comment format via CI script.
"""

import subprocess
import sys
from pathlib import Path

# guardian: allow-silent-swallower -- Exception handling for CI script execution
# guardian: allow-magic-configuration -- CI script path and argument configuration


def validate_guardian_comments(file_path: str) -> tuple[bool, str, str]:
    """Call existing CI script to validate guardian comments."""
    path = Path(file_path)

    # Convert to absolute path if needed
    if not path.is_absolute():
        path = Path.cwd() / path

    # Call the existing CI script
    cmd = ["python", "ops_scripts/ci/guardian_exemption_gate.py", str(path)]

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
        return False, "", "Guardian comment validation timed out"
    except Exception as e:
        return False, "", f"Error running guardian comment validation: {e}"


def main():
    """Main entry point for the skill."""
    if len(sys.argv) != 2:
        print("Usage: python main.py <file>")
        print("Validates guardian comment format in the specified file")
        sys.exit(1)

    # Health check
    if len(sys.argv) == 2 and sys.argv[1] == "--health-check":
        print("[PASS] CI guardian comments health check")
        sys.exit(0)

    file_path = sys.argv[1]

    # Check if file exists
    if not Path(file_path).exists():
        print(f"[ERROR] File not found: {file_path}")
        sys.exit(1)

    success, stdout, stderr = validate_guardian_comments(file_path)

    if success:
        print("[PASS] Guardian comment validation passed")
        if stdout:
            print(stdout)
        sys.exit(0)
    else:
        print("[FAIL] Guardian comment validation failed")
        if stdout:
            print(stdout)
        if stderr:
            print(f"Errors: {stderr}")
        print("\n💡 Guardian comment requirements:")
        print("  1. Format: # guardian: allow-<type> -- <specific justification>")
        print("  2. No generic words (needed, required, temporary, legacy)")
        print("  3. Specific, detailed justification (20+ chars)")
        print("  4. HITL approval for production code")
        print("  5. Must not exceed exemption ceiling")
        sys.exit(1)


if __name__ == "__main__":
    main()
