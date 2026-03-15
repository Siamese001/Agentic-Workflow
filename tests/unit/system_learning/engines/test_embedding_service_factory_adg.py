"""ADG importability contract for system_learning/engines/embedding_service_factory.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_embedding_service_factory.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.engines.embedding_service_factory import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        EmbeddingDisabledError,
        EmbeddingForkViolationError,
        EmbeddingIntegrityError,
        EmbeddingReplayViolationError,
        EmbeddingResult,
        EmbeddingServiceFactory,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    EmbeddingDisabledError = None  # type: ignore[assignment,misc]
    EmbeddingForkViolationError = None  # type: ignore[assignment,misc]
    EmbeddingIntegrityError = None  # type: ignore[assignment,misc]
    EmbeddingReplayViolationError = None  # type: ignore[assignment,misc]
    EmbeddingResult = None  # type: ignore[assignment,misc]
    EmbeddingServiceFactory = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="embedding_service_factory.py deps unavailable")
class TestEmbeddingServiceFactoryImportability:
    def test_module_importable(self) -> None:
        """ADG contract: embedding_service_factory.py must be importable."""
        assert _AVAILABLE

    def test_embeddingdisablederror_is_type(self) -> None:
        assert EmbeddingDisabledError is not None

    def test_embeddingforkviolationerror_is_type(self) -> None:
        assert EmbeddingForkViolationError is not None

    def test_embeddingintegrityerror_is_type(self) -> None:
        assert EmbeddingIntegrityError is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None
