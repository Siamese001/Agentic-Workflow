"""apps_qna paste-set bandit — Wave 4 phase 4.2.

Second bandit in the apps_qna router family. Where W4.1's
``AppsQnaRouteBandit`` decides WHICH routes lead the
``likely_questions`` priority order, this bandit decides WHICH cards
to include in the paste-set given a paste budget.

Design
------
Same architecture as W4.1: wraps the spine ``NamespaceBandit`` rather
than reimplementing Thompson sampling. Domain logic adds:
  - Paste-budget-aware namespace projection (signal_hash × budget_bucket)
  - Card admissibility from the canonical ``_CARD_SPECS`` ordering
  - Cold-start abstention so the existing builder ordering wins until
    n_obs >= 5
  - Constitutional §29 paired ROUTER_DECISION marker + emit_pack_lifecycle_event
    writes per decision

Budget buckets coarse-grain the paste budget so the bandit doesn't
fragment evidence across many similar budgets. Buckets: 8, 12, 18, 25
(matching the natural ChatGPT paste tiers). Any budget maps to its
nearest bucket; the bandit's posterior is keyed on the bucket.
"""

from __future__ import annotations

import hashlib
import logging
import random
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING

from agentic_core.L0_routing.reasoning.namespace_bandit import (
    BetaPosterior,
    NamespaceBandit,
)
from apps_qna.integrations.spine_adapter import emit_pack_lifecycle_event

if TYPE_CHECKING:
    pass

_log = logging.getLogger(__name__)

_MIN_OBSERVATIONS_FOR_BANDIT_PRIORITY: int = 5
_DEFAULT_SEED: int | None = None
_ROUTER_LAYER: str = "L0"
_ROUTER_NAME: str = "apps_qna_paste_bandit"

# Coarse-grained paste budget buckets. Matches the ChatGPT-Project paste
# tiers documented in card_pack_builder._CHATGPT_PROJECT_FILE_CAP. The
# bandit treats budgets within a bucket as equivalent.
_BUDGET_BUCKETS: tuple[int, ...] = (8, 12, 18, 25)


def _bucket_for_budget(budget: int) -> int:
    """Snap a paste-budget int to the nearest bucket."""
    if not _BUDGET_BUCKETS:
        return budget
    return min(_BUDGET_BUCKETS, key=lambda b: abs(b - budget))


def _hash_signal_with_budget(signal: str, budget_bucket: int) -> str:
    """Project (signal, budget_bucket) onto a stable namespace string."""
    if not signal or not signal.strip():
        h = "empty"
    else:
        h = hashlib.sha256(signal.strip().encode("utf-8")).hexdigest()[:12]
    return f"qna_paste_{h}_b{budget_bucket}"


@dataclass(frozen=True)
class CardSelection:
    """One bandit-ranked card for paste-set inclusion."""

    card_id: str
    rank: int
    posterior_alpha: float
    posterior_beta: float
    posterior_mean: float
    thompson_sample: float
    decision_id: str


def _emit_paste_decision_marker(
    *,
    decision_id: str,
    selected: str,
    namespace: str,
    budget_bucket: int,
    posterior_alpha: float,
    posterior_beta: float,
) -> None:
    """Constitutional §29 paired marker for paste decisions."""
    print(
        f"ROUTER_DECISION: layer={_ROUTER_LAYER} router={_ROUTER_NAME} "
        f"decision_id={decision_id} selected={selected} ns={namespace} "
        f"budget_bucket={budget_bucket} "
        f"posterior_alpha={posterior_alpha:.3f} "
        f"posterior_beta={posterior_beta:.3f}"
    )


