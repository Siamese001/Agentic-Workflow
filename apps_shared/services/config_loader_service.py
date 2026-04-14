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

    DEFAULT_MAX_CONFIG_BYTES = 1_048_576

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize the config loader service."""
        self.config = config or {}
        self._cache: dict[str, dict[str, Any]] = {}
        self._allowed_roots = self._normalize_allowed_roots(self.config.get("allowed_config_roots"))
        self._max_config_bytes = int(self.config.get("max_config_bytes", self.DEFAULT_MAX_CONFIG_BYTES))

        # Lifecycle trace emission
        emit_replay_key("config_loader", "init")
        emit_determinism_digest("config_loader", "init")
        _emit_applies_guardrail("p0", "config_loader", "service_init")
        _emit_snapshots_state("p0", "config_loader", "service_state")

    @staticmethod
    def _normalize_allowed_roots(raw_roots: Any) -> tuple[Path, ...]:
        if not raw_roots:
            return ()
        if isinstance(raw_roots, (str, Path)):
            raw_roots = [raw_roots]
        return tuple(Path(root).expanduser().resolve() for root in raw_roots)

    def _resolve_path(self, config_path: str) -> Path:
        path = Path(config_path).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        if self._allowed_roots and not any(
            root == path or root in path.parents for root in self._allowed_roots
        ):
            raise PermissionError(f"Config path is outside allowed roots: {config_path}")
        return path

    def _read_and_parse(self, path: Path) -> dict[str, Any]:
        size = path.stat().st_size
        if size > self._max_config_bytes:
            raise ValueError(f"Config file exceeds max size of {self._max_config_bytes} bytes: {path}")
        with path.open(encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, dict):
            raise ValueError(f"Config payload must be a JSON object: {path}")
        return payload

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

        path = self._resolve_path(config_path)
        cache_key = str(path)
        stat = path.stat()
        fingerprint = (stat.st_mtime_ns, stat.st_size)

        cached = self._cache.get(cache_key)
        if cached and cached["fingerprint"] == fingerprint:
            _emit_records_telemetry_event("p4", "config_loader", "cache_hit")
            return dict(cached["payload"])

        try:
            payload = self._read_and_parse(path)
        except json.JSONDecodeError as exc:
            _log.error("Failed to parse config %s: %s", path, exc)
            _emit_records_telemetry_event("p4", "config_loader", "parse_error")
            raise
        except (OSError, PermissionError, ValueError) as exc:
            _log.error("Failed to load config %s: %s", path, exc)
            _emit_records_telemetry_event("p4", "config_loader", "load_error")
            raise

        self._cache[cache_key] = {
            "fingerprint": fingerprint,
            "payload": payload,
        }
        _log.info("Loaded config from %s", path)
        _emit_records_telemetry_event("p4", "config_loader", "load_complete")
        return dict(payload)

    def clear_cache(self) -> None:
        """Clear the configuration cache."""
        self._cache.clear()
        _emit_records_telemetry_event("p4", "config_loader", "cache_cleared")

    def get_cached_configs(self) -> list[str]:
        """Get list of cached config paths."""
        return list(self._cache)
