"""BGE-M3 embedder wrapper for apps_qna interview card indexing.

Provides fail-soft embedding interface for the BAAI/bge-m3 model.
Output dimension: 1024
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Protocol

import numpy as np

from agentic_core.config.model_catalog import BGE_M3_MODEL_ID

_LOGGER = logging.getLogger(__name__)

# Model configuration
MODEL_NAME = BGE_M3_MODEL_ID
EXPECTED_DIMS = 1024
CACHE_DIR = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface"))


class EmbedderError(Exception):
    """Base exception for embedder failures."""

    pass


class EmbeddingModel(Protocol):
    """Protocol for embedding models."""

    def encode(
        self,
        sentences: str | list[str],
        *,
        normalize_embeddings: bool = True,
        show_progress_bar: bool = False,
    ) -> np.ndarray:
        """Encode sentences to embeddings."""
        ...


class BgeM3Embedder:
    """BGE-M3 embedder with fail-soft error handling.

    Attributes:
        model: The underlying sentence-transformers model (lazy-loaded)
        dims: Output dimension (1024 for BGE-M3)
        model_name: HuggingFace model identifier
    """

    _instance: BgeM3Embedder | None = None
    _model: EmbeddingModel | None = None

    def __new__(cls) -> BgeM3Embedder:
        """Singleton pattern to avoid reloading model."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.dims = EXPECTED_DIMS
            cls._instance.model_name = MODEL_NAME
        return cls._instance

    def _load_model(self) -> EmbeddingModel | None:
        """Lazy-load the BGE-M3 model.

        Returns:
            Loaded model or None if loading fails (fail-soft)
        """
        if self._model is not None:
            return self._model

        try:
            # Delay import until first use
            from sentence_transformers import SentenceTransformer  # noqa: PLC0415

            _LOGGER.info("Loading BGE-M3 model: %s", MODEL_NAME)
            self._model = SentenceTransformer(MODEL_NAME, cache_folder=str(CACHE_DIR))
            _LOGGER.info("BGE-M3 model loaded successfully")
            return self._model
        except ImportError:
            _LOGGER.error(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )
            return None
        except Exception as exc:  # noqa: BLE001 -- fail-soft by design
            _LOGGER.error("Failed to load BGE-M3 model: %s", exc)
            return None

    def embed(self, text: str) -> list[float]:
        """Embed a single text string.

        Args:
            text: Input text to embed

        Returns:
            1024-dimensional embedding vector, or empty list on failure (fail-soft)
        """
        model = self._load_model()
        if model is None:
            return []

        try:
            embedding = model.encode(
                text,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            return embedding.tolist()
        except Exception as exc:  # noqa: BLE001 -- fail-soft by design
            _LOGGER.warning("Embedding failed (fail-soft): %s", exc)
            return []

    def embed_batch(
        self,
        texts: list[str],
        *,
        batch_size: int = 32,
        show_progress: bool = True,
    ) -> list[list[float]]:
        """Embed multiple texts in batches.

        Args:
            texts: List of input texts
            batch_size: Batch size for encoding
            show_progress: Whether to show progress bar

        Returns:
            List of embedding vectors. Failed embeddings return as empty lists.
        """
        if not texts:
            return []

        model = self._load_model()
        if model is None:
            return [[] for _ in texts]

        try:
            embeddings = model.encode(
                texts,
                batch_size=batch_size,
                normalize_embeddings=True,
                show_progress_bar=show_progress,
            )
            return embeddings.tolist()
        except Exception as exc:  # noqa: BLE001 -- fail-soft by design
            _LOGGER.warning("Batch embedding failed (fail-soft): %s", exc)
            return [[] for _ in texts]

    def is_available(self) -> bool:
        """Check if the embedder is available (model can be loaded)."""
        return self._load_model() is not None


def get_embedder() -> BgeM3Embedder:
    """Get the singleton BGE-M3 embedder instance."""
    return BgeM3Embedder()


def embed_text(text: str) -> list[float]:
    """Convenience function: embed a single text.

    Args:
        text: Input text to embed

    Returns:
        1024-dimensional embedding vector, or empty list on failure
    """
    return get_embedder().embed(text)


def embed_texts(texts: list[str], **kwargs) -> list[list[float]]:
    """Convenience function: embed multiple texts.

    Args:
        texts: List of input texts
        **kwargs: Passed to embed_batch()

    Returns:
        List of embedding vectors
    """
    return get_embedder().embed_batch(texts, **kwargs)
