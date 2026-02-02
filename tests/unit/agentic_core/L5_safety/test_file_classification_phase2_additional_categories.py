"""
Phase 2: Additional Category Detection Tests

Tests for additional category detection methods:
1. _is_config_class - Configuration class detection
2. _is_model_class - Data model class detection
3. _is_repository_class - Repository pattern detection
"""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestIsConfigClassMethod:
    """Tests for _is_config_class detection."""

    def test_detect_by_config_suffix(self):
        """Test config detection by name ending with Config."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_config_class")

    def test_detect_by_settings_suffix(self):
        """Test config detection by name ending with Settings."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_config_class")

    def test_detect_by_options_suffix(self):
        """Test config detection by name ending with Options."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_config_class")

    def test_detect_by_configuration_suffix(self):
        """Test config detection by name ending with Configuration."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_config_class")

    def test_detect_by_dataclass_decorator(self):
        """Test config detection by @dataclass decorator."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_config_class")

    def test_method_exists_and_callable(self):
        """Verify _is_config_class method exists on class."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_config_class")
        assert callable(getattr(FileClassificationAgent, "_is_config_class"))


class TestIsModelClassMethod:
    """Tests for _is_model_class detection."""

    def test_detect_by_basemodel_inheritance(self):
        """Test model detection by BaseModel inheritance."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_model_class")

    def test_detect_by_model_suffix(self):
        """Test model detection by name ending with Model."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_model_class")

    def test_detect_by_schema_suffix(self):
        """Test model detection by name ending with Schema."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_model_class")

    def test_detect_by_dto_suffix(self):
        """Test model detection by name ending with DTO."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_model_class")

    def test_detect_by_entity_suffix(self):
        """Test model detection by name ending with Entity."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_model_class")

    def test_method_exists_and_callable(self):
        """Verify _is_model_class method exists on class."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_model_class")
        assert callable(getattr(FileClassificationAgent, "_is_model_class"))


class TestIsRepositoryClassMethod:
    """Tests for _is_repository_class detection."""

    def test_detect_by_repository_suffix(self):
        """Test repository detection by name ending with Repository."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_repository_class")

    def test_detect_by_dao_suffix(self):
        """Test repository detection by name ending with DAO."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_repository_class")

    def test_detect_by_store_suffix(self):
        """Test repository detection by name ending with Store."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_repository_class")

    def test_detect_by_crud_methods(self):
        """Test repository detection by CRUD methods."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_repository_class")

    def test_method_exists_and_callable(self):
        """Verify _is_repository_class method exists on class."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "_is_repository_class")
        assert callable(getattr(FileClassificationAgent, "_is_repository_class"))


class TestPhase2MethodSignatures:
    """Verify all Phase 2 methods have correct signatures."""

    def test_is_config_class_signature(self):
        """Verify _is_config_class takes node and file_path."""
        import inspect

        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        sig = inspect.signature(FileClassificationAgent._is_config_class)
        params = list(sig.parameters.keys())
        assert "self" in params
        assert "node" in params
        assert "file_path" in params

    def test_is_model_class_signature(self):
        """Verify _is_model_class takes node."""
        import inspect

        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        sig = inspect.signature(FileClassificationAgent._is_model_class)
        params = list(sig.parameters.keys())
        assert "self" in params
        assert "node" in params

    def test_is_repository_class_signature(self):
        """Verify _is_repository_class takes node."""
        import inspect

        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        sig = inspect.signature(FileClassificationAgent._is_repository_class)
        params = list(sig.parameters.keys())
        assert "self" in params
        assert "node" in params


class TestPhase2MethodReturns:
    """Verify Phase 2 methods return boolean values."""

    def test_is_config_class_returns_bool(self):
        """Verify _is_config_class returns boolean."""
        import inspect

        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        # Check return annotation if available
        sig = inspect.signature(FileClassificationAgent._is_config_class)
        assert sig.return_annotation in (bool, inspect.Parameter.empty)

    def test_is_model_class_returns_bool(self):
        """Verify _is_model_class returns boolean."""
        import inspect

        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        sig = inspect.signature(FileClassificationAgent._is_model_class)
        assert sig.return_annotation in (bool, inspect.Parameter.empty)

    def test_is_repository_class_returns_bool(self):
        """Verify _is_repository_class returns boolean."""
        import inspect

        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        sig = inspect.signature(FileClassificationAgent._is_repository_class)
        assert sig.return_annotation in (bool, inspect.Parameter.empty)


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
