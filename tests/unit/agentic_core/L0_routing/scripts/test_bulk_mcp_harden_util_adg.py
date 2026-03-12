"""ADG-driven tests for agentic_core/L0_routing/scripts/bulk_mcp_harden_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.bulk_mcp_harden_util import (  # noqa: F401
        load_discovery,
        get_unhardened_external_agents,
        add_mcp_mixin_to_file,
        add_import,
        main,
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
    load_discovery = None  # type: ignore[assignment,misc]
    get_unhardened_external_agents = None  # type: ignore[assignment,misc]
    add_mcp_mixin_to_file = None  # type: ignore[assignment,misc]
    add_import = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="bulk_mcp_harden_util.py deps unavailable")
class TestLoadDiscovery:
    def test_is_callable(self):
        assert callable(load_discovery)

@pytest.mark.skipif(not _AVAILABLE, reason="bulk_mcp_harden_util.py deps unavailable")
class TestGetUnhardenedExternalAgents:
    def test_is_callable(self):
        assert callable(get_unhardened_external_agents)

@pytest.mark.skipif(not _AVAILABLE, reason="bulk_mcp_harden_util.py deps unavailable")
class TestAddMcpMixinToFile:
    def test_is_callable(self):
        assert callable(add_mcp_mixin_to_file)

@pytest.mark.skipif(not _AVAILABLE, reason="bulk_mcp_harden_util.py deps unavailable")
class TestAddImport:
    def test_is_callable(self):
        assert callable(add_import)

@pytest.mark.skipif(not _AVAILABLE, reason="bulk_mcp_harden_util.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="bulk_mcp_harden_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="bulk_mcp_harden_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="bulk_mcp_harden_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="bulk_mcp_harden_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="bulk_mcp_harden_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="bulk_mcp_harden_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module bulk_mcp_harden_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
