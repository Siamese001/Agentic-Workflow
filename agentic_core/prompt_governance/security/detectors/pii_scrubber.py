import re

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

_emit_applies_guardrail("p0", "pii_scrubber", "p0_governance")
_emit_reads_policy_state("p0", "pii_scrubber", "policy_binding")
_emit_snapshots_state("p0", "pii_scrubber", "state_snapshot")
emit_replay_key("p0", "pii_scrubber")
emit_determinism_digest("p0", "pii_scrubber")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class PIIScrubber:
    """
    Sanitizes sensitive information from text.
    """

    EMAIL_PATTERN = "\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b"
    PHONE_PATTERN = "\\b(?:\\+?1[-.]?)?\\(?([0-9]{3})\\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})\\b|\\b([0-9]{3})[-. ]?([0-9]{4})\\b"

    def scrub(self, text: str) -> str:
        """
        Replaces PII with placeholder tokens.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PIIScrubber.scrub")

        if not text:
            return ""
        text = re.sub(self.EMAIL_PATTERN, "[EMAIL_REDACTED]", text)
        text = re.sub(self.PHONE_PATTERN, "[PHONE_REDACTED]", text)
        return text
