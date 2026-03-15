"""
ConfigMixin - Unified configuration Access for Agents

[PHASE 6 MIGRATION] Provides access to SovereignConfigManager.
"""

from agentic_core.config.core.sovereign_config import (
    SovereignConfigManager,
    get_sovereign_config,
)
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


class ConfigMixin:
    """
    Mixin providing typed configuration access.

    Usage:
        class MyAgent(ConfigMixin):
            def run(self):
                limit = self.config.max_audit_log_size
    """

    _config_manager: SovereignConfigManager | None = None

    @property
    def config(self) -> SovereignConfigManager:
        """Lazy-load config singleton."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ConfigMixin.config")

        if self._config_manager is None:
            self._config_manager = get_sovereign_config()
        return self._config_manager
