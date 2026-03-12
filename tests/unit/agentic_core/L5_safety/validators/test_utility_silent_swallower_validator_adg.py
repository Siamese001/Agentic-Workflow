"""ADG-driven tests for agentic_core/L5_safety/validators/utility_silent_swallower_validator.py — fan_in=2.

Contract tests: UtilityScriptClassifier path classification constants and importability.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.validators.utility_silent_swallower_validator import (
    UtilityScriptClassifier,
)


class TestUtilityScriptClassifierImport:
    def test_class_importable(self):
        assert callable(UtilityScriptClassifier)


class TestUtilityScriptClassifierConstants:
    def test_governance_paths_nonempty(self):
        assert len(UtilityScriptClassifier.GOVERNANCE_PATHS) > 0

    def test_diagnostic_paths_nonempty(self):
        assert len(UtilityScriptClassifier.DIAGNOSTIC_PATHS) > 0

    def test_local_dev_paths_nonempty(self):
        assert len(UtilityScriptClassifier.LOCAL_DEV_PATHS) > 0

    def test_governance_paths_are_set(self):
        assert isinstance(UtilityScriptClassifier.GOVERNANCE_PATHS, (set, frozenset))

    def test_known_governance_path_present(self):
        assert any("ci" in p or "L5_safety" in p for p in UtilityScriptClassifier.GOVERNANCE_PATHS)

    def test_known_diagnostic_path_present(self):
        assert any("tools" in p for p in UtilityScriptClassifier.DIAGNOSTIC_PATHS)


class TestUtilityScriptClassifierClassify:
    def test_governance_path_classified(self):
        from pathlib import Path
        category = UtilityScriptClassifier.classify_script(Path("ops_scripts/ci/run_tests.py"))
        assert category == "GOVERNANCE_CRITICAL"

    def test_tests_path_classified(self):
        from pathlib import Path
        category = UtilityScriptClassifier.classify_script(Path("tests/governance/test_something.py"))
        assert category == "GOVERNANCE_CRITICAL"

    def test_local_dev_path_classified(self):
        from pathlib import Path
        category = UtilityScriptClassifier.classify_script(Path("scripts/debug_helper.py"))
        assert category == "LOCAL_DEV_ONLY"

    def test_diagnostic_path_classified(self):
        from pathlib import Path
        category = UtilityScriptClassifier.classify_script(Path("tools/evidence/gather.py"))
        assert category == "DIAGNOSTIC_ONLY"

    def test_unknown_path_defaults_to_governance_critical(self):
        from pathlib import Path
        result = UtilityScriptClassifier.classify_script(Path("completely/unknown/module.py"))
        assert result == "GOVERNANCE_CRITICAL"
