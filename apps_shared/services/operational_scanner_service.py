"""
Operational Scanner Service — apps_shared

Service for scanning codebase for operational tasks.
Aligned with apps_lic service pattern with lifecycle trace integration.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
    _emit_routes_to_capability,
    _emit_snapshots_state,
    _emit_validates_capability,
    emit_determinism_digest,
    emit_replay_key,
)

from apps_shared.config.operational_config import (
    is_allowed_duplicate,
    is_excluded_path,
)

_log = logging.getLogger(__name__)


class OperationalScannerService:
    """Service for operational codebase scanning."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize the operational scanner service."""
        self.config = config or {}
        self._scan_results: list[dict[str, Any]] = []

        # Lifecycle trace emission
        emit_replay_key("op_scanner", "init")
        emit_determinism_digest("op_scanner", "init")
        _emit_applies_guardrail("p0", "op_scanner", "service_init")
        _emit_snapshots_state("p0", "op_scanner", "service_state")

    def scan_directory(
        self,
        directory: str,
        file_extensions: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Scan a directory for operational analysis.

        Args:
            directory: Path to scan
            file_extensions: Optional file extensions to filter

        Returns:
            List of scanned file metadata
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "OperationalScannerService.scan_directory"
        )
        _emit_routes_to_capability("p2", "op_scanner", "filesystem_scan")
        _emit_validates_capability("p2", "op_scanner", "read_permissions")
        _emit_records_telemetry_event("p4", "op_scanner", "scan_start")

        dir_path = Path(directory)
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        scanned: list[dict[str, Any]] = []

        for file_path in dir_path.rglob("*"):
            if not file_path.is_file():
                continue

            # Check exclusion
            if is_excluded_path(str(file_path)):
                continue

            # Check duplicate allowance
            if is_allowed_duplicate(file_path.name):
                # Still track but mark as allowed duplicate
                is_dup = True
            else:
                is_dup = False

            file_info = {
                "path": str(file_path),
                "name": file_path.name,
                "size": file_path.stat().st_size,
                "is_allowed_duplicate": is_dup,
            }
            scanned.append(file_info)

        self._scan_results.extend(scanned)
        _log.info("Scanned %d files in %s", len(scanned), directory)
        _emit_records_telemetry_event("p4", "op_scanner", f"scan_complete:{len(scanned)}")

        return scanned

    def get_scan_summary(self) -> dict[str, Any]:
        """Get summary of scan results."""
        if not self._scan_results:
            return {"total_files": 0, "allowed_duplicates": 0}

        total = len(self._scan_results)
        duplicates = sum(1 for r in self._scan_results if r.get("is_allowed_duplicate"))

        return {
            "total_files": total,
            "allowed_duplicates": duplicates,
            "unique_files": total - duplicates,
        }

    def clear_results(self) -> None:
        """Clear scan results."""
        self._scan_results.clear()
        _emit_records_telemetry_event("p4", "op_scanner", "results_cleared")
