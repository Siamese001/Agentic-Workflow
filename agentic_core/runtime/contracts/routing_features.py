"""Routing feature vector — W1.P1 deposit (additive contract).

Plan: ``.windsurf/plans/l0-routing-calibration-gap-audit-b3c9d4.md`` W1.

Encodes the five features the L0 router MUST be able to consume when it
moves beyond the current ``Path.A/B/C/D`` payload-shape heuristic:

* ``work_class``              — L1 intent taxonomy (factual/compare/analyze/...).
* ``freshness_class``         — freshness SLA required by the L1 plan.
* ``grounding_need_score``    — Vertex-style prediction in [0,1] — "does this
  prompt benefit from grounded retrieval?"
* ``ood_score``               — out-of-distribution / embedding-drift signal
  in [0,1]. 0 = in-distribution; 1 = highly novel.
* ``budget_headroom_ratio``   — remaining token / cost budget as a ratio in
  [0,1]. 1 = full headroom; 0 = cap reached.

This module is **types-only and additive**. It does NOT modify the existing
L1 plan contract or any producer. The feature vector is an independent
artifact that L1 (or a shim over L1 output) can populate and L0 / L6 can
consume. Live wiring is deferred to W3.

Design notes:

* ``FreshnessClass`` is re-exported from
  :mod:`agentic_core.L0_routing.types.routing_artifact_types` — not
  duplicated — so this module and L0 agree on the vocabulary.
* ``RoutingFeatureVector`` is a :class:`~dataclasses.dataclass` with
  ``frozen=True`` and computes a stable :attr:`manifest_hash` so telemetry
  can de-dup / key on feature snapshots.
* No optional feature defaults to a "safe" value silently; callers MUST
  provide each feature. Unknown features use the ``UNKNOWN`` enum member
  or the ``NO_SIGNAL`` score constant so absence is explicit.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal

# NOTE: FreshnessClass is intentionally DUPLICATED here (not imported from
# ``agentic_core.L0_routing.types.routing_artifact_types``) because
# ``agentic_core.runtime.contracts`` sits BELOW ``L0_routing`` in the layer
# gravity stack. A parity test in
# ``tests/unit/runtime/contracts/test_routing_features.py`` enforces that
# the two definitions stay in sync — if one moves, the test fails.

FreshnessClass = Literal["fresh", "bounded", "stale_ok", "volatile"]
"""Freshness SLA classification. MUST match the Literal defined in
``agentic_core.L0_routing.types.routing_artifact_types``. Parity is
enforced by test ``test_freshness_class_parity_with_l0``.
"""

_FRESHNESS_VALUES: frozenset[str] = frozenset(
    {"fresh", "bounded", "stale_ok", "volatile"},
)

__all__ = [
    "FreshnessClass",
    "NO_SIGNAL",
    "RoutingFeatureVector",
    "WorkClass",
    "build_feature_vector",
    "canonical_feature_bytes",
]


NO_SIGNAL: float = -1.0
"""Sentinel score for "caller could not compute this feature".

