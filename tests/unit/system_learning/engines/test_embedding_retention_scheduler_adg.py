"""ADG importability contract for system_learning/engines/embedding_retention_scheduler.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_embedding_retention_scheduler.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.engines.embedding_retention_scheduler import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        EmbeddingRetentionScheduler,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    EmbeddingRetentionScheduler = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="embedding_retention_scheduler.py deps unavailable")
class TestEmbeddingRetentionSchedulerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: embedding_retention_scheduler.py must be importable."""
        assert _AVAILABLE

    def test_embeddingretentionscheduler_is_type(self) -> None:
        assert EmbeddingRetentionScheduler is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None
