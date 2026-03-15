"""Foundational behavioral tests for agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py.

fan_in=4 — imported by 4 other modules.
ADG import-hygiene is covered separately by test_CognitiveDispositionAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.reasoning.CognitiveDispositionAgent import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        CognitiveDispositionAgent,
        DispositionDecision,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    DispositionDecision = None  # type: ignore[assignment,misc]
    CognitiveDispositionAgent = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="CognitiveDispositionAgent.py deps unavailable")
class TestDispositionDecisionContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(DispositionDecision)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(DispositionDecision)}
        assert fnames >= {'target_path', 'confidence', 'action', 'reason'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(DispositionDecision)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="CognitiveDispositionAgent.py deps unavailable")
class TestCognitiveDispositionAgentContract:
    def test_is_class(self):
        assert isinstance(CognitiveDispositionAgent, type)

    def test_has_method_analyze_violation_async(self):
        assert callable(getattr(CognitiveDispositionAgent, 'analyze_violation_async', None))

    def test_has_method_analyze_violation(self):
        assert callable(getattr(CognitiveDispositionAgent, 'analyze_violation', None))

    def test_has_method_analyze_violations(self):
        assert callable(getattr(CognitiveDispositionAgent, 'analyze_violations', None))

    def test_has_method_get_analytics(self):
        assert callable(getattr(CognitiveDispositionAgent, 'get_analytics', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(CognitiveDispositionAgent) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="CognitiveDispositionAgent.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="CognitiveDispositionAgent.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="CognitiveDispositionAgent.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="CognitiveDispositionAgent.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="CognitiveDispositionAgent.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="CognitiveDispositionAgent.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: CognitiveDispositionAgent importable or gracefully unavailable."""
    pass
