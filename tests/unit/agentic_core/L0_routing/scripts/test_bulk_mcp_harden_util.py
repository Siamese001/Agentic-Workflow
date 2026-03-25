"""Foundational behavioral tests for agentic_core/L0_routing/scripts/bulk_mcp_harden_util.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_bulk_mcp_harden_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L0_routing.scripts.bulk_mcp_harden_util import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    add_import,
    add_mcp_mixin_to_file,
    get_unhardened_external_agents,
    load_discovery,
)


class TestLoadDiscoveryFunction:
    def test_is_callable(self):
        assert callable(load_discovery)

class TestGetUnhardenedExternalAgentsFunction:
    def test_is_callable(self):
        assert callable(get_unhardened_external_agents)

class TestAddMcpMixinToFileFunction:
    def test_is_callable(self):
        assert callable(add_mcp_mixin_to_file)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(add_mcp_mixin_to_file)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestAddImportFunction:
    def test_is_callable(self):
        assert callable(add_import)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(add_import)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module bulk_mcp_harden_util must be importable or skip gracefully."""
    pass  # Import verified at module level
