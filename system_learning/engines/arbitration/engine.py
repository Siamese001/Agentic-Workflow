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
        eligible = [c for c in candidates if c.score >= policy.min_score]

        if policy.prefer_lower_cost:
            ranked = sorted(eligible, key=lambda c: (-c.score, c.cost, c.id))
        else:
            ranked = sorted(eligible, key=lambda c: (-c.score, c.id))

        winners = ranked[: policy.max_winners]
        winner_ids = [w.id for w in winners]

        policy_canonical = json.dumps(
            {
                "max_winners": policy.max_winners,
                "min_score": policy.min_score,
                "prefer_lower_cost": policy.prefer_lower_cost,
                "winner_ids": sorted(winner_ids),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        policy_digest = hashlib.sha256(policy_canonical.encode("ascii")).hexdigest()

        return ArbitrationDecision(winner_ids=winner_ids, policy_digest=policy_digest)
