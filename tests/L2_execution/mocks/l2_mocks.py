"""L2 Execution Mocks."""

class MockToolExecutor:
    """Mock tool executor for testing."""
    
    def __init__(self):
        self.calls = []
    
    def execute(self, tool_name, params):
        """Mock execute method."""
        self.calls.append((tool_name, params))
        return {"status": "success", "result": "mock_result"}

class MockExecutionContext:
    """Mock execution context for testing."""
    
    def __init__(self):
        self.user_id = "test_user"
        self.session_id = "test_session"
        self.profile_name = "test_profile"

def test_mock_tool_executor():
    """Test MockToolExecutor."""
    executor = MockToolExecutor()
    result = executor.execute("search", {"query": "test"})
    assert result["status"] == "success"
    assert len(executor.calls) == 1

def test_mock_execution_context():
    """Test MockExecutionContext."""
    ctx = MockExecutionContext()
    assert ctx.user_id == "test_user"
