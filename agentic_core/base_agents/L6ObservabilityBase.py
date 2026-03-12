from __future__ import annotations
'\nL6ObservabilityBase - Consolidated Base for L6 Observability Agents\n\nLayer: L6 - Observability\nResponsibilities:\n- Dashboard operations\n- Telemetry collection\n- Logging coordination\n- Metrics aggregation\n\nMRO HARDENING:\n- Inheritance order: SovereignBaseAgent (root)\n- All L6 agents inherit from this base for consistent observability capabilities\n'
from dataclasses import dataclass
from typing import Any
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

@dataclass
class L6ObservabilityBase(SovereignBaseAgent):
    """
    Consolidated base for L6 Observability agents.

    L6 agents handle:
    - Dashboard data aggregation
    - Telemetry collection and export
    - Logging coordination
    - Metrics and KPI tracking

    MRO: L6ObservabilityBase -> SovereignBaseAgent -> object
    """
    name: str = 'L6ObservabilityBase'
    layer: str = 'L6'

    def __post_init__(self) -> None:
        """Cooperative MRO initialization."""
        super().__post_init__()

    def collect_metrics(self) -> dict[str, Any]:
        """
        Collect metrics from the system.

        Override in subclasses for specialized metric collection.
        """
        return {'metrics': {}, 'timestamp': None}

    def emit_telemetry(self, event: dict[str, Any]) -> bool:
        """
        Emit a telemetry event.

        Override in subclasses for specialized telemetry emission.
        """
        return True

    def aggregate_logs(self, filters: dict[str, Any] | None=None) -> list[dict[str, Any]]:
        """
        Aggregate logs based on filters.

        Override in subclasses for specialized log aggregation.
        """
        return []
