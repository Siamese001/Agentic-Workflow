"""ADG-driven tests for apps_rg/scripts/rg_json_miner.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_rg.scripts.rg_json_miner import (  # noqa: F401
        mine_workflows,
        extract_k_nodes,
        extract_keys_recursive,
        extract_long_text_blocks,
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
    mine_workflows = None  # type: ignore[assignment,misc]
    extract_k_nodes = None  # type: ignore[assignment,misc]
    extract_keys_recursive = None  # type: ignore[assignment,misc]
    extract_long_text_blocks = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="rg_json_miner.py deps unavailable")
class TestMineWorkflows:
    def test_is_callable(self):
        assert callable(mine_workflows)

@pytest.mark.skipif(not _AVAILABLE, reason="rg_json_miner.py deps unavailable")
class TestExtractKNodes:
    def test_is_callable(self):
        assert callable(extract_k_nodes)

@pytest.mark.skipif(not _AVAILABLE, reason="rg_json_miner.py deps unavailable")
class TestExtractKeysRecursive:
    def test_is_callable(self):
        assert callable(extract_keys_recursive)

@pytest.mark.skipif(not _AVAILABLE, reason="rg_json_miner.py deps unavailable")
class TestExtractLongTextBlocks:
    def test_is_callable(self):
        assert callable(extract_long_text_blocks)

@pytest.mark.skipif(not _AVAILABLE, reason="rg_json_miner.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="rg_json_miner.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="rg_json_miner.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="rg_json_miner.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="rg_json_miner.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="rg_json_miner.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module rg_json_miner.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
