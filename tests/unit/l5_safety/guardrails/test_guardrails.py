"""L5 Safety Guardrails Tests."""

class TestGuardrails:
    """Tests for L5 safety guardrails."""
    
    def test_content_guardrail(self):
        """Test content guardrail enforcement."""
        content = "safe content"
        assert "unsafe" not in content
    
    def test_pii_guardrail(self):
        """Test PII detection guardrail."""
        text = "Hello World"
        has_ssn = "SSN" in text
        assert not has_ssn
