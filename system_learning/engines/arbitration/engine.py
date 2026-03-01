"""ArbitrationEngine — deterministic winner selection from ranked candidates."""

from __future__ import annotations

import hashlib
import json

from system_learning.engines.arbitration.types import (
    ArbitrationCandidate,
    ArbitrationDecision,
    ArbitrationPolicy,
)


class ArbitrationEngine:
    """Select winning proposals deterministically per ArbitrationPolicy."""

    def arbitrate(
        self,
        candidates: list[ArbitrationCandidate],
        policy: ArbitrationPolicy,
    ) -> ArbitrationDecision:
        import math

        if not isinstance(candidates, list):
            raise TypeError(f"candidates must be a list, got {type(candidates).__name__}")
        if not isinstance(policy, ArbitrationPolicy):
            raise TypeError(f"policy must be ArbitrationPolicy, got {type(policy).__name__}")

        seen_ids: set[str] = set()
        for c in candidates:
            if not isinstance(c, ArbitrationCandidate):
                raise ValueError(f"each candidate must be ArbitrationCandidate, got {type(c).__name__}")
            if math.isnan(c.score) or math.isinf(c.score):
                raise ValueError(f"candidate '{c.id}' has non-finite score: {c.score}")
            if c.id in seen_ids:
                raise ValueError(f"duplicate candidate id: '{c.id}'")
            seen_ids.add(c.id)

        allowed = set(policy.allowed_kinds) if policy.allowed_kinds else None
        min_score = policy.thresholds.get("min_score", policy.min_score)
        max_winners = policy.caps.get("max_winners", policy.max_winners)

        eligible = [c for c in candidates if c.score >= min_score]
        if allowed is not None:
            ineligible_kinds = {c.kind for c in eligible if c.kind not in allowed}
            if ineligible_kinds:
                raise ValueError(f"candidate kind(s) not in allowed_kinds: {ineligible_kinds}")
            eligible = [c for c in eligible if c.kind in allowed]

        def _sort_key(c: ArbitrationCandidate) -> tuple:
            weight = policy.weights.get(c.kind, 1.0) if policy.weights else 1.0
            effective_score = c.score * weight
            return (-effective_score, c.cost, c.id)

        ranked = sorted(eligible, key=_sort_key)

        winners = ranked[:max_winners]
        winner_ids = tuple(w.id for w in winners)

        canonical = json.dumps(
            {
                "max_winners": max_winners,
                "min_score": min_score,
                "prefer_lower_cost": policy.prefer_lower_cost,
                "winner_ids": sorted(winner_ids),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        canonical_bytes = canonical.encode("ascii")
        digest = hashlib.sha256(canonical_bytes).hexdigest()

        return ArbitrationDecision(
            winner_ids=winner_ids,
            policy_digest=digest,
            deterministic_fingerprint=digest,
            canonical_bytes=canonical_bytes,
        )
