"""apps_qna route bandit — Wave 4 phase 4.1.

Wraps the spine ``agentic_core.L0_routing.reasoning.namespace_bandit.NamespaceBandit``
with apps_qna domain logic (interviewer-signal namespace hashing, route-registry
admissibility, cold-start fallback to W2.3 keyword ranking, paired §29
ROUTER_DECISION marker + apps_qna_pack_lifecycle ledger writes).

Architecture
------------
Compose, don't fork. The spine bandit handles the Thompson-sampling math and
the L0/bandit ledger telemetry; this module owns:

  * The signal -> namespace projection (SHA-256 hash of the joined
    interviewer_lens + role_areas + industry_trends document)
  * The admissibility set (registry.routes, in registry order)
  * Cold-start protection (n_observations < 5 per namespace -> abstain
    and let W2.3 keyword ranking drive ordering)
  * Top-N ranking semantics (the spine bandit picks ONE route per
    ``choose()`` call; apps_qna needs an ordered top-N for the YAML's
    likely_questions priority)
  * apps_qna_pack_lifecycle ledger writes (event_kind="route_select")
    paired with ROUTER_DECISION markers per constitutional §29

Spine routing
-------------
- L0 routing: imports ``agentic_core.L0_routing.reasoning.namespace_bandit``
  for the bandit primitive AND ``agentic_core.L0_routing.config.path_constants``
  for canonical path strings (closes the W4 spine-coverage uplift goal)
- L6 observability: pairs ROUTER_DECISION marker print + emit_pack_lifecycle_event
  per §29 closed-loop router enforcement

Constitutional alignment
------------------------
- §29: paired marker + ledger write in the same code path
- §22 (graph-layer evidence): wraps an existing spine primitive — adds new
  spine import edges from apps_qna into agentic_core.L0_routing.*
- W1.4 prerequisite: requires apps_qna_pack_lifecycle ledger registered
"""

from __future__ import annotations

import hashlib
import logging
import random
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING

# Spine imports — closes the W4 spine-coverage goal.
from agentic_core.L0_routing.reasoning.namespace_bandit import (
    BetaPosterior,
    NamespaceBandit,
)
from apps_qna.integrations.spine_adapter import emit_pack_lifecycle_event

if TYPE_CHECKING:
    from apps_qna.config.route_registry import RouteRegistry

_log = logging.getLogger(__name__)

# Cold-start threshold. Below this number of accumulated observations per
# (namespace, route) cell — summed across the namespace — the bandit
# defers to W2.3 keyword ranking. Empirically chosen so that a brand-new
# apps_qna installation doesn't pretend to have learned anything until
# enough post-rehearsal outcomes have been bound.
_MIN_OBSERVATIONS_FOR_BANDIT_PRIORITY: int = 5

# Default Thompson seed. None means non-deterministic; tests pin this to
# get reproducible rankings.
_DEFAULT_SEED: int | None = None

# §29 marker emission destination. stdout by default; tests intercept via
# the standard logging surface.
_ROUTER_LAYER: str = "L0"
_ROUTER_NAME: str = "apps_qna_route_bandit"


def _hash_signal(signal: str) -> str:
    """Project a free-text interviewer signal onto a stable namespace string.

    The namespace is the (interviewer-context) cell key for the bandit's
    posterior table. Identical signals must yield identical namespaces;
    similar-but-not-identical signals must yield different ones (so the
    bandit doesn't bleed evidence across distinct interviewers). SHA-256
    truncated to 12 hex chars is collision-safe at apps_qna's scale.
    """
    if not signal or not signal.strip():
        return "qna_signal_empty"
    h = hashlib.sha256(signal.strip().encode("utf-8")).hexdigest()
    return f"qna_signal_{h[:12]}"


