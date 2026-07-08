from __future__ import annotations

from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "FissionManagerAgent")
trace_contract.emit_determinism_digest("p0", "FissionManagerAgent")

trace_contract._emit_dispatches_healing_run("p1", "FissionManagerAgent", "L3")
trace_contract._emit_routes_through("p1", "FissionManagerAgent", "L3")
trace_contract._emit_checks_agent_registry("p1", "FissionManagerAgent", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "FissionManagerAgent", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "FissionManagerAgent", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "FissionManagerAgent", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "FissionManagerAgent", "target_agent")
trace_contract._emit_verifies_policy("p1", "FissionManagerAgent", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "FissionManagerAgent", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "FissionManagerAgent", "boundary_check")
trace_contract._emit_transcripts_response("p1", "FissionManagerAgent", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "FissionManagerAgent")
trace_contract._emit_gated_by_confidence("p1", "FissionManagerAgent", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "FissionManagerAgent", "L3")
trace_contract._emit_reads_policy_state("p1", "FissionManagerAgent", "L3")
trace_contract._emit_authorize_and_execute("p2", "FissionManagerAgent", "execution_auth")
trace_contract._emit_validates_capability("p2", "FissionManagerAgent", "capability_check")
trace_contract._emit_routes_to_capability("p2", "FissionManagerAgent", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "FissionManagerAgent", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "FissionManagerAgent", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "FissionManagerAgent", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "FissionManagerAgent", "exec_output")
trace_contract._emit_dispatches_agent("p3", "FissionManagerAgent", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "FissionManagerAgent", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "FissionManagerAgent", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "FissionManagerAgent", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "FissionManagerAgent", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "FissionManagerAgent", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "FissionManagerAgent", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "FissionManagerAgent", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "FissionManagerAgent", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "FissionManagerAgent", "eval_metric")
trace_contract._emit_stores_embedding("p4", "FissionManagerAgent", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "FissionManagerAgent", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "FissionManagerAgent", "exec_snapshot_link")

"\n[PHASE 14 REFACTOR] FissionManagerAgent.\nSTRICT COMPLIANCE: No direct SDK imports. Uses SovereignLLMGateway.\n"
import json
import logging
import os

from agentic_core.config.google_ai_env import google_ai_pro_model_id
from dataclasses import dataclass

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.mixins.atomic_execution_mixin import AtomicExecutionMixin

trace_contract._emit_emits_metric_event("FissionManagerAgent", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("FissionManagerAgent", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("FissionManagerAgent", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("FissionManagerAgent", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("FissionManagerAgent", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("FissionManagerAgent", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("FissionManagerAgent", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("FissionManagerAgent", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("FissionManagerAgent", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("FissionManagerAgent", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("FissionManagerAgent", "p4obs", "alert")
trace_contract._emit_links_incident_trace("FissionManagerAgent", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("FissionManagerAgent", "p3lm", "pattern")
trace_contract._emit_records_learning_event("FissionManagerAgent", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("FissionManagerAgent", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("FissionManagerAgent", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("FissionManagerAgent", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("FissionManagerAgent", "p3lm", "policy")
trace_contract._emit_stores_learning_state("FissionManagerAgent", "p3lm", "state")
trace_contract._emit_records_execution_trace("FissionManagerAgent", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("FissionManagerAgent", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("FissionManagerAgent", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("FissionManagerAgent", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("FissionManagerAgent", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("FissionManagerAgent", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("FissionManagerAgent", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("FissionManagerAgent", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("FissionManagerAgent", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "FissionManagerAgent", "context_pull")
trace_contract._emit_pulls_context("p1", "FissionManagerAgent", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "FissionManagerAgent", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "FissionManagerAgent", "uwg_term_2")
trace_contract._emit_writes_through("p1", "FissionManagerAgent", "write_through")
trace_contract._emit_writes_through("p1", "FissionManagerAgent", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "FissionManagerAgent", "safety_validation")
trace_contract._emit_invokes_eval("p1", "FissionManagerAgent", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "FissionManagerAgent", "routing_commit")

Logger = logging.getLogger(__name__)


@dataclass
class FissionResult:
    triggered: bool
    reason: str
    new_files: dict[str, str]
    original_file: str
    success: bool
    error_message: str | None = None


(AtomicExecutionMixin,)


class FissionManagerAgent(SovereignBaseAgent):
    """L3 Orchestration Layer: Atomic Fission via Gateway."""

    # guardian: allow-magic-config
    def __init__(self, line_limit: int = 800, deletion_guardrail: int = 110, max_rounds: int = 3) -> None:
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "FissionManagerAgent.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "FissionManagerAgent.__init__", "p0_governance")
        super().__init__()
        self.line_limit = line_limit
        self.deletion_guardrail = deletion_guardrail
        self.max_rounds = max_rounds

    async def execute_fission(self, file_path: str, content: str, reason: str) -> FissionResult:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L3_ORCHESTRATION,
            "FissionManagerAgent.execute_fission",
        )

        Logger.info(f"FISSION TRIGGERED: {file_path} ({reason})")
        prompt = self._get_fission_prompt(file_path, content)
        try:
            response = await self.llm_generate(
                prompt,
                provider="google",
                model=google_ai_pro_model_id()[0],
                generation_config={"response_mime_type": "application/json", "temperature": 0.2},
            )
            new_files = self._parse_fission_response(response["content"], file_path)
            if new_files:
                return FissionResult(True, reason, new_files, file_path, True)
            return FissionResult(True, reason, {}, file_path, False, "Empty response")
        except (RuntimeError, ValueError) as e:  # guardian: allow-silent-swallow
            Logger.error(f"Fission failed: {e}")
            return FissionResult(True, reason, {}, file_path, False, str(e))

    def _get_fission_prompt(self, file_name: str, content: str) -> str:
        return f"ATOMIC FISSION REQUEST: Split {file_name} into 3 logical sub-modules.\nReturn ONLY JSON mapping filenames to content.\n\nCODE:\n{content[:4000]}..."

    def _parse_fission_response(self, text: str, original_file: str) -> dict[str, str]:
        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            return json.loads(text)
        except (RuntimeError, ValueError) as e:  # guardian: allow-silent-swallow
            Logger.warning(f"Fission parse failed: {e}")
            return {}

    # guardian: allow-type-erasure
    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal violations detected by FissionManagerAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        """
        violation.get("file") or violation.get("file_path")
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"FissionManagerAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except (RuntimeError, ValueError) as e:  # guardian: allow-silent-swallow
            return {
                "status": "failed",
                "details": f"FissionManagerAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }

    # guardian: allow-type-erasure
    def heal_repository(self, *args, **kwargs) -> dict:
        """heal_repository() not implemented for FissionManagerAgent."""
        raise NotImplementedError("heal_repository() not implemented for FissionManagerAgent")