class AppsQnaPasteBandit:
    """Bandit-driven paste-set composer.

    Usage::

        bandit = AppsQnaPasteBandit(seed=42)
        # Cold-start: returns None (caller falls back to _CARD_SPECS order)
        selection = bandit.choose_paste_set(
            signal="Vrinda probes architecture",
            paste_budget=18,
            admissible_cards=["00_RUNTIME_ROOT.md", ...],
        )
        # ... after rehearsal feedback ...
        bandit.update_outcome(
            namespace="qna_paste_<hash>_b18",
            card_id="13_EXECUTIVE_FIT.md",
            included=True,
            useful=True,
        )
    """

    def __init__(self, *, seed: int | None = _DEFAULT_SEED) -> None:
        self._rng = random.Random(seed)
        self._bandit = NamespaceBandit(seed=seed)

    def total_observations(
        self, namespace: str, admissible_cards: list[str]
    ) -> int:
        """Total observations across all (namespace, card) cells."""
        return sum(
            self._bandit.posterior(namespace, card).n_observations
            for card in admissible_cards
        )

    def choose_paste_set(
        self,
        *,
        signal: str,
        paste_budget: int,
        admissible_cards: list[str],
    ) -> list[CardSelection] | None:
        """Pick the top ``paste_budget`` cards by Thompson sample.

        Returns None on cold-start (caller falls back to the existing
        ``_CARD_SPECS`` paste_order priority).
        """
        if not admissible_cards:
            return None
        if paste_budget <= 0:
            return []

        bucket = _bucket_for_budget(paste_budget)
        namespace = _hash_signal_with_budget(signal, bucket)

        if self.total_observations(namespace, admissible_cards) < _MIN_OBSERVATIONS_FOR_BANDIT_PRIORITY:
            _log.debug(
                "AppsQnaPasteBandit cold-start (ns=%s, n_obs=%d) — falling back",
                namespace,
                self.total_observations(namespace, admissible_cards),
            )
            return None

        scored: list[tuple[str, float, float, float]] = []
        for card in admissible_cards:
            posterior = self._bandit.posterior(namespace, card)
            sampled = posterior.sample(self._rng)
            scored.append((card, sampled, posterior.alpha, posterior.beta))
        scored.sort(key=lambda r: r[1], reverse=True)

        selections: list[CardSelection] = []
        for rank, (card, sampled, alpha, beta) in enumerate(
            scored[:paste_budget], start=1
        ):
            decision_id = uuid.uuid4().hex
            mean = alpha / (alpha + beta) if (alpha + beta) > 0 else 0.5
            selection = CardSelection(
                card_id=card,
                rank=rank,
                posterior_alpha=float(alpha),
                posterior_beta=float(beta),
                posterior_mean=float(mean),
                thompson_sample=float(sampled),
                decision_id=decision_id,
            )
            selections.append(selection)
            _emit_paste_decision_marker(
                decision_id=decision_id,
                selected=card,
                namespace=namespace,
                budget_bucket=bucket,
                posterior_alpha=alpha,
                posterior_beta=beta,
            )
            emit_pack_lifecycle_event(
                event_kind="paste_set_select",
                prediction={
                    "namespace": namespace,
                    "budget_bucket": bucket,
                    "paste_budget_requested": paste_budget,
                    "selected_card": card,
                    "rank": rank,
                    "posterior_alpha": float(alpha),
                    "posterior_beta": float(beta),
                    "thompson_sample": float(sampled),
                },
                score_band="hit",
                metadata={"decision_id": decision_id},
            )
        return selections

    def update_outcome(
        self,
        *,
        namespace: str,
        card_id: str,
        included: bool,
        useful: bool,
        score: float | None = None,
    ) -> None:
        """Bind paste-set outcome.

        Two paths, mutually exclusive:

        * **Bernoulli path** (``score is None``): success = ``included
          AND useful`` — the card was in the paste set AND the operator
          found it useful. Included-but-unused is a False sample (wasted
          budget); not-included is no observation.
        * **Graded path** (``score`` provided — W2.2): ``score ∈ [0, 1]``
          is credited directly to the posterior via
          ``NamespaceBandit.update_graded``. Typical source: card 22
          Learnings "which cards were most useful" rehearsal grade.
          Emits §29 paired marker + ``apps_qna_pack_lifecycle``
          ``paste_outcome_graded`` row.
        """
        if not included:
            # No observation — caller shouldn't have invoked update for
            # cards never in the paste set. Defensive no-op.
            return
        if score is not None:
            self._bandit.update_graded(namespace, card_id, score=score)
            decision_id = uuid.uuid4().hex
            print(
                f"ROUTER_DECISION: layer={_ROUTER_LAYER} router={_ROUTER_NAME} "
                f"decision_id={decision_id} selected={card_id} ns={namespace} "
                f"event=graded_outcome grade_normalized={score:.3f}"
            )
            emit_pack_lifecycle_event(
                event_kind="paste_outcome_graded",
                prediction={
                    "namespace": namespace,
                    "card_id": card_id,
                    "grade_normalized": float(score),
                    "included": True,
                    "useful": bool(useful),
                },
                score_numeric=float(score),
                metadata={"decision_id": decision_id},
            )
            return
        success = bool(useful)
        self._bandit.update(namespace, card_id, success=success)

    def reset(self) -> None:
        self._bandit.reset()


__all__ = [
    "AppsQnaPasteBandit",
    "BetaPosterior",
    "CardSelection",
]
