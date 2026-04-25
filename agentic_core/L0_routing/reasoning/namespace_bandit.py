"""Per-namespace Thompson-sampling bandit for R1B / R3 threshold tuning.

Plan: ``.windsurf/plans/routing-decision-process-enhancement-9c7e4d.md`` Wave W4.

Replaces the single global ``similarity_threshold=0.98`` and the global
abstain floor for R3 with per-namespace, per-route Beta-Bernoulli posteriors
that the router samples from on every dispatch. Closes opportunity 1.1
(per-namespace threshold map) and 1.2 (bandit over admissible routes) from
the routing-enhancement opportunity register.

Design:

1. **Beta-Bernoulli posterior per (namespace, route)**. Conjugate update is
   trivially numerically stable, no sklearn / numpy floor.
2. **Thompson sampling** for action selection — sample from each arm's
   posterior, pick argmax. Asymptotically regret-optimal under stationary
   reward.
3. **Persistence-free at write time** — the bandit is updated on every
   ``backfill_outcome`` event by reading the row from ``decision_events``;
   the in-process posterior is rebuilt at startup from the table.
4. **Fail-soft**. Empty posteriors → uniform Beta(1, 1) prior → bandit
   degrades to random pick from admissible routes, never raises.
"""

from __future__ import annotations

import random
import sqlite3
import threading
from dataclasses import dataclass, field


@dataclass(frozen=True)
class BanditKey:
    """Unique posterior identifier."""

    namespace: str
    route: str


@dataclass
class BetaPosterior:
    """Conjugate Beta(alpha, beta) over Bernoulli success rate."""

    alpha: float = 1.0
    beta: float = 1.0

    def update(self, success: bool) -> None:
        if success:
            self.alpha += 1.0
        else:
            self.beta += 1.0

    def sample(self, rng: random.Random) -> float:
        """Draw a single sample from Beta(alpha, beta)."""
        # Use random.betavariate (deterministic when seeded).
        return rng.betavariate(self.alpha, self.beta)

    @property
    def mean(self) -> float:
        return self.alpha / (self.alpha + self.beta)

    @property
    def n_observations(self) -> int:
        return int(self.alpha + self.beta - 2.0)


class NamespaceBandit:
    """Thread-safe per-namespace Thompson bandit.

    Usage:
        bandit = NamespaceBandit(seed=42)
        bandit.update("legal", "R3", success=True)
        bandit.update("legal", "R1B", success=False)
        chosen = bandit.choose("legal", admissible=["R1B", "R3", "R5"])
    """

    def __init__(self, seed: int | None = None) -> None:
        self._posteriors: dict[BanditKey, BetaPosterior] = {}
        self._lock = threading.Lock()
        self._rng = random.Random(seed)

    def update(self, namespace: str, route: str, *, success: bool) -> None:
        """Update posterior for ``(namespace, route)`` with Bernoulli outcome."""
        key = BanditKey(namespace=namespace, route=route)
        with self._lock:
            posterior = self._posteriors.setdefault(key, BetaPosterior())
            posterior.update(success)

    def posterior(self, namespace: str, route: str) -> BetaPosterior:
        """Read-only snapshot of the posterior. Fresh prior if unseen."""
        key = BanditKey(namespace=namespace, route=route)
        with self._lock:
            posterior = self._posteriors.get(key)
            if posterior is None:
                return BetaPosterior()
            # Return copy so caller cannot mutate state.
            return BetaPosterior(alpha=posterior.alpha, beta=posterior.beta)

    def choose(self, namespace: str, admissible: list[str]) -> str:
        """Pick an admissible route via Thompson sampling.

        Args:
            namespace: Cache / agent class label.
            admissible: Candidate routes — must be non-empty.

        Returns:
            The argmax route. Ties broken by RNG (deterministic when seeded).

        Raises:
            ValueError: When ``admissible`` is empty.
        """
        if not admissible:
            raise ValueError("admissible routes list must be non-empty")
        with self._lock:
            best_route: str | None = None
            best_sample = float("-inf")
            for route in admissible:
                key = BanditKey(namespace=namespace, route=route)
                posterior = self._posteriors.setdefault(key, BetaPosterior())
                sampled = posterior.sample(self._rng)
                if sampled > best_sample:
                    best_sample = sampled
                    best_route = route
            assert best_route is not None  # admissible non-empty above
            return best_route

    def rebuild_from_decision_events(
        self,
        conn: sqlite3.Connection,
        *,
        namespace_field: str = "app_name",
        since_timestamp: float | None = None,
    ) -> int:
        """Rebuild posteriors by replaying ``decision_events`` outcomes.

        Reads only rows where ``outcome_success`` is non-NULL. ``namespace``
        is taken from ``decision_events.<namespace_field>`` (default
        ``app_name``), ``route`` from ``chosen_route``. Returns the number of
        rows applied.

        Idempotent in the sense that identical input rows yield identical
        posteriors — but calling twice DOES double-count, so callers should
        clear via :meth:`reset` before rebuilding.
        """
        if namespace_field not in {"app_name", "request_hash"}:
            raise ValueError(f"unsupported namespace_field={namespace_field!r}")
        cur = conn.cursor()
        sql = (
            f"SELECT {namespace_field}, chosen_route, outcome_success "
            "FROM decision_events "
            "WHERE outcome_success IS NOT NULL"
        )
        params: tuple = ()
        if since_timestamp is not None:
            sql += " AND timestamp >= ?"
            params = (since_timestamp,)
        applied = 0
        for ns, route, outcome in cur.execute(sql, params):
            self.update(ns, route, success=bool(outcome))
            applied += 1
        return applied

    def reset(self) -> None:
        """Clear all posteriors (test / rebuild helper)."""
        with self._lock:
            self._posteriors.clear()

    def snapshot(self) -> dict[BanditKey, BetaPosterior]:
        """Return a deep-copy snapshot of every posterior."""
        with self._lock:
            return {
                key: BetaPosterior(alpha=p.alpha, beta=p.beta)
                for key, p in self._posteriors.items()
            }


__all__ = [
    "BanditKey",
    "BetaPosterior",
    "NamespaceBandit",
]
