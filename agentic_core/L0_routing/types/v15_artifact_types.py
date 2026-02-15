"""G-1-1 (§1.7) — TypedDict SSOT for V15 Core Artifacts.

Parallel TypedDict definitions for the frozen dataclasses in v15_types.py.
These serve as the JSON-schema-aligned target shape during the migration window.

Naming convention: <OriginalName>TD suffix to avoid clobbering dataclass names.

Contract version: 1.0.0
"""

from __future__ import annotations

from typing import Sequence, TypedDict

# ─────────────────────────────────────────────────────────────────────
# §10.4 — ResultArtifact
# ─────────────────────────────────────────────────────────────────────


class ResultArtifactTD(TypedDict):
    """§10.4 — RESULT emitted exclusively by L2 after successful heal."""

    trace_id: str
    execution_outcome: str
    final_state_hash: str
    artifact_class: str
    emitting_layer: str


# ─────────────────────────────────────────────────────────────────────
# §1.7 — HealingPlan
# ─────────────────────────────────────────────────────────────────────


class HealingPlanTD(TypedDict):
    """§1.7 — Typed HealingPlan artifact with all required fields."""

    trace_id: str
    plan_id: str
    manifests: Sequence[str]
    semantic_clock_tick: int
    policy_liaison_node: str
    emitting_layer: str


# ─────────────────────────────────────────────────────────────────────
# §15.6 — IncidentArtifact
# ─────────────────────────────────────────────────────────────────────


class IncidentArtifactTD(TypedDict):
    """§15.6 — INCIDENT with mandatory telemetry event emission."""

    trace_id: str
    incident_id: str
    correlation_hash: str
    severity_enum: str
    telemetry_events: Sequence[str]


# ─────────────────────────────────────────────────────────────────────
# §2.5 — StaleWriteIncident
# ─────────────────────────────────────────────────────────────────────


class StaleWriteIncidentTD(TypedDict):
    """§2.5 — Typed StaleWriteIncident for hash-mismatch detection."""

    trace_id: str
    target_path: str
    expected_hash: str
    actual_hash: str
    semantic_clock_tick: int


# ─────────────────────────────────────────────────────────────────────
# §3.1 — RouteDecisionArtifact
# ─────────────────────────────────────────────────────────────────────


class RouteDecisionArtifactTD(TypedDict):
    """§3.1 — Typed RouteDecision artifact with all 7+ required fields."""

    trace_id: str
    timestamp: str
    route_path: str
    risk_score: float
    budget_est: float
    rationale_enum: str
    policy_config_hash: str


# ─────────────────────────────────────────────────────────────────────
# §11.1 — TokenCapArtifact
# ─────────────────────────────────────────────────────────────────────


class TokenCapArtifactTD(TypedDict):
    """§11.1 — TokenCap enforcement artifact."""

    trace_id: str
    policy_hash: str
    budget_limit: int
    tokens_requested: int
    gate_result: str


# ─────────────────────────────────────────────────────────────────────
# §5.4 — SelfHealingTrigger
# ─────────────────────────────────────────────────────────────────────


class SelfHealingTriggerTD(TypedDict):
    """§5.4 — L6 emits to L2 to trigger healing from observability signals."""

    trace_id: str
    source_layer: str
    target_pipe: str
    signal_hash: str
    severity_enum: str


# ─────────────────────────────────────────────────────────────────────
# §2.8 — AggregateArtifact
# ─────────────────────────────────────────────────────────────────────


class AggregateArtifactTD(TypedDict):
    """§2.8 — AGGREGATE emitted on conditional flows (L2 pre-heal)."""

    trace_id: str
    impact_scope: Sequence[str]
    rollback_vector: str
    risk_delta: float
    pre_heal_assessment: str


# ─────────────────────────────────────────────────────────────────────
# Exports
# ─────────────────────────────────────────────────────────────────────

__all__ = [
    "AggregateArtifactTD",
    "HealingPlanTD",
    "IncidentArtifactTD",
    "ResultArtifactTD",
    "RouteDecisionArtifactTD",
    "SelfHealingTriggerTD",
    "StaleWriteIncidentTD",
    "TokenCapArtifactTD",
]
