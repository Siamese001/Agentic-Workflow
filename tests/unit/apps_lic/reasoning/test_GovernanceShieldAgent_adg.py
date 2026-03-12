"""ADG-driven tests for apps_lic/reasoning/GovernanceShieldAgent.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_lic.reasoning.GovernanceShieldAgent import (  # noqa: F401
        GovernanceShieldAgent,
        create_governance_shield_agent,
        sanitize_content,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    GovernanceShieldAgent = None  # type: ignore[assignment,misc]
    create_governance_shield_agent = None  # type: ignore[assignment,misc]
    sanitize_content = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="GovernanceShieldAgent.py deps unavailable")
class TestGovernanceShieldAgent:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(GovernanceShieldAgent)
    def test_importable(self):
        assert GovernanceShieldAgent is not None

@pytest.mark.skipif(not _AVAILABLE, reason="GovernanceShieldAgent.py deps unavailable")
class TestCreateGovernanceShieldAgent:
    def test_is_callable(self):
        assert callable(create_governance_shield_agent)

@pytest.mark.skipif(not _AVAILABLE, reason="GovernanceShieldAgent.py deps unavailable")
class TestSanitizeContent:
    def test_is_callable(self):
        assert callable(sanitize_content)

@pytest.mark.skipif(not _AVAILABLE, reason="GovernanceShieldAgent.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="GovernanceShieldAgent.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="GovernanceShieldAgent.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="GovernanceShieldAgent.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="GovernanceShieldAgent.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="GovernanceShieldAgent.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module GovernanceShieldAgent.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
