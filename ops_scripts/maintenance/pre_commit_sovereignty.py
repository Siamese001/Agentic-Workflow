"""
File: ops_scripts/maintenance/pre_commit_sovereignty.py
Path: ops_scripts/maintenance/pre_commit_sovereignty.py
Rationale:
    Implements the 'Sovereignty Shield' to prevent non-compliant code from entering
    the version history. This script is the primary local enforcement mechanism.
    Critical Analysis: While local hooks are effective, they can be bypassed with
    --no-verify. Next Steps must include a server-side mirror of this logic in
    GitHub Actions to ensure absolute enforcement.
"""

import logging
import subprocess
import sys

# [HARDENED] Standard logging for audit trail visibility
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
Logger = logging.getLogger("SovereigntyShield")


def run_audit() -> bool:
    """
    Executes the master audit suite in headless validation mode.
    Returns True if compliant, False otherwise.
    """
    Logger.info("🛡️ [SOVEREIGNTY SHIELD] Auditing commit for SSOT compliance...")

    try:
        # [CRITICAL] We invoke execute_ssot.py with --validate to ensure we check
        # without modifying the developer's working tree during the commit phase.
        # --autonomous flag ensures no user prompts are triggered.
        process = subprocess.run(
            [sys.executable, "execute_ssot.py", "--validate", "--autonomous"],
            capture_output=True,
            text=True,
            check=False,
        )

        if process.returncode != 0:
            Logger.error("❌ [BLOCK] Commit rejected due to Sovereignty Violations.")
            # Print the captured output so the developer knows what to fix
            print(process.stdout)
            return False

        Logger.info("✅ [PASS] Repository is compliant. Proceeding with commit.")
        return True

    except Exception as e:
        Logger.error(f"⚠️ [ERROR] Sovereignty audit failed to execute: {e}")
        return False


if __name__ == "__main__":
    # Integration Note: This script should be symlinked to .git/hooks/pre-commit
    if not run_audit():
        sys.exit(1)
