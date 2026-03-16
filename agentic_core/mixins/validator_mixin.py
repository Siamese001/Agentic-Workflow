"""
ValidatorMixin - Unified Validation Access for Agents

[PHASE 5 MIGRATION] Provides single interface to validation operations.
"""

from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "validator_mixin", "p0_governance")
_emit_reads_policy_state("p0", "validator_mixin", "policy_binding")
_emit_snapshots_state("p0", "validator_mixin", "state_snapshot")
emit_replay_key("p0", "validator_mixin")
emit_determinism_digest("p0", "validator_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

try:
    from agentic_core.L5_safety.types.healing_orchestration_types import (
        ValidatorOrchestrator,
        get_validator_orchestrator,
    )
except ImportError:

    class ValidatorOrchestrator:
        """Stub orchestrator when real module is unavailable."""

        pass

    def get_validator_orchestrator():
        return None
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


class ValidatorMixin:
    """
    Mixin providing unified validator orchestrator access.
    """

    _validator_orchestrator: ValidatorOrchestrator | None = None

    @property
    def validator_orchestrator(self) -> ValidatorOrchestrator:
        """Lazy-load validator orchestrator singleton."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ValidatorMixin.validator_orchestrator")

        if self._validator_orchestrator is None:
            self._validator_orchestrator = get_validator_orchestrator()
        return self._validator_orchestrator

    async def orchestrator_validate(self, content: Any, validator_name: str, context: dict = None) -> dict:
        """Execute validation through orchestrator."""
        return await self.validator_orchestrator.validate(content, validator_name, context)
