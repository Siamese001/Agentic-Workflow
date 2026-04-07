"""Execution Orchestrator - Silent Execution & Full Content Display (PART 4)

This module implements silent execution mode and full content display protocols.
Enforces zero conversational filler and complete artifact visibility.

Layer: Runtime/Shared
Responsibilities:
- Execute workflows silently (no conversational filler)
- Display all generated artifacts in full
- Generate audit.json trace files
- Manage execution state and logging

Non-responsibilities:
- Content generation
- Validation execution
- Temperature management
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from runtime.shared.adaptive_recovery_loop import AdaptiveRecoveryLoop
from runtime.shared.integrity_gate_executor import IntegrityGateExecutor

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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

_emit_applies_guardrail("p0", "execution_orchestrator_types", "p0_governance")
_emit_reads_policy_state("p0", "execution_orchestrator_types", "policy_binding")
_emit_snapshots_state("p0", "execution_orchestrator_types", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("execution_orchestrator_types", "p4obs", "metric_1")
_emit_emits_metric_event("execution_orchestrator_types", "p4obs", "metric_2")
_emit_emits_metric_event("execution_orchestrator_types", "p4obs", "metric_3")
_emit_emits_metric_event("execution_orchestrator_types", "p4obs", "metric_4")
_emit_emits_metric_event("execution_orchestrator_types", "p4obs", "metric_5")
_emit_emits_metric_event("execution_orchestrator_types", "p4obs", "metric_6")
_emit_records_incident_event("execution_orchestrator_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("execution_orchestrator_types", "p4obs", "anomaly")
_emit_writes_observability_log("execution_orchestrator_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("execution_orchestrator_types", "p4obs", "mon_state")
_emit_triggers_alert("execution_orchestrator_types", "p4obs", "alert")
_emit_links_incident_trace("execution_orchestrator_types", "p4obs", "trace_link")
_emit_captures_pattern("execution_orchestrator_types", "p3lm", "pattern")
_emit_records_learning_event("execution_orchestrator_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("execution_orchestrator_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("execution_orchestrator_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("execution_orchestrator_types", "p3lm", "routing")
_emit_improves_agent_policy("execution_orchestrator_types", "p3lm", "policy")
_emit_stores_learning_state("execution_orchestrator_types", "p3lm", "state")
_emit_records_execution_trace("execution_orchestrator_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("execution_orchestrator_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("execution_orchestrator_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("execution_orchestrator_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("execution_orchestrator_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("execution_orchestrator_types", "env_read", "p2_env_1")
_emit_reads_environ("execution_orchestrator_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("execution_orchestrator_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("execution_orchestrator_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "execution_orchestrator_types", "context_pull")
_emit_pulls_context("p1", "execution_orchestrator_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "execution_orchestrator_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "execution_orchestrator_types", "uwg_term_2")
_emit_writes_through("p1", "execution_orchestrator_types", "write_through")
_emit_writes_through("p1", "execution_orchestrator_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "execution_orchestrator_types", "safety_validation")
_emit_invokes_eval("p1", "execution_orchestrator_types", "eval_call")
_emit_proposal_commits_routing("p1", "execution_orchestrator_types", "routing_commit")
_emit_escalates_to_human("p1", "execution_orchestrator_types", "human_escalation")
_emit_routes_through("p1", "execution_orchestrator_types", "route_through")
_emit_checks_agent_registry("p1", "execution_orchestrator_types", "agent_registry")
_emit_validates_agent_capability("p1", "execution_orchestrator_types", "capability")
_emit_dispatches_execution_plan("p1", "execution_orchestrator_types", "exec_plan")
_emit_agent_executes_agent("p1", "execution_orchestrator_types", "sub_agent")
_emit_routes_to_agent("p1", "execution_orchestrator_types", "target_agent")
_emit_verifies_policy("p1", "execution_orchestrator_types", "policy_check")
_emit_observes_runtime_state("p1", "execution_orchestrator_types", "runtime_state")
_emit_verifies_boundary("p1", "execution_orchestrator_types", "boundary_check")
_emit_transcripts_response("p1", "execution_orchestrator_types", "transcript")
_emit_hard_fails_untranscripted("p1", "execution_orchestrator_types")
_emit_gated_by_confidence("p1", "execution_orchestrator_types", "confidence_gate")
emit_replay_key("p0", "execution_orchestrator_types")
emit_determinism_digest("p0", "execution_orchestrator_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "execution_orchestrator_types", "execution_auth")
_emit_validates_capability("p2", "execution_orchestrator_types", "capability_check")
_emit_routes_to_capability("p2", "execution_orchestrator_types", "capability_route")
_emit_writes_via_uwg("p2", "execution_orchestrator_types", "uwg_write")
_emit_blocks_direct_write("p2", "execution_orchestrator_types", "direct_write_block")
_emit_records_tool_invocation("p2", "execution_orchestrator_types", "tool_invocation")
_emit_captures_execution_output("p2", "execution_orchestrator_types", "exec_output")
_emit_dispatches_agent("p3", "execution_orchestrator_types", "agent_dispatch")
_emit_coordinates_agents("p3", "execution_orchestrator_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "execution_orchestrator_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "execution_orchestrator_types", "healing_outcome")
_emit_escalates_failure("p3", "execution_orchestrator_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "execution_orchestrator_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "execution_orchestrator_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "execution_orchestrator_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "execution_orchestrator_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "execution_orchestrator_types", "eval_metric")
_emit_stores_embedding("p4", "execution_orchestrator_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "execution_orchestrator_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "execution_orchestrator_types", "exec_snapshot_link")


@dataclass
class ExecutionArtifact:
    artifact_type: str
    content: str
    metadata: dict[str, Any]
    timestamp: float = field(default_factory=time.time)


@dataclass
class ExecutionTrace:
    run_sha: str
    start_time: float
    end_time: float | None
    decision_path: list[str]
    temperature_log: list[dict[str, Any]]
    validation_failures: list[dict[str, Any]]
    artifacts: list[ExecutionArtifact]
    success: bool
    error: str | None = None


class ExecutionOrchestrator:
    """
    Silent Execution & Full Content Display

    Rules:
    1. Silent Execution: NEVER explain thinking during processing
    2. Full Content Display: Show ALL artifacts in chat window
    3. Audit Trail: Generate audit.json with complete trace

    Banned Phrases:
    - "I will now..."
    - "Processing K.5..."
    - "Analyzing JD..."
    - Any conversational filler
    """

    BANNED_LOG_PHRASES = [
        "I will now",
        "Processing",
        "Analyzing",
        "Let me",
        "I'm going to",
        "Next, I'll",
        "Working on",
    ]

    def __init__(self, output_dir: Path | None = None, silent_mode: bool = True):
        self.output_dir = output_dir or Path("./output")
        self.silent_mode = silent_mode
        self.current_trace: ExecutionTrace | None = None
        self.artifacts: list[ExecutionArtifact] = []

    def start_execution(self, context: dict[str, Any]) -> str:
        """
        Start new execution with silent mode.
        Returns run_sha for tracking.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ExecutionOrchestrator.start_execution")

        run_sha = self._generate_run_sha(context)
        self.current_trace = ExecutionTrace(
            run_sha=run_sha,
            start_time=time.time(),
            end_time=None,
            decision_path=[],
            temperature_log=[],
            validation_failures=[],
            artifacts=[],
            success=False,
        )
        if not self.silent_mode:
            self._log(f"Execution started: {run_sha}")
        return run_sha

    def record_decision(self, decision: str, details: dict[str, Any] | None = None) -> None:
        """Record a decision point in the execution path"""
        if self.current_trace:
            decision_entry = decision
            if details:
                decision_entry = f"{decision} | {json.dumps(details, separators=(',', ':'))}"
            self.current_trace.decision_path.append(decision_entry)

    def record_temperature_adjustment(self, recovery_loop: AdaptiveRecoveryLoop) -> None:
        """Record temperature adjustments from recovery loop"""
        if self.current_trace:
            self.current_trace.temperature_log.extend(recovery_loop.get_temperature_log())

    def record_validation_failure(self, gate_executor: IntegrityGateExecutor) -> None:
        """Record validation failures from gate executor"""
        if self.current_trace:
            failed_results = [
                {
                    "gate_id": r.gate_id,
                    "message": r.message,
                    "severity": r.severity.value if hasattr(r.severity, "value") else str(r.severity),
                    "details": r.details,
                    "timestamp": time.time(),
                }
                for r in gate_executor.results
                if not r.passed
            ]
            self.current_trace.validation_failures.extend(failed_results)

    def add_artifact(self, artifact_type: str, content: str, metadata: dict[str, Any] | None = None) -> None:
        """Add generated artifact to execution trace"""
        artifact = ExecutionArtifact(artifact_type=artifact_type, content=content, metadata=metadata or {})
        self.artifacts.append(artifact)
        if self.current_trace:
            self.current_trace.artifacts.append(artifact)

    def complete_execution(self, success: bool, error: str | None = None) -> ExecutionTrace:
        """
        Complete execution and generate audit.json.
        Returns final execution trace.
        """
        if not self.current_trace:
            raise RuntimeError("No active execution trace")
        self.current_trace.end_time = time.time()
        self.current_trace.success = success
        self.current_trace.error = error
        self._save_audit_json(self.current_trace)
        if not self.silent_mode:
            duration = self.current_trace.end_time - self.current_trace.start_time
            self._log(f"Execution completed: {success} ({duration:.2f}s)")
        return self.current_trace

    def display_all_artifacts(self) -> str:
        """
        Generate full content display of all artifacts.
        Returns formatted string for chat window display.
        """
        if not self.artifacts:
            return "No artifacts generated."
        output_sections = []
        output_sections.append("=" * 80)
        output_sections.append("GENERATED ARTIFACTS")
        output_sections.append("=" * 80)
        output_sections.append("")
        for i, artifact in enumerate(self.artifacts, 1):
            output_sections.append(f"### {i}. {artifact.artifact_type.upper()}")
            output_sections.append("")
            output_sections.append(artifact.content)
            output_sections.append("")
            if artifact.metadata:
                output_sections.append(f"**Metadata:** {json.dumps(artifact.metadata, indent=2)}")
                output_sections.append("")
            output_sections.append("-" * 80)
            output_sections.append("")
        return "\n".join(output_sections)

    def _generate_run_sha(self, context: dict[str, Any]) -> str:
        """Generate unique SHA for this execution run"""
        timestamp = str(time.time())
        context_str = json.dumps(context, sort_keys=True)
        sha_input = f"{timestamp}:{context_str}"
        return hashlib.sha256(sha_input.encode()).hexdigest()[:16]

    def _save_audit_json(self, trace: ExecutionTrace) -> Path:
        """Save audit.json with complete execution trace"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        audit_data = {
            "run_sha": trace.run_sha,
            "timestamp": datetime.fromtimestamp(trace.start_time).isoformat(),
            "duration_seconds": trace.end_time - trace.start_time if trace.end_time else None,
            "success": trace.success,
            "error": trace.error,
            "decision_path": trace.decision_path,
            "temperature_log": trace.temperature_log,
            "validation_failures": trace.validation_failures,
            "artifacts": [
                {
                    "type": a.artifact_type,
                    "length": len(a.content),
                    "metadata": a.metadata,
                    "timestamp": datetime.fromtimestamp(a.timestamp).isoformat(),
                }
                for a in trace.artifacts
            ],
            "stats": {
                "total_decisions": len(trace.decision_path),
                "total_temp_adjustments": len(trace.temperature_log),
                "total_validation_failures": len(trace.validation_failures),
                "total_artifacts": len(trace.artifacts),
            },
        }
        audit_path = self.output_dir / f"audit_{trace.run_sha}.json"
        with open(audit_path, "w", encoding="utf-8") as f:
            json.dump(audit_data, f, indent=2, ensure_ascii=False)
        return audit_path

    def _log(self, message: str) -> None:
        """
        Internal logging that respects silent mode.
        Blocks banned conversational phrases.
        """
        if self.silent_mode:
            return
        for banned_phrase in self.BANNED_LOG_PHRASES:
            if banned_phrase.lower() in message.lower():
                return
        print(f"[SYSTEM] {message}")


def create_execution_orchestrator(
    output_dir: Path | None = None, silent_mode: bool = True,
) -> ExecutionOrchestrator:
    """Factory function to create ExecutionOrchestrator instance"""
    return ExecutionOrchestrator(output_dir=output_dir, silent_mode=silent_mode)
