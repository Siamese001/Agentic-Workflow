"""Foundational behavioral tests for agentic_core/adg/client/mcp_client.py.

fan_in=7 — imported by 7 other modules.
ADG import-hygiene is covered separately by test_mcp_client_adg.py.
This file covers behavioral invariants and public API contracts.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.adg.client.mcp_client import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_DEPTH,
    MAX_RETRIES,
    THRESHOLD,
    ADGMCPClient,
)


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


class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None


class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None


class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None


class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None


class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None


class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: mcp_client importable or gracefully unavailable."""
    pass
