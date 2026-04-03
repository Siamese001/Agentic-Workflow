#!/usr/bin/env python3
"""
Contract Gates — Main CI Entrypoint

Runs all contract validation gates in deterministic order.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run_cmd(args, cwd=None):
    """Run a command and return result."""
    result = subprocess.run(args, capture_output=True, text=True, cwd=cwd)
    return result.returncode, result.stdout, result.stderr


# PRE-WRITE HOOKS INTEGRATION
def validate_pre_write_hooks():
    """Validate all pre-write hook skills."""
    skills_dir = Path(".windsurf/skills")
    failed_skills = []

    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir():
            main_script = skill_dir / "main.py"
            if main_script.exists():
                try:
                    result = subprocess.run(
                        ["python", str(main_script), "--health-check"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode != 0:
                        failed_skills.append(skill_dir.name)
                except Exception:
                    failed_skills.append(skill_dir.name)

    if failed_skills:
        print(f"❌ Failed skills: {', '.join(failed_skills)}")
        return False

    print("✅ All pre-write hooks validated")
    return True


def main():
    """Run all contract gates in deterministic order."""
    repo_root = Path(__file__).parent.parent.parent

    # Validate pre-write hooks
    if not validate_pre_write_hooks():
        sys.exit(1)

    # Gate: No archives/ imports in production code (Rule 12)
    print("🔍 Checking for archives/ imports in production code...")
    returncode, stdout, stderr = run_cmd([sys.executable, str(ROOT / "ops_scripts/ci/check_no_archives_imports.py")], cwd=ROOT)
    if returncode != 0:
        print(stdout)
        print(stderr)
        sys.exit(1)
    print("✅ No archives/ imports found")

    # Continue with existing logic...
    return 0


if __name__ == "__main__":
    sys.exit(main())
