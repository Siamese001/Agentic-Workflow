"""meta_learning_replay_binding — Replay key binding struct for meta-learning state.

Encapsulates the three digest components required for deterministic replay:
  - FAISS index digests (per-index W-A-DETERMINISM-DIGEST values)
  - strategy_weights_digest (from MetaLearningAgent.strategy_weights_digest)
  - embedding_model_version (runtime model identifier string)

A replay run that loads from a persisted state must present an identical
``MetaLearningReplayBinding`` to confirm it started from the same learned
state as the original run.

Usage::

    from system_learning.engines.meta_learning_replay_binding import (
        MetaLearningReplayBinding,
    )

    binding = MetaLearningReplayBinding(
        faiss_index_digests={"healing_contexts_v1": store.persist_to_disk(...)},
        strategy_weights_digest=agent.strategy_weights_digest,
        embedding_model_version="BAAI/bge-m3-v1",
    )
    binding.emit()            # prints REPLAY-BINDING line to stdout
    line = binding.to_line()  # "REPLAY-BINDING: <json>"
"""

from __future__ import annotations

import json
from dataclasses import dataclass


@dataclass(frozen=True)
class MetaLearningReplayBinding:
    """Immutable binding of all digest components needed for replay verification.

    All three fields are required.  The binding is emitted as a single
    ``REPLAY-BINDING: <json>`` line to stdout and can be re-parsed and compared
    by a replay runner to verify identical initialisation state.

    Attributes:
        faiss_index_digests: Mapping of index_id -> W-A-DETERMINISM-DIGEST hex.
                             Must contain at least one entry.
        strategy_weights_digest: SHA-256 hex of current MetaLearningAgent weights.
        embedding_model_version: Runtime embedding model identifier string.
    """

    faiss_index_digests: dict[str, str]
    strategy_weights_digest: str
    embedding_model_version: str

    def __post_init__(self) -> None:
        if not self.faiss_index_digests:
            raise ValueError("faiss_index_digests must contain at least one entry")
        if len(self.strategy_weights_digest) != 64:
            raise ValueError(
                f"strategy_weights_digest must be 64-hex chars, got {len(self.strategy_weights_digest)}"
            )
        if not self.embedding_model_version:
            raise ValueError("embedding_model_version must be a non-empty string")

    def to_dict(self) -> dict[str, object]:
        """Return a canonical dict representation (keys sorted)."""
        return {
            "embedding_model_version": self.embedding_model_version,
            "faiss_index_digests": dict(sorted(self.faiss_index_digests.items())),
            "strategy_weights_digest": self.strategy_weights_digest,
        }

    def to_line(self) -> str:
        """Serialise to the canonical ``REPLAY-BINDING: <json>`` log line."""
        payload = json.dumps(self.to_dict(), separators=(",", ":"), sort_keys=True, ensure_ascii=True)
        return f"REPLAY-BINDING: {payload}"

    def emit(self) -> None:
        """Print the canonical REPLAY-BINDING line to stdout exactly once."""
        print(self.to_line())

    @classmethod
    def from_line(cls, line: str) -> MetaLearningReplayBinding:
        """Parse a ``REPLAY-BINDING: <json>`` line back into a binding object.

        Raises:
            ValueError: If the line is not a valid REPLAY-BINDING line or
                        the JSON payload is missing required keys.
        """
        prefix = "REPLAY-BINDING: "
        if not line.startswith(prefix):
            raise ValueError(f"Not a REPLAY-BINDING line: {line!r}")
        raw = json.loads(line[len(prefix) :])
        missing = {"faiss_index_digests", "strategy_weights_digest", "embedding_model_version"} - raw.keys()
        if missing:
            raise ValueError(f"REPLAY-BINDING missing keys: {sorted(missing)}")
        return cls(
            faiss_index_digests=raw["faiss_index_digests"],
            strategy_weights_digest=raw["strategy_weights_digest"],
            embedding_model_version=raw["embedding_model_version"],
        )


__all__ = ["MetaLearningReplayBinding"]
