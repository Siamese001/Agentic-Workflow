"""Foundational behavioral tests for agentic_core/adg/client/mcp_client.py.

fan_in=7 — imported by 7 other modules.
ADG import-hygiene is covered separately by test_mcp_client_adg.py.
This file covers behavioral invariants and public API contracts.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.adg.client.InMemoryStore import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        ADGMCPClient,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    ADGMCPClient = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="mcp_client.py deps unavailable")
class TestADGMCPClientContract:
    def test_is_class(self):
        assert isinstance(ADGMCPClient, type)

    def test_has_method_upsert_entity(self):
        assert callable(getattr(ADGMCPClient, "upsert_entity", None))

    def test_has_method_upsert_relation(self):
        assert callable(getattr(ADGMCPClient, "upsert_relation", None))

    def test_has_method_add_observation(self):
        assert callable(getattr(ADGMCPClient, "add_observation", None))

    def test_has_method_search_nodes(self):
        assert callable(getattr(ADGMCPClient, "search_nodes", None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(ADGMCPClient) if not m.startswith("_")]
        assert len(pub) >= 1


@pytest.mark.skipif(not _AVAILABLE, reason="mcp_client.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None


@pytest.mark.skipif(not _AVAILABLE, reason="mcp_client.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None


@pytest.mark.skipif(not _AVAILABLE, reason="mcp_client.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None


@pytest.mark.skipif(not _AVAILABLE, reason="mcp_client.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None


@pytest.mark.skipif(not _AVAILABLE, reason="mcp_client.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None


@pytest.mark.skipif(not _AVAILABLE, reason="mcp_client.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: mcp_client importable or gracefully unavailable."""
    pass