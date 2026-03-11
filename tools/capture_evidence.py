"""
tools/capture_evidence.py

Captures command output to an evidence file with PowerShell detection guard.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

def capture_command(cmd: list[str], evidence_file: Path) -> int:
    """Run cmd, write stdout+stderr to evidence_file, abort on PowerShell output.

    Args:
        cmd: Command argv list (no shell=True).
        evidence_file: Path to write captured output.

    Returns:
        Exit code of the command.

    Raises:
        RuntimeError: If any output contains 'powershell' or 'pwsh' (case-insensitive).
    """
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    combined = (result.stdout or "") + (result.stderr or "")
    lower = combined.lower()
    if "powershell" in lower or "pwsh" in lower:
        raise RuntimeError(
            f"PowerShell detected in command output. Aborting evidence capture. "
            f"stdout={result.stdout!r} stderr={result.stderr!r}"
        )

    evidence_file.parent.mkdir(parents=True, exist_ok=True)
    with evidence_file.open("w", encoding="utf-8") as f:
        if result.stdout:
            f.write(result.stdout)
        if result.stderr:
            f.write(result.stderr)

    return result.returncode


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: capture_evidence.py <evidence_file> <cmd> [args...]")
        sys.exit(1)
    out_path = Path(sys.argv[1])
    code = capture_command(sys.argv[2:], out_path)
    sys.exit(code)
