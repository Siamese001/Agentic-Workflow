
from agentic_core.prompt_governance.security.detectors.injection_detector import InjectionDetector
from agentic_core.prompt_governance.security.detectors.pii_scrubber import PIIScrubber
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

_emit_applies_guardrail("p0", "governance_hub", "p0_governance")
_emit_reads_policy_state("p0", "governance_hub", "policy_binding")
_emit_snapshots_state("p0", "governance_hub", "state_snapshot")
emit_replay_key("p0", "governance_hub")
emit_determinism_digest("p0", "governance_hub")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class GovernanceHub:
    """
    Main entry point for safety validation.
    Usage: hub.validate_input(user_prompt)
    """

    def __init__(self):
        self.pii_scrubber = PIIScrubber()
        self.injection_detector = InjectionDetector()

    def validate_input(self, text: str) -> str:
        """
        Runs injection checks first, then scrubs PII.
        Returns sanitized text.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "GovernanceHub.validate_input")

        self.injection_detector.scan(text)
        safe_text = self.pii_scrubber.scrub(text)
        return safe_text

    def validate_output(self, text: str) -> str:
        """
        Scans LLM output for data leaks (PII).
        """
        return self.pii_scrubber.scrub(text)
