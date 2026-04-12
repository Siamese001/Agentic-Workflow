"""
Config Loader Service — apps_shared

Service for loading and validating configuration files.
Aligned with apps_lic service pattern with lifecycle trace integration.
"""

from __future__ import annotations

import json
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


class ConfigLoaderService:
    """Service for loading and validating configuration files."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize the config loader service."""
        self.config = config or {}
        self._cache: dict[str, Any] = {}

        # Lifecycle trace emission
        emit_replay_key("config_loader", "init")
        emit_determinism_digest("config_loader", "init")
        _emit_applies_guardrail("p0", "config_loader", "service_init")
        _emit_snapshots_state("p0", "config_loader", "service_state")

    def load_json_config(self, config_path: str) -> dict[str, Any]:
        """Load JSON configuration from file."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L2_EXECUTION,
            "ConfigLoaderService.load_json_config",
        )
        _emit_routes_to_capability("p2", "config_loader", "json_parse")
        _emit_validates_capability("p2", "config_loader", "file_read")
        _emit_records_telemetry_event("p4", "config_loader", "load_start")

        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        # Check cache
        if config_path in self._cache:
            _emit_records_telemetry_event("p4", "config_loader", "cache_hit")
            return self._cache[config_path]

        try:
            with open(path, encoding="utf-8") as f:
                config = json.load(f)

            self._cache[config_path] = config
            _log.info("Loaded config from %s", config_path)
            _emit_records_telemetry_event("p4", "config_loader", "load_complete")

            return config
        except json.JSONDecodeError as exc:
            _log.error("Failed to parse config %s: %s", config_path, exc)
            _emit_records_telemetry_event("p4", "config_loader", "parse_error")
            raise

    def clear_cache(self) -> None:
        """Clear the configuration cache."""
        self._cache.clear()
        _emit_records_telemetry_event("p4", "config_loader", "cache_cleared")

    def get_cached_configs(self) -> list[str]:
        """Get list of cached config paths."""
        return list(self._cache.keys())
