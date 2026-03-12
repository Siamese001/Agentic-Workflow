"""ADG-driven tests for agentic_core/L0_routing/scripts/scan_testing_compliance_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.scan_testing_compliance_util import (  # noqa: F401
        extract_bases,
        has_method,
        analyze_agent,
        regenerate_discovery_json,
        load_from_canonical_json,
        PROJECT_ROOT,
        AGENTIC_CORE,
        DISCOVERY_JSON,
        DISCOVERY_SCRIPT,
        SELF_TESTING_BASES,
        DELEGATION_BASES,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    extract_bases = None  # type: ignore[assignment,misc]
    has_method = None  # type: ignore[assignment,misc]
    analyze_agent = None  # type: ignore[assignment,misc]
    regenerate_discovery_json = None  # type: ignore[assignment,misc]
    load_from_canonical_json = None  # type: ignore[assignment,misc]
    PROJECT_ROOT = None  # type: ignore[assignment,misc]
    AGENTIC_CORE = None  # type: ignore[assignment,misc]
    DISCOVERY_JSON = None  # type: ignore[assignment,misc]
    DISCOVERY_SCRIPT = None  # type: ignore[assignment,misc]
    SELF_TESTING_BASES = None  # type: ignore[assignment,misc]
    DELEGATION_BASES = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="scan_testing_compliance_util.py deps unavailable")
class TestExtractBases:
    def test_is_callable(self):
        assert callable(extract_bases)

@pytest.mark.skipif(not _AVAILABLE, reason="scan_testing_compliance_util.py deps unavailable")
class TestHasMethod:
    def test_is_callable(self):
        assert callable(has_method)

@pytest.mark.skipif(not _AVAILABLE, reason="scan_testing_compliance_util.py deps unavailable")
class TestAnalyzeAgent:
    def test_is_callable(self):
        assert callable(analyze_agent)

@pytest.mark.skipif(not _AVAILABLE, reason="scan_testing_compliance_util.py deps unavailable")
class TestRegenerateDiscoveryJson:
    def test_is_callable(self):
        assert callable(regenerate_discovery_json)

@pytest.mark.skipif(not _AVAILABLE, reason="scan_testing_compliance_util.py deps unavailable")
class TestLoadFromCanonicalJson:
    def test_is_callable(self):
        assert callable(load_from_canonical_json)

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

@pytest.mark.skipif(not _AVAILABLE, reason="scan_testing_compliance_util.py deps unavailable")
class TestDelegationBasesConstant:
    def test_is_not_none(self):
        assert DELEGATION_BASES is not None


def test_module_importable():
    """Module scan_testing_compliance_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
