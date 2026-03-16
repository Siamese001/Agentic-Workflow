"""ADG-driven tests for prompt_governance/security/detectors/pii_scrubber.py — fan_in=1."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_pii_scrubber_adg")
_emit_applies_guardrail("p0", "test_pii_scrubber_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_pii_scrubber_adg", "policy_binding")
_emit_snapshots_state("p0", "test_pii_scrubber_adg", "state_snapshot")
emit_replay_key("p0", "test_pii_scrubber_adg")
emit_determinism_digest("p0", "test_pii_scrubber_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.prompt_governance.security.detectors.pii_scrubber import PIIScrubber


class TestPIIScrubber:
    def test_scrub_empty_string(self):
        scrubber = PIIScrubber()
        assert scrubber.scrub("") == ""

    def test_scrub_email(self):
        scrubber = PIIScrubber()
        result = scrubber.scrub("Contact me at user@example.com for details.")
        assert "[EMAIL_REDACTED]" in result
        assert "user@example.com" not in result

    def test_scrub_phone(self):
        scrubber = PIIScrubber()
        result = scrubber.scrub("Call me at 555-123-4567 anytime.")
        assert "[PHONE_REDACTED]" in result
        assert "555-123-4567" not in result

    def test_clean_text_unchanged(self):
        scrubber = PIIScrubber()
        text = "Hello world, how are you?"
        result = scrubber.scrub(text)
        assert result == text

    def test_has_email_pattern(self):
        assert hasattr(PIIScrubber, "EMAIL_PATTERN")

    def test_has_phone_pattern(self):
        assert hasattr(PIIScrubber, "PHONE_PATTERN")
