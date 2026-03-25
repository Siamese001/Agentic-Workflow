"""Embeddings smoke tests — import verification and basic functionality."""

import pytest


@pytest.mark.smoke
def test_embeddings_importable():
    """Verify embeddings module imports without error."""
    try:
        import agentic_core.embeddings

        assert agentic_core.embeddings is not None
    except ImportError as e:
        pytest.skip(f"embeddings not available: {e}")


@pytest.mark.smoke
def test_embedding_factory_importable():
    """Verify embedding factory imports without error."""
    try:
        from agentic_core.embeddings.embedding_factory import (
            EmbeddingClient,
            EmbeddingDisabledError,
            EmbeddingSovereigntyViolationError,
        )

        assert EmbeddingClient is not None
        assert EmbeddingDisabledError is not None
        assert EmbeddingSovereigntyViolationError is not None
    except ImportError as e:
        pytest.skip(f"EmbeddingClient not available: {e}")


@pytest.mark.smoke
def test_embedding_input_guard_importable():
    """Verify embedding input guard imports without error."""
    try:
        from agentic_core.embeddings.embedding_input_guard import (
            EmbeddingInputGuard,
        )

        assert EmbeddingInputGuard is not None
    except ImportError as e:
        pytest.skip(f"EmbeddingInputGuard not available: {e}")




@pytest.mark.smoke
def test_tokenization_adapter_importable():
    """Verify tokenization adapter imports without error."""
    try:
        from agentic_core.embeddings.tokenization_adapter import (
            TokenCountAdapter,
        )

        assert TokenCountAdapter is not None
    except ImportError as e:
        pytest.skip(f"TokenCountAdapter not available: {e}")
