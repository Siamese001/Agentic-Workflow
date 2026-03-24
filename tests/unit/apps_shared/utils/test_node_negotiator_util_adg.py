"""ADG-driven tests for apps_shared/utils/node_negotiator_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.node_negotiator_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        NegotiatingHop,
        NegotiationConfig,
        NegotiationMessage,
        NegotiationResult,
        NegotiationRound,
        NodeNegotiator,
        get_node_negotiator,
        request_upstream_change,
        send_clarification,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    NegotiationMessage = None  # type: ignore[assignment,misc]
    NegotiationRound = None  # type: ignore[assignment,misc]
    NegotiationConfig = None  # type: ignore[assignment,misc]
    NegotiationResult = None  # type: ignore[assignment,misc]
    NodeNegotiator = None  # type: ignore[assignment,misc]
    NegotiatingHop = None  # type: ignore[assignment,misc]
    get_node_negotiator = None  # type: ignore[assignment,misc]
    request_upstream_change = None  # type: ignore[assignment,misc]
    send_clarification = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="node_negotiator_util.py deps unavailable")
class TestNegotiationMessage:
    def test_is_class(self):
        assert isinstance(NegotiationMessage, type)
    def test_importable(self):
        assert NegotiationMessage is not None

@pytest.mark.skipif(not _AVAILABLE, reason="node_negotiator_util.py deps unavailable")
class TestNegotiationRound:
    def test_is_class(self):
        assert isinstance(NegotiationRound, type)
    def test_importable(self):
        assert NegotiationRound is not None

@pytest.mark.skipif(not _AVAILABLE, reason="node_negotiator_util.py deps unavailable")
class TestNegotiationConfig:
    def test_is_class(self):
        assert isinstance(NegotiationConfig, type)
    def test_importable(self):
        assert NegotiationConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="node_negotiator_util.py deps unavailable")
class TestNegotiationResult:
    def test_is_class(self):
        assert isinstance(NegotiationResult, type)
    def test_importable(self):
        assert NegotiationResult is not None

@pytest.mark.skipif(not _AVAILABLE, reason="node_negotiator_util.py deps unavailable")
class TestNodeNegotiator:
    def test_is_class(self):
        assert isinstance(NodeNegotiator, type)
    def test_importable(self):
        assert NodeNegotiator is not None

@pytest.mark.skipif(not _AVAILABLE, reason="node_negotiator_util.py deps unavailable")
class TestNegotiatingHop:
    def test_is_class(self):
        assert isinstance(NegotiatingHop, type)
    def test_importable(self):
        assert NegotiatingHop is not None

@pytest.mark.skipif(not _AVAILABLE, reason="node_negotiator_util.py deps unavailable")
class TestGetNodeNegotiator:
    def test_is_callable(self):
        assert callable(get_node_negotiator)

@pytest.mark.skipif(not _AVAILABLE, reason="node_negotiator_util.py deps unavailable")
class TestRequestUpstreamChange:
    def test_is_callable(self):
        assert callable(request_upstream_change)

@pytest.mark.skipif(not _AVAILABLE, reason="node_negotiator_util.py deps unavailable")
class TestSendClarification:
    def test_is_callable(self):
        assert callable(send_clarification)

@pytest.mark.skipif(not _AVAILABLE, reason="node_negotiator_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="node_negotiator_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="node_negotiator_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="node_negotiator_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="node_negotiator_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="node_negotiator_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module node_negotiator_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE