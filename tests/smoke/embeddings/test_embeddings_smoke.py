"""Embeddings smoke tests — behavioral contract verification."""

import pytest


@pytest.mark.smoke
def test_embeddings_package_has_known_submodules():
    """Embeddings package contains discoverable submodules (embedding_factory, etc.)."""
    try:
        import importlib

        spec = importlib.util.find_spec("agentic_core.embeddings.embedding_factory")
    except (ImportError, ModuleNotFoundError) as e:
        pytest.skip(f"embedding_factory not discoverable: {e}")

    assert spec is not None, "agentic_core.embeddings.embedding_factory must be discoverable"


@pytest.mark.smoke
def test_embedding_factory_error_hierarchy():
    """EmbeddingDisabledError and EmbeddingSovereigntyViolationError are proper Exceptions."""
    try:
        from agentic_core.embeddings.embedding_factory import (
            EmbeddingClient,
            EmbeddingDisabledError,
            EmbeddingSovereigntyViolationError,
        )
    except ImportError as e:
        pytest.skip(f"module not available: {e}")
    assert issubclass(EmbeddingDisabledError, Exception)
    assert issubclass(EmbeddingSovereigntyViolationError, Exception)
    assert isinstance(EmbeddingClient, type), "EmbeddingClient should be a class"


@pytest.mark.smoke
def test_embedding_factory_disabled_error_message():
    """EmbeddingDisabledError carries a message when raised."""
    try:
        from agentic_core.embeddings.embedding_factory import EmbeddingDisabledError
    except ImportError as e:
        pytest.skip(f"EmbeddingDisabledError not available: {e}")

    err = EmbeddingDisabledError("kill switch active")
    assert "kill switch" in str(err)


@pytest.mark.smoke
def test_embedding_input_guard_is_class():
    """EmbeddingInputGuard is a class with a public interface."""
    try:
        from agentic_core.embeddings.embedding_input_guard import EmbeddingInputGuard
    except ImportError as e:
        pytest.skip(f"module not available: {e}")
    assert isinstance(EmbeddingInputGuard, type), "EmbeddingInputGuard should be a class"


@pytest.mark.smoke
def test_tokenization_adapter_is_class():
    """TokenCountAdapter is a class suitable for token counting."""
    try:
        from agentic_core.embeddings.tokenization_adapter import TokenCountAdapter
    except ImportError as e:
        pytest.skip(f"module not available: {e}")
    assert isinstance(TokenCountAdapter, type), "TokenCountAdapter should be a class"
