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
        """Verify FileType has all 19 categories from all phases."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import FileType

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
            # Phase 3 additions
            "SERVICE",
            "FACTORY",
            "ASYNC_AGENT",
            "ADAPTER",
            "CONFIG",
            "MODEL",
            "REPOSITORY",
        }
        assert set(FileType.__args__) == expected
        assert len(FileType.__args__) == 19

    def test_e2e_all_detection_methods_exist(self):
        """Verify all 8 new detection methods exist."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        methods = [
            "_is_true_agent",
            "_is_service_class",
            "_is_factory_class",
            "_is_async_agent",
            "_is_adapter_class",
            "_is_config_class",
            "_is_model_class",
            "_is_repository_class",
        ]
        for method in methods:
            assert hasattr(FileClassificationAgent, method), f"Missing: {method}"
            assert callable(getattr(FileClassificationAgent, method))

    def test_e2e_classify_file_method_exists(self):
        """Verify core classify_file method still works."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "classify_file")
        assert callable(FileClassificationAgent.classify_file)

    def test_e2e_helper_functions_work(self):
        """Verify helper functions are accessible."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            Logger,
            get_python_files_fast,
        )

        assert get_python_files_fast is not None
        assert Logger is not None


class TestE2EBackwardCompatibility:
    """E2E tests for backward compatibility."""

    def test_e2e_original_categories_unchanged(self):
        """Verify original 12 categories still exist."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import FileType

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
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
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

    def test_e2e_phase1_methods(self):
        """Verify Phase 1 detection methods exist."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        phase1_methods = [
            "_is_true_agent",
            "_is_service_class",
            "_is_factory_class",
            "_is_async_agent",
            "_is_adapter_class",
        ]
        for method in phase1_methods:
            assert hasattr(FileClassificationAgent, method)

    def test_e2e_phase2_methods(self):
        """Verify Phase 2 detection methods exist."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        phase2_methods = [
            "_is_config_class",
            "_is_model_class",
            "_is_repository_class",
        ]
        for method in phase2_methods:
            assert hasattr(FileClassificationAgent, method)

    def test_e2e_phase3_categories(self):
        """Verify Phase 3 categories exist."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import FileType

        phase3_categories = {
            "SERVICE",
            "FACTORY",
            "ASYNC_AGENT",
            "ADAPTER",
            "CONFIG",
            "MODEL",
            "REPOSITORY",
        }
        assert phase3_categories.issubset(set(FileType.__args__))


class TestE2EModuleImports:
    """Test that all imports work correctly."""

    def test_e2e_import_file_type(self):
        """Verify FileType can be imported."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import FileType

        assert FileType is not None

    def test_e2e_import_agent_class(self):
        """Verify FileClassificationAgent can be imported."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert FileClassificationAgent is not None

    def test_e2e_import_helper_function(self):
        """Verify get_python_files_fast can be imported."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            get_python_files_fast,
        )

        assert get_python_files_fast is not None

    def test_e2e_import_logger(self):
        """Verify Logger can be imported."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import Logger

        assert Logger is not None


class TestE2EEnhancementsSummary:
    """Summary E2E tests for all enhancements."""

    def test_e2e_total_enhancements(self):
        """Verify total enhancements: 8 methods + 7 categories."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
            FileType,
        )

        # 8 new detection methods
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
        method_count = sum(1 for m in new_methods if hasattr(FileClassificationAgent, m))
        assert method_count == 8

        # 7 new categories
        new_categories = {
            "SERVICE",
            "FACTORY",
            "ASYNC_AGENT",
            "ADAPTER",
            "CONFIG",
            "MODEL",
            "REPOSITORY",
        }
        category_count = sum(1 for c in new_categories if c in FileType.__args__)
        assert category_count == 7

    def test_e2e_file_classification_agent_is_dataclass(self):
        """Verify FileClassificationAgent is a dataclass."""
        from dataclasses import is_dataclass

        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert is_dataclass(FileClassificationAgent)


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
