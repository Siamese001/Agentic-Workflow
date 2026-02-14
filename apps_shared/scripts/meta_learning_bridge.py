"""APPS_* Meta-Learning Emit-Only Bridge — Wave 7.0.9.

Pure emit-only bridge for APPS_* domains to produce meta-learning artifacts.
Calls L7 builders to construct frozen, deterministic artifacts.

HARD RULES
----------
- MUST NOT import any executors.
- MUST NOT call any apply/mutation functions from L7.
- MUST NOT write files or mutate any configuration.
- Returns artifacts only; callers decide what to do with them.
"""

from __future__ import annotations

from agentic_core.L0_routing.types.v15_p2_types import SemanticClockSnapshot
from agentic_core.L7_meta_learning.types.app_signal_types import (
    AppSignalEventArtifact,
    build_app_signal_event,
)
from agentic_core.L7_meta_learning.types.meta_learning_types import (
    MetaLearningProposalArtifact,
    build_meta_learning_proposal,
)


def emit_app_signal_event(
    *,
    app_id: str,
    run_id: str,
    message_id: str,
    metric_name: str,
    metric_value: float,
    semantic_clock: SemanticClockSnapshot,
    segment_id: str | None = None,
    outcome_label: str | None = None,
    timestamp_utc: str | None = None,
) -> AppSignalEventArtifact:
    """Emit an APP_SIGNAL_EVENT artifact via the L7 builder.

    Pure function — no side effects, no file writes, no apply calls.

    Parameters
    ----------
    app_id : str
        Application identifier (e.g. "apps_rg", "apps_lic").
    run_id : str
        Unique run/session identifier.
    message_id : str
        Unique message identifier within the run.
    metric_name : str
        Name of the metric (must be non-empty).
    metric_value : float
        Observed metric value (must be finite).
    semantic_clock : SemanticClockSnapshot
        Required immutable clock snapshot.
    segment_id : str | None
        Optional sub-segment identifier.
    outcome_label : str | None
        Optional categorical outcome label.
    timestamp_utc : str | None
        Optional ISO-8601 timestamp string.

    Returns
    -------
    AppSignalEventArtifact
        Frozen, deterministic signal event artifact.
    """
    return build_app_signal_event(
        app_id=app_id,
        run_id=run_id,
        message_id=message_id,
        segment_id=segment_id,
        metric_name=metric_name,
        metric_value=metric_value,
        outcome_label=outcome_label,
        timestamp_utc=timestamp_utc,
        semantic_clock=semantic_clock,
    )


def propose_from_signal_aggregate(
    *,
    app_id: str,
    target_component: str,
    before: dict,
    after: dict,
    metric_name: str,
    baseline: float,
    candidate: float,
    evidence_hash: str,
    semantic_clock: SemanticClockSnapshot,
    policy_config_hash: str | None = None,
) -> MetaLearningProposalArtifact:
    """Build a MetaLearningProposalArtifact from an APP signal aggregate.

    Pure function — no side effects, no file writes, no apply calls.
    The proposer field is set to "apps_<name>" derived from app_id.

    Parameters
    ----------
    app_id : str
        Application identifier (e.g. "apps_rg", "apps_lic").
    target_component : str
        Target of the proposed change (must NOT be in IMMUTABLE_COMPONENTS).
    before, after : dict
        State before and after the proposed change.
    metric_name : str
        Name of the objective metric.
    baseline, candidate : float
        Metric values before and after the proposed change.
    evidence_hash : str
        SHA-256 of the supporting evidence bundle.
    semantic_clock : SemanticClockSnapshot
        Required immutable clock snapshot.
    policy_config_hash : str | None
        Optional hash of the governing policy config.

    Returns
    -------
    MetaLearningProposalArtifact
        Frozen, deterministic proposal artifact.
    """
    proposer = app_id if app_id.startswith("apps_") else f"apps_{app_id}"
    return build_meta_learning_proposal(
        semantic_clock=semantic_clock,
        proposer=proposer,
        target_component=target_component,
        before=before,
        after=after,
        metric_name=metric_name,
        baseline=baseline,
        candidate=candidate,
        evidence_hash=evidence_hash,
        policy_config_hash=policy_config_hash,
    )
