"""RAG Parameter Proposer — proposes retrieval-augmented generation parameter adjustments.

Analyzes retrieval quality metrics (recall, precision, top_k efficiency) and
proposes bounded adjustments to RAG parameters like similarity_cutoff and top_k.

All logic is pure and deterministic — no wall-clock reads, no randomness.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)
_LOW_RECALL_THRESHOLD = 0.6
_HIGH_NOISE_THRESHOLD = 0.4
_TOP_K_MIN = 3
_TOP_K_MAX = 20
_SIMILARITY_CUTOFF_MIN = 0.3
_SIMILARITY_CUTOFF_MAX = 0.95
_SIMILARITY_DELTA = 0.05
_MIN_OBSERVATIONS = 5


@dataclass(frozen=True, slots=True)
class RAGChangePackage:
    """Immutable RAG parameter adjustment proposal."""

    surface_name: str
    parameter: str
    old_value: float
    new_value: float
    justification: str
    snapshot_id: str

    def canonical_bytes(self) -> bytes:
        data = {
            "surface_name": self.surface_name,
            "parameter": self.parameter,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "justification": self.justification,
            "snapshot_id": self.snapshot_id,
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


class RAGParameterProposer:
    """Concrete RAG proposer conforming to the RAGProposer Protocol."""

    def propose(
        self, snapshot: Any, metrics: Any, config: Any, now_utc: int, history: Any, cooldown: Any, sample: Any
    ) -> RAGChangePackage | None:
        """Propose RAG parameter changes based on retrieval quality metrics.

        Parameters
        ----------
        metrics : dict
            Must contain ``"rag_recall"``, ``"rag_precision"``,
            ``"rag_observation_count"``, and optionally ``"rag_top_k"``
            and ``"rag_similarity_cutoff"``.
        config : dict
            Current RAG config with ``"similarity_cutoff"`` and ``"top_k"``.
        """
        if not isinstance(metrics, dict) or not isinstance(config, dict):
            return None
        recall = metrics.get("rag_recall", 1.0)
        precision = metrics.get("rag_precision", 1.0)
        n_obs = metrics.get("rag_observation_count", 0)
        if n_obs < _MIN_OBSERVATIONS:
            return None
        snapshot_id = getattr(snapshot, "snapshot_id", "unknown")
        current_cutoff = config.get("similarity_cutoff", 0.7)
        if recall < _LOW_RECALL_THRESHOLD:
            new_cutoff = max(current_cutoff - _SIMILARITY_DELTA, _SIMILARITY_CUTOFF_MIN)
            if new_cutoff != current_cutoff:
                return RAGChangePackage(
                    surface_name="rag_similarity_cutoff",
                    parameter="similarity_cutoff",
                    old_value=current_cutoff,
                    new_value=round(new_cutoff, 4),
                    justification=f"RAG recall {recall:.3f} < {_LOW_RECALL_THRESHOLD}; lowering cutoff from {current_cutoff} to {new_cutoff:.4f}",
                    snapshot_id=snapshot_id,
                )
        if precision < _HIGH_NOISE_THRESHOLD:
            new_cutoff = min(current_cutoff + _SIMILARITY_DELTA, _SIMILARITY_CUTOFF_MAX)
            if new_cutoff != current_cutoff:
                return RAGChangePackage(
                    surface_name="rag_similarity_cutoff",
                    parameter="similarity_cutoff",
                    old_value=current_cutoff,
                    new_value=round(new_cutoff, 4),
                    justification=f"RAG precision {precision:.3f} < {_HIGH_NOISE_THRESHOLD}; raising cutoff from {current_cutoff} to {new_cutoff:.4f}",
                    snapshot_id=snapshot_id,
                )
        return None


__all__ = ["RAGParameterProposer", "RAGChangePackage"]
