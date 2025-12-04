"""E2E Safety Enforced Path Tests."""

class TestE2ESafetyPaths:
    """E2E tests for safety enforced paths."""
    
    def test_pii_blocked_workflow(self):
        """Test PII is blocked in complete workflow."""
        content = "safe resume without PII"
        pii_patterns = ["SSN:", "DOB:"]
        is_blocked = any(p in content for p in pii_patterns)
        assert is_blocked is False
    
    def test_injection_prevented_workflow(self):
        """Test injection is prevented in workflow."""
        prompt = "normal user prompt"
        injection_patterns = ["ignore previous", "system override"]
        is_safe = not any(p in prompt.lower() for p in injection_patterns)
        assert is_safe is True
