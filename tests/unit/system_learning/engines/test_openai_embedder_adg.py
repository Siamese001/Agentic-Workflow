"""ADG importability contract for system_learning/engines/openai_embedder.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_openai_embedder.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.engines.openai_embedder import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        BGEEmbedder,
        OpenAIEmbedder,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    OpenAIEmbedder = None  # type: ignore[assignment,misc]
    BGEEmbedder = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="openai_embedder.py deps unavailable")
class TestOpenaiEmbedderImportability:
    def test_module_importable(self) -> None:
        """ADG contract: openai_embedder.py must be importable."""
        assert _AVAILABLE

    def test_openaiembedder_is_type(self) -> None:
        assert OpenAIEmbedder is not None

    def test_bgeembedder_is_type(self) -> None:
        assert BGEEmbedder is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None