"""V7 6C.S3A Signal Fusion Engine.

Fuses BUS P (preference grades) + BUS T (telemetry) + outcome / trajectory /
governance evals + human calibration + drift / anomaly + HITL outcomes +
denial/reroute reasons + replay failures + incident reports + red-team
labels into a single, weighted ``FusedSignalBundle`` consumed by 6C RCA.

Reference
---------
``docs/reference/06_Shadow_Evaluation_System_Learning/06_Shadow_Evaluation_System_Learning_v7.md``
section 6C S3A "SIGNAL FUSION".
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class SignalSource(str, Enum):
    """Per v7 S3A "FUSES" list."""

    BUS_P_PREFERENCE = "bus_p_preference"
    BUS_T_TELEMETRY = "bus_t_telemetry"
    OUTCOME_EVAL = "outcome_eval"
    TRAJECTORY_EVAL = "trajectory_eval"
    GOVERNANCE_REGRESSION = "governance_regression"
    HUMAN_CALIBRATION = "human_calibration"
    DRIFT_ANOMALY = "drift_anomaly"
    HITL_OUTCOME = "hitl_outcome"
    DENIAL_REROUTE = "denial_reroute"
    REPLAY_FAILURE = "replay_failure"
    INCIDENT_REPORT = "incident_report"
    RED_TEAM = "red_team"
    PRODUCTION_SUPPORT = "production_support"


# Per-source default reliability prior. Higher = more authoritative.
_SOURCE_RELIABILITY: dict[SignalSource, float] = {
    SignalSource.HUMAN_CALIBRATION: 1.0,
    SignalSource.RED_TEAM: 0.95,
    SignalSource.INCIDENT_REPORT: 0.95,
    SignalSource.PRODUCTION_SUPPORT: 0.9,
    SignalSource.GOVERNANCE_REGRESSION: 0.9,
    SignalSource.OUTCOME_EVAL: 0.85,
    SignalSource.TRAJECTORY_EVAL: 0.85,
    SignalSource.HITL_OUTCOME: 0.85,
    SignalSource.REPLAY_FAILURE: 0.8,
    SignalSource.DRIFT_ANOMALY: 0.7,
    SignalSource.DENIAL_REROUTE: 0.7,
    SignalSource.BUS_T_TELEMETRY: 0.6,
    SignalSource.BUS_P_PREFERENCE: 0.4,
}


@dataclass(frozen=True)
class Signal:
    """One incoming signal."""

    source: SignalSource
    severity: float  # 0.0 = noise, 1.0 = catastrophic
    confidence: float  # 0.0 = guess, 1.0 = certain
    sample_size: int
    recency_seconds: float  # 0 = now, larger = older
    reproducibility: float  # 0.0 = one-off, 1.0 = consistent
    user_impact: float  # 0.0 = none, 1.0 = full
    policy_criticality: float  # 0.0 = nice-to-have, 1.0 = hard-constraint
    affected_surface: str  # free-form id (e.g. "L2:tool.search")


@dataclass(frozen=True)
class FusedSignalBundle:
    """Output of signal fusion per v7 S3A."""

    fused_severity: float
    fused_confidence: float
    severity_class: str  # "low" | "medium" | "high" | "critical"
    confidence_band: str  # "low" | "medium" | "high"
    drift_cluster_candidates: tuple[str, ...]
    affected_surface_candidates: tuple[str, ...]
    recommended_investigation: str
    raw_signal_count: int
    weighted_sources: tuple[tuple[str, float], ...]  # (source.value, weight)


def _recency_weight(recency_seconds: float, half_life_seconds: float = 86400.0) -> float:
    """Exponential decay so older signals weigh less. Default half-life 24h."""
    if recency_seconds <= 0:
        return 1.0
    return 0.5 ** (recency_seconds / half_life_seconds)


def _sample_size_weight(n: int) -> float:
    """log10-style growth, capped at 1.0 (so n=10 -> ~1.0)."""
    if n <= 0:
        return 0.1
    return float(min(1.0, math.log10(1 + n) / math.log10(11)))


class SignalFusionEngine:
    """Combine heterogeneous signals into a single weighted bundle."""

    def fuse(self, signals: Iterable[Signal]) -> FusedSignalBundle:
        signals_list = list(signals)
        if not signals_list:
            return FusedSignalBundle(
                fused_severity=0.0,
                fused_confidence=0.0,
                severity_class="low",
                confidence_band="low",
                drift_cluster_candidates=(),
                affected_surface_candidates=(),
                recommended_investigation="no_signals",
                raw_signal_count=0,
                weighted_sources=(),
            )

        weighted_sev_sum = 0.0
        weighted_conf_sum = 0.0
        weight_sum = 0.0
        per_source_weight: dict[SignalSource, float] = {}
        surfaces: dict[str, float] = {}

        for sig in signals_list:
            reliability = _SOURCE_RELIABILITY.get(sig.source, 0.5)
            recency_w = _recency_weight(sig.recency_seconds)
            n_w = _sample_size_weight(sig.sample_size)
            # Combined weight blends reliability x recency x sample-size x
            # reproducibility, plus user-impact and policy-criticality
            # boosts that v7 S3A says must affect signal weight.
            w = (
                reliability
                * recency_w
                * n_w
                * (0.5 + 0.5 * sig.reproducibility)
                * (1.0 + 0.5 * sig.user_impact)
                * (1.0 + 0.5 * sig.policy_criticality)
            )
            w = max(0.0, w)
            weighted_sev_sum += sig.severity * w
            weighted_conf_sum += sig.confidence * w
            weight_sum += w
            per_source_weight[sig.source] = (
                per_source_weight.get(sig.source, 0.0) + w
            )
            surfaces[sig.affected_surface] = (
                surfaces.get(sig.affected_surface, 0.0) + w
            )

        fused_sev = weighted_sev_sum / weight_sum if weight_sum > 0 else 0.0
        fused_conf = weighted_conf_sum / weight_sum if weight_sum > 0 else 0.0

        if fused_sev >= 0.85:
            sev_class = "critical"
        elif fused_sev >= 0.6:
            sev_class = "high"
        elif fused_sev >= 0.3:
            sev_class = "medium"
        else:
            sev_class = "low"

        if fused_conf >= 0.75:
            conf_band = "high"
        elif fused_conf >= 0.4:
            conf_band = "medium"
        else:
            conf_band = "low"

        # Investigation recommendation per fused severity x confidence.
        if sev_class in {"critical", "high"} and conf_band in {"high", "medium"}:
            rec = "open_incident_rca_immediately"
        elif sev_class in {"critical", "high"} and conf_band == "low":
            rec = "gather_more_evidence_before_rca"
        elif sev_class == "medium":
            rec = "queue_for_pattern_synthesis"
        else:
            rec = "monitor_only"

        sorted_surfaces = tuple(
            s for s, _ in sorted(surfaces.items(), key=lambda kv: -kv[1])
        )
        sorted_sources = tuple(
            (src.value, weight)
            for src, weight in sorted(
                per_source_weight.items(), key=lambda kv: -kv[1]
            )
        )

        return FusedSignalBundle(
            fused_severity=fused_sev,
            fused_confidence=fused_conf,
            severity_class=sev_class,
            confidence_band=conf_band,
            drift_cluster_candidates=sorted_surfaces[:5],
            affected_surface_candidates=sorted_surfaces,
            recommended_investigation=rec,
            raw_signal_count=len(signals_list),
            weighted_sources=sorted_sources,
        )


__all__ = [
    "SignalSource",
    "Signal",
    "FusedSignalBundle",
    "SignalFusionEngine",
]
