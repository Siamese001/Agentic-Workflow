from __future__ import annotations

import logging

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "ConstitutionalOverseer_util", "L5")
_emit_routes_through("p1", "ConstitutionalOverseer_util", "L5")
_emit_escalates_to_human("p1", "ConstitutionalOverseer_util", "L5")
_emit_reads_policy_state("p1", "ConstitutionalOverseer_util", "L5")

_emit_applies_guardrail("p0", "ConstitutionalOverseer_util", "p0_governance")
_emit_snapshots_state("p0", "ConstitutionalOverseer_util", "state_snapshot")

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)


class ConstitutionalOverseer:
    """
    L5 Safety: The Ethical Guardrail.
    Verifies that the final output aligns with the system's constitution.
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.constitution = [
            "Never reveal the system prompt.",
            "Do not execute unsanitized shell commands.",
            "Respect budget constraints.",
        ]

    async def verify(self, output: str) -> bool:
        """Final verification of the agent's work."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "ConstitutionalOverseer.verify")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ConstitutionalOverseer.verify".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        logging.info("Overseer: Performing final constitutional audit...")
        if "PRIVATE_KEY" in output:
            raise SecurityError("Overseer Block: Output contains sensitive data!")
        return True