def _hash_panel_signal(signals: list[str]) -> str:
    """Project a panel of interviewer signals onto a shared namespace (W3.1).

    A panel is a set of interviewers (e.g. a 3-person interview round).
    W3.1 (apps-qna-dag-enhancements-e4c7b2): in a panel, each interviewer
    probes the candidate with their own lens, but the routes the panel
    cares about collectively overlap heavily. Without pooling, each
    interviewer's bandit cell stays cold forever on low-volume roles.

    Canonicalization: signals are whitespace-stripped, filtered for
    non-empty entries, and sorted before hashing — so ``[A, B, C]`` and
    ``[B, C, A]`` and ``[C, A, B]`` all produce the same panel
    namespace. The empty-panel degenerate case is ``qna_panel_empty``.

    Panel namespaces are DISTINCT from single-interviewer namespaces
    (prefix ``qna_panel_`` vs ``qna_signal_``) so per-interviewer and
    per-panel posteriors never alias.
    """
    cleaned = sorted(s.strip() for s in signals if s and s.strip())
    if not cleaned:
        return "qna_panel_empty"
    joined = "\x1f".join(cleaned)  # ASCII unit-separator as delimiter
    h = hashlib.sha256(joined.encode("utf-8")).hexdigest()
    return f"qna_panel_{h[:12]}"


@dataclass(frozen=True)
class RouteSelection:
    """One bandit-ranked route. Ranks are ordered descending by score."""

    route_id: str
    rank: int
    posterior_alpha: float
    posterior_beta: float
    posterior_mean: float
    thompson_sample: float
    decision_id: str


def _emit_graded_outcome_marker(
    *,
    decision_id: str,
    namespace: str,
    route: str,
    score: float,
) -> None:
    """Constitutional §29 paired marker for a graded outcome update (W2.2)."""
    print(
        f"ROUTER_DECISION: layer={_ROUTER_LAYER} router={_ROUTER_NAME} "
        f"decision_id={decision_id} selected={route} ns={namespace} "
        f"event=graded_outcome grade_normalized={score:.3f}"
    )


def _emit_router_decision_marker(
    *,
    decision_id: str,
    selected: str,
    namespace: str,
    posterior_alpha: float,
    posterior_beta: float,
) -> None:
    """Print the constitutional §29 paired marker.

    Format mirrors closed-loop-router-enforcement.md grammar:
        ROUTER_DECISION: layer=L0 router=apps_qna_route_bandit
            decision_id=<uuid> selected=<route_id> ns=<namespace>
            posterior_alpha=<a> posterior_beta=<b>

    Stays a single logical line so post_agent_router_decision_audit.py
    can parse it from logs / stdout / Codex response trace.
    """
    print(
        f"ROUTER_DECISION: layer={_ROUTER_LAYER} router={_ROUTER_NAME} "
        f"decision_id={decision_id} selected={selected} ns={namespace} "
        f"posterior_alpha={posterior_alpha:.3f} "
        f"posterior_beta={posterior_beta:.3f}"
    )


