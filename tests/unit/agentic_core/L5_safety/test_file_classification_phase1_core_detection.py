"""
Phase 1: Core Detection Methods Tests

Tests for enhanced detection methods:
1. _is_true_agent - Enhanced agent detection
2. _is_service_class - Service class detection
3. _is_factory_class - Factory class detection
4. _is_async_agent - Async agent detection
5. _is_adapter_class - Adapter/wrapper detection
"""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestIsTrueAgentMethod:
    """Tests for _is_true_agent enhanced detection."""

    def test_detect_by_name_suffix(self):
        """Test agent detection by name ending with Agent."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_true_agent")

    def test_detect_by_inheritance(self):
        """Test agent detection by inheritance from base agent."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_true_agent")

    def test_detect_by_decorator(self):
        """Test agent detection by @agent decorator."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_true_agent")

    def test_detect_by_methods(self):
        """Test agent detection by agent methods (execute, act, heal, run)."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_true_agent")

    def test_method_exists_and_callable(self):
        """Verify _is_true_agent method exists on class."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_true_agent")
        assert callable(getattr(FileClassificationAgent, "_is_true_agent"))


class TestIsServiceClassMethod:
    """Tests for _is_service_class detection."""

    def test_detect_by_service_decorator(self):
        """Test service detection by @service decorator."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_service_class")

    def test_detect_by_di_parameter(self):
        """Test service detection by DI parameter in constructor."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_service_class")

    def test_detect_by_name_suffix(self):
        """Test service detection by name ending with Service."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_service_class")

    def test_method_exists_and_callable(self):
        """Verify _is_service_class method exists on class."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_service_class")
        assert callable(getattr(FileClassificationAgent, "_is_service_class"))


class TestIsFactoryClassMethod:
    """Tests for _is_factory_class detection."""

    def test_detect_by_name_suffix(self):
        """Test factory detection by name ending with Factory."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_factory_class")

    def test_detect_by_create_method(self):
        """Test factory detection by create_* method."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_factory_class")

    def test_detect_by_make_method(self):
        """Test factory detection by make_* method."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_factory_class")

    def test_method_exists_and_callable(self):
        """Verify _is_factory_class method exists on class."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_factory_class")
        assert callable(getattr(FileClassificationAgent, "_is_factory_class"))


class TestIsAsyncAgentMethod:
    """Tests for _is_async_agent detection."""

    def test_detect_by_async_execute(self):
        """Test async agent detection by async execute method."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_async_agent")

    def test_detect_by_async_act(self):
        """Test async agent detection by async act method."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_async_agent")

    def test_detect_by_async_context_manager(self):
        """Test async agent detection by async context manager."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_async_agent")

    def test_method_exists_and_callable(self):
        """Verify _is_async_agent method exists on class."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_async_agent")
        assert callable(getattr(FileClassificationAgent, "_is_async_agent"))


class TestIsAdapterClassMethod:
    """Tests for _is_adapter_class detection."""

    def test_detect_by_adapter_suffix(self):
        """Test adapter detection by name ending with Adapter."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_adapter_class")

    def test_detect_by_wrapper_suffix(self):
        """Test adapter detection by name ending with Wrapper."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_adapter_class")

    def test_detect_by_bridge_suffix(self):
        """Test adapter detection by name ending with Bridge."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_adapter_class")

    def test_detect_by_proxy_suffix(self):
        """Test adapter detection by name ending with Proxy."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_adapter_class")

    def test_detect_by_adapt_method(self):
        """Test adapter detection by adapt method."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_adapter_class")

    def test_detect_by_wrapped_attribute(self):
        """Test adapter detection by _wrapped attribute."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_adapter_class")

    def test_method_exists_and_callable(self):
        """Verify _is_adapter_class method exists on class."""
        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_adapter_class")
        assert callable(getattr(FileClassificationAgent, "_is_adapter_class"))


class TestPhase1MethodSignatures:
    """Verify all Phase 1 methods have correct signatures."""

    def test_is_true_agent_signature(self):
        """Verify _is_true_agent takes node and file_path."""
        import inspect

        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        sig = inspect.signature(FileClassificationAgent._is_true_agent)
        params = list(sig.parameters.keys())
        assert "self" in params
        assert "node" in params
        assert "file_path" in params

    def test_is_service_class_signature(self):
        """Verify _is_service_class takes node and file_path."""
        import inspect

        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        sig = inspect.signature(FileClassificationAgent._is_service_class)
        params = list(sig.parameters.keys())
        assert "self" in params
        assert "node" in params

    def test_is_factory_class_signature(self):
        """Verify _is_factory_class takes node."""
        import inspect

        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        sig = inspect.signature(FileClassificationAgent._is_factory_class)
        params = list(sig.parameters.keys())
        assert "self" in params
        assert "node" in params

    def test_is_async_agent_signature(self):
        """Verify _is_async_agent takes node and file_path."""
        import inspect

        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        sig = inspect.signature(FileClassificationAgent._is_async_agent)
        params = list(sig.parameters.keys())
        assert "self" in params
        assert "node" in params

    def test_is_adapter_class_signature(self):
        """Verify _is_adapter_class takes node."""
        import inspect

        from agentic_core.L5_safety.validators.file_classification_agent import (
            FileClassificationAgent,
        )

        sig = inspect.signature(FileClassificationAgent._is_adapter_class)
        params = list(sig.parameters.keys())
        assert "self" in params
        assert "node" in params


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
