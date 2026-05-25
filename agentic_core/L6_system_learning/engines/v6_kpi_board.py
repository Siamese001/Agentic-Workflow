"""V6 KPI Board — typed aggregator for the 11 KPIs in v6 lines 231-245.

This module is the canonical, typed surface for the V6 Shadow Evaluation +
System Learning health board. It does **not** populate KPI samples — engines
elsewhere in ``system_learning/`` and ``agentic_core/L6_observability/`` are
responsible for measurement. This module provides:

1. A ``V6KPIName`` enum and ``V6KPISample`` typed record so producers and
   consumers agree on the schema.
2. A frozen ``V6_KPI_SPECS`` registry encoding the green-condition thresholds
   from v6 lines 234-244 verbatim.
3. ``V6KPIBoard`` aggregator that records samples, returns the latest per
   KPI, and computes compound health per the v6 HEALTH DEFINITION
   (lines 34-36).

Reference
---------
``docs/reference/06_Shadow_Evaluation_System_Learning/06_Shadow_Evaluation_System_Learning_v6.md``

Design
------
- Pure, no I/O. Construction is cheap; safe to instantiate per-test.
- Thread-safety is the caller's responsibility; this is a typed surface, not
  a service.
- Threshold direction (``"<="`` vs ``">="``) is encoded explicitly so the
  green-evaluator never has to guess.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Iterable, Mapping


class V6KPIName(str, Enum):
    """The 11 V6 KPIs (v6 lines 234-244, in spec order)."""

    TRACE_INGEST_FRESHNESS = "trace_ingest_freshness"
    EVAL_COVERAGE_OF_RUNS = "eval_coverage_of_runs"
    JUDGE_UNKNOWN_BUDGET_COMPLIANCE = "judge_unknown_budget_compliance"
    JUDGE_HUMAN_KAPPA_FRESHNESS = "judge_human_kappa_freshness"
    RCA_TO_PROPOSAL_LEAD_TIME = "rca_to_proposal_lead_time"
    GAUNTLET_FALSE_PROMOTE_RATE = "gauntlet_false_promote_rate"
    UWG_INK_PATH_UNIQUENESS = "uwg_ink_path_uniqueness"
    REPLAY_DIVERGENCE_LOCALIZATION = "replay_divergence_localization"
    EVAL_FRESHNESS_ON_WRITE = "eval_freshness_on_write"
    EXEMPLAR_HIT_RATE = "exemplar_hit_rate"
    SATURATION_WATCH = "saturation_watch"


class ThresholdDirection(str, Enum):
    """Direction of the green condition.

    ``LE`` means *value must be <= threshold to be green* (e.g. age, lead time).
    ``GE`` means *value must be >= threshold to be green* (e.g. coverage rate).
    ``EQ`` means *value must equal threshold* (e.g. uniqueness counter == 0).
    """

    LE = "<="
    GE = ">="
    EQ = "=="


@dataclass(frozen=True)
class V6KPISpec:
    """Spec for a single V6 KPI.

    Attributes
    ----------
    name : V6KPIName
    phase : phase identifier from v6 (``6A``, ``6B``, ``6C``, ``6D``, ``6B/S2D``, ``cross``).
    green_condition : human-readable green condition (verbatim from v6).
    failure_meaning : human-readable failure meaning (verbatim from v6).
    threshold : numeric threshold (None for purely qualitative KPIs).
    unit : unit of the threshold (``"seconds"``, ``"ratio"``, ``"count"``,
        ``"percent"``).
    direction : ``ThresholdDirection`` to evaluate ``value`` against ``threshold``.
    """

    name: V6KPIName
    phase: str
    green_condition: str
    failure_meaning: str
    threshold: float | None
    unit: str
    direction: ThresholdDirection


# v6 KPI Board (lines 231-245), encoded once and frozen.
_V6_KPI_SPECS_RAW: tuple[V6KPISpec, ...] = (
    V6KPISpec(
        name=V6KPIName.TRACE_INGEST_FRESHNESS,
        phase="6A",
        green_condition="newest ingested span age <= 10 minutes",
        failure_meaning="stale night tapes",
        threshold=600.0,
        unit="seconds",
        direction=ThresholdDirection.LE,
    ),
    V6KPISpec(
        name=V6KPIName.EVAL_COVERAGE_OF_RUNS,
        phase="6B",
        green_condition=">= 98% of last-24h runs have eval record",
        failure_meaning="learning sees blind spots",
        threshold=0.98,
        unit="ratio",
        direction=ThresholdDirection.GE,
    ),
    V6KPISpec(
        name=V6KPIName.JUDGE_UNKNOWN_BUDGET_COMPLIANCE,
        phase="6B",
        green_condition=">= 95% within rubric unknown_budget",
        failure_meaning="judges forced false certainty",
        threshold=0.95,
        unit="ratio",
        direction=ThresholdDirection.GE,
    ),
    V6KPISpec(
        name=V6KPIName.JUDGE_HUMAN_KAPPA_FRESHNESS,
        phase="6B/S2D",
        green_condition="latest calibration <= 7 days per rubric",
        failure_meaning="grader drift not bounded",
        threshold=7.0 * 86400.0,
        unit="seconds",
        direction=ThresholdDirection.LE,
    ),
    V6KPISpec(
        name=V6KPIName.RCA_TO_PROPOSAL_LEAD_TIME,
        phase="6C",
        green_condition="p95 incident-close -> proposal <= 24 hours",
        failure_meaning="system learns too slowly",
        threshold=24.0 * 3600.0,
        unit="seconds",
        direction=ThresholdDirection.LE,
    ),
    V6KPISpec(
        name=V6KPIName.GAUNTLET_FALSE_PROMOTE_RATE,
        phase="6D",
        green_condition="reverted promotions <= 1%",
        failure_meaning="unsafe promotion pressure",
        threshold=0.01,
        unit="ratio",
        direction=ThresholdDirection.LE,
    ),
    V6KPISpec(
        name=V6KPIName.UWG_INK_PATH_UNIQUENESS,
        phase="6D",
        green_condition="non-UWG writers detected = 0",
        failure_meaning="sovereignty breach",
        threshold=0.0,
        unit="count",
        direction=ThresholdDirection.EQ,
    ),
    V6KPISpec(
        name=V6KPIName.REPLAY_DIVERGENCE_LOCALIZATION,
        phase="6D",
        green_condition=">= 90% failed replays pinpoint a span",
        failure_meaning="replay proof not diagnostic",
        threshold=0.90,
        unit="ratio",
        direction=ThresholdDirection.GE,
    ),
    V6KPISpec(
        name=V6KPIName.EVAL_FRESHNESS_ON_WRITE,
        phase="6D",
        green_condition="100% writes have fresh gating eval",
        failure_meaning="stale eval allowed commit",
        threshold=1.0,
        unit="ratio",
        direction=ThresholdDirection.GE,
    ),
    V6KPISpec(
        name=V6KPIName.EXEMPLAR_HIT_RATE,
        phase="cross",
        green_condition=">= 20% plans consult and use exemplar hit",
        failure_meaning="learning not reused",
        threshold=0.20,
        unit="ratio",
        direction=ThresholdDirection.GE,
    ),
    V6KPISpec(
        name=V6KPIName.SATURATION_WATCH,
        phase="6B",
        green_condition="<= 10% capability evals static >= 30 days",
        failure_meaning="eval suite is aging",
        threshold=0.10,
        unit="ratio",
        direction=ThresholdDirection.LE,
    ),
)


V6_KPI_SPECS: Mapping[V6KPIName, V6KPISpec] = MappingProxyType(
    {spec.name: spec for spec in _V6_KPI_SPECS_RAW}
)
"""Frozen registry of all 11 V6 KPI specs, keyed by :class:`V6KPIName`."""


@dataclass(frozen=True)
class V6KPISample:
    """A single observed KPI sample.

    Attributes
    ----------
    name : V6KPIName
    value : observed numeric value in the spec's ``unit``.
    timestamp : epoch seconds when the sample was taken.
    source : free-form provenance tag (e.g. ``"telemetry_consumer"``).
    metadata : optional extra context.
    """

    name: V6KPIName
    value: float
    timestamp: float
    source: str
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class V6KPIStatus:
    """Evaluated status for a single KPI sample against its spec."""

    sample: V6KPISample
    spec: V6KPISpec
    is_green: bool
    reason: str


@dataclass(frozen=True)
class V6HealthSnapshot:
    """Compound health per v6 HEALTH DEFINITION (lines 34-36).

    The pipeline is healthy only when ingest freshness, eval coverage,
    calibration freshness, replay localization, false-promote rate, and UWG
    uniqueness are **all** green together. ``is_healthy`` is True iff every
    KPI in :attr:`HEALTH_REQUIRED_KPIS` reports green.

    Missing KPIs (no sample yet) are treated as **not green** — silence is
    not health.
    """

    timestamp: float
    statuses: Mapping[V6KPIName, V6KPIStatus]
    missing: tuple[V6KPIName, ...]
    is_healthy: bool
    reason: str


HEALTH_REQUIRED_KPIS: frozenset[V6KPIName] = frozenset(
    {
        V6KPIName.TRACE_INGEST_FRESHNESS,
        V6KPIName.EVAL_COVERAGE_OF_RUNS,
        V6KPIName.JUDGE_HUMAN_KAPPA_FRESHNESS,
        V6KPIName.REPLAY_DIVERGENCE_LOCALIZATION,
        V6KPIName.GAUNTLET_FALSE_PROMOTE_RATE,
        V6KPIName.UWG_INK_PATH_UNIQUENESS,
    }
)
"""KPIs explicitly named in the v6 HEALTH DEFINITION (lines 34-36)."""


def evaluate_sample(sample: V6KPISample, spec: V6KPISpec | None = None) -> V6KPIStatus:
    """Return :class:`V6KPIStatus` for ``sample`` against its spec.

    If ``spec`` is omitted, the spec is looked up in :data:`V6_KPI_SPECS`.
    """
    spec = spec if spec is not None else V6_KPI_SPECS[sample.name]
    if spec.threshold is None:
        return V6KPIStatus(
            sample=sample,
            spec=spec,
            is_green=True,
            reason=f"{spec.name.value}: spec has no numeric threshold; treated as green",
        )

    threshold = spec.threshold
    value = sample.value
    if spec.direction is ThresholdDirection.LE:
        green = value <= threshold
        op = "<="
    elif spec.direction is ThresholdDirection.GE:
        green = value >= threshold
        op = ">="
    else:  # EQ
        green = value == threshold
        op = "=="
    reason = (
        f"{spec.name.value}={value:.6g} {op} {threshold:.6g} ({spec.unit}) -> "
        f"{'GREEN' if green else 'RED'}"
    )
    return V6KPIStatus(sample=sample, spec=spec, is_green=green, reason=reason)


class V6KPIBoard:
    """Typed aggregator over the 11 V6 KPIs.

    Producers call :meth:`record` with a :class:`V6KPISample`. Consumers call
    :meth:`latest`, :meth:`evaluate_all`, or :meth:`health_snapshot`.

    The board is intentionally minimal — no time-series retention, no alert
    fan-out. It is a typed surface, not a TSDB. Higher-level dashboards may
    layer retention and alerting on top.
    """

    def __init__(self) -> None:
        self._latest: dict[V6KPIName, V6KPISample] = {}

    # ---- write side ----------------------------------------------------

    def record(self, sample: V6KPISample) -> None:
        """Record ``sample``. Replaces any prior sample for the same KPI."""
        if not isinstance(sample, V6KPISample):
            raise TypeError(f"expected V6KPISample, got {type(sample).__name__}")
        if sample.name not in V6_KPI_SPECS:
            raise ValueError(f"unknown KPI name: {sample.name!r}")
        self._latest[sample.name] = sample

    def record_value(
        self,
        name: V6KPIName,
        value: float,
        *,
        source: str,
        timestamp: float | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> V6KPISample:
        """Convenience wrapper: build a :class:`V6KPISample` and record it."""
        ts = timestamp if timestamp is not None else time.time()
        sample = V6KPISample(
            name=name,
            value=float(value),
            timestamp=ts,
            source=source,
            metadata=dict(metadata) if metadata is not None else {},
        )
        self.record(sample)
        return sample

    # ---- read side -----------------------------------------------------

    def latest(self, name: V6KPIName) -> V6KPISample | None:
        """Return the most recent sample for ``name`` or ``None``."""
        return self._latest.get(name)

    def all_latest(self) -> Mapping[V6KPIName, V6KPISample]:
        """Return a snapshot mapping of every KPI with a recorded sample."""
        return MappingProxyType(dict(self._latest))

    def evaluate_all(self) -> Mapping[V6KPIName, V6KPIStatus]:
        """Evaluate all recorded samples; missing KPIs are absent from the map."""
        return MappingProxyType(
            {name: evaluate_sample(sample) for name, sample in self._latest.items()}
        )

    def health_snapshot(
        self,
        required: Iterable[V6KPIName] | None = None,
        *,
        now: float | None = None,
    ) -> V6HealthSnapshot:
        """Compute compound health per v6 HEALTH DEFINITION.

        Parameters
        ----------
        required : iterable of KPIs that MUST be green for healthy status.
            Defaults to :data:`HEALTH_REQUIRED_KPIS`.
        now : epoch seconds for the snapshot timestamp; defaults to ``time.time()``.

        Returns
        -------
        V6HealthSnapshot
        """
        ts = now if now is not None else time.time()
        required_set = (
            HEALTH_REQUIRED_KPIS
            if required is None
            else frozenset(required)
        )
        statuses = self.evaluate_all()
        missing: list[V6KPIName] = []
        red: list[V6KPIName] = []
        for name in required_set:
            status = statuses.get(name)
            if status is None:
                missing.append(name)
            elif not status.is_green:
                red.append(name)
        if not missing and not red:
            healthy = True
            reason = (
                f"healthy: all {len(required_set)} required KPIs green"
            )
        else:
            healthy = False
            parts = []
            if missing:
                parts.append(f"missing samples for: {sorted(m.value for m in missing)}")
            if red:
                parts.append(f"red KPIs: {sorted(r.value for r in red)}")
            reason = "; ".join(parts)
        return V6HealthSnapshot(
            timestamp=ts,
            statuses=statuses,
            missing=tuple(sorted(missing, key=lambda n: n.value)),
            is_healthy=healthy,
            reason=reason,
        )

    def reset(self) -> None:
        """Drop all recorded samples (test hook)."""
        self._latest.clear()


__all__ = [
    "V6KPIName",
    "V6KPISpec",
    "V6KPISample",
    "V6KPIStatus",
    "V6HealthSnapshot",
    "V6KPIBoard",
    "ThresholdDirection",
    "V6_KPI_SPECS",
    "HEALTH_REQUIRED_KPIS",
    "evaluate_sample",
]
