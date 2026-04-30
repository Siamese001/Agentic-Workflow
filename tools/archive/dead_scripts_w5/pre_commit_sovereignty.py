"""
File: ops_scripts/maintenance/pre_commit_sovereignty.py
Path: ops_scripts/maintenance/pre_commit_sovereignty.py
"""

import logging
import subprocess
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
Logger = logging.getLogger("SovereigntyShield")


def run_audit() -> bool:
    """Execute the master audit suite in headless validation mode."""
    Logger.info("🛡️ [SOVEREIGNTY SHIELD] Auditing commit for SSOT compliance...")

    try:
        process = subprocess.run(
            [sys.executable, "execute_ssot.py", "--validate", "--autonomous"],
            capture_output=True,
            text=True,
            check=False,
            timeout=300,
        )

        if process.returncode != 0:
            Logger.error("❌ [BLOCK] Commit rejected due to Sovereignty Violations.")
            print(process.stdout)
            if process.stderr:
                print(process.stderr)
            return False

        Logger.info("✅ [PASS] Repository is compliant. Proceeding with commit.")
        return True

    except (OSError, subprocess.SubprocessError) as exc:
        Logger.error("⚠️ [ERROR] Sovereignty audit failed to execute: %s", exc)
        return False


if __name__ == "__main__":
    if not run_audit():
        sys.exit(1)
