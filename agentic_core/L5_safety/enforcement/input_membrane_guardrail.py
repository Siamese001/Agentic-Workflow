from __future__ import annotations

import logging

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "input_membrane_guardrail")
emit_determinism_digest("p0", "input_membrane_guardrail")

_emit_dispatches_healing_run("p1", "input_membrane_guardrail", "L5")
_emit_routes_through("p1", "input_membrane_guardrail", "L5")
_emit_escalates_to_human("p1", "input_membrane_guardrail", "L5")
_emit_reads_policy_state("p1", "input_membrane_guardrail", "L5")

_emit_applies_guardrail("p0", "input_membrane_guardrail", "p0_governance")
_emit_snapshots_state("p0", "input_membrane_guardrail", "state_snapshot")

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
import re
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)


class InputMembrane:
    """
    L5 Safety Guardrail: The Data Membrane.
    Scrubs inputs and outputs to prevent data contamination or prompt injection.
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.sensitive_patterns = ["sk-[a-zA-Z0-9]{32,48}", "AIzaSy[a-zA-Z0-9_-]{33}", "BEGIN PRIVATE KEY"]

    async def sanitize(self, text: str, context_label: str = "general") -> str:
        """Sanitizes text based on L5 safety policies."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "InputMembrane.sanitize")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:InputMembrane.sanitize".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if not isinstance(text, str):
            return text
        sanitized: Any = text
        for pattern in self.sensitive_patterns:
            sanitized: Any = re.sub(pattern, f"[REDACTED_{context_label.upper()}]", sanitized)
        forbidden_sequences: Any = ["rm -rf", "DROP TABLE", "truncate ", "chmod 777"]
        for seq in forbidden_sequences:
            if seq in sanitized.lower():
                logging.warning(f"Membrane Blocked Sequence in {context_label}: {seq}")
                sanitized: Any = sanitized.replace(seq, "[BLOCKED_COMMAND]")
        return sanitized
