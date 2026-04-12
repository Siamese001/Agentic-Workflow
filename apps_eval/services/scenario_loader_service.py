"""
Scenario Loader Service — apps_eval

Loads and validates test scenarios from various sources.
Aligned with apps_lic service pattern with lifecycle trace integration.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
    _emit_routes_to_capability,
    _emit_snapshots_state,
)

_log = logging.getLogger(__name__)


class ScenarioLoaderService:
    """Service for loading and validating test scenarios."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize the scenario loader service."""
        self.config = config or {}
        self._scenarios: dict[str, dict[str, Any]] = {}
        _emit_snapshots_state("p0", "scenario_loader", "init")

    def load_from_file(self, file_path: str) -> list[dict[str, Any]]:
        """Load scenarios from a JSON file."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L2_EXECUTION,
            "ScenarioLoaderService.load_from_file",
        )
        _emit_routes_to_capability("p2", "scenario_loader", "json_parse")

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Scenario file not found: {file_path}")

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            scenarios = data.get("scenarios", [])

            for scenario in scenarios:
                scenario_id = scenario.get("scenario_id", f"scen_{len(self._scenarios)}")
                self._scenarios[scenario_id] = scenario

            _log.info("Loaded %d scenarios from %s", len(scenarios), file_path)
            _emit_records_telemetry_event("p4", "scenario_loader", f"loaded:{len(scenarios)}")
            return scenarios

        except json.JSONDecodeError as exc:
            _log.error("Failed to parse scenario file: %s", exc)
            raise

    def load_from_directory(self, directory: str) -> list[dict[str, Any]]:
        """Load all scenario files from a directory."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L2_EXECUTION,
            "ScenarioLoaderService.load_from_directory",
        )

        dir_path = Path(directory)
        if not dir_path.exists():
            raise FileNotFoundError(f"Scenario directory not found: {directory}")

        all_scenarios: list[dict[str, Any]] = []
        for scenario_file in dir_path.glob("*.json"):
            scenarios = self.load_from_file(str(scenario_file))
            all_scenarios.extend(scenarios)

        _emit_records_telemetry_event("p4", "scenario_loader", f"dir_loaded:{len(all_scenarios)}")
        return all_scenarios

    def get_scenario(self, scenario_id: str) -> dict[str, Any] | None:
        """Get a specific scenario by ID."""
        return self._scenarios.get(scenario_id)

    def get_all_scenarios(self) -> list[dict[str, Any]]:
        """Get all loaded scenarios."""
        return list(self._scenarios.values())

    def validate_scenario(self, scenario: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate a scenario has required fields."""
        errors: list[str] = []
        required = ["scenario_id", "description", "expected_behavior"]

        for field in required:
            if field not in scenario:
                errors.append(f"Missing required field: {field}")

        return len(errors) == 0, errors
