"""Behavioral tests for L4_state config dataclasses.

Covers:
- ledger_retention_config.LedgerRetentionConfig defaults + ledger_config singleton.
- memory_store_config.MemoryStoreConfig defaults + env-sourced STORAGE_ROOT.
- Module-level constants (MAX_RETRIES, THRESHOLD, …) have stable types.
"""

from __future__ import annotations

import importlib
from unittest.mock import patch

import pytest

from agentic_core.L4_state.config import (
    ledger_retention_config as ledger_mod,
    memory_store_config as memory_mod,
)
from agentic_core.L4_state.config.ledger_retention_config import (
    LedgerRetentionConfig,
    ledger_config,
)
from agentic_core.L4_state.config.memory_store_config import (
    MemoryStoreConfig,
    memory_config,
)


# ---- LedgerRetentionConfig ------------------------------------------

class TestLedgerRetentionConfig:
    def test_defaults(self) -> None:
        c = LedgerRetentionConfig()
        assert c.AUDIT_RETENTION_DAYS == 90
        assert c.ENABLE_HASH_CHAINING is True
        assert c.TRACE_SAMPLING_RATE == 1.0
        assert c.MAX_TRACE_DEPTH == 64
        assert c.TRACK_FILE_LINEAGE is True
        assert c.MAX_GENEALOGY_GENERATIONS == 20

    def test_singleton_instance_exists(self) -> None:
        assert isinstance(ledger_config, LedgerRetentionConfig)

    def test_is_dataclass(self) -> None:
        import dataclasses
        assert dataclasses.is_dataclass(LedgerRetentionConfig)

    def test_fields_are_overridable(self) -> None:
        c = LedgerRetentionConfig(AUDIT_RETENTION_DAYS=7)
        assert c.AUDIT_RETENTION_DAYS == 7


# ---- MemoryStoreConfig ----------------------------------------------

class TestMemoryStoreConfig:
    def test_vector_defaults(self) -> None:
        c = MemoryStoreConfig()
        assert c.VECTOR_DIMENSIONS == 1536
        assert c.VECTOR_METRIC == "cosine"

    def test_stm_defaults(self) -> None:
        c = MemoryStoreConfig()
        assert c.STM_TTL_SECONDS == 3600
        assert c.MAX_THOUGHTS_IN_CONTEXT == 50

    def test_checkpoint_defaults(self) -> None:
        c = MemoryStoreConfig()
        assert c.ENABLE_AUTO_CHECKPOINTS is True
        assert c.CHECKPOINT_INTERVAL_SECONDS == 300
        assert c.MAX_SNAPSHOTS_TO_RETAIN == 10

    def test_storage_root_from_env(self) -> None:
        # Module-level default reads the env var at import time — need reload
        with patch.dict("os.environ", {"L4_STORAGE_ROOT": "/custom/path"}):
            reloaded = importlib.reload(memory_mod)
            assert reloaded.MemoryStoreConfig().STORAGE_ROOT == "/custom/path"

    def test_singleton_instance_exists(self) -> None:
        assert isinstance(memory_config, MemoryStoreConfig)


# ---- Module-level constants ----------------------------------------

class TestModuleLevelConstants:
    @pytest.mark.parametrize("module", [ledger_mod, memory_mod])
    def test_max_retries_is_positive_int(self, module: object) -> None:
        assert isinstance(module.MAX_RETRIES, int)
        assert module.MAX_RETRIES > 0

    @pytest.mark.parametrize("module", [ledger_mod, memory_mod])
    def test_threshold_in_unit_range(self, module: object) -> None:
        assert 0 <= module.THRESHOLD <= 1

    @pytest.mark.parametrize("module", [ledger_mod, memory_mod])
    def test_default_timeout_positive(self, module: object) -> None:
        assert module.DEFAULT_TIMEOUT > 0
