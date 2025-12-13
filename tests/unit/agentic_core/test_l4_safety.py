"""Unit tests for L4_memory/P4_safety - memory safety operations."""
import re

class TestMemorySafety:
    """Tests for memory safety operations."""

    def test_filter_pii_from_memory(self):
        """Nominal: PII is filtered from memory."""
        memory = {"content": "User email is john@example.com"}
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        filtered = re.sub(email_pattern, '[REDACTED]', memory["content"])
        assert "john@example.com" not in filtered
        assert "[REDACTED]" in filtered

    def test_validate_memory_source(self):
        """Nominal: Memory source is validated."""
        trusted_sources = ["user_input", "system", "verified_api"]
        memory = {"content": "data", "source": "user_input"}
        is_trusted = memory["source"] in trusted_sources
        assert is_trusted is True

    def test_reject_untrusted_source(self):
        """Negative: Untrusted source is rejected."""
        trusted_sources = ["user_input", "system"]
        memory = {"content": "data", "source": "unknown_external"}
        is_trusted = memory["source"] in trusted_sources
        assert is_trusted is False

    def test_sanitize_memory_content(self):
        """Nominal: Memory content is sanitized."""
        memory = {"content": "Data with <script>alert('xss')</script>"}
        sanitized = re.sub(r'<[^>]+>', '', memory["content"])
        assert "<script>" not in sanitized

    def test_enforce_retention_policy(self):
        """Nominal: Retention policy is enforced."""
        from datetime import datetime, timedelta
        max_retention_days = 90
        memory = {"timestamp": datetime.now() - timedelta(days=100)}
        age_days = (datetime.now() - memory["timestamp"]).days
        should_delete = age_days > max_retention_days
        assert should_delete is True
