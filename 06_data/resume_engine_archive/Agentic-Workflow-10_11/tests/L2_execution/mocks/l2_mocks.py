"""L2 Execution Layer Mocks."""

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
