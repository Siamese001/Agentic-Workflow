"""Tests for VerificationGateProtocol."""

from agentic_core.utils.verification_protocol import (
    VerificationGateProtocol,
    VerificationRequest,
    VerificationResult,
)


class TestVerificationRequest:
    """Tests for VerificationRequest dataclass."""

    def test_create_request(self):
        """Test creating a verification request."""
        request = VerificationRequest(
            file_path="/path/to/file.py",
            action_type="modify_function",
            target_node="my_function",
        )
        assert request.file_path == "/path/to/file.py"
        assert request.action_type == "modify_function"
        assert request.target_node == "my_function"
        assert request.context == {}

    def test_create_request_with_context(self):
        """Test creating request with context."""
        context = {"agent": "TestAgent", "reason": "refactoring"}
        request = VerificationRequest(
            file_path="/path/to/file.py",
            action_type="delete_import",
            target_node="os",
            context=context,
        )
        assert request.context == context

    def test_request_none_context_defaults_to_empty_dict(self):
        """Test that None context becomes empty dict."""
        request = VerificationRequest(
            file_path="/path/to/file.py",
            action_type="modify_function",
            target_node="func",
            context=None,
        )
        assert request.context == {}


class TestVerificationResult:
    """Tests for VerificationResult dataclass."""

    def test_create_success_result(self):
        """Test creating a successful result."""
        result = VerificationResult(success=True)
        assert result.success is True
        assert result.reason is None
        assert result.metadata == {}

    def test_create_failure_result(self):
        """Test creating a failure result."""
        result = VerificationResult(
            success=False,
            reason="target_not_found",
            metadata={"searched_nodes": ["func1", "func2"]},
        )
        assert result.success is False
        assert result.reason == "target_not_found"
        assert result.metadata == {"searched_nodes": ["func1", "func2"]}

    def test_result_none_metadata_defaults_to_empty_dict(self):
        """Test that None metadata becomes empty dict."""
        result = VerificationResult(success=True, metadata=None)
        assert result.metadata == {}


class MockVerificationGate(VerificationGateProtocol):
    """Mock implementation for testing."""

    def __init__(self, available: bool = True):
        self._available = available

    def verify_action(self, request: VerificationRequest) -> VerificationResult:
        validation_error = self.validate_request(request)
        if validation_error:
            return VerificationResult(success=False, reason=validation_error)
        return VerificationResult(success=True, reason="verified")

    def is_available(self) -> bool:
        return self._available

    def get_supported_actions(self) -> list[str]:
        return self.SUPPORTED_ACTIONS


class TestVerificationGateProtocol:
    """Tests for VerificationGateProtocol."""

    def test_supported_actions_defined(self):
        """Test that supported actions are defined."""
        assert len(VerificationGateProtocol.SUPPORTED_ACTIONS) > 0
        assert "modify_function" in VerificationGateProtocol.SUPPORTED_ACTIONS
        assert "delete_import" in VerificationGateProtocol.SUPPORTED_ACTIONS

    def test_mock_implementation(self):
        """Test mock implementation works."""
        gate = MockVerificationGate()
        request = VerificationRequest(
            file_path="/test.py",
            action_type="modify_function",
            target_node="test_func",
        )
        result = gate.verify_action(request)
        assert result.success is True

    def test_mock_is_available(self):
        """Test is_available method."""
        gate = MockVerificationGate(available=True)
        assert gate.is_available() is True

        gate = MockVerificationGate(available=False)
        assert gate.is_available() is False

    def test_mock_get_supported_actions(self):
        """Test get_supported_actions method."""
        gate = MockVerificationGate()
        actions = gate.get_supported_actions()
        assert isinstance(actions, list)
        assert len(actions) > 0

    def test_validate_request_missing_file_path(self):
        """Test validation rejects missing file_path."""
        gate = MockVerificationGate()
        request = VerificationRequest(
            file_path="",
            action_type="modify_function",
            target_node="test",
        )
        error = gate.validate_request(request)
        assert error == "file_path is required"

    def test_validate_request_missing_action_type(self):
        """Test validation rejects missing action_type."""
        gate = MockVerificationGate()
        request = VerificationRequest(
            file_path="/test.py",
            action_type="",
            target_node="test",
        )
        error = gate.validate_request(request)
        assert error == "action_type is required"

    def test_validate_request_unsupported_action(self):
        """Test validation rejects unsupported action."""
        gate = MockVerificationGate()
        request = VerificationRequest(
            file_path="/test.py",
            action_type="unsupported_action",
            target_node="test",
        )
        error = gate.validate_request(request)
        assert "unsupported action_type" in error

    def test_validate_request_missing_target_node(self):
        """Test validation rejects missing target_node."""
        gate = MockVerificationGate()
        request = VerificationRequest(
            file_path="/test.py",
            action_type="modify_function",
            target_node="",
        )
        error = gate.validate_request(request)
        assert error == "target_node is required"

    def test_validate_request_valid(self):
        """Test validation passes for valid request."""
        gate = MockVerificationGate()
        request = VerificationRequest(
            file_path="/test.py",
            action_type="modify_function",
            target_node="test_func",
        )
        error = gate.validate_request(request)
        assert error is None