Any consumer that receives ``NO_SIGNAL`` for a numeric feature MUST fall
back to the default behavior for that path (usually: do not let the
missing signal fire the gate). Never treat ``NO_SIGNAL`` as a real score.
"""


class WorkClass(str, Enum):
    """Intent taxonomy emitted by L1 ``I3 DETAILS + WORK CLASS``.

    Values mirror the v33 process map §[2] I3 bullets and the v5 L1
    doctrine ``§ I4 JOB CLASS`` 12-row enumeration:
    *summarize / compare / explain / analyze / classify / plan / act /
    create / edit / retrieve / decide* (escalate is modelled via
    ``EscalationHint`` rather than a work class).

    ``factual`` and ``generate`` predate the v5 list and remain
    accepted aliases (factual ≈ retrieve, generate ≈ create).
    """

    SUMMARIZE = "summarize"
    COMPARE = "compare"
    EXPLAIN = "explain"
    ANALYZE = "analyze"
    CLASSIFY = "classify"
    PLAN = "plan"
    ACT = "act"
    CREATE = "create"
    EDIT = "edit"
    RETRIEVE = "retrieve"
    DECIDE = "decide"
    # Pre-v5 calibration aliases (kept for back-compat).
    FACTUAL = "factual"
    GENERATE = "generate"
    UNKNOWN = "unknown"


def _validate_unit_or_sentinel(name: str, value: float) -> float:
    """Return ``value`` if it is in ``[0,1]`` or equals :data:`NO_SIGNAL`.

    Raises:
        ValueError: ``value`` is not a number, is NaN, or is outside
            ``[0,1]`` and not :data:`NO_SIGNAL`.
    """
    if not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric, got {type(value).__name__}")
    numeric = float(value)
    if numeric != numeric:  # NaN check — NaN != NaN
        raise ValueError(f"{name} must not be NaN")
    if numeric == NO_SIGNAL:
        return numeric
    if not 0.0 <= numeric <= 1.0:
        raise ValueError(
            f"{name} must be in [0.0, 1.0] or NO_SIGNAL ({NO_SIGNAL}); got {numeric!r}",
        )
    return numeric


@dataclass(frozen=True)
class RoutingFeatureVector:
    """Typed snapshot of routing features for one request.

    All five fields are required. Scores that cannot be computed MUST use
    :data:`NO_SIGNAL`; unknown class fields MUST use :attr:`WorkClass.UNKNOWN`
    or ``"unknown"`` (for :class:`FreshnessClass`-equivalent literal).

    Fields:
        work_class: L1 intent taxonomy.
        freshness_class: Freshness SLA required (``fresh`` / ``bounded`` /
            ``stale_ok`` / ``volatile``). Literal sourced from the
            existing L0 routing artifact types module.
        grounding_need_score: Probability in ``[0,1]`` that grounded
            retrieval helps, else :data:`NO_SIGNAL`.
        ood_score: OOD / novelty score in ``[0,1]``, else :data:`NO_SIGNAL`.
            ``0`` = in-distribution, ``1`` = highly novel.
        budget_headroom_ratio: Remaining budget in ``[0,1]``, else
            :data:`NO_SIGNAL`. ``1`` = full headroom, ``0`` = cap reached.
        metadata: Optional free-form dict for ad-hoc telemetry. Keys MUST
            be JSON-safe (str keys, primitive values). Values are NOT
            included in :attr:`manifest_hash` unless a caller sorts them
            into the canonical bytes path.
        manifest_hash: sha256 hex digest over the canonical JSON of the
            five primary features. Auto-computed.
    """

    work_class: WorkClass
    freshness_class: FreshnessClass
    grounding_need_score: float
    ood_score: float
    budget_headroom_ratio: float
    metadata: dict[str, Any] = field(default_factory=dict)
    manifest_hash: str = ""

    def __post_init__(self) -> None:
        # Validate numeric scores first — fail fast on bad input.
        validated_ground = _validate_unit_or_sentinel(
            "grounding_need_score",
            self.grounding_need_score,
        )
        validated_ood = _validate_unit_or_sentinel("ood_score", self.ood_score)
        validated_budget = _validate_unit_or_sentinel(
            "budget_headroom_ratio",
            self.budget_headroom_ratio,
        )

        # Validate enum fields. FreshnessClass is a Literal; validate by membership.
        if not isinstance(self.work_class, WorkClass):
            raise ValueError(
                f"work_class must be WorkClass enum, got {type(self.work_class).__name__}",
            )
        if self.freshness_class not in _FRESHNESS_VALUES:
            raise ValueError(
                f"freshness_class must be one of fresh/bounded/stale_ok/volatile; "
                f"got {self.freshness_class!r}",
            )

        # Re-set the coerced floats (dataclass is frozen → object.__setattr__).
        object.__setattr__(self, "grounding_need_score", validated_ground)
        object.__setattr__(self, "ood_score", validated_ood)
        object.__setattr__(self, "budget_headroom_ratio", validated_budget)

        # Compute the manifest hash if caller did not supply one.
        if not self.manifest_hash:
            digest = hashlib.sha256(canonical_feature_bytes(self)).hexdigest()
            object.__setattr__(self, "manifest_hash", digest)

    def has_grounding_signal(self) -> bool:
        """True when :attr:`grounding_need_score` is a real score (not NO_SIGNAL)."""
        return self.grounding_need_score != NO_SIGNAL

    def has_ood_signal(self) -> bool:
        """True when :attr:`ood_score` is a real score (not NO_SIGNAL)."""
        return self.ood_score != NO_SIGNAL

    def has_budget_signal(self) -> bool:
        """True when :attr:`budget_headroom_ratio` is a real score (not NO_SIGNAL)."""
        return self.budget_headroom_ratio != NO_SIGNAL

    def to_dict(self) -> dict[str, Any]:
        """JSON-safe serialization — used by telemetry and replay."""
        return {
            "work_class": self.work_class.value,
            "freshness_class": self.freshness_class,
            "grounding_need_score": self.grounding_need_score,
            "ood_score": self.ood_score,
            "budget_headroom_ratio": self.budget_headroom_ratio,
            "metadata": dict(self.metadata),
            "manifest_hash": self.manifest_hash,
        }


def canonical_feature_bytes(features: RoutingFeatureVector) -> bytes:
    """Deterministic byte serialization of the PRIMARY fields only.

    ``metadata`` and ``manifest_hash`` are intentionally excluded so that
    two vectors with identical primary features hash identically even if
    metadata differs (e.g. different trace ids).
    """
    canonical = {
        "work_class": features.work_class.value,
        "freshness_class": features.freshness_class,
        "grounding_need_score": round(features.grounding_need_score, 6),
        "ood_score": round(features.ood_score, 6),
        "budget_headroom_ratio": round(features.budget_headroom_ratio, 6),
    }
    return json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")


def build_feature_vector(
    *,
    work_class: WorkClass | str = WorkClass.UNKNOWN,
    freshness_class: FreshnessClass = "bounded",
    grounding_need_score: float = NO_SIGNAL,
    ood_score: float = NO_SIGNAL,
    budget_headroom_ratio: float = NO_SIGNAL,
    metadata: dict[str, Any] | None = None,
) -> RoutingFeatureVector:
    """Convenience constructor with safe defaults.

    Default behavior: every score defaults to :data:`NO_SIGNAL`, and
    ``work_class`` defaults to :attr:`WorkClass.UNKNOWN`. This means a
    caller that only knows a subset of features can still build a valid
    vector — consumers then observe the explicit "unknown" markers via
    :meth:`RoutingFeatureVector.has_grounding_signal` etc.

    Args:
        work_class: ``WorkClass`` enum or its string value.
        freshness_class: One of ``"fresh"``, ``"bounded"``,
            ``"stale_ok"``, ``"volatile"``.
        grounding_need_score: In ``[0,1]`` or :data:`NO_SIGNAL`.
        ood_score: In ``[0,1]`` or :data:`NO_SIGNAL`.
        budget_headroom_ratio: In ``[0,1]`` or :data:`NO_SIGNAL`.
        metadata: Optional free-form dict.

    Raises:
        ValueError: propagated from :class:`RoutingFeatureVector`
            validation — out-of-range score, invalid freshness literal,
            or non-enum work_class string.
    """
    if isinstance(work_class, str):
        try:
            work_class_enum = WorkClass(work_class)
        except ValueError as exc:
            raise ValueError(
                f"work_class {work_class!r} is not a valid WorkClass value",
            ) from exc
    else:
        work_class_enum = work_class

    return RoutingFeatureVector(
        work_class=work_class_enum,
        freshness_class=freshness_class,
        grounding_need_score=float(grounding_need_score),
        ood_score=float(ood_score),
        budget_headroom_ratio=float(budget_headroom_ratio),
        metadata=dict(metadata or {}),
    )
