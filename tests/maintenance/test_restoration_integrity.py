"""
file: tests/maintenance/test_restoration_integrity.py
description: Verifies the 10 restored agents are importable and free of deprecated dependencies.
             Also verifies the recent terminal_colors move.
"""

import importlib
import inspect
import sys

import pytest

# --- Configuration ---
RESTORED_AGENTS_MAP = [
    # (Class Name, Full Module Path)
    ("MetaLearningAgent", "agentic_core.L1_cognition.thought_engine.MetaLearningAgent"),
    ("StrategicRecommendationAgent", "agentic_core.L1_cognition.thought_engine.StrategicRecommendationAgent"),
    ("BudgetAgent", "agentic_core.L1_cognition.thought_engine.BudgetAgent"),
    ("CodeDeduplicationAgent", "agentic_core.L5_safety.validators.CodeDeduplicationAgent"),
    ("PatternEnforcerAgent", "agentic_core.L5_safety.validators.PatternEnforcerAgent"),
    ("DeadlockDetectorAgent", "agentic_core.L5_safety.validators.DeadlockDetectorAgent"),
    ("IntegrityGateExecutorAgent", "agentic_core.L5_safety.validators.IntegrityGateExecutorAgent"),
    ("TypeMechanicAgent", "agentic_core.L5_safety.validators.TypeMechanicAgent"),
    ("DocumentationAgent", "agentic_core.L5_safety.validators.DocumentationAgent"),
    ("BenchmarkingAgent", "agentic_core.L6_observability.BenchmarkingAgent"),
]

class TestRestorationIntegrity:

    def test_terminal_colors_migration(self):
        """
        TC-001: Verifies terminal_colors is accessible in its new home.
        """
        try:
            import agentic_core.utils.terminal_colors as tc
            assert hasattr(tc, 'PrintColors'), "terminal_colors module missing PrintColors class"
        except ImportError:
            pytest.fail("Could not import agentic_core.utils.terminal_colors. Move may be incomplete.")

    def test_filesystem_agent_import_safety(self):
        """
        TC-002: Verifies FilesystemAgent does not crash on internal imports.
        """
        try:
            from agentic_core.L5_safety.validators.FilesystemAgent import FilesystemAgent
            # Just importing it is often enough to trigger module-level errors
            assert FilesystemAgent is not None
        except ImportError as e:
            pytest.fail(f"FilesystemAgent is broken: {e}")

    @pytest.mark.parametrize("class_name, module_path", RESTORED_AGENTS_MAP)
    def test_agent_importability(self, class_name, module_path):
        """
        TC-003: Verifies that the restored module exists and the class can be imported.
        """
        try:
            module = importlib.import_module(module_path)
        except ImportError as e:
            pytest.fail(f"CRITICAL: Could not import {module_path}.\nError: {e}")
        except SyntaxError as e:
            pytest.fail(f"CRITICAL: Syntax Error in {module_path}: {e}")

        if not hasattr(module, class_name):
            pytest.fail(f"Class '{class_name}' not found in {module_path}")

    @pytest.mark.parametrize("class_name, module_path", RESTORED_AGENTS_MAP)
    def test_no_deprecated_mixins(self, class_name, module_path):
        """
        TC-004: Ensures restored agents are not using 'MCPHardenedMixin' or 'archives' imports.
        """
        try:
            module = importlib.import_module(module_path)
            agent_class = getattr(module, class_name)

            # 1. Check MRO for deprecated mixins
            mro_names = [c.__name__ for c in inspect.getmro(agent_class)]
            if "MCPHardenedMixin" in mro_names:
                pytest.fail(
                    f"{class_name} uses deprecated 'MCPHardenedMixin'. "
                    "ACTION: Remove it or replace with standard SafetyMixin."
                )

            # 2. Check source code for forbidden strings (crude but effective for imports)
            source = inspect.getsource(module)
            if "archives." in source:
                 pytest.fail(f"{class_name} still contains imports from 'archives.'")

        except ImportError:
            pytest.skip(f"Skipping mixin check for {class_name} due to import failure")

if __name__ == "__main__":
    sys.exit(pytest.main(["-v", __file__]))
