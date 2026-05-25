"""Embedding registry - placeholder for test compatibility."""


class EmbeddingRegistry:
    """Placeholder embedding registry class."""

    def register(self, name, embedder):
        """Placeholder register method."""
        pass


def register_embedding(name, embedder):
    """Placeholder register embedding function."""
    pass


EMBEDDING_REGISTRY = {}


def register_embedder(name: str, embedder):
    """Register an embedder."""
    EMBEDDING_REGISTRY[name] = embedder
    return embedder