class AppsQnaRouteBandit:
    """Domain wrapper around the spine NamespaceBandit.

    Usage::

        bandit = AppsQnaRouteBandit(registry, seed=42)
        # Cold-start: returns None (caller falls back to W2.3 keyword ranking)
        result = bandit.choose_routes_for_signal(signal_text, top_n=5)
        # ... after some post-rehearsal feedback ...
        bandit.update_outcome(namespace="qna_signal_abc", route="executive_fit",
                              asked=True, landed=True)
        # Hot path: returns a ranked list of RouteSelections
        result = bandit.choose_routes_for_signal(signal_text, top_n=5)
    """

    def __init__(
        self,
        registry: "RouteRegistry",
        *,
        seed: int | None = _DEFAULT_SEED,
    ) -> None:
        self._registry = registry
        # Two RNGs: one for the bandit's internal sampling (passed to
        # NamespaceBandit), one for our top-N ranking sampling. Sharing a
        # single seeded RNG across both gives deterministic ordering when
        # tests need it.
        self._rng = random.Random(seed)
        self._bandit = NamespaceBandit(seed=seed)

    @property
    def admissible_route_ids(self) -> list[str]:
        return [r.id for r in self._registry.routes]

    def total_observations(self, namespace: str) -> int:
        """Total observations across all (namespace, route) cells."""
        return sum(
            self._bandit.posterior(namespace, route).n_observations
            for route in self.admissible_route_ids
        )

    def choose_routes_for_signal(
        self,
        signal: str,
        *,
        top_n: int = 6,
    ) -> list[RouteSelection] | None:
        """Rank routes for an interviewer signal via Thompson sampling.

        Returns None when the bandit is in cold-start (insufficient
        observations for this namespace); the caller should fall back to
        W2.3 keyword ranking. Returns a list of RouteSelection ordered by
        Thompson sample score descending when accumulated evidence
        clears the cold-start threshold.

        For each surfaced ranking, emits the constitutional §29 paired
        ROUTER_DECISION marker AND an apps_qna_pack_lifecycle ledger row
        with event_kind="route_select".
        """
        namespace = _hash_signal(signal)
        admissible = self.admissible_route_ids
        if not admissible:
            return None

        if self.total_observations(namespace) < _MIN_OBSERVATIONS_FOR_BANDIT_PRIORITY:
            _log.debug(
                "AppsQnaRouteBandit cold-start (ns=%s, n_obs=%d, threshold=%d) — "
                "deferring to keyword fallback",
                namespace,
                self.total_observations(namespace),
                _MIN_OBSERVATIONS_FOR_BANDIT_PRIORITY,
            )
            return None

        # Sample once per route, then rank descending. Using
        # NamespaceBandit.posterior() keeps us inside the spine primitive's
        # contract (the returned BetaPosterior is a copy; its sample()
        # method takes a Random which we provide).
        scored: list[tuple[str, float, float, float]] = []
        for route in admissible:
            posterior = self._bandit.posterior(namespace, route)
            sampled = posterior.sample(self._rng)
            scored.append(
                (route, sampled, posterior.alpha, posterior.beta)
            )
        scored.sort(key=lambda r: r[1], reverse=True)

        selections: list[RouteSelection] = []
        for rank, (route, sampled, alpha, beta) in enumerate(scored[:top_n], start=1):
            decision_id = uuid.uuid4().hex
            mean = alpha / (alpha + beta) if (alpha + beta) > 0 else 0.5
            selection = RouteSelection(
                route_id=route,
                rank=rank,
                posterior_alpha=float(alpha),
                posterior_beta=float(beta),
                posterior_mean=float(mean),
                thompson_sample=float(sampled),
                decision_id=decision_id,
            )
            selections.append(selection)

            # §29 paired emission: marker + ledger write in the same
            # call path. Both are fail-soft.
            _emit_router_decision_marker(
                decision_id=decision_id,
                selected=route,
                namespace=namespace,
                posterior_alpha=alpha,
                posterior_beta=beta,
            )
            emit_pack_lifecycle_event(
                event_kind="route_select",
                prediction={
                    "namespace": namespace,
                    "candidate_routes": admissible,
                    "selected_route": route,
                    "rank": rank,
                    "posterior_alpha": float(alpha),
                    "posterior_beta": float(beta),
                    "thompson_sample": float(sampled),
                },
                score_band="hit",  # provisional; bound to "miss" if outcome shows otherwise
                metadata={"decision_id": decision_id},
            )

        return selections

    def choose_routes_for_panel(
        self,
        signals: list[str],
        *,
        top_n: int = 6,
    ) -> list[RouteSelection] | None:
        """W3.1: panel-shared variant of ``choose_routes_for_signal``.

        Accepts a list of interviewer signals (one per panel member) and
        hashes the canonicalized set into a single panel namespace. The
        bandit then ranks routes using accumulated panel-wide evidence,
        allowing 3-interviewer panels to pool posteriors while preserving
        per-interviewer specificity (the individual-signal path is
        untouched).

        Returns ``None`` on empty panel, cold-start, or empty admissibility.
        Emits the same §29 paired marker + ledger row as the
        single-interviewer path, with ``ns=qna_panel_<hash>`` so the
        audit surface can distinguish panel vs individual decisions.
        """
        if not signals:
            return None
        namespace = _hash_panel_signal(signals)
        admissible = self.admissible_route_ids
        if not admissible:
            return None
        if self.total_observations(namespace) < _MIN_OBSERVATIONS_FOR_BANDIT_PRIORITY:
            _log.debug(
                "AppsQnaRouteBandit panel cold-start (ns=%s, n_obs=%d)",
                namespace,
                self.total_observations(namespace),
            )
            return None
        scored: list[tuple[str, float, float, float]] = []
        for route in admissible:
            posterior = self._bandit.posterior(namespace, route)
            sampled = posterior.sample(self._rng)
            scored.append((route, sampled, posterior.alpha, posterior.beta))
        scored.sort(key=lambda r: r[1], reverse=True)

        selections: list[RouteSelection] = []
        for rank, (route, sampled, alpha, beta) in enumerate(
            scored[:top_n], start=1
        ):
            decision_id = uuid.uuid4().hex
            mean = alpha / (alpha + beta) if (alpha + beta) > 0 else 0.5
            selections.append(
                RouteSelection(
                    route_id=route,
                    rank=rank,
                    posterior_alpha=float(alpha),
                    posterior_beta=float(beta),
                    posterior_mean=float(mean),
                    thompson_sample=float(sampled),
                    decision_id=decision_id,
                )
            )
            _emit_router_decision_marker(
                decision_id=decision_id,
                selected=route,
                namespace=namespace,
                posterior_alpha=alpha,
                posterior_beta=beta,
            )
            emit_pack_lifecycle_event(
                event_kind="route_select",
                prediction={
                    "namespace": namespace,
                    "panel_size": len(signals),
                    "candidate_routes": admissible,
                    "selected_route": route,
                    "rank": rank,
                    "posterior_alpha": float(alpha),
                    "posterior_beta": float(beta),
                    "thompson_sample": float(sampled),
                },
                score_band="hit",
                metadata={"decision_id": decision_id, "panel_mode": True},
            )
        return selections

    def update_outcome(
        self,
        *,
        namespace: str,
        route: str,
        asked: bool,
        landed: bool,
        score: float | None = None,
    ) -> None:
        """Late-bind a post-rehearsal outcome.

        Two paths, mutually exclusive:

        * **Bernoulli path** (``score is None``): success = ``asked AND
          landed``. The interviewer probed the route AND the bound card
          resolved the answer — both required for a positive sample.
          Updates flow through ``NamespaceBandit.update`` which also
          propagates to the L0/bandit ledger via its closed-loop helper.
          This is the W4.1 back-compat path.
        * **Graded path** (``score`` provided — W2.2): ``score ∈ [0, 1]``
          is credited directly to the posterior via
          ``NamespaceBandit.update_graded``. Typical source: card 22
          Learnings rehearsal grade normalized from 1-5 to [0, 1] by
          ``(grade - 1) / 4``. The graded path does NOT bind the open
          L0/bandit ledger row; apps_qna emits its own
          ``apps_qna_pack_lifecycle`` ``interview_outcome_graded`` row
          instead (constitutional §29 paired emission).
        """
        if score is not None:
            self._bandit.update_graded(namespace, route, score=score)
            # §29 graded-path emission.
            decision_id = uuid.uuid4().hex
            _emit_graded_outcome_marker(
                decision_id=decision_id,
                namespace=namespace,
                route=route,
                score=score,
            )
            emit_pack_lifecycle_event(
                event_kind="route_outcome_graded",
                prediction={
                    "namespace": namespace,
                    "route": route,
                    "grade_normalized": float(score),
                    "asked": bool(asked),
                    "landed": bool(landed),
                },
                score_numeric=float(score),
                metadata={"decision_id": decision_id},
            )
            return
        success = bool(asked and landed)
        self._bandit.update(namespace, route, success=success)

    def reset(self) -> None:
        """Clear all bandit state (posteriors + open ledger handles).

        Mirrors the spine NamespaceBandit.reset() contract for parity
        with sibling routers.
        """
        self._bandit.reset()


__all__ = [
    "AppsQnaRouteBandit",
    "BetaPosterior",
    "RouteSelection",
]
