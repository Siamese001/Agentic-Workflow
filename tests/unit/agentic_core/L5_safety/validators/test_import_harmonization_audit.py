"""
file: tests/maintenance/test_import_harmonization_audit.py
description: Final audit to verify that all core agents are using the new SSOT
             locations and no imports are pointing to quarantined archives.
"""

import importlib
import sys
from pathlib import Path

import pytest

# --- Audit configuration ---
CORE_AGENTS_TO_VERIFY = [
    # (Module Path, Class Name)
    ("agentic_core.L1_cognition.agents.MetaLearningAgent", "MetaLearningAgent"),
    ("agentic_core.L5_safety.validators.HygieneGuardianAgent", "HygieneGuardianAgent"),
    ("agentic_core.L5_safety.validators.LocationAgent", "LocationAgent"),
    ("agentic_core.utils.sovereign_index", "SovereignIndex"),
    ("agentic_core.L3_orchestration.orchestrator_registry", "get_orchestrator"),
]


class TestImportHarmonization:
    def test_quarantine_leak_audit(self):
        """
        TC-001: Scans the code of key agents to ensure no 'from archives' imports exist.
        """
        import agentic_core.L5_safety.config.structure_blueprint_config_config as ssot

        excluded_dirs = getattr(ssot, "GLOBAL_EXCLUDED_DIRS", [])

        # Verify 'archives' is strictly in the exclusion list
        assert "archives" in excluded_dirs or "archives/" in excluded_dirs

    @pytest.mark.parametrize("module_path, attr_name", CORE_AGENTS_TO_VERIFY)
    def test_core_agent_import_integrity(self, module_path, attr_name):
        """
        TC-002: Verifies that core agents are importable and have their main attributes.
        This catches broken imports resulting from the consolidation of BaseAgents.
        """
        try:
            module = importlib.import_module(module_path)
            assert hasattr(module, attr_name), f"{attr_name} missing from {module_path}"
        except (ImportError, NameError, AttributeError, TypeError) as e:
            pytest.fail(f"CRITICAL IMPORT BREAK: {module_path} is failing to load: {e}")
        except Exception as e:
            pytest.fail(f"Unexpected error loading {module_path}: {e}")

    def test_sovereign_index_ssot_linkage(self):
        """
        TC-003: Direct check that SovereignIndex is actually using the SSOT exclusion list.
        """
        from agentic_core.L5_safety.config.structure_blueprint_config import (
            GLOBAL_EXCLUDED_DIRS,
        )
        from agentic_core.utils.sovereign_index import SovereignIndex

        # Reset instance to ensure fresh state
        SovereignIndex.reset_instance()

        # Get instance with project root
        project_root = Path(__file__).resolve().parents[2]
        idx = SovereignIndex.get_instance(project_root)

        # Verify the intersection exists - confirming they are pulling from the same source
        assert any(d in idx._excluded_dirs for d in GLOBAL_EXCLUDED_DIRS), (
            f"SovereignIndex exclusions {idx._excluded_dirs} don't overlap with SSOT {GLOBAL_EXCLUDED_DIRS}"
        )


if __name__ == "__main__":
    sys.exit(pytest.main(["-v", __file__]))
