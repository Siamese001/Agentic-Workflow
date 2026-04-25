"""
Tests for UniversalWriteGateway - write operation control and validation.

Coverage:
- Write operation initialization
- Write request validation
- Path and permission checks
- Write policy enforcement
- Atomic write operations
- Error handling for write failures
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from agentic_core.L2_execution.enforcement.UniversalWriteGateway import UniversalWriteGateway


class TestUniversalWriteGateway:
    """Test suite for UniversalWriteGateway."""

    def test_init_with_valid_policies(self):
        """Test initialization with valid write policies."""
        policies = {
            "allowed_paths": ["/src", "/docs"],
            "forbidden_paths": ["/archive", "/.git"],
            "require_approval": False
        }
        gateway = UniversalWriteGateway(policies=policies)
        assert gateway.policies == policies

    def test_init_with_missing_policies(self):
        """Test initialization fails with missing required policies."""
        policies = {}  # Missing required fields
        with pytest.raises(ValueError):
            UniversalWriteGateway(policies=policies)

    def test_validate_write_request_success(self):
        """Test successful validation of write request."""
        policies = {
            "allowed_paths": ["/src", "/docs"],
            "forbidden_paths": ["/archive"],
            "require_approval": False
        }
        gateway = UniversalWriteGateway(policies=policies)
        
        request = {
            "path": "/src/main.py",
            "operation": "write",
            "requires_approval": False
        }
        result = gateway.validate(request)
        
        assert result.valid is True

    def test_validate_forbidden_path(self):
        """Test validation fails for forbidden path."""
        policies = {
            "allowed_paths": ["/src", "/docs"],
            "forbidden_paths": ["/archive", "/.git"],
            "require_approval": False
        }
        gateway = UniversalWriteGateway(policies=policies)
        
        request = {
            "path": "/archive/old.py",  # Forbidden
            "operation": "write",
            "requires_approval": False
        }
        result = gateway.validate(request)
        
        assert result.valid is False
        assert "forbidden" in result.violation_reason.lower()

    def test_validate_disallowed_path(self):
        """Test validation fails for path outside allowed list."""
        policies = {
            "allowed_paths": ["/src"],
            "forbidden_paths": [],
            "require_approval": False
        }
        gateway = UniversalWriteGateway(policies=policies)
        
        request = {
            "path": "/tmp/test.py",  # Not in allowed_paths
            "operation": "write",
            "requires_approval": False
        }
        result = gateway.validate(request)
        
        assert result.valid is False

    def test_enforce_write_policy(self):
        """Test write policy enforcement."""
        policies = {
            "allowed_paths": ["/src"],
            "forbidden_paths": ["/archive"],
            "require_approval": False
        }
        gateway = UniversalWriteGateway(policies=policies)
        
        request = {
            "path": "/src/main.py",
            "content": "test content",
            "operation": "write"
        }
        
        # Should not raise for valid request
        gateway.enforce(request)

    def test_enforce_blocks_forbidden_write(self):
        """Test enforcement blocks writes to forbidden paths."""
        policies = {
            "allowed_paths": ["/src"],
            "forbidden_paths": ["/archive"],
            "require_approval": False
        }
        gateway = UniversalWriteGateway(policies=policies)
        
        request = {
            "path": "/archive/test.py",
            "content": "test content",
            "operation": "write"
        }
        
        with pytest.raises(PermissionError):
            gateway.enforce(request)

    def test_atomic_write_operation(self):
        """Test atomic write operation."""
        policies = {
            "allowed_paths": ["/src"],
            "forbidden_paths": [],
            "require_approval": False
        }
        gateway = UniversalWriteGateway(policies=policies)
        
        with patch("builtins.open", create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            gateway.write_atomic(
                path="/src/test.py",
                content="test content"
            )
            
            mock_open.assert_called_once()
            mock_file.write.assert_called_once_with("test content")

    def test_handle_write_failure(self):
        """Test graceful handling of write failure."""
        policies = {
            "allowed_paths": ["/src"],
            "forbidden_paths": [],
            "require_approval": False
        }
        gateway = UniversalWriteGateway(policies=policies)
        
        with patch("builtins.open", side_effect=IOError("Write failed")):
            with pytest.raises(IOError):
                gateway.write_atomic(
                    path="/src/test.py",
                    content="test content"
                )

    def test_update_policies_runtime(self):
        """Test updating policies at runtime."""
        policies = {
            "allowed_paths": ["/src"],
            "forbidden_paths": [],
            "require_approval": False
        }
        gateway = UniversalWriteGateway(policies=policies)
        
        new_policies = {
            "allowed_paths": ["/src", "/docs"],  # Added docs
            "forbidden_paths": [],
            "require_approval": False
        }
        gateway.update_policies(new_policies)
        
        assert "/docs" in gateway.policies["allowed_paths"]

    def test_get_policy_status(self):
        """Test retrieving current policy status."""
        policies = {
            "allowed_paths": ["/src"],
            "forbidden_paths": ["/archive"],
            "require_approval": False
        }
        gateway = UniversalWriteGateway(policies=policies)
        
        status = gateway.get_status()
        assert "allowed_paths" in status
        assert "forbidden_paths" in status

    def test_check_path_permissions(self):
        """Test path permission checking."""
        policies = {
            "allowed_paths": ["/src"],
            "forbidden_paths": ["/archive"],
            "require_approval": False
        }
        gateway = UniversalWriteGateway(policies=policies)
        
        assert gateway.check_permission("/src/test.py") is True
        assert gateway.check_permission("/archive/test.py") is False
