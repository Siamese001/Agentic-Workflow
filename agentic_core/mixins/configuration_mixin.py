"""
import uuid
ConfigMixin - Unified configuration Access for Agents

[PHASE 6 MIGRATION] Provides access to SovereignConfigManager.
"""

from agentic_core.config.core.sovereign_config import (
    SovereignConfigManager,
    get_sovereign_config,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "configuration_mixin", "p0_governance")
_emit_reads_policy_state("p0", "configuration_mixin", "policy_binding")
_emit_snapshots_state("p0", "configuration_mixin", "state_snapshot")
emit_replay_key("p0", "configuration_mixin")
emit_determinism_digest("p0", "configuration_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


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
