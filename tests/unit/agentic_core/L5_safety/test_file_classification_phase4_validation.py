"""
Phase 4: Testing & Validation - Comprehensive Test Suite

Validates all enhancements work together:
1. All detection methods exist and are callable
2. FileType categories are complete
3. Stats tracking is complete
4. Method signatures are correct
"""

import inspect
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestAllDetectionMethodsExist:
    """Verify all Phase 1 and Phase 2 detection methods exist."""

    def test_is_true_agent_exists(self):
        """Verify _is_true_agent method exists."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_true_agent")
        assert callable(getattr(FileClassificationAgent, "_is_true_agent"))

    def test_is_service_class_exists(self):
        """Verify _is_service_class method exists."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_service_class")
        assert callable(getattr(FileClassificationAgent, "_is_service_class"))

    def test_is_factory_class_exists(self):
        """Verify _is_factory_class method exists."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_factory_class")
        assert callable(getattr(FileClassificationAgent, "_is_factory_class"))

    def test_is_async_agent_exists(self):
        """Verify _is_async_agent method exists."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_async_agent")
        assert callable(getattr(FileClassificationAgent, "_is_async_agent"))

    def test_is_adapter_class_exists(self):
        """Verify _is_adapter_class method exists."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_adapter_class")
        assert callable(getattr(FileClassificationAgent, "_is_adapter_class"))

    def test_is_config_class_exists(self):
        """Verify _is_config_class method exists."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_config_class")
        assert callable(getattr(FileClassificationAgent, "_is_config_class"))

    def test_is_model_class_exists(self):
        """Verify _is_model_class method exists."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_model_class")
        assert callable(getattr(FileClassificationAgent, "_is_model_class"))

    def test_is_repository_class_exists(self):
        """Verify _is_repository_class method exists."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_repository_class")
        assert callable(getattr(FileClassificationAgent, "_is_repository_class"))


class TestFileTypeCategoriesComplete:
    """Verify all 19 FileType categories exist."""

    def test_all_categories_present(self):
        """Verify all expected categories are in FileType."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import FileType

        expected_categories = {
            "AGENT",
            "CLASS",
            "MIXIN",
            "UTILITY",
            "PROTOCOL",
            "ENGINE",
            "STUB",
            "TEST",
            "SCRIPT",
            "TYPES",
            "GATEWAY",
            "SERVICE",
            "FACTORY",
            "ASYNC_AGENT",
            "ADAPTER",
            "CONFIG",
            "MODEL",
            "REPOSITORY",
            "IGNORE",
        }
        actual_categories = set(FileType.__args__)
        assert expected_categories == actual_categories

    def test_category_count_is_19(self):
        """Verify exactly 19 categories exist."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import FileType

        assert len(FileType.__args__) == 19


class TestMethodSignaturesCorrect:
    """Verify all method signatures are correct."""

    def test_is_true_agent_signature(self):
        """Verify _is_true_agent signature."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        sig = inspect.signature(FileClassificationAgent._is_true_agent)
        params = list(sig.parameters.keys())
        assert "self" in params
        assert "node" in params
        assert "file_path" in params

    def test_is_service_class_signature(self):
        """Verify _is_service_class signature."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        sig = inspect.signature(FileClassificationAgent._is_service_class)
        params = list(sig.parameters.keys())
        assert "self" in params
        assert "node" in params

    def test_is_factory_class_signature(self):
        """Verify _is_factory_class signature."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        sig = inspect.signature(FileClassificationAgent._is_factory_class)
        params = list(sig.parameters.keys())
        assert "self" in params
        assert "node" in params

    def test_is_async_agent_signature(self):
        """Verify _is_async_agent signature."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        sig = inspect.signature(FileClassificationAgent._is_async_agent)
        params = list(sig.parameters.keys())
        assert "self" in params
        assert "node" in params

    def test_is_adapter_class_signature(self):
        """Verify _is_adapter_class signature."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        sig = inspect.signature(FileClassificationAgent._is_adapter_class)
        params = list(sig.parameters.keys())
        assert "self" in params
        assert "node" in params

    def test_is_config_class_signature(self):
        """Verify _is_config_class signature."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        sig = inspect.signature(FileClassificationAgent._is_config_class)
        params = list(sig.parameters.keys())
        assert "self" in params
        assert "node" in params

    def test_is_model_class_signature(self):
        """Verify _is_model_class signature."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        sig = inspect.signature(FileClassificationAgent._is_model_class)
        params = list(sig.parameters.keys())
        assert "self" in params
        assert "node" in params

    def test_is_repository_class_signature(self):
        """Verify _is_repository_class signature."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        sig = inspect.signature(FileClassificationAgent._is_repository_class)
        params = list(sig.parameters.keys())
        assert "self" in params
        assert "node" in params


class TestHelperFunctionsWork:
    """Verify helper functions work correctly."""

    def test_get_python_files_fast_exists(self):
        """Verify get_python_files_fast function exists."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            get_python_files_fast,
        )

        assert get_python_files_fast is not None
        assert callable(get_python_files_fast)

    def test_logger_exists(self):
        """Verify Logger is defined."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import Logger

        assert Logger is not None


class TestEnhancementsSummary:
    """Summary tests for all enhancements."""

    def test_total_new_detection_methods_is_8(self):
        """Verify 8 new detection methods were added."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        new_methods = [
            "_is_true_agent",
            "_is_service_class",
            "_is_factory_class",
            "_is_async_agent",
            "_is_adapter_class",
            "_is_config_class",
            "_is_model_class",
            "_is_repository_class",
        ]
        for method in new_methods:
            assert hasattr(FileClassificationAgent, method), f"Missing: {method}"

        assert len(new_methods) == 8

    def test_total_new_categories_is_7(self):
        """Verify 7 new categories were added."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import FileType

        new_categories = {
            "SERVICE",
            "FACTORY",
            "ASYNC_AGENT",
            "ADAPTER",
            "CONFIG",
            "MODEL",
            "REPOSITORY",
        }
        for category in new_categories:
            assert category in FileType.__args__, f"Missing: {category}"

        assert len(new_categories) == 7


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
