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

import hashlib
import json
from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


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
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "MetaLearningReplayBinding.to_line")

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


def compute_replay_key(
    *, trace_id: str, transcript_hash: str, strategy_weights_digest: str, faiss_index_digests: dict[str, str]
) -> str:
    """Compute a deterministic replay key binding all execution-state digests.

    The replay key is the SHA-256 of the pipe-concatenated canonical components:

        trace_id | transcript_hash | strategy_weights_digest | <sorted faiss digests>

    FAISS index digests are sorted by ``index_id`` before concatenation so the
    result is independent of insertion order.

    Args:
        trace_id: Unique trace/run identifier (e.g. UUID or timestamp string).
        transcript_hash: SHA-256 hex of the raw replay transcript bytes.
        strategy_weights_digest: SHA-256 hex from MetaLearningAgent.strategy_weights_digest.
        faiss_index_digests: Mapping of index_id -> W-A-DETERMINISM-DIGEST hex.
                             Must contain at least one entry.

    Returns:
        64-char lowercase hex SHA-256 replay key.

    Raises:
        ValueError: If faiss_index_digests is empty or any digest is not 64 hex chars.
    """
    if not faiss_index_digests:
        raise ValueError("faiss_index_digests must contain at least one entry")
    if len(strategy_weights_digest) != 64:
        raise ValueError(f"strategy_weights_digest must be 64-hex chars, got {len(strategy_weights_digest)}")
    sorted_faiss = "|".join((f"{k}:{v}" for k, v in sorted(faiss_index_digests.items())))
    binding = json.dumps(
        {
            "faiss_index_digests_sorted": sorted_faiss,
            "strategy_weights_digest": strategy_weights_digest,
            "trace_id": trace_id,
            "transcript_hash": transcript_hash,
        },
        separators=(",", ":"),
        sort_keys=True,
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(binding).hexdigest()


__all__ = ["MetaLearningReplayBinding", "compute_replay_key"]
