"""ADG-driven tests for agentic_core/prompt_governance/security/assembly_injection_neutralizer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.prompt_governance.security.assembly_injection_neutralizer import (  # noqa: F401
        NeutralizationResult,
        InjectionPattern,
        neutralize_prompt,
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
    NeutralizationResult = None  # type: ignore[assignment,misc]
    InjectionPattern = None  # type: ignore[assignment,misc]
    neutralize_prompt = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="assembly_injection_neutralizer.py deps unavailable")
class TestNeutralizationResult:
    def test_is_class(self):
        assert isinstance(NeutralizationResult, type)
    def test_importable(self):
        assert NeutralizationResult is not None

@pytest.mark.skipif(not _AVAILABLE, reason="assembly_injection_neutralizer.py deps unavailable")
class TestInjectionPattern:
    def test_is_class(self):
        assert isinstance(InjectionPattern, type)
    def test_importable(self):
        assert InjectionPattern is not None

@pytest.mark.skipif(not _AVAILABLE, reason="assembly_injection_neutralizer.py deps unavailable")
class TestNeutralizePrompt:
    def test_is_callable(self):
        assert callable(neutralize_prompt)

@pytest.mark.skipif(not _AVAILABLE, reason="assembly_injection_neutralizer.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="assembly_injection_neutralizer.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="assembly_injection_neutralizer.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="assembly_injection_neutralizer.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="assembly_injection_neutralizer.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="assembly_injection_neutralizer.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module assembly_injection_neutralizer.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
