"""L2.3 Meta-Prior Provider Port — seam for injecting live success-rate priors.

This port is the ONLY allowed path for meta-learning data to enter the
heal-time routing computation. It is read-only from the perspective of L2.3.

Contracts:
- get_prior() MUST be synchronous and deterministic given the same store state.
- Returns float in [0.0, 1.0].  Default neutral prior = 0.50.
- NO side effects. NO writes. NO imports of L4 state directly.
"""

from __future__ import annotations

from typing import Protocol

_NEUTRAL_PRIOR: float = 0.5


class MetaPriorProvider(Protocol):
    """Read-only seam for retrieving heal-time meta-learning priors."""

    def get_prior(self, error_signature: str) -> float:
        """Return historical success rate prior for error_signature.

        Parameters
        ----------
        error_signature : str
            Deterministic error class identifier from HealingInput.

        Returns
        -------
        float
            Prior in [0.0, 1.0].  Returns _NEUTRAL_PRIOR if unknown.
        """
        ...


class NeutralMetaPriorProvider:
    """Fallback provider that always returns the neutral prior.

    Used when no L4-backed store is available (e.g., cold start, test isolation).
    """

    def get_prior(self, error_signature: str) -> float:
        return _NEUTRAL_PRIOR


__all__ = ["MetaPriorProvider", "NeutralMetaPriorProvider", "_NEUTRAL_PRIOR"]
