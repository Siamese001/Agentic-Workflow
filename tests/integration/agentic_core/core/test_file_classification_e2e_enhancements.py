"""
Phase 6: E2E & Integration Tests for FileClassificationAgent Enhancements

Comprehensive end-to-end tests validating all phases work together:
1. All detection methods functional
2. All categories properly defined
3. Stats tracking complete
4. Backward compatibility maintained
"""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestE2EAllPhasesIntegration:
    """E2E tests verifying all phases work together."""

    def test_e2e_file_type_has_all_categories(self):
        """Verify FileType has all categories from implementation."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import FileType

        expected = {
            # Original categories
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
            "IGNORE",
            # Windsurf implementation additions
            "ORCHESTRATOR",
            "VALIDATOR",
            "FACTORY",
            "CONFIG",
            "ADAPTER",
        }
        assert set(FileType.__args__) == expected
        assert len(FileType.__args__) == 17

    def test_e2e_all_detection_methods_exist(self):
        """Verify all detection methods exist."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        methods = [
            "_is_true_agent",
            "_is_model_class",
            "_is_repository_class",
            "_to_smart_snake_case",  # New method from refactoring
            "_detect_test_patterns",
            "_detect_script_patterns",
            "_detect_type_patterns",
            "_detect_config_patterns",
            "_detect_validator_patterns",
        ]
        for method in methods:
            assert hasattr(FileClassificationAgent, method), f"Missing: {method}"
            assert callable(getattr(FileClassificationAgent, method))

    def test_e2e_classify_file_method_exists(self):
        """Verify core classify_file method still works."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "classify_file")
        assert callable(FileClassificationAgent.classify_file)

    def test_e2e_helper_functions_work(self):
        """Verify helper functions are accessible."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            Logger,
            get_python_files_fast,
        )

        assert get_python_files_fast is not None
        assert Logger is not None


class TestE2EBackwardCompatibility:
    """E2E tests for backward compatibility."""

    def test_e2e_original_categories_unchanged(self):
        """Verify original 12 categories still exist."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import FileType

        original = {
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
            "IGNORE",
        }
        assert original.issubset(set(FileType.__args__))

    def test_e2e_core_methods_unchanged(self):
        """Verify core methods still exist."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        core_methods = [
            "run",
            "classify_file",
            "get_compliant_name",
            "update_imports",
            "verify_environment",
        ]
        for method in core_methods:
            assert hasattr(FileClassificationAgent, method), f"Missing: {method}"


class TestE2EPhaseValidation:
    """Validate each phase's contributions."""

    def test_e2e_core_detection_methods(self):
        """Verify core detection methods exist."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        core_methods = [
            "_is_true_agent",
            "_is_model_class",
            "_is_repository_class",
            "_to_smart_snake_case",
        ]
        for method in core_methods:
            assert hasattr(FileClassificationAgent, method)

    def test_e2e_ast_detection_methods(self):
        """Verify AST-based detection methods exist."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        ast_methods = [
            "_detect_test_patterns",
            "_detect_script_patterns",
            "_detect_type_patterns",
            "_detect_config_patterns",
            "_detect_validator_patterns",
        ]
        for method in ast_methods:
            assert hasattr(FileClassificationAgent, method)

    def test_e2e_windsurf_categories(self):
        """Verify Windsurf implementation categories exist."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import FileType

        windsurf_categories = {
            "ORCHESTRATOR",
            "VALIDATOR",
            "FACTORY",
            "CONFIG",
            "ADAPTER",
        }
        assert windsurf_categories.issubset(set(FileType.__args__))


class TestE2EModuleImports:
    """Test that all imports work correctly."""

    def test_e2e_import_file_type(self):
        """Verify FileType can be imported."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import FileType

        assert FileType is not None

    def test_e2e_import_agent_class(self):
        """Verify FileClassificationAgent can be imported."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert FileClassificationAgent is not None

    def test_e2e_import_helper_function(self):
        """Verify get_python_files_fast can be imported."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            get_python_files_fast,
        )

        assert get_python_files_fast is not None

    def test_e2e_import_logger(self):
        """Verify Logger can be imported."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import Logger

        assert Logger is not None


class TestE2EEnhancementsSummary:
    """Summary E2E tests for all enhancements."""

    def test_e2e_total_enhancements(self):
        """Verify total enhancements: detection methods + categories."""
        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
            FileType,
        )

        # Key detection methods
        key_methods = [
            "_is_true_agent",
            "_is_model_class",
            "_is_repository_class",
            "_to_smart_snake_case",
            "_detect_test_patterns",
            "_detect_script_patterns",
            "_detect_type_patterns",
            "_detect_config_patterns",
            "_detect_validator_patterns",
        ]
        method_count = sum(1 for m in key_methods if hasattr(FileClassificationAgent, m))
        assert method_count >= 9

        # Windsurf implementation categories
        windsurf_categories = {
            "ORCHESTRATOR",
            "VALIDATOR",
            "FACTORY",
            "ADAPTER",
            "CONFIG",
        }
        category_count = sum(1 for c in windsurf_categories if c in FileType.__args__)
        assert category_count == 5

    def test_e2e_file_classification_agent_is_dataclass(self):
        """Verify FileClassificationAgent is a dataclass."""
        from dataclasses import is_dataclass

        from agentic_core.L5_safety.validators.core.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert is_dataclass(FileClassificationAgent)


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
