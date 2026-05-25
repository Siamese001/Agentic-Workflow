"""V7 KPI Board — extended typed aggregator over v6 + v7 + governance + exit + L2 KPIs.

This module extends ``v6_kpi_board`` with the new KPIs introduced by:

- ``docs/reference/06_Shadow_Evaluation_System_Learning/06_Shadow_Evaluation_System_Learning_v7.md``
- ``docs/reference/00_L5_Policy_Plane/Governance & Safety v4.md`` and ``v5.md``
- ``docs/reference/05_Exit_Evaluation_&_Control/05_Live_Runtime_Exit_Control_&_Evaluation_v6.md``
- ``docs/reference/04_L2_Execute/04_L2_Execute_v4.md``

It re-exports the v6 surface unchanged (``V6KPIName``, ``V6KPIBoard``,
``V6KPISample``, ``V6_KPI_SPECS``) and adds:

- ``V7KPIName`` — enum of every NEW KPI (no overlap with v6 names).
- ``V7_KPI_SPECS`` — frozen registry of new specs.
- ``UnifiedKPIBoard`` — accepts either a v6 OR v7 KPI sample.
- ``ALL_KPI_SPECS`` — merged frozen mapping.

Design discipline
-----------------
- **No new behavior** beyond v6 board semantics: same threshold directions,
  same green-evaluation logic, same dataclass shape.
- **No producer logic** here — engines elsewhere call ``board.record_value(...)``.
- **No I/O, no time-series retention** — pure typed surface.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from .v6_kpi_board import (  # re-export
    HEALTH_REQUIRED_KPIS,
    ThresholdDirection,
    V6_KPI_SPECS,
    V6HealthSnapshot,
    V6KPIBoard,
    V6KPIName,
    V6KPISample,
    V6KPISpec,
    V6KPIStatus,
    evaluate_sample,
)


# ---------------------------------------------------------------------------
# V7 KPI names (no overlap with V6KPIName)
# ---------------------------------------------------------------------------


class V7KPIName(str, Enum):
    """New KPIs from v7 / governance v4-v5 / exit v6 / L2 v4."""

    # --- v7 6A: Ingest --------------------------------------------------
    EVIDENCE_FIELD_COMPLETENESS = "evidence_field_completeness"
    ORPHAN_ARTIFACT_RATE = "orphan_artifact_rate"
    OBSERVER_LAW_VIOLATION_COUNT = "observer_law_violation_count"
    EVAL_READINESS_COVERAGE = "eval_readiness_coverage"

    # --- v7 6B: Evaluate ------------------------------------------------
    OUTCOME_EVAL_COVERAGE = "outcome_eval_coverage"
    TRAJECTORY_EVAL_COVERAGE = "trajectory_eval_coverage"
    GOVERNANCE_EVAL_COVERAGE = "governance_eval_coverage"
    GOLDEN_SET_REGRESSION_PASS_RATE = "golden_set_regression_pass_rate"

    # --- v7 6C: RCA / Synth ---------------------------------------------
    ROOT_CAUSE_LOCALIZATION_RATE = "root_cause_localization_rate"
    PROPOSAL_EVIDENCE_COMPLETENESS = "proposal_evidence_completeness"
    HELD_PROPOSAL_AGING_P95 = "held_proposal_aging_p95"

    # --- v7 6D: Promote / Update ----------------------------------------
    ROLLBACK_REACHABILITY = "rollback_reachability"
    BUS_U_ACTIVATION_CORRECTNESS = "bus_u_activation_correctness"

    # --- v7 cross-cutting ----------------------------------------------
    CITATION_SUPPORT_DRIFT = "citation_support_drift"
    ABSTAIN_REFUSAL_CALIBRATION_DRIFT = "abstain_refusal_calibration_drift"

    # --- L5 Governance v4/v5 -------------------------------------------
    GUARDRAIL_BANK_PASS_RATE = "guardrail_bank_pass_rate"
    EGRESS_INSPECTOR_BLOCK_RATE = "egress_inspector_block_rate"
    CAPABILITY_TOKEN_TTL_VIOLATIONS = "capability_token_ttl_violations"
    CAPABILITY_TOKEN_SCOPE_VIOLATIONS = "capability_token_scope_violations"
    PRINCIPAL_CHAIN_PROPAGATION_COMPLETENESS = "principal_chain_propagation_completeness"
    DELEGATION_DEPTH_BREACHES = "delegation_depth_breaches"
    HARD_CONSTRAINT_REMEDIATE_ATTEMPTS = "hard_constraint_remediate_attempts"
    RISK_TIER_BAND_COVERAGE = "risk_tier_band_coverage"
    STANDARDS_FINGERPRINT_ATTACHMENT_RATE = "standards_fingerprint_attachment_rate"
    REPLAY_ENVELOPE_RECONSTRUCTION_SUCCESS_RATE = "replay_envelope_reconstruction_success_rate"
    MCP_CONNECTOR_ALLOWLIST_VIOLATIONS = "mcp_connector_allowlist_violations"
    SHADOW_BYPASS_ATTEMPTS_DETECTED = "shadow_bypass_attempts_detected"
    GUARD_MODEL_REVIEW_AGREEMENT_RATE = "guard_model_review_agreement_rate"

    # --- Exit & Eval v6 ------------------------------------------------
    X3_DISPOSITION_UNIQUENESS = "x3_disposition_uniqueness"
    SILENT_FALLBACK_COUNT = "silent_fallback_count"
    UNAUTHORIZED_L4_WRITE_ATTEMPTS = "unauthorized_l4_write_attempts"
    UNKNOWN_TO_X3B_ROUTING_CORRECTNESS = "unknown_to_x3b_routing_correctness"
    COMMIT_PATH_CLEARANCE_COMPLETENESS = "commit_path_clearance_completeness"
    ANSWER_ONLY_CLEARANCE_COMPLETENESS = "answer_only_clearance_completeness"
    SAFE_ABSTAIN_RATE = "safe_abstain_rate"
    COMMITTED_ARTIFACT_UWG_RECEIPT_COMPLETENESS = "committed_artifact_uwg_receipt_completeness"

    # --- L2 Execute v4 -------------------------------------------------
    PASS_K_COMMIT_RELIABILITY = "pass_k_commit_reliability"
    PER_TRIAL_ISOLATION_VIOLATIONS = "per_trial_isolation_violations"
    BOUNDED_WORK_OVERRUN_RATE = "bounded_work_overrun_rate"
    CONFIDENCE_ROUTING_MISROUTE_RATE = "confidence_routing_misroute_rate"


# ---------------------------------------------------------------------------
# Spec registry — every new KPI gets its threshold and direction.
# ---------------------------------------------------------------------------


def _spec(
    name: V7KPIName,
    *,
    phase: str,
    green: str,
    fail: str,
    threshold: float | None,
    unit: str,
    direction: ThresholdDirection,
) -> V6KPISpec:
    """Construct a V6KPISpec from a V7KPIName.

    We deliberately reuse :class:`V6KPISpec` as the spec dataclass — its
    ``name`` field is typed as ``V6KPIName`` but the enum is ``str``-backed,
    so any string-valued name works at runtime. This keeps a single typed
    surface across both name spaces without code duplication.
    """
    return V6KPISpec(
        name=name,  # type: ignore[arg-type]
        phase=phase,
        green_condition=green,
        failure_meaning=fail,
        threshold=threshold,
        unit=unit,
        direction=direction,
    )


_V7_KPI_SPECS_RAW: tuple[V6KPISpec, ...] = (
    # v7 6A
    _spec(V7KPIName.EVIDENCE_FIELD_COMPLETENESS,
          phase="6A", green=">= 99% required normalized fields present",
          fail="graders see broken packets",
          threshold=0.99, unit="ratio", direction=ThresholdDirection.GE),
    _spec(V7KPIName.ORPHAN_ARTIFACT_RATE,
          phase="6A", green="<= 0.5% artifacts lack trace/run linkage",
          fail="lineage is leaking",
          threshold=0.005, unit="ratio", direction=ThresholdDirection.LE),
    _spec(V7KPIName.OBSERVER_LAW_VIOLATION_COUNT,
          phase="6A", green="0 writes / live mutations from L6",
          fail="sovereignty breach",
          threshold=0.0, unit="count", direction=ThresholdDirection.EQ),
    _spec(V7KPIName.EVAL_READINESS_COVERAGE,
          phase="6A/6B", green=">= 98% runs evaluable within 24h",
          fail="blind learning surface",
          threshold=0.98, unit="ratio", direction=ThresholdDirection.GE),
    # v7 6B
    _spec(V7KPIName.OUTCOME_EVAL_COVERAGE,
          phase="6B", green=">= 98% of last-24h runs have outcome eval",
          fail="answer quality not measured",
          threshold=0.98, unit="ratio", direction=ThresholdDirection.GE),
    _spec(V7KPIName.TRAJECTORY_EVAL_COVERAGE,
          phase="6B", green=">= 98% of non-RET executions graded",
          fail="path quality not measured",
          threshold=0.98, unit="ratio", direction=ThresholdDirection.GE),
    _spec(V7KPIName.GOVERNANCE_EVAL_COVERAGE,
          phase="6B", green="100% high-risk / write / HITL paths checked",
          fail="guardrail drift hidden",
          threshold=1.0, unit="ratio", direction=ThresholdDirection.GE),
    _spec(V7KPIName.GOLDEN_SET_REGRESSION_PASS_RATE,
          phase="6B/6D", green=">= 99% critical golden cases pass",
          fail="proposed learning breaks basics",
          threshold=0.99, unit="ratio", direction=ThresholdDirection.GE),
    # v7 6C
    _spec(V7KPIName.ROOT_CAUSE_LOCALIZATION_RATE,
          phase="6C", green=">= 90% incidents have first_bad_span/class",
          fail="RCA too vague to fix",
          threshold=0.90, unit="ratio", direction=ThresholdDirection.GE),
    _spec(V7KPIName.PROPOSAL_EVIDENCE_COMPLETENESS,
          phase="6C", green="100% proposals link eval + RCA + evidence",
          fail="proposal is opinion, not evidence",
          threshold=1.0, unit="ratio", direction=ThresholdDirection.GE),
    _spec(V7KPIName.HELD_PROPOSAL_AGING_P95,
          phase="6C", green="p95 hold age <= agreed TTL",
          fail="board backlog accumulating",
          threshold=7.0 * 86400.0, unit="seconds",
          direction=ThresholdDirection.LE),
    # v7 6D
    _spec(V7KPIName.ROLLBACK_REACHABILITY,
          phase="6D", green="100% promotions have tested rollback handle",
          fail="unsafe rollout",
          threshold=1.0, unit="ratio", direction=ThresholdDirection.GE),
    _spec(V7KPIName.BUS_U_ACTIVATION_CORRECTNESS,
          phase="6D", green="100% updates activate only at future run_start",
          fail="current-run mutation risk",
          threshold=1.0, unit="ratio", direction=ThresholdDirection.GE),
    # v7 cross
    _spec(V7KPIName.CITATION_SUPPORT_DRIFT,
          phase="cross", green="support precision stays within threshold",
          fail="groundedness degrading",
          threshold=0.05, unit="ratio", direction=ThresholdDirection.LE),
    _spec(V7KPIName.ABSTAIN_REFUSAL_CALIBRATION_DRIFT,
          phase="cross", green="false abstain/refusal within rubric band",
          fail="safety/helpfulness imbalance",
          threshold=0.10, unit="ratio", direction=ThresholdDirection.LE),
    # L5 v4/v5
    _spec(V7KPIName.GUARDRAIL_BANK_PASS_RATE,
          phase="L5", green=">= 95% guardrail-bank checks pass",
          fail="guardrail bank degraded",
          threshold=0.95, unit="ratio", direction=ThresholdDirection.GE),
    _spec(V7KPIName.EGRESS_INSPECTOR_BLOCK_RATE,
          phase="L5", green="block rate within rubric band",
          fail="egress inspector mis-tuned",
          threshold=0.20, unit="ratio", direction=ThresholdDirection.LE),
    _spec(V7KPIName.CAPABILITY_TOKEN_TTL_VIOLATIONS,
          phase="L5", green="0 expired-token uses",
          fail="TTL not enforced",
          threshold=0.0, unit="count", direction=ThresholdDirection.EQ),
    _spec(V7KPIName.CAPABILITY_TOKEN_SCOPE_VIOLATIONS,
          phase="L5", green="0 out-of-scope token uses",
          fail="scope not enforced",
          threshold=0.0, unit="count", direction=ThresholdDirection.EQ),
    _spec(V7KPIName.PRINCIPAL_CHAIN_PROPAGATION_COMPLETENESS,
          phase="L5", green="100% calls carry full principal chain",
          fail="identity propagation broken",
          threshold=1.0, unit="ratio", direction=ThresholdDirection.GE),
    _spec(V7KPIName.DELEGATION_DEPTH_BREACHES,
          phase="L5", green="0 delegation-depth breaches",
          fail="A2A boundary violated",
          threshold=0.0, unit="count", direction=ThresholdDirection.EQ),
    _spec(V7KPIName.HARD_CONSTRAINT_REMEDIATE_ATTEMPTS,
          phase="L5", green="0 REMEDIATE attempts on hard_constraint",
          fail="hard-constraint discipline broken",
          threshold=0.0, unit="count", direction=ThresholdDirection.EQ),
    _spec(V7KPIName.RISK_TIER_BAND_COVERAGE,
          phase="L5", green="100% calls classified into LOW/MOD/HIGH",
          fail="risk-tier classifier blind spots",
          threshold=1.0, unit="ratio", direction=ThresholdDirection.GE),
    _spec(V7KPIName.STANDARDS_FINGERPRINT_ATTACHMENT_RATE,
          phase="L5", green="100% certifications carry standards fingerprint",
          fail="compliance attestation broken",
          threshold=1.0, unit="ratio", direction=ThresholdDirection.GE),
    _spec(V7KPIName.REPLAY_ENVELOPE_RECONSTRUCTION_SUCCESS_RATE,
          phase="L5", green=">= 99% envelopes independently reconstructable",
          fail="forensic replay broken",
          threshold=0.99, unit="ratio", direction=ThresholdDirection.GE),
    _spec(V7KPIName.MCP_CONNECTOR_ALLOWLIST_VIOLATIONS,
          phase="L5", green="0 unallowed MCP connector calls",
          fail="connector allowlist bypassed",
          threshold=0.0, unit="count", direction=ThresholdDirection.EQ),
    _spec(V7KPIName.SHADOW_BYPASS_ATTEMPTS_DETECTED,
          phase="L5", green="0 undetected shadow bypass attempts",
          fail="bypass discovery degraded",
          threshold=0.0, unit="count", direction=ThresholdDirection.EQ),
    _spec(V7KPIName.GUARD_MODEL_REVIEW_AGREEMENT_RATE,
          phase="L5", green=">= 90% guard-model agreement on HIGH-risk",
          fail="guard-model misaligned",
          threshold=0.90, unit="ratio", direction=ThresholdDirection.GE),
    # Exit v6
    _spec(V7KPIName.X3_DISPOSITION_UNIQUENESS,
          phase="Exit", green="100% runs exit exactly one X3 disposition",
          fail="multi-disposition or no-disposition runs",
          threshold=1.0, unit="ratio", direction=ThresholdDirection.GE),
    _spec(V7KPIName.SILENT_FALLBACK_COUNT,
          phase="Exit", green="0 silent fallbacks",
          fail="invariant 2 broken",
          threshold=0.0, unit="count", direction=ThresholdDirection.EQ),
    _spec(V7KPIName.UNAUTHORIZED_L4_WRITE_ATTEMPTS,
          phase="Exit", green="0 non-UWG L4 writes",
          fail="invariants 4-7 broken",
          threshold=0.0, unit="count", direction=ThresholdDirection.EQ),
    _spec(V7KPIName.UNKNOWN_TO_X3B_ROUTING_CORRECTNESS,
          phase="Exit", green="100% material UNKNOWN -> X3B",
          fail="invariant 25 broken",
          threshold=1.0, unit="ratio", direction=ThresholdDirection.GE),
    _spec(V7KPIName.COMMIT_PATH_CLEARANCE_COMPLETENESS,
          phase="Exit", green="100% commits clear X1A-F + G + H + I + J",
          fail="invariant 22 broken",
          threshold=1.0, unit="ratio", direction=ThresholdDirection.GE),
    _spec(V7KPIName.ANSWER_ONLY_CLEARANCE_COMPLETENESS,
          phase="Exit", green="100% answer-only clears X1A-F + H + I",
          fail="invariant 23 broken",
          threshold=1.0, unit="ratio", direction=ThresholdDirection.GE),
    _spec(V7KPIName.SAFE_ABSTAIN_RATE,
          phase="Exit", green="safe-abstain within rubric band",
          fail="abstain calibration drifting",
          threshold=0.20, unit="ratio", direction=ThresholdDirection.LE),
    _spec(V7KPIName.COMMITTED_ARTIFACT_UWG_RECEIPT_COMPLETENESS,
          phase="Exit", green="100% committed-artifact refs carry UWG receipt",
          fail="invariant 27 broken",
          threshold=1.0, unit="ratio", direction=ThresholdDirection.GE),
    # L2 v4
    _spec(V7KPIName.PASS_K_COMMIT_RELIABILITY,
          phase="L2", green=">= 99% commits hit pass^k threshold",
          fail="commit-path reliability broken",
          threshold=0.99, unit="ratio", direction=ThresholdDirection.GE),
    _spec(V7KPIName.PER_TRIAL_ISOLATION_VIOLATIONS,
          phase="L2", green="0 cross-trial state bleed",
          fail="invariant 9 broken",
          threshold=0.0, unit="count", direction=ThresholdDirection.EQ),
    _spec(V7KPIName.BOUNDED_WORK_OVERRUN_RATE,
          phase="L2", green="<= 1% steps exceed bounded budget",
          fail="bounded-work invariant slipping",
          threshold=0.01, unit="ratio", direction=ThresholdDirection.LE),
    _spec(V7KPIName.CONFIDENCE_ROUTING_MISROUTE_RATE,
          phase="L2", green="<= 5% misrouted confidence-aware dispatches",
          fail="confidence routing degraded",
          threshold=0.05, unit="ratio", direction=ThresholdDirection.LE),
)


V7_KPI_SPECS: Mapping[V7KPIName, V6KPISpec] = MappingProxyType(
    {spec.name: spec for spec in _V7_KPI_SPECS_RAW}  # type: ignore[misc]
)
"""Frozen registry of all v7+governance+exit+L2 KPI specs."""


# Merged spec mapping. Mypy can't unify the two enum types, so we type the
# merged map as ``Mapping[str, V6KPISpec]`` — name lookups go through
# ``.value`` at runtime.
ALL_KPI_SPECS: Mapping[str, V6KPISpec] = MappingProxyType(
    {**{n.value: s for n, s in V6_KPI_SPECS.items()},
     **{n.value: s for n, s in V7_KPI_SPECS.items()}}
)
"""Unified mapping over both v6 and v7 specs, keyed by the string KPI name."""


# ---------------------------------------------------------------------------
# Unified board: accepts samples for any registered name.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class V7KPISample:
    """Sample for a v7 (or governance/exit/L2) KPI.

    Mirrors :class:`V6KPISample` but typed against :class:`V7KPIName`.
    """

    name: V7KPIName
    value: float
    timestamp: float
    source: str
    metadata: Mapping[str, object]


class UnifiedKPIBoard(V6KPIBoard):
    """KPI board that accepts both v6 and v7 KPI samples.

    Inherits all v6 behavior; v7 names lookup via :data:`ALL_KPI_SPECS`.
    """

    def record(self, sample) -> None:  # type: ignore[override]
        """Record a v6 or v7 sample.

        Accepts either :class:`V6KPISample` or :class:`V7KPISample` (or any
        object exposing ``.name``, ``.value``, ``.timestamp``, ``.source``,
        ``.metadata``).
        """
        name_obj = getattr(sample, "name", None)
        if name_obj is None:
            raise ValueError("sample missing .name attribute")
        name_value = name_obj.value if hasattr(name_obj, "value") else str(name_obj)
        if name_value not in ALL_KPI_SPECS:
            raise ValueError(f"unknown KPI name: {name_value!r}")
        # Store keyed by the original enum object (v6 or v7) — V6KPIBoard's
        # internal dict is typed against V6KPIName, but keys are the actual
        # enum members at runtime.
        self._latest[name_obj] = sample  # type: ignore[index]


__all__ = [
    # re-exports from v6
    "V6KPIName",
    "V6KPISample",
    "V6KPISpec",
    "V6KPIStatus",
    "V6HealthSnapshot",
    "V6KPIBoard",
    "V6_KPI_SPECS",
    "HEALTH_REQUIRED_KPIS",
    "ThresholdDirection",
    "evaluate_sample",
    # new in v7
    "V7KPIName",
    "V7KPISample",
    "V7_KPI_SPECS",
    "ALL_KPI_SPECS",
    "UnifiedKPIBoard",
]
