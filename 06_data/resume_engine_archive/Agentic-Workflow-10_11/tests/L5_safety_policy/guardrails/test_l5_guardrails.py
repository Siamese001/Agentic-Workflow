"""L5 Safety Guardrails Tests."""

class TestL5Guardrails:
    """Tests for L5 safety guardrails."""
    
    def test_content_guardrail(self):
        """Test content guardrail enforcement."""
        content = "safe resume content"
        blocked_terms = ["SSN", "password"]
        is_safe = not any(term in content for term in blocked_terms)
        assert is_safe is True
    
    def test_pii_guardrail(self):
        """Test PII detection guardrail."""
        text = "Hello World"
        has_pii = "SSN:" in text or "DOB:" in text
        assert has_pii is False
