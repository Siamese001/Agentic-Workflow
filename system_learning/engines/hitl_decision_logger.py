"""
HITL Decision Logger — Wave 6.

Appends structured HITL decision records to the active evidence file so every
human-in-the-loop choice is auditable and replayable.

Design constraints:
- Pure stdlib (no third-party imports).
- Thread-safe via module-level lock.
- Deterministic record format (no wall-clock timestamps in keys).
- ASCII-only output (evidence file byte-scan invariant §2).
"""

from __future__ import annotations

import os
import threading
from pathlib import Path
from typing import Any

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

_lock = threading.Lock()
_decision_counter: int = 0

_DEFAULT_EVIDENCE_PATH = Path("docs/reports/evidence/wave6_evidence.md")


def _get_evidence_path() -> Path:
    env_val = os.environ.get("HITL_EVIDENCE_FILE")
    if env_val:
        return Path(env_val)
    return _DEFAULT_EVIDENCE_PATH


def log_hitl_decision(
    agent: str,
    file_path: str,
    violation: str,
    proposed: str,
    decision: str,
    extra: dict[str, Any] | None = None,
) -> int:
    """Append one HITL decision record to the evidence file.

    Args:
        agent:      Agent class name that triggered the gate.
        file_path:  Relative or absolute path of the affected file.
        violation:  Violation type string (e.g. PASCAL_IN_NON_AGENT_FOLDER).
        proposed:   What the agent was about to do (e.g. ARCHIVE, MOVE).
        decision:   Outcome after HITL review (e.g. APPROVED, SKIPPED, MANUAL).
        extra:      Optional additional key-value pairs appended to the record.

    Returns:
        The sequential decision number (1-based).
    """
    global _decision_counter
    evidence_path = _get_evidence_path()

    with _lock:
        _decision_counter += 1
        n = _decision_counter

        lines = [
            f"\nHITL_DECISION_{n}: Agent={agent} | File={file_path}",
            f"  Violation={violation} | Proposed={proposed} | Decision={decision}",
        ]
        if extra:
            for k, v in extra.items():
                safe_k = str(k).replace("\n", " ")
                safe_v = str(v).replace("\n", " ")
                lines.append(f"  {safe_k}={safe_v}")

        record = "\n".join(lines) + "\n"

        # Byte-scan: replace any non-ASCII byte with '?'
        safe_record = record.encode("ascii", errors="replace").decode("ascii")

        try:
            evidence_path.parent.mkdir(parents=True, exist_ok=True)
            with open(evidence_path, "a", encoding="ascii", errors="replace") as fh:
                fh.write(safe_record)
        except OSError:
            pass

        return n


def get_decision_count() -> int:
    """Return number of decisions logged in this process lifetime."""
    with _lock:
        return _decision_counter


def reset_for_testing() -> None:
    """Reset counter — test use only."""
    global _decision_counter
    with _lock:
        _decision_counter = 0
