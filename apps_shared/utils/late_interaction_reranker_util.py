"""Late Interaction Reranker - SOTA Layer for Precise Document Ranking.

This component uses a Cross-Encoder to re-sort retrieved documents,
ensuring the most relevant context hits the LLM first.
"""

import logging
import time

logger = logging.getLogger(__name__)


class LateInteractionReranker:
    """Reranks documents using a Cross-Encoder for late interaction scoring.

    Uses a cross-encoder to examine every word interaction between query
    and document, providing superior ranking accuracy compared to bi-encoders.
    """

    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3", lazy_load: bool = True):
        """Initialize the Late Interaction Reranker.

        Args:
            model_name: Name of the cross-encoder model to use
            lazy_load: Whether to load model on first use (recommended)
        """
        self.model_name = model_name
        self.lazy_load = lazy_load
        self._model = None
        self._model_loaded = False
        self._fallback_mode = False

        logger.info(f"Initialized LateInteractionReranker: model={model_name}, lazy={lazy_load}")

    @property
    def is_available(self) -> bool:
        """Check if the reranker is available (model loaded or can be loaded)."""
        if self._model_loaded:
            return not self._fallback_mode
        if self._fallback_mode:
            return False
        # Try to check availability without loading
        try:
            from sentence_transformers import CrossEncoder  # noqa: F401

            return True
        except ImportError:
            logger.warning("sentence_transformers not available, reranker will be in fallback mode")
            return False

    def _load_model(self) -> bool:
        """Load the cross-encoder model.

        Returns:
            True if model loaded successfully, False if in fallback mode
        """
        if self._model_loaded:
            return not self._fallback_mode

        try:
            # Import sentence_transformers
            import torch  # noqa: F401
            from sentence_transformers import CrossEncoder

            logger.info(f"Loading CrossEncoder model: {self.model_name}")
            start_time = time.time()

            # Load the model
            self._model = CrossEncoder(self.model_name)

            load_time = time.time() - start_time
            logger.info(f"Model loaded in {load_time:.2f}s")

            self._model_loaded = True
            self._fallback_mode = False
            return True

        except ImportError as e:
            logger.error(f"Failed to import sentence_transformers: {e}")
            logger.warning("Reranker will operate in fallback mode (no reranking)")
            self._fallback_mode = True
            self._model_loaded = True  # Mark as loaded to avoid retrying
            return False
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {e}")
            logger.warning("Reranker will operate in fallback mode (no reranking)")
            self._fallback_mode = True
            self._model_loaded = True
            return False

    def rerank(
        self,
        query: str,
        documents: list[str],
        top_k: int | None = None,
        batch_size: int = 32,
    ) -> list[str]:
        """Rerank documents based on query relevance.

        Args:
            query: Query string
            documents: List of document texts to rank
            top_k: Number of top documents to return (None for all)
            batch_size: Batch size for model inference

        Returns:
            Reranked list of document texts
        """
        # Validate inputs
        if not query:
            logger.warning("Empty query provided, returning original documents")
            return documents[:top_k] if top_k else documents

        if not documents:
            logger.warning("No documents provided for reranking")
            return []

        # Load model if needed
        if not self._model_loaded:
            if not self._load_model():
                # Fallback mode: return original order
                logger.info("Reranker in fallback mode, returning original order")
                return documents[:top_k] if top_k else documents

        # Fallback mode check
        if self._fallback_mode:
            return documents[:top_k] if top_k else documents

        # Limit top_k to available documents
        if top_k is None:
            top_k = len(documents)
        else:
            top_k = min(top_k, len(documents))

        # Create query-document pairs
        pairs = [(query, doc) for doc in documents]

        try:
            # Score pairs in batches
            logger.debug(f"Reranking {len(documents)} documents")
            start_time = time.time()

            scores = self._model.predict(pairs, batch_size=batch_size, show_progress_bar=False)

            # Sort documents by score (descending)
            scored_docs = list(zip(documents, scores, strict=False))
            scored_docs.sort(key=lambda x: x[1], reverse=True)

            # Extract reranked documents
            reranked = [doc for doc, _ in scored_docs[:top_k]]

            elapsed = time.time() - start_time
            logger.debug(f"Reranking completed in {elapsed:.3f}s")

            # Log score distribution for monitoring
            if scores is not None and len(scores) > 0:
                score_stats = {
                    "min": float(min(scores)),
                    "max": float(max(scores)),
                    "mean": float(sum(scores) / len(scores)),
                }
                logger.debug(f"Score distribution: {score_stats}")

            return reranked

        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            # Fallback to original order
            logger.info("Falling back to original document order")
            return documents[:top_k]

    def rerank_with_scores(
        self,
        query: str,
        documents: list[str],
        top_k: int | None = None,
        batch_size: int = 32,
    ) -> list[tuple[str, float]]:
        """Rerank documents and return with scores.

        Args:
            query: Query string
            documents: List of document texts to rank
            top_k: Number of top documents to return (None for all)
            batch_size: Batch size for model inference

        Returns:
            List of (document, score) tuples sorted by score
        """
        # Validate inputs
        if not query or not documents:
            return []

        # Load model if needed
        if not self._model_loaded:
            if not self._load_model():
                # Fallback mode: return original order with dummy scores
                return [(doc, 0.0) for doc in (documents[:top_k] if top_k else documents)]

        # Fallback mode check
        if self._fallback_mode:
            return [(doc, 0.0) for doc in (documents[:top_k] if top_k else documents)]

        # Limit top_k
        if top_k is None:
            top_k = len(documents)
        else:
            top_k = min(top_k, len(documents))

        # Create pairs and score
        pairs = [(query, doc) for doc in documents]

        try:
            scores = self._model.predict(pairs, batch_size=batch_size, show_progress_bar=False)

            # Sort and return with scores
            scored_docs = list(zip(documents, scores, strict=False))
            scored_docs.sort(key=lambda x: x[1], reverse=True)

            return scored_docs[:top_k]

        except Exception as e:
            logger.error(f"Reranking with scores failed: {e}")
            return [(doc, 0.0) for doc in (documents[:top_k] if top_k else documents)]

    def get_model_info(self) -> dict:
        """Get information about the loaded model.

        Returns:
            Dictionary with model information
        """
        info = {
            "model_name": self.model_name,
            "loaded": self._model_loaded,
            "fallback_mode": self._fallback_mode,
            "available": self.is_available,
        }

        if self._model_loaded and not self._fallback_mode:
            # Try to get additional model info
            try:
                if hasattr(self._model, "config"):
                    info.update(
                        {
                            "max_seq_length": getattr(
                                self._model.config,
                                "max_position_embeddings",
                                "unknown",
                            ),
                            "num_labels": getattr(self._model.config, "num_labels", "unknown"),
                        },
                    )
            except Exception:
                pass

        return info


# Convenience function for direct usage
def rerank_documents(
    query: str,
    documents: list[str],
    model_name: str = "BAAI/bge-reranker-v2-m3",
    top_k: int = 5,
) -> list[str]:
    """Rerank documents using default settings.

    Args:
        query: Query string
        documents: List of document texts
        model_name: Model to use for reranking
        top_k: Number of top documents to return

    Returns:
        Reranked list of documents
    """
    reranker = LateInteractionReranker(model_name=model_name)
    return reranker.rerank(query, documents, top_k=top_k)


# Fallback pass-through reranker for when dependencies are missing
class PassThroughReranker:
    """Fallback reranker that returns documents in original order."""

    def __init__(self, *args, **kwargs):
        """Initialize the pass-through reranker."""
        logger.warning("Using PassThroughReranker - no actual reranking will be performed")

    def rerank(self, query: str, documents: list[str], top_k: int | None = None) -> list[str]:
        """Return documents in original order."""
        return documents[:top_k] if top_k else documents

    def rerank_with_scores(
        self,
        query: str,
        documents: list[str],
        top_k: int | None = None,
    ) -> list[tuple[str, float]]:
        """Return documents with dummy scores."""
        return [(doc, 0.0) for doc in (documents[:top_k] if top_k else documents)]
