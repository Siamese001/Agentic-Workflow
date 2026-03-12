"""ADG-driven tests for prompt_governance/security/detectors/pii_scrubber.py — fan_in=1."""
from __future__ import annotations

import pytest

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
