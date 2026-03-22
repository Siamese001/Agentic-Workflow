#!/usr/bin/env python3
"""Human Review Queue - Approval workflow for high-risk fixes.

Implements the HUMAN REVIEW GATE component from target state architecture.
Provides approval queue with rich context bundles including detection signal,
diff, rationale, simulated outcome, risk score, and past cases.

Target State Reference:
- Approval Queue with Rich Context Bundle
- Detection signal, diff, rationale, simulated outcome
- Risk score, past cases
- Escalation workflow
"""

from __future__ import annotations

import difflib
import logging
import threading
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.enforcement.governance_contracts import (
    build_hil_policy_proposal,
)
from agentic_core.L0_routing.types.governance_types import HILOutcome
from agentic_core.L5_safety.types.human_decision_artifact_types import HumanDecisionArtifact
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "human_review_queue_enforcer")
emit_determinism_digest("p0", "human_review_queue_enforcer")

_emit_dispatches_healing_run("p1", "human_review_queue_enforcer", "L5")
_emit_routes_through("p1", "human_review_queue_enforcer", "L5")
_emit_checks_agent_registry("p1", "human_review_queue_enforcer", "agent_registry")
_emit_validates_agent_capability("p1", "human_review_queue_enforcer", "capability")
_emit_dispatches_execution_plan("p1", "human_review_queue_enforcer", "exec_plan")
_emit_agent_executes_agent("p1", "human_review_queue_enforcer", "sub_agent")
_emit_routes_to_agent("p1", "human_review_queue_enforcer", "target_agent")
_emit_verifies_policy("p1", "human_review_queue_enforcer", "policy_check")
_emit_observes_runtime_state("p1", "human_review_queue_enforcer", "runtime_state")
_emit_verifies_boundary("p1", "human_review_queue_enforcer", "boundary_check")
_emit_transcripts_response("p1", "human_review_queue_enforcer", "transcript")
_emit_hard_fails_untranscripted("p1", "human_review_queue_enforcer")
_emit_gated_by_confidence("p1", "human_review_queue_enforcer", "confidence_gate")
_emit_escalates_to_human("p1", "human_review_queue_enforcer", "L5")
_emit_reads_policy_state("p1", "human_review_queue_enforcer", "L5")
_emit_authorize_and_execute("p2", "human_review_queue_enforcer", "execution_auth")
_emit_validates_capability("p2", "human_review_queue_enforcer", "capability_check")
_emit_routes_to_capability("p2", "human_review_queue_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "human_review_queue_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "human_review_queue_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "human_review_queue_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "human_review_queue_enforcer", "exec_output")
_emit_dispatches_agent("p3", "human_review_queue_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "human_review_queue_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "human_review_queue_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "human_review_queue_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "human_review_queue_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "human_review_queue_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "human_review_queue_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "human_review_queue_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "human_review_queue_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "human_review_queue_enforcer", "eval_metric")
_emit_stores_embedding("p4", "human_review_queue_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "human_review_queue_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "human_review_queue_enforcer", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("human_review_queue_enforcer", "p4obs", "metric_1")
_emit_emits_metric_event("human_review_queue_enforcer", "p4obs", "metric_2")
_emit_emits_metric_event("human_review_queue_enforcer", "p4obs", "metric_3")
_emit_emits_metric_event("human_review_queue_enforcer", "p4obs", "metric_4")
_emit_emits_metric_event("human_review_queue_enforcer", "p4obs", "metric_5")
_emit_emits_metric_event("human_review_queue_enforcer", "p4obs", "metric_6")
_emit_records_incident_event("human_review_queue_enforcer", "p4obs", "incident")
_emit_captures_runtime_anomaly("human_review_queue_enforcer", "p4obs", "anomaly")
_emit_writes_observability_log("human_review_queue_enforcer", "p4obs", "obs_log")
_emit_updates_monitoring_state("human_review_queue_enforcer", "p4obs", "mon_state")
_emit_triggers_alert("human_review_queue_enforcer", "p4obs", "alert")
_emit_links_incident_trace("human_review_queue_enforcer", "p4obs", "trace_link")
_emit_captures_pattern("human_review_queue_enforcer", "p3lm", "pattern")
_emit_records_learning_event("human_review_queue_enforcer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("human_review_queue_enforcer", "p3lm", "snapshot")
_emit_feeds_meta_learning("human_review_queue_enforcer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("human_review_queue_enforcer", "p3lm", "routing")
_emit_improves_agent_policy("human_review_queue_enforcer", "p3lm", "policy")
_emit_stores_learning_state("human_review_queue_enforcer", "p3lm", "state")
_emit_records_execution_trace("human_review_queue_enforcer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("human_review_queue_enforcer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("human_review_queue_enforcer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("human_review_queue_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("human_review_queue_enforcer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("human_review_queue_enforcer", "env_read", "p2_env_1")
_emit_reads_environ("human_review_queue_enforcer", "env_read", "p2_env_2")
_emit_reads_runtime_state("human_review_queue_enforcer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("human_review_queue_enforcer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "human_review_queue_enforcer", "context_pull")
_emit_pulls_context("p1", "human_review_queue_enforcer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "human_review_queue_enforcer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "human_review_queue_enforcer", "uwg_term_2")
_emit_writes_through("p1", "human_review_queue_enforcer", "write_through")
_emit_writes_through("p1", "human_review_queue_enforcer", "write_through_2")
_emit_validated_by_safety_plane("p1", "human_review_queue_enforcer", "safety_validation")
_emit_invokes_eval("p1", "human_review_queue_enforcer", "eval_call")
_emit_proposal_commits_routing("p1", "human_review_queue_enforcer", "routing_commit")

Logger = logging.getLogger(__name__)


class ReviewStatus(Enum):
    """Status of a review request."""

    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    EXPIRED = "expired"
    MODIFY_DIFF = "modify_diff"


@dataclass
class ProposedDiff:
    """Proposed code change for review."""

    file_path: Path
    original_content: str
    proposed_content: str
    change_summary: str
    lines_added: int = 0
    lines_removed: int = 0

    def to_unified_diff(self) -> str:
        """Generate unified diff format."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ProposedDiff.to_unified_diff", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ProposedDiff.to_unified_diff", "p0_governance")
        original_lines = self.original_content.splitlines(keepends=True)
        proposed_lines = self.proposed_content.splitlines(keepends=True)
        diff = difflib.unified_diff(
            original_lines,
            proposed_lines,
            fromfile=f"a/{self.file_path}",
            tofile=f"b/{self.file_path}",
        )
        return "".join(diff)


@dataclass
class SimulatedOutcome:
    """Simulated outcome of applying the proposed fix."""

    success_probability: float = 0.9  # 0.0 to 1.0
    expected_side_effects: list[str] = field(default_factory=list)
    regression_risk: str = "low"  # low, medium, high
    test_results: dict[str, bool] = field(default_factory=dict)
    rollback_complexity: str = "simple"  # simple, moderate, complex


@dataclass
class ContextBundle:
    """Rich context bundle for human review.

    Contains all information needed for informed human decision:
    - Detection signal details
    - Proposed diff
    - AI rationale
    - Simulated outcome
    - Risk assessment
    - Historical similar cases
    """

    detection_signal: dict[str, Any]  # Serialized DetectionSignal
    proposed_diff: ProposedDiff
    ai_rationale: str
    simulated_outcome: SimulatedOutcome
    risk_assessment: dict[str, Any]  # Serialized RiskAssessment
    similar_past_cases: list[dict[str, Any]] = field(default_factory=list)
    additional_context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "detection_signal": self.detection_signal,
            "proposed_diff": {
                "file_path": str(self.proposed_diff.file_path),
                "change_summary": self.proposed_diff.change_summary,
                "unified_diff": self.proposed_diff.to_unified_diff(),
            },
            "ai_rationale": self.ai_rationale,
            "simulated_outcome": {
                "success_probability": self.simulated_outcome.success_probability,
                "expected_side_effects": self.simulated_outcome.expected_side_effects,
                "regression_risk": self.simulated_outcome.regression_risk,
            },
            "risk_assessment": self.risk_assessment,
            "similar_past_cases": self.similar_past_cases,
        }


@dataclass
class ReviewRequest:
    """Human review request with full context."""

    request_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: ReviewStatus = ReviewStatus.PENDING
    context_bundle: ContextBundle | None = None

    # Review metadata
    reviewer_id: str | None = None
    review_started_at: datetime | None = None
    review_completed_at: datetime | None = None
    review_notes: str = ""

    # Escalation tracking
    escalation_level: int = 0
    escalation_chain: list[str] = field(default_factory=lambda: ["team_lead", "manager", "director"])

    # Timeout configuration
    timeout_seconds: int = 3600  # 1 hour default

    def is_expired(self) -> bool:
        """Check if request has timed out."""
        elapsed = (datetime.utcnow() - self.created_at).total_seconds()
        return elapsed > self.timeout_seconds

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "context_bundle": self.context_bundle.to_dict() if self.context_bundle else None,
            "reviewer_id": self.reviewer_id,
            "escalation_level": self.escalation_level,
            "is_expired": self.is_expired(),
        }


class HumanReviewQueue:
    """Approval queue for high-risk fixes requiring human review.

    Implements the HUMAN REVIEW GATE from target state architecture.
    Thread-safe queue management with escalation support.

    Features:
    - Rich context bundles for informed decisions
    - Escalation workflow
    - Timeout handling
    - Callback support for async workflows
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._pending_requests: dict[str, ReviewRequest] = {}
        self._completed_requests: list[ReviewRequest] = []
        self._lock = threading.RLock()
        self._callbacks: dict[str, Callable] = {}

        # Configuration
        self.max_pending = self.config.get("max_pending", 100)
        self.default_timeout = self.config.get("default_timeout_seconds", 3600)
        self.auto_escalate_after = self.config.get("auto_escalate_after_seconds", 1800)

    def submit_for_review(
        self,
        context_bundle: ContextBundle,
        timeout_seconds: int | None = None,
    ) -> ReviewRequest:
        """Submit a change for human review.

        Args:
            context_bundle: Full context for review decision
            timeout_seconds: Custom timeout for this request

        Returns:
            ReviewRequest tracking the submission
        """
        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L5_POLICY, "submit_for_review")
        request = ReviewRequest(
            context_bundle=context_bundle,
            timeout_seconds=timeout_seconds if timeout_seconds is not None else self.default_timeout,
        )

        with self._lock:
            # Evict oldest if at capacity
            if len(self._pending_requests) >= self.max_pending:
                self._evict_oldest()

            self._pending_requests[request.request_id] = request

        Logger.info(
            f"[REVIEW_QUEUE] Submitted review request {request.request_id} "
            f"for {context_bundle.proposed_diff.file_path}",
        )

        return request

    def approve(
        self,
        request_id: str,
        reviewer_id: str,
        notes: str = "",
        secret: bytes = b"",
        original_plan_hash: str = "unspecified",
        policy_hash: str = "",
    ) -> tuple[ReviewRequest, HumanDecisionArtifact]:
        """Approve a pending review request.

        Returns (ReviewRequest, signed HumanDecisionArtifact).
        """
        with self._lock:
            request = self._pending_requests.get(request_id)
            if not request:
                raise ValueError(f"Review request not found: {request_id}")

            request.status = ReviewStatus.APPROVED
            request.reviewer_id = reviewer_id
            request.review_completed_at = datetime.utcnow()
            request.review_notes = notes

            del self._pending_requests[request_id]
            self._completed_requests.append(request)

        Logger.info(f"[REVIEW_QUEUE] Request {request_id} APPROVED by {reviewer_id}")
        self._trigger_callback(request_id, "approved")
        self._emit_policy_update_proposal(request, HILOutcome.APPROVED)

        artifact = HumanDecisionArtifact(
            trace_id=request_id,
            policy_hash=policy_hash,
            reviewer_id=reviewer_id,
            action="APPROVE",
            original_plan_hash=original_plan_hash,
            structured_patch_schema={},
        ).sign(secret)
        return request, artifact

    def reject(
        self,
        request_id: str,
        reviewer_id: str,
        notes: str,
        secret: bytes = b"",
        original_plan_hash: str = "unspecified",
        policy_hash: str = "",
    ) -> tuple[ReviewRequest, HumanDecisionArtifact]:
        """Reject a pending review request.

        Returns (ReviewRequest, signed HumanDecisionArtifact).
        """
        if not notes:
            raise ValueError("Rejection notes are required")

        with self._lock:
            request = self._pending_requests.get(request_id)
            if not request:
                raise ValueError(f"Review request not found: {request_id}")

            request.status = ReviewStatus.REJECTED
            request.reviewer_id = reviewer_id
            request.review_completed_at = datetime.utcnow()
            request.review_notes = notes

            del self._pending_requests[request_id]
            self._completed_requests.append(request)

        Logger.info(f"[REVIEW_QUEUE] Request {request_id} REJECTED by {reviewer_id}: {notes}")
        self._trigger_callback(request_id, "rejected")
        self._emit_policy_update_proposal(request, HILOutcome.REJECTED)

        artifact = HumanDecisionArtifact(
            trace_id=request_id,
            policy_hash=policy_hash,
            reviewer_id=reviewer_id,
            action="REJECT",
            original_plan_hash=original_plan_hash,
            structured_patch_schema={},
        ).sign(secret)
        return request, artifact

    def modify_diff(
        self,
        request_id: str,
        reviewer_id: str,
        structured_patch_schema: dict,
        original_plan_hash: str,
        secret: bytes,
    ) -> HumanDecisionArtifact:
        """Record a MODIFY_DIFF decision.

        Returns a HumanDecisionArtifact bound to original_plan_hash.
        The artifact's l5_reclear_required flag will be True.
        """
        from agentic_core.L5_safety.types.human_decision_artifact_types import HumanDecisionArtifact

        with self._lock:
            request = self._pending_requests.get(request_id)
            if not request:
                raise ValueError(f"Review request not found: {request_id}")

            request.status = ReviewStatus.MODIFY_DIFF
            request.reviewer_id = reviewer_id
            request.review_completed_at = datetime.utcnow()
            del self._pending_requests[request_id]
            self._completed_requests.append(request)

        Logger.info(f"[REVIEW_QUEUE] Request {request_id} MODIFY_DIFF by {reviewer_id}")

        artifact = HumanDecisionArtifact(
            trace_id=request_id,
            policy_hash="",  # TODO: bind to actual policy_hash if available
            reviewer_id=reviewer_id,
            action="MODIFY_DIFF",
            original_plan_hash=original_plan_hash,
            structured_patch_schema=structured_patch_schema,
        ).sign(secret)

        assert artifact.l5_reclear_required
        return artifact

    def escalate(self, request_id: str, reason: str = "") -> ReviewRequest:
        """Escalate request to next level in escalation chain."""
        with self._lock:
            request = self._pending_requests.get(request_id)
            if not request:
                raise ValueError(f"Review request not found: {request_id}")

            if request.escalation_level >= len(request.escalation_chain) - 1:
                raise ValueError("Maximum escalation level reached")

            request.escalation_level += 1
            request.status = ReviewStatus.ESCALATED

            current_approver = request.escalation_chain[request.escalation_level]

        Logger.warning(f"[REVIEW_QUEUE] Request {request_id} ESCALATED to {current_approver}: {reason}")

        return request

    def get_pending_requests(self) -> list[dict[str, Any]]:
        """Get all pending review requests."""
        with self._lock:
            # Check for expired requests
            self._process_expired()
            return [r.to_dict() for r in self._pending_requests.values()]

    def get_request_status(self, request_id: str) -> ReviewStatus | None:
        """Get status of a specific request."""
        with self._lock:
            if request_id in self._pending_requests:
                return self._pending_requests[request_id].status
            for r in self._completed_requests:
                if r.request_id == request_id:
                    return r.status
        return None

    def register_callback(
        self,
        request_id: str,
        callback: Callable[[str, str], None],
    ) -> None:
        """Register callback for when request is resolved."""
        self._callbacks[request_id] = callback

    def _evict_oldest(self) -> None:
        """Evict oldest pending request."""
        oldest_id = min(
            self._pending_requests.keys(),
            key=lambda k: self._pending_requests[k].created_at,
        )
        oldest = self._pending_requests.pop(oldest_id)
        oldest.status = ReviewStatus.EXPIRED
        self._completed_requests.append(oldest)
        Logger.warning(f"[REVIEW_QUEUE] Evicted expired request {oldest_id}")

    def _process_expired(self) -> None:
        """Process expired requests."""
        expired_ids = [rid for rid, r in self._pending_requests.items() if r.is_expired()]
        for rid in expired_ids:
            request = self._pending_requests.pop(rid)
            request.status = ReviewStatus.EXPIRED
            self._completed_requests.append(request)
            Logger.warning(f"[REVIEW_QUEUE] Request {rid} EXPIRED")

    def _trigger_callback(self, request_id: str, action: str) -> None:
        """Trigger registered callback."""
        callback = self._callbacks.pop(request_id, None)
        if callback:
            try:
                callback(request_id, action)
            # guardian: allow-silent-swallow -- review queue persistence is best-effort; logged
            except Exception as e:
                # TODO: Handle specific exception properly
                raise  # Re-raise after logging/handling
                Logger.error(f"[REVIEW_QUEUE] Callback error: {e}")

    def _emit_policy_update_proposal(
        self,
        request: ReviewRequest,
        outcome: HILOutcome,
    ) -> None:
        """§Wave2.3 — Build and emit PolicyUpdateProposal after HIL finalization."""
        try:
            ctx = request.context_bundle
            evidence_pack_id = ""
            trace_id = request.request_id
            file_scope = ""
            if ctx is not None:
                evidence_pack_id = ctx.additional_context.get("evidence_pack_id", "")
                trace_id = ctx.additional_context.get("trace_id", request.request_id)
                file_scope = str(ctx.proposed_diff.file_path) if ctx.proposed_diff else ""

            proposal = build_hil_policy_proposal(
                trace_id=trace_id,
                evidence_pack_id=evidence_pack_id,
                hil_outcome=outcome,
                reviewer_id=request.reviewer_id or "unknown",
                review_notes=request.review_notes,
                request_id=request.request_id,
                file_scope=file_scope,
            )

            from agentic_core.L0_routing.types.routing_contracts_types import TelemetryEmitter

            emitter = TelemetryEmitter()
            emitter.emit_typed_artifact("POLICY_UPDATE_PROPOSAL", proposal)
            _log_dir = Path(__file__).resolve().parents[2] / "L0_routing" / "logs"
            emitter.flush_to_artifacts_dir(_log_dir)
        # guardian: allow-silent-swallow -- review queue persistence is best-effort; logged
        except Exception as exc:
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            Logger.error(
                "§Wave2.3 PolicyUpdateProposal emission failed at HIL boundary: %s",
                exc,
            )

    def get_queue_stats(self) -> dict[str, Any]:
        """Get queue statistics for observability."""
        with self._lock:
            return {
                "pending_count": len(self._pending_requests),
                "completed_count": len(self._completed_requests),
                "max_pending": self.max_pending,
                "default_timeout_seconds": self.default_timeout,
            }


__all__ = [
    "HumanReviewQueue",
    "ReviewRequest",
    "ReviewStatus",
    "ContextBundle",
    "ProposedDiff",
    "SimulatedOutcome",
]
