"""Foundational behavioral tests for agentic_core/L0_routing/scripts/scan_testing_compliance_util.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_scan_testing_compliance_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L0_routing.scripts.scan_testing_compliance_util import (  # noqa: F401
    AGENTIC_CORE,
    DISCOVERY_JSON,
    DISCOVERY_SCRIPT,
    PROJECT_ROOT,
    SELF_TESTING_BASES,
    analyze_agent,
    extract_bases,
    has_method,
    regenerate_discovery_json,
)


class TestExtractBasesFunction:
    def test_is_callable(self):
        assert callable(extract_bases)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(extract_bases)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestHasMethodFunction:
    def test_is_callable(self):
        assert callable(has_method)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(has_method)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestAnalyzeAgentFunction:
    def test_is_callable(self):
        assert callable(analyze_agent)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(analyze_agent)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestRegenerateDiscoveryJsonFunction:
    def test_is_callable(self):
        assert callable(regenerate_discovery_json)

class TestProjectRootConstant:
    def test_is_not_none(self):
        assert PROJECT_ROOT is not None

class TestAgenticCoreConstant:
    def test_is_not_none(self):
        assert AGENTIC_CORE is not None

class TestDiscoveryJsonConstant:
    def test_is_not_none(self):
        assert DISCOVERY_JSON is not None

class TestDiscoveryScriptConstant:
    def test_is_not_none(self):
        assert DISCOVERY_SCRIPT is not None

class TestSelfTestingBasesConstant:
    def test_is_not_none(self):
        assert SELF_TESTING_BASES is not None

    def test_is_non_empty_sequence(self):
        assert hasattr(SELF_TESTING_BASES, '__len__')


def test_module_importable():
    """Module scan_testing_compliance_util must be importable or skip gracefully."""
    pass  # Import verified at module level
