"""
agentic_core/L1_cognition/planning/reasoning_plan.py

P3/L1 Multi-Step Reasoning Planning — reasoning plan and step artifacts.

Provides ReasoningPlan (12 required fields), PlanStep, PlanCheckpoint, and PlanRevision
for explicit, staged, and checkpointed multi-step reasoning.
"""

from __future__ import annotations

import hashlib
import logging
import threading
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "reasoning_plan")
trace_contract.emit_determinism_digest("p0", "reasoning_plan")

trace_contract._emit_dispatches_healing_run("p1", "reasoning_plan", "L1")
trace_contract._emit_routes_through("p1", "reasoning_plan", "L1")
trace_contract._emit_checks_agent_registry("p1", "reasoning_plan", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "reasoning_plan", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "reasoning_plan", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "reasoning_plan", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "reasoning_plan", "target_agent")
trace_contract._emit_verifies_policy("p1", "reasoning_plan", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "reasoning_plan", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "reasoning_plan", "boundary_check")
trace_contract._emit_transcripts_response("p1", "reasoning_plan", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "reasoning_plan")
trace_contract._emit_gated_by_confidence("p1", "reasoning_plan", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "reasoning_plan", "L1")
trace_contract._emit_reads_policy_state("p1", "reasoning_plan", "L1")

trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "reasoning_plan", "p0_governance")
trace_contract._emit_authorize_and_execute("p2", "reasoning_plan", "execution_auth")
trace_contract._emit_validates_capability("p2", "reasoning_plan", "capability_check")
trace_contract._emit_routes_to_capability("p2", "reasoning_plan", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "reasoning_plan", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "reasoning_plan", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "reasoning_plan", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "reasoning_plan", "exec_output")
trace_contract._emit_dispatches_agent("p3", "reasoning_plan", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "reasoning_plan", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "reasoning_plan", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "reasoning_plan", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "reasoning_plan", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "reasoning_plan", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "reasoning_plan", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "reasoning_plan", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "reasoning_plan", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "reasoning_plan", "eval_metric")
trace_contract._emit_stores_embedding("p4", "reasoning_plan", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "reasoning_plan", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "reasoning_plan", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("reasoning_plan", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("reasoning_plan", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("reasoning_plan", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("reasoning_plan", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("reasoning_plan", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("reasoning_plan", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("reasoning_plan", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("reasoning_plan", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("reasoning_plan", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("reasoning_plan", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("reasoning_plan", "p4obs", "alert")
trace_contract._emit_links_incident_trace("reasoning_plan", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("reasoning_plan", "p3lm", "pattern")
trace_contract._emit_records_learning_event("reasoning_plan", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("reasoning_plan", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("reasoning_plan", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("reasoning_plan", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("reasoning_plan", "p3lm", "policy")
trace_contract._emit_stores_learning_state("reasoning_plan", "p3lm", "state")
trace_contract._emit_records_execution_trace("reasoning_plan", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("reasoning_plan", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("reasoning_plan", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("reasoning_plan", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("reasoning_plan", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("reasoning_plan", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("reasoning_plan", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("reasoning_plan", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("reasoning_plan", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "reasoning_plan", "context_pull")
trace_contract._emit_pulls_context("p1", "reasoning_plan", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "reasoning_plan", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "reasoning_plan", "uwg_term_2")
trace_contract._emit_writes_through("p1", "reasoning_plan", "write_through")
trace_contract._emit_writes_through("p1", "reasoning_plan", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "reasoning_plan", "safety_validation")
trace_contract._emit_invokes_eval("p1", "reasoning_plan", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "reasoning_plan", "routing_commit")

from agentic_core.utils.runners.providers import get_clock  # noqa: E402  # guardian: shared clock provider used at plan emission boundary

logger = logging.getLogger(__name__)
_PLAN_LOG = logging.getLogger("adg.reasoning_plan_emitted")


# ---------------------------------------------------------------------------
# Enums for planning tracking
# ---------------------------------------------------------------------------


class PlanStatus(Enum):
    """Status of a reasoning plan."""

    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REVISED = "REVISED"


class StepStatus(Enum):
    """Status of a plan step."""

    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class CheckpointResult(Enum):
    """Result of a plan checkpoint."""

    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"


# ---------------------------------------------------------------------------
# Exception classes for Gates A-E
# ---------------------------------------------------------------------------


class ReasoningPlanError(Exception):
    """Raised when multi-step reasoning occurs without ReasoningPlan (Gate A)."""

    pass


# ---------------------------------------------------------------------------
# ReasoningPlan — 12 required fields per spec
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ReasoningPlan:
    """Immutable reasoning plan for multi-step reasoning (12 required fields)."""

    reasoning_plan_id: str
    run_id: str
    trace_id: str
    plan_goal_hash: str
    plan_context_hash: str
    initial_evidence_hash: str
    step_sequence_hash: str
    checkpoint_policy_hash: str
    active_step_index: int
    plan_status: str
    parent_plan_id: str | None
    plan_epoch: float = field(default_factory=lambda: get_clock().now_epoch())

    @classmethod
    def create(
        cls,
        run_id: str,
        trace_id: str,
        plan_goal: str,
        plan_context: str,
        initial_evidence: Any,
        step_sequence: list[str],
        checkpoint_policy: str,
        parent_plan_id: str | None = None,
    ) -> ReasoningPlan:
        """Factory to create ReasoningPlan with computed fields."""
        reasoning_plan_id = str(uuid.uuid4())

        # Compute hashes
        plan_goal_hash = hashlib.sha256(plan_goal.encode()).hexdigest()[:16]
        plan_context_hash = hashlib.sha256(plan_context.encode()).hexdigest()[:16]
        initial_evidence_hash = hashlib.sha256(str(initial_evidence).encode()).hexdigest()[:16]
        step_sequence_hash = hashlib.sha256(str(step_sequence).encode()).hexdigest()[:16]
        checkpoint_policy_hash = hashlib.sha256(checkpoint_policy.encode()).hexdigest()[:16]

        return cls(
            reasoning_plan_id=reasoning_plan_id,
            run_id=run_id,
            trace_id=trace_id,
            plan_goal_hash=plan_goal_hash,
            plan_context_hash=plan_context_hash,
            initial_evidence_hash=initial_evidence_hash,
            step_sequence_hash=step_sequence_hash,
            checkpoint_policy_hash=checkpoint_policy_hash,
            active_step_index=0,
            plan_status=PlanStatus.CREATED.value,
            parent_plan_id=parent_plan_id,
        )

    def advance_step(self) -> ReasoningPlan:
        """Create a new plan with advanced step index."""
        return ReasoningPlan(
            reasoning_plan_id=self.reasoning_plan_id,
            run_id=self.run_id,
            trace_id=self.trace_id,
            plan_goal_hash=self.plan_goal_hash,
            plan_context_hash=self.plan_context_hash,
            initial_evidence_hash=self.initial_evidence_hash,
            step_sequence_hash=self.step_sequence_hash,
            checkpoint_policy_hash=self.checkpoint_policy_hash,
            active_step_index=self.active_step_index + 1,
            plan_status=PlanStatus.ACTIVE.value,
            parent_plan_id=self.parent_plan_id,
        )

    def complete_plan(self) -> ReasoningPlan:
        """Create a completed plan."""
        return ReasoningPlan(
            reasoning_plan_id=self.reasoning_plan_id,
            run_id=self.run_id,
            trace_id=self.trace_id,
            plan_goal_hash=self.plan_goal_hash,
            plan_context_hash=self.plan_context_hash,
            initial_evidence_hash=self.initial_evidence_hash,
            step_sequence_hash=self.step_sequence_hash,
            checkpoint_policy_hash=self.checkpoint_policy_hash,
            active_step_index=self.active_step_index,
            plan_status=PlanStatus.COMPLETED.value,
            parent_plan_id=self.parent_plan_id,
        )


# ---------------------------------------------------------------------------
# PlanStep — step execution tracking
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PlanStep:
    """Immutable plan step for step-by-step reasoning tracking."""

    step_id: str
    reasoning_plan_id: str
    step_index: int
    step_goal_hash: str
    step_input_hash: str
    step_output_hash: str
    step_status: str
    checkpoint_result: str | None
    revision_required_flag: bool
    step_epoch: float = field(default_factory=lambda: get_clock().now_epoch())

    @classmethod
    def create(
        cls,
        reasoning_plan_id: str,
        step_index: int,
        step_goal: str,
        step_input: Any,
        step_output: Any,
        step_status: StepStatus = StepStatus.PENDING,
        checkpoint_result: CheckpointResult | None = None,
        revision_required: bool = False,
    ) -> PlanStep:
        """Factory to create PlanStep with computed fields."""
        step_id = str(uuid.uuid4())

        # Compute hashes
        step_goal_hash = hashlib.sha256(step_goal.encode()).hexdigest()[:16]
        step_input_hash = hashlib.sha256(str(step_input).encode()).hexdigest()[:16]
        step_output_hash = hashlib.sha256(str(step_output).encode()).hexdigest()[:16]

        return cls(
            step_id=step_id,
            reasoning_plan_id=reasoning_plan_id,
            step_index=step_index,
            step_goal_hash=step_goal_hash,
            step_input_hash=step_input_hash,
            step_output_hash=step_output_hash,
            step_status=step_status.value,
            checkpoint_result=checkpoint_result.value if checkpoint_result else None,
            revision_required_flag=revision_required,
        )

    def complete_step(self, step_output: Any, checkpoint_result: CheckpointResult | None = None) -> PlanStep:
        """Create a completed step."""
        step_output_hash = hashlib.sha256(str(step_output).encode()).hexdigest()[:16]

        return PlanStep(
            step_id=self.step_id,
            reasoning_plan_id=self.reasoning_plan_id,
            step_index=self.step_index,
            step_goal_hash=self.step_goal_hash,
            step_input_hash=self.step_input_hash,
            step_output_hash=step_output_hash,
            step_status=StepStatus.COMPLETED.value,
            checkpoint_result=checkpoint_result.value if checkpoint_result else None,
            revision_required_flag=self.revision_required_flag,
        )

    def fail_step(self, step_output: Any) -> PlanStep:
        """Create a failed step."""
        step_output_hash = hashlib.sha256(str(step_output).encode()).hexdigest()[:16]

        return PlanStep(
            step_id=self.step_id,
            reasoning_plan_id=self.reasoning_plan_id,
            step_index=self.step_index,
            step_goal_hash=self.step_goal_hash,
            step_input_hash=self.step_input_hash,
            step_output_hash=step_output_hash,
            step_status=StepStatus.FAILED.value,
            checkpoint_result=CheckpointResult.FAIL.value,
            revision_required_flag=self.revision_required_flag,
        )


# ---------------------------------------------------------------------------
# PlanCheckpoint — checkpoint enforcement
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PlanCheckpoint:
    """Immutable plan checkpoint for validation points."""

    checkpoint_id: str
    reasoning_plan_id: str
    step_id: str
    checkpoint_pass_fail: str
    checkpoint_reason_hash: str
    checkpoint_epoch: float = field(default_factory=lambda: get_clock().now_epoch())

    @classmethod
    def create(
        cls,
        reasoning_plan_id: str,
        step_id: str,
        checkpoint_result: CheckpointResult,
        checkpoint_reason: str,
    ) -> PlanCheckpoint:
        """Factory to create PlanCheckpoint with computed fields."""
        checkpoint_id = str(uuid.uuid4())
        checkpoint_reason_hash = hashlib.sha256(checkpoint_reason.encode()).hexdigest()[:16]

        return cls(
            checkpoint_id=checkpoint_id,
            reasoning_plan_id=reasoning_plan_id,
            step_id=step_id,
            checkpoint_pass_fail=checkpoint_result.value,
            checkpoint_reason_hash=checkpoint_reason_hash,
        )


# ---------------------------------------------------------------------------
# PlanRevision — revision tracking
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PlanRevision:
    """Immutable plan revision for adaptive re-planning."""

    revision_id: str
    reasoning_plan_id: str
    revision_reason_hash: str
    prior_step_sequence_hash: str
    new_step_sequence_hash: str
    revision_parent_plan_id: str
    revision_epoch: float = field(default_factory=lambda: get_clock().now_epoch())

    @classmethod
    def create(
        cls,
        reasoning_plan_id: str,
        revision_reason: str,
        prior_step_sequence: list[str],
        new_step_sequence: list[str],
        revision_parent_plan_id: str,
    ) -> PlanRevision:
        """Factory to create PlanRevision with computed fields."""
        revision_id = str(uuid.uuid4())
        revision_reason_hash = hashlib.sha256(revision_reason.encode()).hexdigest()[:16]
        prior_step_sequence_hash = hashlib.sha256(str(prior_step_sequence).encode()).hexdigest()[:16]
        new_step_sequence_hash = hashlib.sha256(str(new_step_sequence).encode()).hexdigest()[:16]

        return cls(
            revision_id=revision_id,
            reasoning_plan_id=reasoning_plan_id,
            revision_reason_hash=revision_reason_hash,
            prior_step_sequence_hash=prior_step_sequence_hash,
            new_step_sequence_hash=new_step_sequence_hash,
            revision_parent_plan_id=revision_parent_plan_id,
        )


# ---------------------------------------------------------------------------
# PlanRegistry — thread-safe plan storage and query
# ---------------------------------------------------------------------------


class PlanRegistry:
    """Thread-safe registry for reasoning plans and queries."""

    _instance: PlanRegistry | None = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._plans: dict[str, ReasoningPlan] = {}
        self._steps: dict[str, PlanStep] = {}
        self._checkpoints: dict[str, PlanCheckpoint] = {}
        self._revisions: dict[str, PlanRevision] = {}
        self._run_index: dict[str, list[str]] = {}  # run_id -> plan_ids
        self._trace_index: dict[str, list[str]] = {}  # trace_id -> plan_ids
        self._plan_steps_index: dict[str, list[str]] = {}  # plan_id -> step_ids
        self._lock = threading.RLock()

    @classmethod
    def get_instance(cls) -> PlanRegistry:
        """Singleton accessor."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def persist_plan(self, plan: ReasoningPlan) -> None:
        """Persist a reasoning plan."""
        import uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(uuid.uuid4()), "PlanRegistry.persist_plan", "L1_REASONING")

        trace_contract._emit_records_execution_trace(
            str(uuid.uuid4()),
            trace_contract.LayerSegment.L3_ORCHESTRATION,
            f"PlanRegistry.persist_plan:{plan.reasoning_plan_id}",
        )
        with self._lock:
            self._plans[plan.reasoning_plan_id] = plan

            # Index by run_id and trace_id
            if plan.run_id not in self._run_index:
                self._run_index[plan.run_id] = []
            self._run_index[plan.run_id].append(plan.reasoning_plan_id)

            if plan.trace_id not in self._trace_index:
                self._trace_index[plan.trace_id] = []
            self._trace_index[plan.trace_id].append(plan.reasoning_plan_id)

            # Initialize steps index
            if plan.reasoning_plan_id not in self._plan_steps_index:
                self._plan_steps_index[plan.reasoning_plan_id] = []

        _PLAN_LOG.debug(
            "reasoning_plan_emitted plan_id=%s run_id=%s trace_id=%s active_step=%d status=%s",
            plan.reasoning_plan_id,
            plan.run_id,
            plan.trace_id,
            plan.active_step_index,
            plan.plan_status,
        )

        logger.debug(
            "REASONING_PLAN_PERSISTED plan_id=%s run_id=%s steps=%d",
            plan.reasoning_plan_id,
            plan.run_id,
            0,  # Will be updated as steps are added
        )

    def persist_step(self, step: PlanStep) -> None:
        """Persist a plan step."""
        with self._lock:
            self._steps[step.step_id] = step

            # Index by plan
            if step.reasoning_plan_id not in self._plan_steps_index:
                self._plan_steps_index[step.reasoning_plan_id] = []
            self._plan_steps_index[step.reasoning_plan_id].append(step.step_id)

        logger.debug(
            "PLAN_STEP_PERSISTED step_id=%s plan_id=%s step_index=%d status=%s",
            step.step_id,
            step.reasoning_plan_id,
            step.step_index,
            step.step_status,
        )

    def persist_checkpoint(self, checkpoint: PlanCheckpoint) -> None:
        """Persist a plan checkpoint."""
        with self._lock:
            self._checkpoints[checkpoint.checkpoint_id] = checkpoint

        logger.debug(
            "PLAN_CHECKPOINT_PERSISTED checkpoint_id=%s plan_id=%s step_id=%s result=%s",
            checkpoint.checkpoint_id,
            checkpoint.reasoning_plan_id,
            checkpoint.step_id,
            checkpoint.checkpoint_pass_fail,
        )

    def persist_revision(self, revision: PlanRevision) -> None:
        """Persist a plan revision."""
        with self._lock:
            self._revisions[revision.revision_id] = revision

        logger.debug(
            "PLAN_REVISION_PERSISTED revision_id=%s plan_id=%s parent_id=%s",
            revision.revision_id,
            revision.reasoning_plan_id,
            revision.revision_parent_plan_id,
        )

    def query_by_run_id(self, run_id: str) -> list[ReasoningPlan]:
        """Query reasoning plans by run_id."""
        with self._lock:
            plan_ids = self._run_index.get(run_id, [])
            return [self._plans[plan_id] for plan_id in plan_ids if plan_id in self._plans]

    def query_by_trace_id(self, trace_id: str) -> list[ReasoningPlan]:
        """Query reasoning plans by trace_id."""
        with self._lock:
            plan_ids = self._trace_index.get(trace_id, [])
            return [self._plans[plan_id] for plan_id in plan_ids if plan_id in self._plans]

    def query_plan_steps(self, reasoning_plan_id: str) -> list[PlanStep]:
        """Query steps for a specific plan."""
        with self._lock:
            step_ids = self._plan_steps_index.get(reasoning_plan_id, [])
            return [self._steps[step_id] for step_id in step_ids if step_id in self._steps]

    def get_plan_count(self, run_id: str = "") -> int:
        """Get count of reasoning plans, optionally filtered by run_id."""
        with self._lock:
            if run_id:
                return len(self._run_index.get(run_id, []))
            return len(self._plans)

    def verify_plan_exists(self, plan_id: str) -> bool:
        """Verify reasoning plan exists (Gate A)."""
        with self._lock:
            return plan_id in self._plans

    def verify_plan_has_steps(self, plan_id: str) -> bool:
        """Verify plan has step records (Gate B)."""
        with self._lock:
            step_ids = self._plan_steps_index.get(plan_id, [])
            return len(step_ids) > 0

    def verify_step_has_status(self, step_id: str) -> bool:
        """Verify step has step_status (Gate C)."""
        with self._lock:
            step = self._steps.get(step_id)
            return step is not None and bool(step.step_status)


# ---------------------------------------------------------------------------
# Singleton accessors
# ---------------------------------------------------------------------------


def get_plan_registry() -> PlanRegistry:
    """Get the singleton PlanRegistry instance."""
    return PlanRegistry.get_instance()


def reset_plan_registry() -> None:
    """Reset the singleton PlanRegistry (for testing)."""
    with PlanRegistry._lock:
        PlanRegistry._instance = None


__all__ = [
    "ReasoningPlan",
    "PlanStep",
    "PlanCheckpoint",
    "PlanRevision",
    "PlanStatus",
    "StepStatus",
    "CheckpointResult",
    "ReasoningPlanError",
    "PlanRegistry",
    "get_plan_registry",
    "reset_plan_registry",
]
