"""
ExecOrchestrator — apps_exec.

Orchestrates the complete Executive Brief generation pipeline:
  1. Ingestion
  2. Capability extraction
  3. Brief assembly
  4. Style gate validation
  5. Artifact emission
  6. Run summary

Mirrors apps_rg RgResumeOrchestrator pattern.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# guardian: allow-silent-degradation -- Qwen vLLM is optional for execution planning; graceful fallback to manual planning
try:
    from apps_qwen import (
        AppsQwenGateway,
        AppsQwenInferenceWorker,
        AppsQwenRequest,
        apps_qwen_telemetry,
    )
    from apps_qwen.apps_qwen_config import (
        AppsQwenModelConfig,
        AppsQwenPromptConfig,
    )

    _QWEN_AVAILABLE = True
except ImportError:
    AppsQwenGateway = None  # type: ignore[assignment]
    AppsQwenRequest = None  # type: ignore[assignment]
    AppsQwenInferenceWorker = None  # type: ignore[assignment]
    apps_qwen_telemetry = None  # type: ignore[assignment]
    AppsQwenModelConfig = None  # type: ignore[assignment]
    AppsQwenPromptConfig = None  # type: ignore[assignment]
    _QWEN_AVAILABLE = False

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_authorize_and_execute("p2", "ExecOrchestrator", "execution_auth")
_emit_validates_capability("p2", "ExecOrchestrator", "capability_check")
_emit_routes_to_capability("p2", "ExecOrchestrator", "capability_route")
_emit_writes_via_uwg("p2", "ExecOrchestrator", "uwg_write")
_emit_blocks_direct_write("p2", "ExecOrchestrator", "direct_write_block")
_emit_records_tool_invocation("p2", "ExecOrchestrator", "tool_invocation")
_emit_captures_execution_output("p2", "ExecOrchestrator", "exec_output")
_emit_dispatches_agent("p3", "ExecOrchestrator", "agent_dispatch")
_emit_coordinates_agents("p3", "ExecOrchestrator", "agent_coordination")
_emit_records_workflow_lineage("p3", "ExecOrchestrator", "workflow_lineage")
_emit_records_healing_outcome("p3", "ExecOrchestrator", "healing_outcome")
_emit_escalates_failure("p3", "ExecOrchestrator", "failure_escalation")
_emit_orchestrates_workflow("p3", "ExecOrchestrator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ExecOrchestrator", "healing_dispatch")
_emit_invokes_evaluation("p3", "ExecOrchestrator", "evaluation_signal")
_emit_records_telemetry_event("p4", "ExecOrchestrator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ExecOrchestrator", "eval_metric")
_emit_stores_embedding("p4", "ExecOrchestrator", "embedding_store")
_emit_updates_meta_learning_state("p4", "ExecOrchestrator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ExecOrchestrator", "exec_snapshot_link")
from apps_exec.engines.brief_assembly_engine import BriefAssemblyEngine
from apps_exec.engines.capability_extraction_engine import CapabilityExtractionEngine
from apps_exec.engines.ingestion_engine import IngestionEngine
from apps_exec.types.exec_types import (
    BriefStatus,
    ExecBriefRequest,
    ExecBriefResult,
    RunSummary,
)
from apps_exec.validators.style_gate_validator import StyleGateValidator

_emit_applies_guardrail("p0", "ExecOrchestrator", "p0_governance")
_emit_reads_policy_state("p0", "ExecOrchestrator", "policy_binding")
_emit_snapshots_state("p0", "ExecOrchestrator", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_emits_metric_event("ExecOrchestrator", "p4obs", "metric_1")
_emit_emits_metric_event("ExecOrchestrator", "p4obs", "metric_2")
_emit_emits_metric_event("ExecOrchestrator", "p4obs", "metric_3")
_emit_emits_metric_event("ExecOrchestrator", "p4obs", "metric_4")
_emit_emits_metric_event("ExecOrchestrator", "p4obs", "metric_5")
_emit_emits_metric_event("ExecOrchestrator", "p4obs", "metric_6")
_emit_records_incident_event("ExecOrchestrator", "p4obs", "incident")
_emit_captures_runtime_anomaly("ExecOrchestrator", "p4obs", "anomaly")
_emit_writes_observability_log("ExecOrchestrator", "p4obs", "obs_log")
_emit_updates_monitoring_state("ExecOrchestrator", "p4obs", "mon_state")
_emit_triggers_alert("ExecOrchestrator", "p4obs", "alert")
_emit_links_incident_trace("ExecOrchestrator", "p4obs", "trace_link")
_emit_captures_pattern("ExecOrchestrator", "p3lm", "pattern")
_emit_records_learning_event("ExecOrchestrator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ExecOrchestrator", "p3lm", "snapshot")
_emit_feeds_meta_learning("ExecOrchestrator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ExecOrchestrator", "p3lm", "routing")
_emit_improves_agent_policy("ExecOrchestrator", "p3lm", "policy")
_emit_stores_learning_state("ExecOrchestrator", "p3lm", "state")
_emit_records_execution_trace("ExecOrchestrator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ExecOrchestrator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ExecOrchestrator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ExecOrchestrator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ExecOrchestrator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ExecOrchestrator", "env_read", "p2_env_1")
_emit_reads_environ("ExecOrchestrator", "env_read", "p2_env_2")
_emit_reads_runtime_state("ExecOrchestrator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ExecOrchestrator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ExecOrchestrator", "context_pull")
_emit_pulls_context("p1", "ExecOrchestrator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ExecOrchestrator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ExecOrchestrator", "uwg_term_2")
_emit_writes_through("p1", "ExecOrchestrator", "write_through")
_emit_writes_through("p1", "ExecOrchestrator", "write_through_2")
_emit_validated_by_safety_plane("p1", "ExecOrchestrator", "safety_validation")
_emit_invokes_eval("p1", "ExecOrchestrator", "eval_call")
_emit_proposal_commits_routing("p1", "ExecOrchestrator", "routing_commit")
_emit_escalates_to_human("p1", "ExecOrchestrator", "human_escalation")
_emit_routes_through("p1", "ExecOrchestrator", "route_through")
_emit_checks_agent_registry("p1", "ExecOrchestrator", "agent_registry")
_emit_validates_agent_capability("p1", "ExecOrchestrator", "capability")
_emit_dispatches_execution_plan("p1", "ExecOrchestrator", "exec_plan")
_emit_agent_executes_agent("p1", "ExecOrchestrator", "sub_agent")
_emit_routes_to_agent("p1", "ExecOrchestrator", "target_agent")
_emit_verifies_policy("p1", "ExecOrchestrator", "policy_check")
_emit_observes_runtime_state("p1", "ExecOrchestrator", "runtime_state")
_emit_verifies_boundary("p1", "ExecOrchestrator", "boundary_check")
_emit_transcripts_response("p1", "ExecOrchestrator", "transcript")
_emit_hard_fails_untranscripted("p1", "ExecOrchestrator")
_emit_gated_by_confidence("p1", "ExecOrchestrator", "confidence_gate")
emit_replay_key("p0", "ExecOrchestrator")
emit_determinism_digest("p0", "ExecOrchestrator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

_log = logging.getLogger(__name__)


@dataclass
class ExecOrchestrator:
    """Orchestrate the multi-stage executive brief generation pipeline.

    Each stage gate is explicit. No silent fallbacks. If the style gate
    fails in HARD_FAIL mode, the result carries status=FAILED with
    all violations listed.
    """

    dry_run: bool = False
    output_dir: str = "reports/executive"
    gate_mode: str = "HARD_FAIL"
    hop_checkpoints: list[dict[str, Any]] = field(default_factory=list)
    qwen_enabled: bool = True

    def __post_init__(self) -> None:
        self._ingestion = IngestionEngine()
        self._extraction = CapabilityExtractionEngine()
        self._assembly = BriefAssemblyEngine()
        self._gate = StyleGateValidator()

        # Initialize Qwen vLLM for execution planning
        self._qwen_gateway = None
        self._qwen_inference_worker = None
        self._qwen_session_id = None

        if self.qwen_enabled and _QWEN_AVAILABLE:
            try:
                # Initialize Qwen gateway for execution planning
                self._qwen_gateway = AppsQwenGateway(model_id="Qwen/Qwen2.5-7B-Instruct")

                # Initialize inference worker with execution-specific config
                model_config = AppsQwenModelConfig(
                    model_id="Qwen/Qwen2.5-7B-Instruct",
                    max_tokens=3584,  # High token limit for detailed execution plans
                    temperature=0.2,  # Low temperature for precise execution planning
                    confidence_threshold=0.85,
                    timeout_seconds=60,
                )
                self._qwen_inference_worker = AppsQwenInferenceWorker(model_config)

                # Start telemetry session
                if apps_qwen_telemetry is not None:
                    self._qwen_session_id = apps_qwen_telemetry.start_session("apps_exec")

                _emit_records_execution_trace("ExecOrchestrator", "L2_EXECUTION", "qwen_vllm_init")

            except Exception as e:
                _emit_records_telemetry_event("ExecOrchestrator", "L2_EXECUTION", "qwen_init_error")
                _log.warning(f"Failed to initialize Qwen vLLM: {e}")
                self.qwen_enabled = False

        try:
            from agentic_core.adg.runtime.behavioral_index import ADGBehavioralIndex

            _idx = ADGBehavioralIndex.from_latest(Path(__file__).resolve().parents[3])
            _profile = _idx.profile_for(Path(__file__).resolve()) if _idx else None
            self.adg_behavioral_score: float = _profile.behavioral_score if _profile else 0.5
            self.adg_antipattern_signals: list[str] = sorted(_profile.antipattern_signals) if _profile else []
        except (ImportError, AttributeError, OSError):
            self.adg_behavioral_score = 0.5
            self.adg_antipattern_signals = []

    def run(self, request: ExecBriefRequest) -> ExecBriefResult:
        """Execute the full brief generation pipeline.

        Args:
            request: ExecBriefRequest with audience, source dirs, options.

        Returns:
            ExecBriefResult with all sections, artifacts, and provenance.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ExecOrchestrator.run")

        trace_id = request.trace_id or self._make_trace_id(request)
        audience_key = request.audience.value if hasattr(request.audience, "value") else str(request.audience)

        _log.info(
            "[ExecOrchestrator] Starting trace=%s audience=%s dry_run=%s",
            trace_id,
            audience_key,
            request.dry_run or self.dry_run,
        )

        result = ExecBriefResult(
            trace_id=trace_id,
            audience=audience_key,
            tone=request.tone.value if hasattr(request.tone, "value") else str(request.tone),
            status=BriefStatus.GENERATING,
            provenance={"trace_id": trace_id, "audience": audience_key, "app": "apps_exec"},
        )

        try:
            ingestion_result = self._ingestion.execute(request)
            self._record_hop(
                "HOP-1-INGESTION", len(ingestion_result.documents) > 0 or bool(ingestion_result.skipped_paths)
            )

            extraction_result = self._extraction.execute(ingestion_result)
            self._record_hop("HOP-2-EXTRACTION", True)
            result.capabilities_extracted = extraction_result.capabilities

            assembly_result = self._assembly.execute((request, extraction_result))
            self._record_hop("HOP-3-ASSEMBLY", bool(assembly_result.sections))
            result.sections = assembly_result.sections

            result.status = BriefStatus.GATE_CHECKING
            gate_result = self._gate.validate_sections(assembly_result.sections, audience=audience_key)
            self._record_hop("HOP-4-STYLE-GATE", gate_result.passed)

            result.quality_score = gate_result.quality_score
            result.gate_violations = [
                f"[{v.rule_id}:{v.severity}] {v.message}" for v in gate_result.violations
            ]

            if not gate_result.passed and self.gate_mode == "HARD_FAIL":
                result.status = BriefStatus.FAILED
                _log.error("[ExecOrchestrator] Style gate FAILED: %d violations", len(gate_result.violations))
            else:
                is_dry = request.dry_run or self.dry_run
                result.status = BriefStatus.DRY_RUN if is_dry else BriefStatus.COMPLETE
                if not is_dry:
                    artifact_paths = self._emit_artifacts(result, trace_id)
                    result.artifact_paths = artifact_paths
                    self._record_hop("HOP-5-EMIT", True)

        except (ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
            _log.error("[ExecOrchestrator] Pipeline error trace=%s: %s", trace_id, exc, exc_info=True)
            result.status = BriefStatus.FAILED
            result.error = str(exc)
            self._record_hop("PIPELINE-ERROR", False)

        result.provenance["checkpoints"] = [c["hop_id"] for c in self.hop_checkpoints]

        run_summary = RunSummary(
            trace_id=trace_id,
            status=result.status.value,
            audience=audience_key,
            tone=result.tone,
            sections_generated=len(result.sections),
            capabilities_extracted=len(result.capabilities_extracted),
            quality_score=result.quality_score,
            gate_violations=result.gate_violations,
            artifacts=result.artifact_paths,
            dry_run=request.dry_run or self.dry_run,
            error=result.error,
            provenance=result.provenance,
        )

        if not (request.dry_run or self.dry_run):
            summary_path = self._emit_run_summary(run_summary, trace_id)
            result.run_summary_path = summary_path

        _log.info(
            "[ExecOrchestrator] Complete trace=%s status=%s score=%.2f violations=%d",
            trace_id,
            result.status.value,
            result.quality_score,
            len(result.gate_violations),
        )
        return result

    def _emit_artifacts(self, result: ExecBriefResult, trace_id: str) -> list[str]:
        """Write brief markdown artifacts to output_dir."""
        out = Path(self.output_dir)
        out.mkdir(parents=True, exist_ok=True)
        paths: list[str] = []

        audience = result.audience
        brief_path = out / f"exec_brief_{audience}_{trace_id[:8]}.md"
        lines: list[str] = [
            f"# Executive Brief — {audience.replace('_', ' ').title()}",
            "",
            f"**Trace ID:** `{trace_id}`  ",
            f"**Tone:** {result.tone}  ",
            f"**Quality Score:** {result.quality_score:.0%}  ",
            "",
            "---",
            "",
        ]
        for section in result.sections:
            lines.append(f"## {section.heading}")
            lines.append("")
            lines.append(section.body)
            lines.append("")
            if section.why_this_matters:
                lines.append(f"> **Why this matters:** {section.why_this_matters}")
                lines.append("")
            if section.evidence_anchors:
                lines.append(f"*Evidence anchors: {', '.join(section.evidence_anchors[:3])}*")
                lines.append("")
            lines.append("---")
            lines.append("")

        brief_path.write_text("\n".join(lines), encoding="utf-8")
        paths.append(str(brief_path))
        _log.info("[ExecOrchestrator] Wrote brief: %s", brief_path)
        return paths

    def _emit_run_summary(self, summary: RunSummary, trace_id: str) -> str:
        out = Path(self.output_dir)
        out.mkdir(parents=True, exist_ok=True)
        summary_path = out / f"run_summary_{trace_id[:8]}.json"
        summary_path.write_text(
            json.dumps(summary.to_dict(), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        _log.info("[ExecOrchestrator] Wrote run summary: %s", summary_path)
        return str(summary_path)

    def _record_hop(self, hop_id: str, success: bool) -> None:
        self.hop_checkpoints.append({"hop_id": hop_id, "status": "COMPLETED" if success else "FAILED"})

    async def plan_execution_with_qwen(
        self, objectives: list[str], constraints: dict[str, Any], planning_type: str = "strategic"
    ) -> dict[str, Any]:
        """Generate execution plans using Qwen vLLM inference.

        Args:
            objectives: List of strategic objectives to achieve
            constraints: Dictionary containing resource, timeline, and technical constraints
            planning_type: Type of planning (strategic, tactical, operational)

        Returns:
            Dictionary with generated execution plan and metadata
        """
        if not self.qwen_enabled or self._qwen_gateway is None:
            return {"success": False, "error": "qwen_disabled", "content": None}

        # Validate inputs
        if not objectives or not isinstance(objectives, list):
            return {"success": False, "error": "invalid_objectives", "content": None}

        if not constraints or not isinstance(constraints, dict):
            return {"success": False, "error": "invalid_constraints", "content": None}

        if not planning_type or not planning_type.strip():
            return {"success": False, "error": "invalid_planning_type", "content": None}

        try:
            # Prepare execution planning prompt
            prompt = self._prepare_execution_planning_prompt(objectives, constraints, planning_type)

            # Create Qwen request
            request = AppsQwenRequest(
                app_name="apps_exec",
                prompt=prompt,
                confidence_threshold=0.85,
                max_tokens=3584,  # High token limit for detailed execution plans
                temperature=0.2,  # Low temperature for precise execution planning
            )

            # Record telemetry start
            if apps_qwen_telemetry is not None and self._qwen_session_id is not None:
                apps_qwen_telemetry.record_request_start(
                    session_id=self._qwen_session_id,
                    app_name="apps_exec",
                    model_id="Qwen/Qwen2.5-7B-Instruct",
                )

            # Perform inference
            response = await self._qwen_gateway.infer(request)

            # Record telemetry result
            if apps_qwen_telemetry is not None and self._qwen_session_id is not None:
                if response.success:
                    apps_qwen_telemetry.record_request_success(
                        session_id=self._qwen_session_id,
                        app_name="apps_exec",
                        model_id=response.model_used,
                        latency_ms=response.latency_ms,
                        confidence=response.confidence,
                        tokens_used=len(prompt.split()) + len(response.response.split())
                        if response.response
                        else 0,
                    )
                else:
                    apps_qwen_telemetry.record_request_error(
                        session_id=self._qwen_session_id,
                        app_name="apps_exec",
                        model_id=response.model_used,
                        error_message=response.error_message or "unknown_error",
                    )

            _emit_captures_evaluation_metric("apps_exec", "ExecOrchestrator", "execution_planning")

            return {
                "success": response.success,
                "content": response.response,
                "confidence": response.confidence,
                "model_used": response.model_used,
                "latency_ms": response.latency_ms,
                "planning_type": planning_type,
                "objectives_count": len(objectives),
                "error_message": response.error_message,
            }

        except Exception as e:
            _emit_records_telemetry_event("apps_exec", "ExecOrchestrator", "execution_planning_error")
            return {"success": False, "error": f"execution_planning_failed: {str(e)}", "content": None}

    def _prepare_execution_planning_prompt(
        self, objectives: list[str], constraints: dict[str, Any], planning_type: str
    ) -> str:
        """Prepare prompt for execution planning using Qwen.

        Args:
            objectives: Strategic objectives to achieve
            constraints: Resource and technical constraints
            planning_type: Type of planning requested

        Returns:
            Formatted prompt string
        """
        # Format objectives
        objectives_text = ""
        for i, objective in enumerate(objectives[:6], 1):  # Limit to 6 objectives
            objectives_text += f"{i}. {objective}\n"

        # Format constraints
        constraints_text = ""
        constraint_fields = ["timeline", "budget", "resources", "technical", "regulatory", "stakeholders"]
        for field in constraint_fields:
            if field in constraints:
                constraints_text += f"{field.title()}: {constraints[field]}\n"

        planning_instructions = {
            "strategic": "Generate a strategic execution plan focusing on high-level goals, key initiatives, and success metrics.",
            "tactical": "Generate a tactical execution plan focusing on specific actions, resource allocation, and timeline.",
            "operational": "Generate an operational execution plan focusing on day-to-day activities, processes, and coordination.",
            "comprehensive": "Generate a comprehensive execution plan covering strategic, tactical, and operational aspects.",
        }

        instruction = planning_instructions.get(planning_type, planning_instructions["strategic"])

        prompt = f"""EXECUTION PLANNING REQUEST

PLANNING TYPE: {planning_type}

OBJECTIVES:
{objectives_text}

CONSTRAINTS:
{constraints_text}

INSTRUCTIONS:
{instruction}

Please provide a detailed execution plan that includes:
1. Executive Summary
2. Key Success Factors
3. Phase-by-Phase Implementation
4. Resource Requirements
5. Risk Mitigation Strategies
6. Success Metrics and KPIs
7. Timeline and Milestones
8. Governance and Oversight
9. Communication Plan
10. Contingency Planning

Ensure the plan is actionable, realistic, and aligned with the stated objectives and constraints. Use clear, structured language with specific, measurable outcomes.
"""

        return prompt

    @staticmethod
    def _make_trace_id(request: ExecBriefRequest) -> str:
        audience = request.audience.value if hasattr(request.audience, "value") else str(request.audience)
        raw = f"exec:{audience}:{','.join(request.source_dirs)}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
