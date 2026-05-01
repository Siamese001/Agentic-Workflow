"""Reply-signal feedback engine — closes the W4-P10 learning loop.

W4-P10 of the apps_lic LinkedIn response-rate maximization plan
(Notion page 35327693-f55c-81e2-9b58-debeeb48bb35, Bundle B).

Takes a stream of per-message reply events and emits structured
per-cell posteriors (Beta) and prior deltas that feed back into:

    1. MessagePlanner.section_templates      (template-level priors)
    2. ProfilePlanner archetype thresholds   (archetype-level priors)
    3. SubjectLineVariantSelector bandit     (subject-variant priors)

The engine is stateless — all state lives in ``ReplyFeedbackLedger``,
which callers persist. The posterior model is Beta(alpha=sends_replied+1,
beta=sends_unreplied+1) — a Laplace-smoothed binomial posterior, same
family used by ``NamespaceBandit`` (W1-P1). Using the same family means
the posteriors are compatible — a subject-variant posterior from the
bandit can be merged with one from this engine via alpha/beta addition.

Promotion criterion
-------------------
A cell is "promotable" when its Wilson-CI lower bound at 95% confidence
exceeds the fleet baseline by at least ``UPLIFT_PROMOTE_THRESHOLD``.
The fleet baseline is the pooled reply rate across ALL cells in the
same ledger (not just same archetype) — the goal is detecting any cell
that beats the house average. Promotable cells carry a prior delta
callers apply to the respective planner.

Regret / dimmer
---------------
Cells with Wilson-CI upper bound at 95% BELOW the fleet baseline by at
least ``DOWNLIFT_DIM_THRESHOLD`` are "dim-worthy" and carry a negative
prior delta. Neutral cells (overlapping CI with fleet baseline) carry
zero delta.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Final, List, Mapping, Optional, Tuple

from apps_lic.config.outreach_experiment_cells import (
    LATTICE_FINGERPRINT,
    cell_id,
    is_valid_cell_id,
)

# Minimum per-cell sample size before its posterior is eligible to drive
# a prior update. Below this floor, we still track the cell but don't
# let it move production priors.
MIN_SAMPLES_FOR_PROMOTION: Final[int] = 30

# Wilson-CI uplift threshold for PROMOTE verdict (5 percentage points
# above fleet baseline). Matches the L6/promo band from closed-loop
# router enforcement (§29) to keep promotion semantics consistent.
UPLIFT_PROMOTE_THRESHOLD: Final[float] = 0.05

# Wilson-CI downlift threshold for DIM verdict.
DOWNLIFT_DIM_THRESHOLD: Final[float] = 0.05

# Z-score for 95% Wilson CI.
_Z_95: Final[float] = 1.96

# Prior delta magnitudes. These values are added to the downstream
# planner's existing priors — small enough that one noisy promotion
# doesn't swing behavior; large enough that sustained uplift compounds.
PROMOTE_PRIOR_DELTA: Final[float] = 0.10
DIM_PRIOR_DELTA: Final[float] = -0.10


@dataclass
class CellPosterior:
    """Per-cell reply-rate posterior — Beta(alpha, beta).

    Attributes:
        cell_id: Canonical cell id string.
        sends: Total sends this cell has accumulated.
        replies: Total replies observed on sends from this cell.
        last_updated_utc: Timestamp of the most recent event ingestion.
    """

    cell_id: str
    sends: int = 0
    replies: int = 0
    last_updated_utc: Optional[datetime] = None

    @property
    def unreplied(self) -> int:
        """Unreplied sends, floored at zero."""
        return max(0, self.sends - self.replies)

    @property
    def alpha(self) -> float:
        """Beta distribution alpha = replies + 1 (Laplace smoothing)."""
        return float(self.replies + 1)

    @property
    def beta(self) -> float:
        """Beta distribution beta = unreplied + 1 (Laplace smoothing)."""
        return float(self.unreplied + 1)

    @property
    def posterior_mean(self) -> float:
        """Beta posterior mean = alpha / (alpha + beta)."""
        return self.alpha / (self.alpha + self.beta)


@dataclass
class ReplyFeedbackLedger:
    """Durable container of per-cell posteriors.

    Persistence is OUT OF SCOPE — callers serialise this object
    (dataclass.asdict or a SQLite binder). The engine never writes to
    disk itself; that keeps unit tests deterministic.

    Attributes:
        lattice_fingerprint: Fingerprint of the experiment cell lattice
            at ledger creation. If the lattice changes (add/remove
            cell), the binder detects drift by comparing this to the
            current ``LATTICE_FINGERPRINT``.
        posteriors: Cell-id -> CellPosterior map.
    """

    lattice_fingerprint: str = field(default_factory=lambda: LATTICE_FINGERPRINT)
    posteriors: dict[str, CellPosterior] = field(default_factory=dict)


@dataclass(frozen=True)
class CellVerdict:
    """Output of one ``evaluate_cell`` call.

    Attributes:
        cell_id: Canonical cell id.
        verdict: One of ``promote`` / ``dim`` / ``neutral`` / ``insufficient_data``.
        posterior_mean: Current Beta posterior mean.
        wilson_lower: Wilson-CI lower bound at 95%.
        wilson_upper: Wilson-CI upper bound at 95%.
        fleet_baseline: Pooled reply rate across all ledger cells.
        prior_delta: The prior adjustment callers should apply to the
            downstream planner for this cell. 0.0 for neutral /
            insufficient_data.
        reason: Human-readable rationale.
    """

    cell_id: str
    verdict: str
    posterior_mean: float
    wilson_lower: float
    wilson_upper: float
    fleet_baseline: float
    prior_delta: float
    reason: str


class ReplySignalFeedbackEngine:
    """Stateless engine — operates on a caller-provided ledger."""

    def record_event(
        self,
        ledger: ReplyFeedbackLedger,
        *,
        archetype: str,
        template: str,
        subject_variant: str,
        replied: bool,
        event_time_utc: Optional[datetime] = None,
    ) -> CellPosterior:
        """Ingest one send-or-reply event into the ledger.

        Args:
            ledger: Target ``ReplyFeedbackLedger`` (mutated in place).
            archetype / template / subject_variant: Cell axis values.
                Must correspond to a valid lattice cell; invalid
                combinations raise ``ValueError`` so callers cannot
                silently poison the ledger.
            replied: True when the send received a reply.
            event_time_utc: When the event occurred. Defaults to now(UTC).

        Returns:
            The updated ``CellPosterior`` for this cell.

        Raises:
            ValueError: When (archetype, template, subject_variant) is
                not a valid cell in the lattice.
        """
        cid = cell_id(archetype, template, subject_variant)
        if not is_valid_cell_id(cid):
            raise ValueError(
                f"Invalid cell: archetype={archetype!r} template={template!r} "
                f"subject_variant={subject_variant!r}. Not in the materialised lattice."
            )
        posterior = ledger.posteriors.setdefault(cid, CellPosterior(cell_id=cid))
        posterior.sends += 1
        if replied:
            posterior.replies += 1
        posterior.last_updated_utc = event_time_utc or datetime.now(timezone.utc)
        return posterior

    def fleet_baseline(self, ledger: ReplyFeedbackLedger) -> float:
        """Pooled reply rate across every cell in the ledger.

        Uses Laplace smoothing on the pool to avoid pathological 0/0 or
        1/1 fleet baselines when the ledger is empty or only has
        replies.
        """
        total_sends = sum(p.sends for p in ledger.posteriors.values())
        total_replies = sum(p.replies for p in ledger.posteriors.values())
        return (total_replies + 1) / (total_sends + 2)

    def evaluate_cell(
        self,
        ledger: ReplyFeedbackLedger,
        cell_id_str: str,
    ) -> CellVerdict:
        """Score one cell against the fleet baseline."""
        baseline = self.fleet_baseline(ledger)
        posterior = ledger.posteriors.get(cell_id_str)
        if posterior is None or posterior.sends < MIN_SAMPLES_FOR_PROMOTION:
            mean = posterior.posterior_mean if posterior is not None else 0.5
            return CellVerdict(
                cell_id=cell_id_str,
                verdict="insufficient_data",
                posterior_mean=mean,
                wilson_lower=0.0,
                wilson_upper=1.0,
                fleet_baseline=baseline,
                prior_delta=0.0,
                reason=(
                    f"cell has {posterior.sends if posterior else 0} sends; "
                    f"need >= {MIN_SAMPLES_FOR_PROMOTION} for prior update"
                ),
            )
        lo, hi = _wilson_ci(posterior.replies, posterior.sends, _Z_95)
        if lo >= baseline + UPLIFT_PROMOTE_THRESHOLD:
            return CellVerdict(
                cell_id=cell_id_str,
                verdict="promote",
                posterior_mean=posterior.posterior_mean,
                wilson_lower=lo,
                wilson_upper=hi,
                fleet_baseline=baseline,
                prior_delta=PROMOTE_PRIOR_DELTA,
                reason=(
                    f"wilson_lower {lo:.3f} >= baseline {baseline:.3f} + "
                    f"{UPLIFT_PROMOTE_THRESHOLD:.2f}"
                ),
            )
        if hi <= baseline - DOWNLIFT_DIM_THRESHOLD:
            return CellVerdict(
                cell_id=cell_id_str,
                verdict="dim",
                posterior_mean=posterior.posterior_mean,
                wilson_lower=lo,
                wilson_upper=hi,
                fleet_baseline=baseline,
                prior_delta=DIM_PRIOR_DELTA,
                reason=(
                    f"wilson_upper {hi:.3f} <= baseline {baseline:.3f} - "
                    f"{DOWNLIFT_DIM_THRESHOLD:.2f}"
                ),
            )
        return CellVerdict(
            cell_id=cell_id_str,
            verdict="neutral",
            posterior_mean=posterior.posterior_mean,
            wilson_lower=lo,
            wilson_upper=hi,
            fleet_baseline=baseline,
            prior_delta=0.0,
            reason="Wilson CI overlaps fleet baseline",
        )

    def evaluate_all(self, ledger: ReplyFeedbackLedger) -> List[CellVerdict]:
        """Evaluate every cell currently present in the ledger.

        Cells never observed do not appear — add them by recording at
        least one event first.
        """
        return [self.evaluate_cell(ledger, cid) for cid in sorted(ledger.posteriors)]

    def emit_prior_deltas(
        self,
        ledger: ReplyFeedbackLedger,
    ) -> Mapping[str, float]:
        """Aggregate per-cell deltas into per-axis deltas.

        Output shape:
            {
              "archetype:EXECUTIVE": +0.10,
              "archetype:SENIOR_TA": -0.10,
              "template:followup_1": 0.00,
              "subject_variant:question": +0.05,
              ...
            }

        The aggregation is mean-of-deltas within each axis level,
        weighted by the number of cells contributing. Neutral cells
        contribute 0.0; insufficient_data cells are excluded entirely.
        Callers applying these deltas MUST clamp downstream to the
        planner's allowed prior range.
        """
        verdicts = self.evaluate_all(ledger)
        eligible = [v for v in verdicts if v.verdict != "insufficient_data"]
        axis_sums: dict[str, Tuple[float, int]] = {}
        for v in eligible:
            cell = v.cell_id.split(".", 2)
            if len(cell) != 3:
                continue
            archetype, template, subject_variant = cell
            for key in (
                f"archetype:{archetype}",
                f"template:{template}",
                f"subject_variant:{subject_variant}",
            ):
                total, count = axis_sums.get(key, (0.0, 0))
                axis_sums[key] = (total + v.prior_delta, count + 1)
        return {
            key: (total / count if count else 0.0)
            for key, (total, count) in axis_sums.items()
        }


# ----------------------------------------------------------------------
# Wilson confidence interval — exact formula, no scipy dependency.
# ----------------------------------------------------------------------


def _wilson_ci(replies: int, sends: int, z: float) -> tuple[float, float]:
    """Wilson-score interval for a binomial proportion.

    Args:
        replies: Observed successes.
        sends: Total trials.
        z: Z-score for desired confidence level (1.96 for 95%).

    Returns:
        (lower_bound, upper_bound). When sends == 0 returns (0.0, 1.0)
        (maximally uncertain).
    """
    if sends <= 0:
        return (0.0, 1.0)
    p = replies / sends
    denom = 1.0 + (z * z) / sends
    centre = (p + (z * z) / (2 * sends)) / denom
    spread = (z * math.sqrt(p * (1 - p) / sends + (z * z) / (4 * sends * sends))) / denom
    return (max(0.0, centre - spread), min(1.0, centre + spread))


__all__ = [
    "CellPosterior",
    "CellVerdict",
    "DIM_PRIOR_DELTA",
    "DOWNLIFT_DIM_THRESHOLD",
    "MIN_SAMPLES_FOR_PROMOTION",
    "PROMOTE_PRIOR_DELTA",
    "ReplyFeedbackLedger",
    "ReplySignalFeedbackEngine",
    "UPLIFT_PROMOTE_THRESHOLD",
]
