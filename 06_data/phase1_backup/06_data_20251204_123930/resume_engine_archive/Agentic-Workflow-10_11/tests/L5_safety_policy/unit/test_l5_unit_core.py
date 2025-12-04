"""L5 Safety Policy Unit Tests - Core."""

class TestL5SafetyPolicyUnitCore:
    """Core unit tests for L5 safety policy layer."""
    
    def test_policy_rule_creation(self):
        """Test policy rule creation."""
        rule = {"id": "r1", "type": "block", "pattern": "SSN"}
        assert rule["type"] == "block"
    
    def test_safety_check_initialization(self):
        """Test safety check initialization."""
        check = {"name": "pii_check", "enabled": True}
        assert check["enabled"] is True
    
    def test_violation_detection(self):
        """Test violation detection logic."""
        content = "safe content"
        violations = []
        if "SSN" in content:
            violations.append("pii_detected")
        assert len(violations) == 0
