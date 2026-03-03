"""Arbitration engine for deterministic multi-agent proposal selection."""

from __future__ import annotations

import hashlib
import json
import math
from typing import Sequence

from .types import ArbitrationCandidate, ArbitrationDecision, ArbitrationPolicy


class ArbitrationEngine:
    """Deterministic arbitration engine for multi-agent proposal selection."""

    def arbitrate(
        self,
        candidates: Sequence[ArbitrationCandidate],
        policy: ArbitrationPolicy,
    ) -> ArbitrationDecision:
        """Arbitrate between competing proposals deterministically."""

        # Validate inputs
        if candidates is None:
            raise TypeError("Candidates cannot be None")

        if not candidates:
            return ArbitrationDecision(
                winner_ids=(),
                merged_payload=None,
                rationale_codes=("no_candidates",),
                deterministic_fingerprint=self._compute_fingerprint((), None, ()),
            )

        # Check for duplicate IDs
        ids = [c.id for c in candidates]
        if len(ids) != len(set(ids)):
            raise ValueError(f"Duplicate candidate IDs detected: {[id for id in ids if ids.count(id) > 1]}")

        # Validate candidate fields
        for candidate in candidates:
            if math.isnan(candidate.score) or math.isinf(candidate.score):
                raise ValueError(f"Invalid score for candidate {candidate.id}: {candidate.score}")

            if candidate.kind not in policy.allowed_kinds:
                raise ValueError(f"Unknown kind '{candidate.kind}' for candidate {candidate.id}")

        # Filter candidates by minimum score threshold
        min_score = policy.thresholds.get("min_score", 0.0)
        valid_candidates = [c for c in candidates if c.score >= min_score]

        if not valid_candidates:
            return ArbitrationDecision(
                winner_ids=(),
                merged_payload=None,
                rationale_codes=("no_valid_candidates",),
                deterministic_fingerprint=self._compute_fingerprint((), None, ()),
            )

        # Apply kind weights to scores
        weighted_candidates = []
        for candidate in valid_candidates:
            weight = policy.weights.get(candidate.kind, 1.0)
            weighted_score = candidate.score * weight
            weighted_candidates.append((weighted_score, candidate))

        # Sort by total ordering:
        # 1. Primary: higher weighted score wins
        # 2. Secondary: lower cost wins (bounded cost comparison)
        # 3. Tertiary: stable kind ordering (alphabetical)
        # 4. Final: lexicographic ID (ensures total ordering)
        def sort_key(item):
            weighted_score, candidate = item
            return (
                -weighted_score,  # Negative for descending score
                candidate.cost,  # Lower cost is better
                candidate.kind,  # Alphabetical kind ordering
                candidate.id,  # Lexicographic ID for final tie-break
            )

        sorted_candidates = sorted(weighted_candidates, key=sort_key)

        # Select winners based on policy caps
        max_winners = policy.caps.get("max_winners", len(sorted_candidates))
        winners = sorted_candidates[:max_winners]
        winner_ids = tuple(candidate.id for _, candidate in winners)

        # Generate rationale codes
        rationale_codes = []
        if len(winners) < len(valid_candidates):
            rationale_codes.append("cap_applied")
        rationale_codes.append("weighted_scoring")

        # Create merged payload (simple concatenation for now)
        merged_payload = None
        if len(winners) > 1:
            merged_payload = {
                "merged_from": winner_ids,
                "individual_payloads": [candidate.payload for _, candidate in winners],
            }

        # Compute deterministic fingerprint
        fingerprint = self._compute_fingerprint(winner_ids, merged_payload, tuple(rationale_codes))

        return ArbitrationDecision(
            winner_ids=winner_ids,
            merged_payload=merged_payload,
            rationale_codes=tuple(rationale_codes),
            deterministic_fingerprint=fingerprint,
        )

    def _compute_fingerprint(
        self,
        winner_ids: tuple[str, ...],
        merged_payload: dict[str, Any] | None,
        rationale_codes: tuple[str, ...],
    ) -> str:
        """Compute deterministic fingerprint for the decision."""
        data = {
            "winner_ids": winner_ids,
            "merged_payload": merged_payload,
            "rationale_codes": rationale_codes,
        }
        canonical = json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")
        return hashlib.sha256(canonical).hexdigest()
