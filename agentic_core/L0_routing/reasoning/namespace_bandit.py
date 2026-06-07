"""Per-namespace Thompson-sampling bandit for R1B / R3 threshold tuning.

Plan: ``docs/archive/windsurf/legacy-tree/plans/routing-decision-process-enhancement-9c7e4d.md`` Wave W4.

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

import logging
import random
import sqlite3
import threading
from dataclasses import dataclass, field

_LOGGER = logging.getLogger(__name__)

# Constitutional §29 closed-loop wiring (W5.4). Lazy singleton so this module
# stays importable when `tools.ledgers` is absent.
_BANDIT_HELPER = None  # type: ignore[var-annotated]


def _get_bandit_helper():
    global _BANDIT_HELPER  # noqa: PLW0603
    if _BANDIT_HELPER is not None:
        return _BANDIT_HELPER
    try:
        from tools.ledgers.router_helper import RouterClosedLoopHelper  # noqa: PLC0415

        _BANDIT_HELPER = RouterClosedLoopHelper(
            layer="L0",
            router="bandit",
            ledger_name="router_l0_bandit",
            repo_area="agentic_core/L0_routing/reasoning/namespace_bandit.py",
        )
        return _BANDIT_HELPER
    except ImportError:  # guardian: allow-log-and-swallow -- helper unavailable must not break bandit
        _LOGGER.debug("RouterClosedLoopHelper unavailable for L0/bandit", exc_info=True)
        return None


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

    def update_graded(self, score: float) -> None:
        """Additive graded update — ``score`` in ``[0.0, 1.0]``.

        Credits ``alpha += score`` and ``beta += (1.0 - score)``. One
        graded outcome is therefore one unit of ``n_observations`` (since
        ``alpha + beta`` increases by exactly 1), matching the semantics
        of ``update(success)`` for cold-start accounting. This is the
        minimal-disruption extension invoked by W2.2 of
        ``apps-qna-dag-enhancements-e4c7b2``.

        Values outside [0, 1] are clamped. Bernoulli-equivalent call sites
        should keep using ``update(success)`` to avoid float drift.
        """
        if score != score:  # NaN check without importing math
            raise ValueError("score must not be NaN")
        clamped = 0.0 if score < 0.0 else 1.0 if score > 1.0 else float(score)
        self.alpha += clamped
        self.beta += 1.0 - clamped

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
        # W5.4: most recent open decision handle per (namespace, route) so
        # update() can bind outcomes. Bounded by number of distinct cells
        # touched in a session. None when telemetry is unavailable.
        self._open_handles: dict[BanditKey, object] = {}

    def update(self, namespace: str, route: str, *, success: bool) -> None:
        """Update posterior for ``(namespace, route)`` with Bernoulli outcome.

        W5.4 (closed-loop-l0-bandit-wiring): also binds the outcome to the
        most recent open ROUTER_DECISION row for this (namespace, route) cell.
        Fail-soft: telemetry never breaks the bandit update.
        """
        key = BanditKey(namespace=namespace, route=route)
        with self._lock:
            posterior = self._posteriors.setdefault(key, BetaPosterior())
            posterior.update(success)
            alpha_after = posterior.alpha
            beta_after = posterior.beta
            handle = self._open_handles.pop(key, None)
        helper = _get_bandit_helper()
        if helper is not None and handle is not None:
            try:
                helper.bind_outcome(
                    handle,
                    success=success,
                    outcome_extras={
                        "posterior_alpha_after": float(alpha_after),
                        "posterior_beta_after": float(beta_after),
                    },
                )
            except (AttributeError, TypeError, ValueError, RuntimeError):  # guardian: allow-log-and-swallow -- telemetry is best-effort
                _LOGGER.debug("namespace_bandit bind_outcome failed", exc_info=True)

    def update_graded(
        self, namespace: str, route: str, *, score: float
    ) -> None:
        """Update posterior with a graded outcome in ``[0, 1]``.

        W2.2 (apps-qna-dag-enhancements-e4c7b2): additive surface that
        preserves the existing Bernoulli ``update()`` path for back-compat
        while exposing a graded credit assignment for callers that have a
        richer signal (e.g. a rehearsal grade in 1-5 stars normalized to
        [0, 1]). Values outside [0, 1] are clamped inside ``BetaPosterior``.

        Does NOT interact with the closed-loop router helper — the paired
        ``ROUTER_DECISION:`` marker + ledger binding is the caller's
        responsibility (apps_qna emits its own §29 markers at the domain
        layer). Callers wanting the bound-outcome path should continue to
        use ``update(success=bool)``.
        """
        key = BanditKey(namespace=namespace, route=route)
        with self._lock:
            posterior = self._posteriors.setdefault(key, BetaPosterior())
            posterior.update_graded(score)

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
            best_alpha = 1.0
            best_beta = 1.0
            best_mean = 0.5
            for route in admissible:
                key = BanditKey(namespace=namespace, route=route)
                posterior = self._posteriors.setdefault(key, BetaPosterior())
                sampled = posterior.sample(self._rng)
                if sampled > best_sample:
                    best_sample = sampled
                    best_route = route
                    best_alpha = posterior.alpha
                    best_beta = posterior.beta
                    best_mean = posterior.alpha / (posterior.alpha + posterior.beta)
            assert best_route is not None  # admissible non-empty above
            chosen_key = BanditKey(namespace=namespace, route=best_route)
        # W5.4: record decision via helper (outside the lock so ledger I/O
        # never serializes routing). Stash the handle for update() to bind.
        helper = _get_bandit_helper()
        if helper is not None:
            try:
                handle = helper.record_decision(
                    selected=best_route,
                    cell={"namespace": namespace, "admissible": sorted(admissible)},
                    predicted_p_success=float(best_mean),
                    eu_score=float(best_sample),
                    prediction_extras={
                        "posterior_alpha": float(best_alpha),
                        "posterior_beta": float(best_beta),
                    },
                )
                with self._lock:
                    self._open_handles[chosen_key] = handle
            except (AttributeError, TypeError, ValueError, RuntimeError):  # guardian: allow-log-and-swallow -- telemetry is best-effort
                _LOGGER.debug("namespace_bandit record_decision failed", exc_info=True)
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
        """Clear all posteriors AND any unbound decision handles.

        Bug fix (2026-04-26): the previous implementation cleared
        ``_posteriors`` but left ``_open_handles`` populated. After
        reset(), the next ``update()`` would ``pop()`` a stale handle
        from a pre-reset decision and bind the fresh-prior outcome to
        the wrong ledger row, polluting the closed-loop telemetry. We
        now clear both maps under the same lock so the bandit's view
        of "what has been decided but not yet bound" is consistent
        with its posterior state.
        """
        with self._lock:
            self._posteriors.clear()
            self._open_handles.clear()

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
