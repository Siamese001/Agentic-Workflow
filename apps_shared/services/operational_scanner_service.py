"""
Operational Scanner Service — apps_shared

Service for scanning codebase for operational tasks.
Aligned with apps_lic service pattern with lifecycle trace integration.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
from tqdm import tqdm

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

    @staticmethod
    def _normalize_extensions(file_extensions: list[str] | None) -> set[str] | None:
        if not file_extensions:
            return None
        normalized = set()
        for ext in file_extensions:
            cleaned = str(ext).strip().lower()
            if cleaned:
                normalized.add(cleaned if cleaned.startswith(".") else f".{cleaned}")
        return normalized or None

    def scan_directory(
        self,
        directory: str,
        file_extensions: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Scan a directory for operational analysis."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L2_EXECUTION,
            "OperationalScannerService.scan_directory",
        )
        _emit_routes_to_capability("p2", "op_scanner", "filesystem_scan")
        _emit_validates_capability("p2", "op_scanner", "read_permissions")
        _emit_records_telemetry_event("p4", "op_scanner", "scan_start")

        dir_path = Path(directory).expanduser().resolve()
        if not dir_path.is_dir():
            raise FileNotFoundError(f"Directory not found: {directory}")

        allowed_extensions = self._normalize_extensions(file_extensions)
        max_files = int(self.config.get("max_files", 50_000))
        scanned: list[dict[str, Any]] = []
        skipped = 0

        for file_path in tqdm(sorted(dir_path.rglob("*")), desc="Processing", unit="item"):
            if len(scanned) >= max_files:
                _emit_applies_guardrail("p0", "op_scanner", "max_files_reached")
                break
            if not file_path.is_file() or file_path.is_symlink():
                continue
            if allowed_extensions and file_path.suffix.lower() not in allowed_extensions:
                continue

            if is_excluded_path(str(file_path)):
                continue

            try:
                stat = file_path.stat()
            except OSError:
                skipped += 1
                continue

            file_info = {
                "path": str(file_path),
                "name": file_path.name,
                "size": stat.st_size,
                "is_allowed_duplicate": is_allowed_duplicate(file_path.name),
            }
            scanned.append(file_info)

        self._scan_results.extend(scanned)
        _log.info("Scanned %d files in %s (%d skipped)", len(scanned), dir_path, skipped)
        _emit_records_telemetry_event(
            "p4",
            "op_scanner",
            f"scan_complete:{len(scanned)}:skipped={skipped}",
        )

        return scanned

    def get_scan_summary(self) -> dict[str, Any]:
        """Get summary of scan results."""
        if not self._scan_results:
            return {"total_files": 0, "allowed_duplicates": 0, "unique_files": 0}

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
