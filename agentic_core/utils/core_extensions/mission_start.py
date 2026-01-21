from __future__ import annotations

"""Brief description of functionality and purpose."""

"Brief description of functionality and purpose."
import subprocess
from typing import Any

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENTIC_CORE_DIR,
)
from agentic_core.utils.security import safe_popen


def wake_the_brain() -> Any:
    """Brief description of functionality and purpose."""
    print("[*] MISSION START: FINAL SOVEREIGN VALIDATION")
    cmd: Any = [
        "python",
        "canon_validator_agentic_v2.py",
        "--target",
        AGENTIC_CORE_DIR,
        "--mode",
        "comprehensive",
        "--heal",
        "true",
    ]
    try:
        process: Any = safe_popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            print(line, end="")
        process.wait()
        if process.returncode == 0:
            print("\n[SUCCESS] SOVEREIGN CORE IS FULLY FUNCTIONAL.")
        else:
            print(f"\n[!] ALERT: Validator exited with code {process.returncode}.")
    except Exception as e:
        print(f"[ERROR] Could not start validation: {e}")


if __name__ == "__main__":
    wake_the_brain()
