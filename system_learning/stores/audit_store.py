"""Concrete AuditStore — reads compliance report data as audit slices.

Reads from ``logs/compliance_reports/`` to produce byte-serialized audit
slices for the meta-learning pipeline.  All I/O is explicit (no background
scanning) and deterministic given the same file contents.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

logger = logging.getLogger(__name__)


class FileBackedAuditStore:
    """File-backed audit store reading from compliance report directory.

    Parameters
    ----------
    reports_dir : Path
        Directory containing compliance report JSON files.
    """

    def __init__(self, reports_dir: Path) -> None:
        self._reports_dir = Path(reports_dir)

    def read_audit_slice(self, window_start_utc: int, window_end_utc: int) -> bytes:
        """Read audit data within the given time window.

        Scans compliance report files and returns a JSON-serialized byte
        payload containing all reports whose timestamps fall within
        ``[window_start_utc, window_end_utc]``.  If no reports match or
        the directory is empty, returns an empty JSON array (``b"[]"``).

        Parameters
        ----------
        window_start_utc : int
            Start of the time window (inclusive).
        window_end_utc : int
            End of the time window (inclusive).

        Returns
        -------
        bytes
            JSON-encoded list of matching report dicts.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "FileBackedAuditStore.read_audit_slice")

        if not self._reports_dir.exists():
            return b"[]"
        matched: list[dict] = []
        for report_path in sorted(self._reports_dir.glob("*.json")):
            try:
                data = json.loads(report_path.read_text(encoding="utf-8"))
                ts = data.get("timestamp_utc") or data.get("created_utc", 0)
                if isinstance(ts, str):
                    ts = 0
                if window_start_utc <= ts <= window_end_utc:
                    matched.append(data)
                elif ts == 0:
                    matched.append(data)
            except (json.JSONDecodeError, OSError) as exc:
                logger.debug("Skipping unreadable report %s: %s", report_path.name, exc)
                continue
        return json.dumps(matched, separators=(",", ":"), sort_keys=True).encode("utf-8")


class InMemoryAuditStore:
    """In-memory audit store for testing.

    Pre-loaded with byte slices keyed by ``(window_start, window_end)`` tuples.
    Falls back to ``b"[]"`` for unknown windows.
    """

    def __init__(self, slices: dict[tuple[int, int], bytes] | None = None) -> None:
        self._slices: dict[tuple[int, int], bytes] = slices or {}

    def read_audit_slice(self, window_start_utc: int, window_end_utc: int) -> bytes:
        return self._slices.get((window_start_utc, window_end_utc), b"[]")

    def add_slice(self, window_start_utc: int, window_end_utc: int, data: bytes) -> None:
        self._slices[window_start_utc, window_end_utc] = data


__all__ = ["FileBackedAuditStore", "InMemoryAuditStore"]
