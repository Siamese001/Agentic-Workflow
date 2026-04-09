"""Execution policy dataclasses for ADG CI gates.

Defines the augmented classification model from the P0-P3 execution policy
enhancement wave. These dataclasses are attached to every GateResult and
GateViolation to give each finding its full operational context.

Classification dimensions (all required):
    stage           — when the gate runs: "preflight" or "full"
    repairability   — how it can be fixed
    gate_action     — what blocking semantics apply
    artifact_policy — what artifact format is emitted
    signal_source   — what data surface drives the gate
    evidence_tier   — whether the signal is canonical truth or a derived explainer

Ratchet dimensions (P1/P2 gates):
    gross, net, new, resolved, critical_new, critical_near_sink,
    critical_cross_layer, modified_area_count

Trend dimensions (P3 gates):
    history, consecutive_increases, hotspot_modules, promotion_candidate
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Allowed values — used for validation in gate_ssot_catalog.py
# ---------------------------------------------------------------------------

VALID_STAGES = frozenset({"preflight", "full", "preflight+full"})

VALID_REPAIRABILITY = frozenset({"auto_fix_safe", "suggest_only", "manual_only"})

VALID_GATE_ACTIONS = frozenset({"halt", "ratchet", "watch"})

VALID_ARTIFACT_POLICIES = frozenset(
    {
        "minimal_failure_artifact",
        "full_adg_report",
        "trend_only",
        "path_explainer_artifact",
        "snapshot_diff_artifact",
        "parity_failure_artifact",
        "neighborhood_artifact",
    }
)

VALID_SIGNAL_SOURCES = frozenset({"canonical_policy", "sqlite_mv_ci", "graphdb_ci"})

VALID_EVIDENCE_TIERS = frozenset({"truth", "derived_explainer"})

VALID_PATH_CRITICALITY_CLASSES = frozenset({"ingress", "execution", "sink", "write", "provider", "unknown"})


# ---------------------------------------------------------------------------
# ExecutionPolicy — attached to every GateResult
# ---------------------------------------------------------------------------


@dataclass
class ExecutionPolicy:
    """Operational classification for a gate family.

    Every gate in the SSOT catalog must declare all six fields.
    Defaults are provided to allow progressive migration of legacy gates,
    but the SSOT catalog enforces completeness at catalog build time.
    """

    stage: str = "full"
    repairability: str = "manual_only"
    gate_action: str = "halt"
    artifact_policy: str = "full_adg_report"
    signal_source: str = "canonical_policy"
    evidence_tier: str = "truth"

    def validate(self) -> list[str]:
        """Return list of validation errors. Empty = valid."""
        errors: list[str] = []
        if self.stage not in VALID_STAGES:
            errors.append(f"stage={self.stage!r} not in {sorted(VALID_STAGES)}")
        if self.repairability not in VALID_REPAIRABILITY:
            errors.append(f"repairability={self.repairability!r} not in {sorted(VALID_REPAIRABILITY)}")
        if self.gate_action not in VALID_GATE_ACTIONS:
            errors.append(f"gate_action={self.gate_action!r} not in {sorted(VALID_GATE_ACTIONS)}")
        if self.artifact_policy not in VALID_ARTIFACT_POLICIES:
            errors.append(
                f"artifact_policy={self.artifact_policy!r} not in {sorted(VALID_ARTIFACT_POLICIES)}"
            )
        if self.signal_source not in VALID_SIGNAL_SOURCES:
            errors.append(f"signal_source={self.signal_source!r} not in {sorted(VALID_SIGNAL_SOURCES)}")
        if self.evidence_tier not in VALID_EVIDENCE_TIERS:
            errors.append(f"evidence_tier={self.evidence_tier!r} not in {sorted(VALID_EVIDENCE_TIERS)}")
        return errors

    def to_dict(self) -> dict[str, str]:
        return {
            "stage": self.stage,
            "repairability": self.repairability,
            "gate_action": self.gate_action,
            "artifact_policy": self.artifact_policy,
            "signal_source": self.signal_source,
            "evidence_tier": self.evidence_tier,
        }


# ---------------------------------------------------------------------------
# RatchetResult — attached to P1/P2 GateResults
# ---------------------------------------------------------------------------


@dataclass
class RatchetResult:
    """Path-aware ratchet outcome for P1/P2 gates.

    Extends simple count-delta ratchets with structural criticality fields
    so that a gate can block not just on count regression but also on
    location (sink/write/provider proximity) and modified-area concentration.
    """

    gross: int = 0
    net: int = 0
    new: int = 0
    resolved: int = 0
    critical_new: int = 0
    critical_near_sink: int = 0
    critical_cross_layer: int = 0
    modified_area_count: int = 0
    blocked: bool = False
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "gross": self.gross,
            "net": self.net,
            "new": self.new,
            "resolved": self.resolved,
            "critical_new": self.critical_new,
            "critical_near_sink": self.critical_near_sink,
            "critical_cross_layer": self.critical_cross_layer,
            "modified_area_count": self.modified_area_count,
            "blocked": self.blocked,
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RatchetResult":
        return cls(
            gross=data.get("gross", 0),
            net=data.get("net", 0),
            new=data.get("new", 0),
            resolved=data.get("resolved", 0),
            critical_new=data.get("critical_new", 0),
            critical_near_sink=data.get("critical_near_sink", 0),
            critical_cross_layer=data.get("critical_cross_layer", 0),
            modified_area_count=data.get("modified_area_count", 0),
            blocked=data.get("blocked", False),
            reason=data.get("reason", ""),
        )


# ---------------------------------------------------------------------------
# TrendResult — attached to P3 GateResults
# ---------------------------------------------------------------------------


@dataclass
class TrendResult:
    """Trend and promotion tracking for P3 watch-only gates.

    P3 gates do not block but must trend and surface promotion candidates
    when violations accumulate near critical paths.
    """

    history: list[dict[str, Any]] = field(default_factory=list)
    consecutive_increases: int = 0
    hotspot_modules: list[str] = field(default_factory=list)
    promotion_candidate: bool = False
    promotion_reason: str = ""

    PROMOTION_THRESHOLD_CONSECUTIVE = 3

    def update(self, current_gross: int, current_hotspots: list[str]) -> None:
        """Append current run to history and recompute trend metrics."""
        entry: dict[str, Any] = {
            "gross": current_gross,
            "hotspots": current_hotspots,
        }
        self.history.append(entry)

        if len(self.history) >= 2 and self.history[-1]["gross"] > self.history[-2]["gross"]:
            self.consecutive_increases += 1
        else:
            self.consecutive_increases = 0

        hotspot_counts: dict[str, int] = {}
        window = self.history[-10:]
        for run in window:
            for mod in run.get("hotspots", []):
                hotspot_counts[mod] = hotspot_counts.get(mod, 0) + 1
        threshold = max(1, len(window) // 2)
        self.hotspot_modules = [m for m, c in hotspot_counts.items() if c >= threshold]

    def evaluate_promotion(self, near_critical_path: bool) -> None:
        """Set promotion_candidate if threshold met near critical paths."""
        if self.consecutive_increases >= self.PROMOTION_THRESHOLD_CONSECUTIVE and near_critical_path:
            self.promotion_candidate = True
            self.promotion_reason = (
                f"Consecutive increases={self.consecutive_increases} "
                f"with {len(self.hotspot_modules)} hotspot module(s) "
                "near critical path"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "history": self.history,
            "consecutive_increases": self.consecutive_increases,
            "hotspot_modules": self.hotspot_modules,
            "promotion_candidate": self.promotion_candidate,
            "promotion_reason": self.promotion_reason,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TrendResult":
        obj = cls(
            history=data.get("history", []),
            consecutive_increases=data.get("consecutive_increases", 0),
            hotspot_modules=data.get("hotspot_modules", []),
            promotion_candidate=data.get("promotion_candidate", False),
            promotion_reason=data.get("promotion_reason", ""),
        )
        return obj
