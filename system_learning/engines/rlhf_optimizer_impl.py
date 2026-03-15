"""RLHF Optimizer Implementation — converts DPO batches into threshold proposals.

Concrete implementation of the ``RLHFOptimizer`` Protocol defined in
``system_learning/engines/rlhf_optimizer.py``.  Takes serialized DPO batch
data and produces threshold adjustment proposals based on preference signals.

All logic is pure and deterministic — no wall-clock reads, no randomness.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

logger = logging.getLogger(__name__)
_PREFERENCE_SIGNAL_THRESHOLD = 0.6
_MAX_DELTA = 0.05
_DEFAULT_DELTA = 0.02
_MIN_PAIRS = 3


@dataclass(frozen=True, slots=True)
class RLHFChangePackage:
    """Immutable RLHF-driven threshold change proposal."""

    surface_name: str
    parameter: str
    direction: str
    delta: float
    justification: str
    snapshot_id: str
    pair_count: int
    preference_strength: float

    def canonical_bytes(self) -> bytes:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RLHFChangePackage.canonical_bytes")

        data = {
            "surface_name": self.surface_name,
            "parameter": self.parameter,
            "direction": self.direction,
            "delta": self.delta,
            "justification": self.justification,
            "snapshot_id": self.snapshot_id,
            "pair_count": self.pair_count,
            "preference_strength": self.preference_strength,
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


class DefaultRLHFOptimizer:
    """Concrete RLHF optimizer conforming to the RLHFOptimizer Protocol.

    Analyzes DPO pair batches to determine if human preferences indicate
    a systematic direction for threshold adjustments.
    """

    def propose_from_dpo(
        self, dpo_batch_bytes: bytes, snapshot_id: str = "unknown"
    ) -> RLHFChangePackage | None:
        """Propose threshold changes from DPO preference pairs.

        Parameters
        ----------
        dpo_batch_bytes : bytes
            JSON-serialized DPO batch.  Expected structure::

                {
                    "pairs": [
                        {"chosen": {...}, "rejected": {...}, "surface": "..."},
                        ...
                    ]
                }
        snapshot_id : str
            Pipeline snapshot ID.

        Returns
        -------
        RLHFChangePackage | None
            Proposal or None if preferences are weak/insufficient.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "DefaultRLHFOptimizer.propose_from_dpo")

        try:
            batch = json.loads(dpo_batch_bytes.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            logger.debug("Failed to decode DPO batch bytes")
            return None
        pairs = batch.get("pairs", [])
        if len(pairs) < _MIN_PAIRS:
            return None
        surface_votes: dict[str, list[str]] = {}
        for pair in pairs:
            surface = pair.get("surface", "unknown")
            chosen = pair.get("chosen", {})
            rejected = pair.get("rejected", {})
            chosen_val = chosen.get("threshold", 0.0)
            rejected_val = rejected.get("threshold", 0.0)
            if chosen_val > rejected_val:
                direction = "increase"
            elif chosen_val < rejected_val:
                direction = "decrease"
            else:
                continue
            if surface not in surface_votes:
                surface_votes[surface] = []
            surface_votes[surface].append(direction)
        best_surface = None
        best_strength = 0.0
        best_direction = "increase"
        for surface, votes in surface_votes.items():
            if not votes:
                continue
            increase_count = sum(1 for v in votes if v == "increase")
            decrease_count = len(votes) - increase_count
            total = len(votes)
            if increase_count >= decrease_count:
                strength = increase_count / total
                direction = "increase"
            else:
                strength = decrease_count / total
                direction = "decrease"
            if strength > best_strength and total >= _MIN_PAIRS:
                best_strength = strength
                best_direction = direction
                best_surface = surface
        if best_surface is None or best_strength < _PREFERENCE_SIGNAL_THRESHOLD:
            return None
        delta = min(_DEFAULT_DELTA, _MAX_DELTA)
        return RLHFChangePackage(
            surface_name=best_surface,
            parameter="threshold",
            direction=best_direction,
            delta=delta,
            justification=f"DPO analysis of {len(pairs)} pairs shows {best_strength:.1%} preference to {best_direction} '{best_surface}' threshold",
            snapshot_id=snapshot_id,
            pair_count=len(pairs),
            preference_strength=round(best_strength, 4),
        )


__all__ = ["DefaultRLHFOptimizer", "RLHFChangePackage"]
