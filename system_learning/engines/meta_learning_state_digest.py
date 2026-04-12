"""meta_learning_state_digest — Combined determinism digest for meta-learning state.

Combines FAISS index digests, strategy-weights digest, and embedding model version
into a single ``META_LEARNING_STATE_DIGEST`` that is stable across two identical
runs and can be bound into replay transcripts (h3, h5).

Usage::

    from system_learning.engines.meta_learning_state_digest import (
        compute_meta_learning_state_digest,
    )

    digest = compute_meta_learning_state_digest(
        faiss_index_digests={"healing_contexts_v1": "<hex>", ...},
        strategy_weights_digest="<hex>",
        embedding_model_version="BAAI/bge-m3-v1",
    )
    print(f"META_LEARNING_STATE_DIGEST: {digest}")

The returned digest is a 64-hex SHA-256 string.  The function is deterministic:
identical inputs always produce the identical output.
"""

from __future__ import annotations

import hashlib
import json


def compute_meta_learning_state_digest(
    *,
    faiss_index_digests: dict[str, str],
    strategy_weights_digest: str,
    embedding_model_version: str,
) -> str:
    """Compute a single deterministic digest covering the full meta-learning state.

    Args:
        faiss_index_digests: Mapping of index_id -> W-A-DETERMINISM-DIGEST (64-hex)
                             as returned by ``LocalFAISSStore.persist_to_disk()``.
                             The dict must contain at least one entry.
        strategy_weights_digest: SHA-256 hex digest of the current strategy weights
                                 as returned by ``MetaLearningAgent.strategy_weights_digest``.
        embedding_model_version: Runtime embedding model version string
                                 (e.g. ``"BAAI/bge-m3-v1"`` or ``"hash-fallback-v1"``).

    Returns:
        64-char lowercase hex SHA-256 digest.  Print as::

            META_LEARNING_STATE_DIGEST: <digest>

    Raises:
        ValueError: If ``faiss_index_digests`` is empty.
    """
    if not faiss_index_digests:
        raise ValueError("faiss_index_digests must contain at least one entry")
    binding = json.dumps(
        {
            "embedding_model_version": embedding_model_version,
            "faiss_index_digests": dict(sorted(faiss_index_digests.items())),
            "strategy_weights_digest": strategy_weights_digest,
        },
        separators=(",", ":"),
        sort_keys=True,
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(binding).hexdigest()


def emit_meta_learning_state_digest(
    *,
    faiss_index_digests: dict[str, str],
    strategy_weights_digest: str,
    embedding_model_version: str,
) -> str:
    """Compute and print ``META_LEARNING_STATE_DIGEST`` to stdout.

    Wrapper around :func:`compute_meta_learning_state_digest` that also prints
    the result in the canonical format expected by the determinism proof standard.
    The digest is printed exactly once per call.

    Returns:
        The 64-hex digest string (same as the printed value).
    """
    digest = compute_meta_learning_state_digest(
        faiss_index_digests=faiss_index_digests,
        strategy_weights_digest=strategy_weights_digest,
        embedding_model_version=embedding_model_version,
    )
    print(f"META_LEARNING_STATE_DIGEST: {digest}")
    return digest


__all__ = ["compute_meta_learning_state_digest", "emit_meta_learning_state_digest"]
