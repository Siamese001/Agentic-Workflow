"""Concrete ConfigProvider — provides current routing/threshold configs for the pipeline.

Reads from ``runtime_state.json`` and an optional config directory to supply
the meta-learning pipeline with current configuration state.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

logger = logging.getLogger(__name__)


class FileBackedConfigProvider:
    """File-backed config provider reading from runtime state and config files.

    Parameters
    ----------
    runtime_state_path : Path
        Path to ``runtime_state.json``.
    config_dir : Path | None
        Optional directory containing per-surface config JSON files.
    """

    def __init__(
        self,
        runtime_state_path: Path,
        config_dir: Path | None = None,
    ) -> None:
        self._runtime_state_path = Path(runtime_state_path)
        self._config_dir = Path(config_dir) if config_dir else None

    def _load_runtime_state(self) -> dict[str, Any]:
        if not self._runtime_state_path.exists():
            return {}
        try:
            return json.loads(self._runtime_state_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def get_current_configs(self) -> dict[str, bytes]:
        """Return materialized config bytes keyed by surface name.

        Reads from the config directory (if available) or falls back to
        extracting config sections from runtime_state.json.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "FileBackedConfigProvider.get_current_configs")

        configs: dict[str, bytes] = {}

        # Try config directory first
        if self._config_dir and self._config_dir.exists():
            for cfg_path in sorted(self._config_dir.glob("*.json")):
                surface = cfg_path.stem
                try:
                    raw = cfg_path.read_bytes()
                    configs[surface] = raw
                except OSError:
                    continue

        # Fall back to runtime_state sections
        if not configs:
            state = self._load_runtime_state()
            for key in ("meta_learning", "healing_config", "routing_config"):
                section = state.get(key)
                if section is not None:
                    configs[key] = json.dumps(
                        section, separators=(",", ":"), sort_keys=True
                    ).encode("utf-8")

        return configs

    def get_last_update_utc(self, surface_name: str) -> int | None:
        """Return last update timestamp for a surface from runtime state."""
        state = self._load_runtime_state()
        # Convention: "<surface>_last_update" key in state
        key = f"{surface_name}_last_update"
        val = state.get(key)
        if isinstance(val, int):
            return val
        # Try nested in meta_learning section
        ml = state.get("meta_learning", {})
        val = ml.get(key)
        return val if isinstance(val, int) else None

    def get_param_history(self, surface_name: str, n: int) -> tuple[float, ...]:
        """Return last N parameter values for a surface.

        Reads from runtime state ``"<surface>_history"`` key, expected to
        be a list of floats.
        """
        state = self._load_runtime_state()
        key = f"{surface_name}_history"
        history = state.get(key, [])
        if not isinstance(history, list):
            return ()
        # Take last N, coerce to float
        values: list[float] = []
        for v in history[-n:]:
            try:
                values.append(float(v))
            except (TypeError, ValueError):
                continue
        return tuple(values)


class InMemoryConfigProvider:
    """In-memory config provider for testing."""

    def __init__(self) -> None:
        self._configs: dict[str, bytes] = {}
        self._last_updates: dict[str, int] = {}
        self._histories: dict[str, list[float]] = {}

    def set_config(self, surface: str, data: bytes) -> None:
        self._configs[surface] = data

    def set_last_update(self, surface: str, utc: int) -> None:
        self._last_updates[surface] = utc

    def set_history(self, surface: str, values: list[float]) -> None:
        self._histories[surface] = values

    def get_current_configs(self) -> dict[str, bytes]:
        return dict(self._configs)

    def get_last_update_utc(self, surface_name: str) -> int | None:
        return self._last_updates.get(surface_name)

    def get_param_history(self, surface_name: str, n: int) -> tuple[float, ...]:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "InMemoryConfigProvider.get_param_history")

        history = self._histories.get(surface_name, [])
        return tuple(history[-n:])


class InMemoryBaselineMetricsProvider:
    """In-memory baseline metrics provider for testing / initial bootstrap.

    Returns neutral baseline metrics that pass shadow validation by default.
    """

    def __init__(self, production: Any = None, shadow: Any = None) -> None:
        self._production = production
        self._shadow = shadow

    def production_metrics(self) -> Any:
        return self._production

    def shadow_metrics(self, pkg: Any) -> Any:  # noqa: ARG002
        return self._shadow


__all__ = [
    "FileBackedConfigProvider",
    "InMemoryConfigProvider",
    "InMemoryBaselineMetricsProvider",
]
