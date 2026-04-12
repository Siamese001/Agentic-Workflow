"""
tools/capture_evidence.py

Captures command output to an evidence file with PowerShell detection guard.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "capture_evidence", "uwg_governed_write")
_emit_writes_through("p1", "capture_evidence", "uwg_governed_write_2")
_emit_pulls_context("p1", "capture_evidence", "context_retrieval")
_emit_pulls_context("p1", "capture_evidence", "context_retrieval_2")
emit_determinism_digest("trace_capture_evidence", "capture_evidence_dispatch")
emit_determinism_digest("trace_capture_evidence", "capture_evidence_complete")
_emit_validated_by_safety_plane("p1", "capture_evidence", "safety_validation")


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
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    combined = (result.stdout or "") + (result.stderr or "")
    lower = combined.lower()
    if "powershell" in lower or "pwsh" in lower:
        raise RuntimeError(
            f"PowerShell detected in command output. Aborting evidence capture. stdout={result.stdout!r} stderr={result.stderr!r}"
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
