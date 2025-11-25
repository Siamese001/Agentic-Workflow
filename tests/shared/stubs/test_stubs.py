"""Shared Test Stubs."""

class StubSafetyEngine:
    """Stub safety engine for testing."""
    
    def evaluate(self, context):
        """Stub evaluate method."""
        return StubPolicyResult()

class StubPolicyResult:
    """Stub policy result for testing."""
    
    def __init__(self):
        self.blocking_findings = []
        self.warnings = []

def test_stub_safety_engine():
    """Test StubSafetyEngine."""
    engine = StubSafetyEngine()
    result = engine.evaluate({})
    assert result.blocking_findings == []
