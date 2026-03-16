from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "shared_infrastructure_config", "p0_governance")
_emit_reads_policy_state("p0", "shared_infrastructure_config", "policy_binding")
_emit_snapshots_state("p0", "shared_infrastructure_config", "state_snapshot")
emit_replay_key("p0", "shared_infrastructure_config")
emit_determinism_digest("p0", "shared_infrastructure_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""
Shared Infrastructure
Provides shared infrastructure services and domain configuration.
"""
import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

Logger: Any = logging.getLogger(__name__)


@dataclass
class DomainConfig:
    """Domain-specific configuration."""

    engine_type: str
    settings: dict[str, Any]
    metadata: dict[str, Any]


class SharedInfrastructure:
    """Shared infrastructure services."""

    def __init__(self):
        """Initialize shared infrastructure."""
        self._configs: dict[str, DomainConfig] = {}
        Logger.debug("SharedInfrastructure initialized")

    def create_domain_config(self, engine_type: str) -> DomainConfig:
        """Create domain configuration for engine type."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SharedInfrastructure.create_domain_config")

        config: Any = DomainConfig(engine_type=engine_type, settings={}, metadata={})
        self._configs[engine_type] = config
        Logger.debug(f"Domain config created for: {engine_type}")
        return config

    def get_domain_config(self, engine_type: str) -> DomainConfig | None:
        """Get domain configuration."""
        return self._configs.get(engine_type)


_shared_infrastructure: SharedInfrastructure | None = None


def get_shared_infrastructure() -> SharedInfrastructure:
    """Get shared infrastructure singleton."""
    global _shared_infrastructure
    if _shared_infrastructure is None:
        _shared_infrastructure = SharedInfrastructure()
    return _shared_infrastructure


__all__ = ["DomainConfig", "SharedInfrastructure", "get_shared_infrastructure"]
