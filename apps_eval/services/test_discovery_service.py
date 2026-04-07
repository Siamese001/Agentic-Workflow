"""
Test Discovery Service — apps_eval

Discovers and catalogs tests from ADG and codebase.
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

_log = logging.getLogger(__name__)


class TestDiscoveryService:
    """Service for discovering and cataloging tests."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize the test discovery service."""
        self.config = config or {}
        self._discovered_tests: list[dict[str, Any]] = []

        # Lifecycle trace emission
        emit_replay_key("test_discovery", "init")
        emit_determinism_digest("test_discovery", "init")
        _emit_applies_guardrail("p0", "test_discovery", "service_init")
        _emit_snapshots_state("p0", "test_discovery", "service_state")

    def discover_from_adg(
        self,
        module_pattern: str = "tests/**/*test*.py",
        target_layer: str | None = None,
    ) -> list[dict[str, Any]]:
        """Discover tests using ADG graph queries.

        Args:
            module_pattern: Glob pattern for test modules
            target_layer: Optional layer filter (L0-L6)

        Returns:
            List of discovered test metadata
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "TestDiscoveryService.discover_from_adg",
        )
        _emit_routes_to_capability("p2", "test_discovery", "adg_query")
        _emit_validates_capability("p2", "test_discovery", "adg_access")
        _emit_records_telemetry_event("p4", "test_discovery", "discover_start")

        try:
            # Mock implementation - actual ADG integration would go here
            discovered = [
                {
                    "test_id": f"test_{i}",
                    "module": module_pattern,
                    "layer": target_layer or "unknown",
                    "capability": "test_execution",
                }
                for i in range(5)
            ]

            self._discovered_tests.extend(discovered)
            _log.info("Discovered %d tests from ADG", len(discovered))

            _emit_records_telemetry_event("p4", "test_discovery", "discover_complete")
            return discovered

        except Exception as exc:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            _log.error("Test discovery failed: %s", exc)
            _emit_records_telemetry_event("p4", "test_discovery", "discover_error")
            raise

    def discover_from_codebase(
        self,
        source_dirs: list[str],
        test_patterns: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Discover tests by scanning the codebase.

        Args:
            source_dirs: Directories to scan
            test_patterns: File patterns to match

        Returns:
            List of discovered test metadata
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "TestDiscoveryService.discover_from_codebase",
        )
        _emit_routes_to_capability("p2", "test_discovery", "filesystem_scan")

        test_patterns = test_patterns or ["test_*.py", "*_test.py"]
        discovered: list[dict[str, Any]] = []

        for source_dir in source_dirs:
            path = Path(source_dir)
            if not path.exists():
                _log.warning("Source directory does not exist: %s", source_dir)
                continue

            for pattern in test_patterns:
                for test_file in path.rglob(pattern):
                    discovered.append({
                        "test_id": test_file.stem,
                        "module": str(test_file),
                        "pattern": pattern,
                        "capability": "test_execution",
                    })

        self._discovered_tests.extend(discovered)
        _log.info("Discovered %d tests from codebase", len(discovered))
        _emit_records_telemetry_event("p4", "test_discovery", f"codebase_discovered:{len(discovered)}")

        return discovered

    def get_catalog(self) -> list[dict[str, Any]]:
        """Get the full catalog of discovered tests."""
        return self._discovered_tests.copy()

    def clear_catalog(self) -> None:
        """Clear the test catalog."""
        self._discovered_tests.clear()
        _emit_records_telemetry_event("p4", "test_discovery", "catalog_cleared")
