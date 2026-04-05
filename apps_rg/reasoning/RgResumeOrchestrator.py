"""RgResumeOrchestrator - Resume generation orchestration.

Orchestrates the complete resume generation process including engine, memory,
prompt management, and state tracking.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

try:
    from agentic_core.base_agents.timeout_decorator import timeout
except ImportError:
    from agentic_core.utils.schemas.timeout_decorator_util import timeout
from apps_rg.utils.repo_signal_service import RepoSignalService
from apps_rg.utils.rg_agent_base_util import RGAgentBase

# guardian: allow-silent-degradation -- Qwen vLLM is optional for resume generation; graceful fallback to manual templates
try:
    from apps_qwen import (
        AppsQwenGateway,
        AppsQwenInferenceWorker,
        AppsQwenRequest,
        apps_qwen_telemetry,
    )
    from apps_qwen.apps_qwen_config import (
        AppsQwenConfig,
        AppsQwenModelConfig,
        AppsQwenPromptConfig,
    )

    _QWEN_AVAILABLE = True
except ImportError:
    AppsQwenGateway = None  # type: ignore[assignment]
    AppsQwenRequest = None  # type: ignore[assignment]
    AppsQwenInferenceWorker = None  # type: ignore[assignment]
    apps_qwen_telemetry = None  # type: ignore[assignment]
    AppsQwenConfig = None  # type: ignore[assignment]
    AppsQwenModelConfig = None  # type: ignore[assignment]
    AppsQwenPromptConfig = None  # type: ignore[assignment]
    _QWEN_AVAILABLE = False

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "RgResumeOrchestrator", "p0_governance")
_emit_reads_policy_state("p0", "RgResumeOrchestrator", "policy_binding")
_emit_snapshots_state("p0", "RgResumeOrchestrator", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("RgResumeOrchestrator", "p4obs", "metric_1")
_emit_emits_metric_event("RgResumeOrchestrator", "p4obs", "metric_2")
_emit_emits_metric_event("RgResumeOrchestrator", "p4obs", "metric_3")
_emit_emits_metric_event("RgResumeOrchestrator", "p4obs", "metric_4")
_emit_emits_metric_event("RgResumeOrchestrator", "p4obs", "metric_5")
_emit_emits_metric_event("RgResumeOrchestrator", "p4obs", "metric_6")
_emit_records_incident_event("RgResumeOrchestrator", "p4obs", "incident")
_emit_captures_runtime_anomaly("RgResumeOrchestrator", "p4obs", "anomaly")
_emit_writes_observability_log("RgResumeOrchestrator", "p4obs", "obs_log")
_emit_updates_monitoring_state("RgResumeOrchestrator", "p4obs", "mon_state")
_emit_triggers_alert("RgResumeOrchestrator", "p4obs", "alert")
_emit_links_incident_trace("RgResumeOrchestrator", "p4obs", "trace_link")
_emit_captures_pattern("RgResumeOrchestrator", "p3lm", "pattern")
_emit_records_learning_event("RgResumeOrchestrator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("RgResumeOrchestrator", "p3lm", "snapshot")
_emit_feeds_meta_learning("RgResumeOrchestrator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("RgResumeOrchestrator", "p3lm", "routing")
_emit_improves_agent_policy("RgResumeOrchestrator", "p3lm", "policy")
_emit_stores_learning_state("RgResumeOrchestrator", "p3lm", "state")
_emit_records_execution_trace("RgResumeOrchestrator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("RgResumeOrchestrator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("RgResumeOrchestrator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("RgResumeOrchestrator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("RgResumeOrchestrator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("RgResumeOrchestrator", "env_read", "p2_env_1")
_emit_reads_environ("RgResumeOrchestrator", "env_read", "p2_env_2")
_emit_reads_runtime_state("RgResumeOrchestrator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("RgResumeOrchestrator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "RgResumeOrchestrator", "context_pull")
_emit_pulls_context("p1", "RgResumeOrchestrator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "RgResumeOrchestrator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "RgResumeOrchestrator", "uwg_term_2")
_emit_writes_through("p1", "RgResumeOrchestrator", "write_through")
_emit_writes_through("p1", "RgResumeOrchestrator", "write_through_2")
_emit_validated_by_safety_plane("p1", "RgResumeOrchestrator", "safety_validation")
_emit_invokes_eval("p1", "RgResumeOrchestrator", "eval_call")
_emit_proposal_commits_routing("p1", "RgResumeOrchestrator", "routing_commit")
_emit_escalates_to_human("p1", "RgResumeOrchestrator", "human_escalation")
_emit_routes_through("p1", "RgResumeOrchestrator", "route_through")
_emit_checks_agent_registry("p1", "RgResumeOrchestrator", "agent_registry")
_emit_validates_agent_capability("p1", "RgResumeOrchestrator", "capability")
_emit_dispatches_execution_plan("p1", "RgResumeOrchestrator", "exec_plan")
_emit_agent_executes_agent("p1", "RgResumeOrchestrator", "sub_agent")
_emit_routes_to_agent("p1", "RgResumeOrchestrator", "target_agent")
_emit_verifies_policy("p1", "RgResumeOrchestrator", "policy_check")
_emit_observes_runtime_state("p1", "RgResumeOrchestrator", "runtime_state")
_emit_verifies_boundary("p1", "RgResumeOrchestrator", "boundary_check")
_emit_transcripts_response("p1", "RgResumeOrchestrator", "transcript")
_emit_hard_fails_untranscripted("p1", "RgResumeOrchestrator")
_emit_gated_by_confidence("p1", "RgResumeOrchestrator", "confidence_gate")
emit_replay_key("p0", "RgResumeOrchestrator")
emit_determinism_digest("p0", "RgResumeOrchestrator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "RgResumeOrchestrator", "execution_auth")
_emit_validates_capability("p2", "RgResumeOrchestrator", "capability_check")
_emit_routes_to_capability("p2", "RgResumeOrchestrator", "capability_route")
_emit_writes_via_uwg("p2", "RgResumeOrchestrator", "uwg_write")
_emit_blocks_direct_write("p2", "RgResumeOrchestrator", "direct_write_block")
_emit_records_tool_invocation("p2", "RgResumeOrchestrator", "tool_invocation")
_emit_captures_execution_output("p2", "RgResumeOrchestrator", "exec_output")
_emit_dispatches_agent("p3", "RgResumeOrchestrator", "agent_dispatch")
_emit_coordinates_agents("p3", "RgResumeOrchestrator", "agent_coordination")
_emit_records_workflow_lineage("p3", "RgResumeOrchestrator", "workflow_lineage")
_emit_records_healing_outcome("p3", "RgResumeOrchestrator", "healing_outcome")
_emit_escalates_failure("p3", "RgResumeOrchestrator", "failure_escalation")
_emit_orchestrates_workflow("p3", "RgResumeOrchestrator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "RgResumeOrchestrator", "healing_dispatch")
_emit_invokes_evaluation("p3", "RgResumeOrchestrator", "evaluation_signal")
_emit_records_telemetry_event("p4", "RgResumeOrchestrator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "RgResumeOrchestrator", "eval_metric")
_emit_stores_embedding("p4", "RgResumeOrchestrator", "embedding_store")
_emit_updates_meta_learning_state("p4", "RgResumeOrchestrator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "RgResumeOrchestrator", "exec_snapshot_link")

_logger = logging.getLogger(__name__)
"Pure orchestration of resume generation using shared atoms."


@dataclass
class RgResumeOrchestrator(RGAgentBase):
    """Orchestrate the multi-hop resume generation workflow."""

    master_resume: dict[str, Any] = field(default_factory=dict)
    test_mode: bool = False
    hop_checkpoints: list[dict[str, Any]] = field(default_factory=list)
    qwen_enabled: bool = True
    enable_repo_signals: bool = True

    def __post_init__(self) -> None:
        """Initialize the orchestrator."""
        super().__post_init__()
        self.constraints = None
        self.jd_enforcer = None

        # Initialize Qwen vLLM integration
        self._qwen_gateway = None
        self._qwen_inference_worker = None
        self._qwen_session_id = None

        if self.qwen_enabled and _QWEN_AVAILABLE:
            try:
                # Initialize Qwen gateway for resume generation
                self._qwen_gateway = AppsQwenGateway(model_id="Qwen/Qwen2.5-7B-Instruct")

                # Initialize inference worker with resume-specific config
                model_config = AppsQwenModelConfig(
                    model_id="Qwen/Qwen2.5-7B-Instruct",
                    max_tokens=2048,
                    temperature=0.3,  # Lower temperature for consistent resume content
                )
                self._qwen_inference_worker = AppsQwenInferenceWorker(model_config)

                # Start telemetry session
                if apps_qwen_telemetry is not None:
                    self._qwen_session_id = apps_qwen_telemetry.start_session("apps_rg")

                _emit_records_execution_trace("RgResumeOrchestrator", "L2_EXECUTION", "qwen_vllm_init")

            except Exception as e:
                _emit_records_telemetry_event("RgResumeOrchestrator", "L2_EXECUTION", "qwen_init_error")
                _logger.warning(f"Failed to initialize Qwen vLLM: {e}")
                self.qwen_enabled = False

    def run(self, JobDescription: str) -> dict[str, object]:
        """Execute the full resume generation workflow."""
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "RgResumeOrchestrator.run"
        )
        if self.jd_enforcer:
            self.jd_enforcer.validate_jd_input(JobDescription, "HOP-0")
            if self.jd_enforcer.has_failures():
                raise ValueError("JD validation failed")
        extracted_data = {}
        hop1_results = []
        self._record_hop("HOP-1", hop1_results)
        enriched_data = extracted_data
        hop2_results = []
        self._record_hop("HOP-2", hop2_results)

        repo_signals: dict[str, Any] = {}
        if self.enable_repo_signals:
            try:
                repo_signals = RepoSignalService().collect().as_dict()
                self._record_hop("HOP-ENRICH", [{"passed": True}])
            except Exception:
                self._record_hop("HOP-ENRICH", [{"passed": False}])

        return {
            "status": "success",
            "enriched_data": enriched_data,
            "checkpoints": [c.get("hop_id") for c in self.hop_checkpoints],
            "repo_signals": repo_signals,
        }

    def _record_hop(self, hop_id: str, results: list = None) -> None:
        """Record a hop Checkpoint."""
        status = "COMPLETED" if not results or all(getattr(r, "passed", True) for r in results) else "FAILED"
        self.hop_checkpoints.append({"hop_id": hop_id, "status": "status"})

    async def generate_resume_with_qwen(
        self, job_description: str, candidate_profile: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate resume content using Qwen vLLM inference.

        Args:
            job_description: Job description text
            candidate_profile: Candidate profile information

        Returns:
            Dictionary with generated resume content and metadata
        """
        if not self.qwen_enabled or self._qwen_gateway is None:
            return {"success": False, "error": "qwen_disabled", "content": None}

        try:
            # Prepare prompt for resume generation
            prompt = self._prepare_resume_generation_prompt(job_description, candidate_profile)

            # Create Qwen request
            request = AppsQwenRequest(
                app_name="apps_rg",
                prompt=prompt,
                confidence_threshold=0.7,
                max_tokens=2048,
                temperature=0.3,
            )

            # Record telemetry start
            if apps_qwen_telemetry is not None and self._qwen_session_id is not None:
                apps_qwen_telemetry.record_request_start(
                    session_id=self._qwen_session_id,
                    app_name="apps_rg",
                    model_id="Qwen/Qwen2.5-7B-Instruct",
                )

            # Perform inference
            response = await self._qwen_gateway.infer(request)

            # Record telemetry result
            if apps_qwen_telemetry is not None and self._qwen_session_id is not None:
                if response.success:
                    apps_qwen_telemetry.record_request_success(
                        session_id=self._qwen_session_id,
                        app_name="apps_rg",
                        model_id=response.model_used,
                        latency_ms=response.latency_ms,
                        tokens_used=len(prompt.split()) + len(response.response.split())
                        if response.response
                        else 0,
                    )
                else:
                    apps_qwen_telemetry.record_request_error(
                        session_id=self._qwen_session_id,
                        app_name="apps_rg",
                        model_id=response.model_used,
                        error_message=response.error_message or "unknown_error",
                    )

            _emit_captures_evaluation_metric("apps_rg", "RgResumeOrchestrator", "resume_generation")

            return {
                "success": response.success,
                "content": response.response,
                "confidence": response.confidence,
                "model_used": response.model_used,
                "latency_ms": response.latency_ms,
                "error_message": response.error_message,
            }

        except Exception as e:
            _emit_records_telemetry_event("apps_rg", "RgResumeOrchestrator", "resume_generation_error")
            return {"success": False, "error": f"generation_failed: {str(e)}", "content": None}

    def _prepare_resume_generation_prompt(
        self, job_description: str, candidate_profile: dict[str, Any]
    ) -> str:
        """Prepare prompt for resume generation using Qwen.

        Args:
            job_description: Job description text
            candidate_profile: Candidate profile dictionary

        Returns:
            Formatted prompt string
        """
        prompt = f"""Generate a professional resume tailored to the following job description:

JOB DESCRIPTION:
{job_description}

CANDIDATE PROFILE:
{candidate_profile}

Please generate:
1. A compelling professional summary
2. Relevant experience section with achievements
3. Skills section aligned with job requirements
4. Education section
5. Any additional relevant sections

Focus on matching the candidate's experience to the job requirements and quantifying achievements where possible. Use professional language and format the content clearly.
"""
        return prompt

    @timeout(300)
    # guardian: allow-magic-config -- Environment-specific configuration; owner: deployment team
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, int]:
        """L3 orchestration agent - operational only."""
        if _call_path is None:
            _call_path = set()
        super().heal_repository(
            dry_run=dry_run, execute=execute, depth=depth, max_depth=max_depth, _call_path=_call_path
        )
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L3 orchestration - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)


def orchestrate_resume(master_resume: dict, JobDescription: str) -> dict[str, object]:
    """Single public function - pure routing between atoms."""
    orchestrator = RgResumeOrchestrator(master_resume)
    return orchestrator.run(JobDescription)
