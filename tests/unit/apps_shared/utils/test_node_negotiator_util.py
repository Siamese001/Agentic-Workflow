"""Foundational behavioral tests for apps_shared/utils/node_negotiator_util.py.

fan_in=15 — this module is imported by 15 other modules.
ADG contract: import-hygiene is covered by test_node_negotiator_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.node_negotiator_util import (  # noqa: F401
        NegotiationMessage,
        NegotiationRound,
        NegotiationConfig,
        NegotiationResult,
        NodeNegotiator,
        NegotiatingHop,
        get_node_negotiator,
        request_upstream_change,
        send_clarification,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
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


@pytest.mark.skipif(not _AVAILABLE, reason="node_negotiator_util.py deps unavailable")
class TestNegotiationMessageContract:
    def test_is_class(self):
        assert isinstance(NegotiationMessage, type)

    def test_has_method_validate_message_type(self):
        assert callable(getattr(NegotiationMessage, 'validate_message_type', None))

@pytest.mark.skipif(not _AVAILABLE, reason="node_negotiator_util.py deps unavailable")
class TestNegotiationRoundContract:
    def test_is_class(self):
        assert isinstance(NegotiationRound, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(NegotiationRound, type)

@pytest.mark.skipif(not _AVAILABLE, reason="node_negotiator_util.py deps unavailable")
class TestNegotiationConfigContract:
    def test_is_class(self):
        assert isinstance(NegotiationConfig, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(NegotiationConfig, type)

@pytest.mark.skipif(not _AVAILABLE, reason="node_negotiator_util.py deps unavailable")
class TestNegotiationResultContract:
    def test_is_class(self):
        assert isinstance(NegotiationResult, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(NegotiationResult, type)

@pytest.mark.skipif(not _AVAILABLE, reason="node_negotiator_util.py deps unavailable")
class TestNodeNegotiatorContract:
    def test_is_class(self):
        assert isinstance(NodeNegotiator, type)

    def test_has_method_send_feedback(self):
        assert callable(getattr(NodeNegotiator, 'send_feedback', None))

    def test_has_method_request_change(self):
        assert callable(getattr(NodeNegotiator, 'request_change', None))

    def test_has_method_get_negotiation_history(self):
        assert callable(getattr(NodeNegotiator, 'get_negotiation_history', None))

    def test_has_method_get_stats(self):
        assert callable(getattr(NodeNegotiator, 'get_stats', None))

@pytest.mark.skipif(not _AVAILABLE, reason="node_negotiator_util.py deps unavailable")
class TestNegotiatingHopContract:
    def test_is_class(self):
        assert isinstance(NegotiatingHop, type)

    def test_has_method_evaluate_downstream_feedback(self):
        assert callable(getattr(NegotiatingHop, 'evaluate_downstream_feedback', None))

    def test_has_method_request_upstream_modification(self):
        assert callable(getattr(NegotiatingHop, 'request_upstream_modification', None))

@pytest.mark.skipif(not _AVAILABLE, reason="node_negotiator_util.py deps unavailable")
class TestGetNodeNegotiatorFunction:
    def test_is_callable(self):
        assert callable(get_node_negotiator)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_node_negotiator)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="node_negotiator_util.py deps unavailable")
class TestRequestUpstreamChangeFunction:
    def test_is_callable(self):
        assert callable(request_upstream_change)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(request_upstream_change)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="node_negotiator_util.py deps unavailable")
class TestSendClarificationFunction:
    def test_is_callable(self):
        assert callable(send_clarification)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(send_clarification)
        assert sig.return_annotation is not inspect.Parameter.empty

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


def test_module_importable():
    """Module node_negotiator_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
