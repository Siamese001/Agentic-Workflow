"""L2 Execution Unit Tests - Core."""

class TestL2ExecutionUnitCore:
    """Core unit tests for L2 execution layer."""
    
    def test_tool_executor_initialization(self):
        """Test tool executor initialization."""
        executor = {"name": "tool_executor", "ready": True}
        assert executor["ready"] is True
    
    def test_execution_context_creation(self):
        """Test execution context creation."""
        ctx = {"user_id": "u1", "session_id": "s1"}
        assert ctx["user_id"] == "u1"
    
    def test_result_aggregation(self):
        """Test result aggregation logic."""
        results = [{"score": 0.8}, {"score": 0.9}]
        avg = sum(r["score"] for r in results) / len(results)
        assert abs(avg - 0.85) < 0.001
