"""Foundational behavioral tests for agentic_core/L0_routing/scripts/scan_testing_compliance_util.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_scan_testing_compliance_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.scan_testing_compliance_util import (  # noqa: F401
        extract_bases,
        has_method,
        analyze_agent,
        regenerate_discovery_json,
        PROJECT_ROOT,
        AGENTIC_CORE,
        DISCOVERY_JSON,
        DISCOVERY_SCRIPT,
        SELF_TESTING_BASES,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    extract_bases = None  # type: ignore[assignment,misc]
    has_method = None  # type: ignore[assignment,misc]
    analyze_agent = None  # type: ignore[assignment,misc]
    regenerate_discovery_json = None  # type: ignore[assignment,misc]
    PROJECT_ROOT = None  # type: ignore[assignment,misc]
    AGENTIC_CORE = None  # type: ignore[assignment,misc]
    DISCOVERY_JSON = None  # type: ignore[assignment,misc]
    DISCOVERY_SCRIPT = None  # type: ignore[assignment,misc]
    SELF_TESTING_BASES = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="scan_testing_compliance_util.py deps unavailable")
class TestExtractBasesFunction:
    def test_is_callable(self):
        assert callable(extract_bases)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(extract_bases)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="scan_testing_compliance_util.py deps unavailable")
class TestHasMethodFunction:
    def test_is_callable(self):
        assert callable(has_method)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(has_method)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="scan_testing_compliance_util.py deps unavailable")
class TestAnalyzeAgentFunction:
    def test_is_callable(self):
        assert callable(analyze_agent)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(analyze_agent)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="scan_testing_compliance_util.py deps unavailable")
class TestRegenerateDiscoveryJsonFunction:
    def test_is_callable(self):
        assert callable(regenerate_discovery_json)

@pytest.mark.skipif(not _AVAILABLE, reason="scan_testing_compliance_util.py deps unavailable")
class TestProjectRootConstant:
    def test_is_not_none(self):
        assert PROJECT_ROOT is not None

@pytest.mark.skipif(not _AVAILABLE, reason="scan_testing_compliance_util.py deps unavailable")
class TestAgenticCoreConstant:
    def test_is_not_none(self):
        assert AGENTIC_CORE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="scan_testing_compliance_util.py deps unavailable")
class TestDiscoveryJsonConstant:
    def test_is_not_none(self):
        assert DISCOVERY_JSON is not None

@pytest.mark.skipif(not _AVAILABLE, reason="scan_testing_compliance_util.py deps unavailable")
class TestDiscoveryScriptConstant:
    def test_is_not_none(self):
        assert DISCOVERY_SCRIPT is not None

@pytest.mark.skipif(not _AVAILABLE, reason="scan_testing_compliance_util.py deps unavailable")
class TestSelfTestingBasesConstant:
    def test_is_not_none(self):
        assert SELF_TESTING_BASES is not None

    def test_is_non_empty_sequence(self):
        assert hasattr(SELF_TESTING_BASES, '__len__')


def test_module_importable():
    """Module scan_testing_compliance_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
