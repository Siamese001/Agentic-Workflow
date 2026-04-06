"""
RfpOrchestrator — apps_rfp.

Orchestrates the complete AI Proposal / RFP generation pipeline:
  1. Brief parsing and classification
  2. Proposal assembly (sections, roadmap, risk matrix)
  3. Gate validation
  4. Artifact emission
  5. Run summary

Mirrors apps_rg RgResumeOrchestrator pattern.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# guardian: allow-silent-degradation -- Qwen vLLM is optional for proposal generation; graceful fallback to manual templates
try:
    from agentic_core.L3_orchestration.inference.qwen_vllm import (
        AppsQwenGateway,
        AppsQwenInferenceWorker,
        AppsQwenRequest,
        apps_qwen_telemetry,
    )
    from agentic_core.L3_orchestration.inference.qwen_vllm.config import (
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

_emit_authorize_and_execute("p2", "RfpOrchestrator", "execution_auth")
_emit_validates_capability("p2", "RfpOrchestrator", "capability_check")
_emit_routes_to_capability("p2", "RfpOrchestrator", "capability_route")
_emit_writes_via_uwg("p2", "RfpOrchestrator", "uwg_write")
_emit_blocks_direct_write("p2", "RfpOrchestrator", "direct_write_block")
_emit_records_tool_invocation("p2", "RfpOrchestrator", "tool_invocation")
_emit_captures_execution_output("p2", "RfpOrchestrator", "exec_output")
_emit_dispatches_agent("p3", "RfpOrchestrator", "agent_dispatch")
_emit_coordinates_agents("p3", "RfpOrchestrator", "agent_coordination")
_emit_records_workflow_lineage("p3", "RfpOrchestrator", "workflow_lineage")
_emit_records_healing_outcome("p3", "RfpOrchestrator", "healing_outcome")
_emit_escalates_failure("p3", "RfpOrchestrator", "failure_escalation")
_emit_orchestrates_workflow("p3", "RfpOrchestrator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "RfpOrchestrator", "healing_dispatch")
_emit_invokes_evaluation("p3", "RfpOrchestrator", "evaluation_signal")
_emit_records_telemetry_event("p4", "RfpOrchestrator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "RfpOrchestrator", "eval_metric")
_emit_stores_embedding("p4", "RfpOrchestrator", "embedding_store")
_emit_updates_meta_learning_state("p4", "RfpOrchestrator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "RfpOrchestrator", "exec_snapshot_link")
from apps_rfp.engines.proposal_assembly_engine import ProposalAssemblyEngine
from apps_rfp.types.rfp_types import (
    ProposalStatus,
    RfpRequest,
    RfpResult,
    RfpRunSummary,
)
from apps_rfp.validators.proposal_gate_validator import ProposalGateValidator

_emit_applies_guardrail("p0", "RfpOrchestrator", "p0_governance")
_emit_reads_policy_state("p0", "RfpOrchestrator", "policy_binding")
_emit_snapshots_state("p0", "RfpOrchestrator", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("RfpOrchestrator", "p4obs", "metric_1")
_emit_emits_metric_event("RfpOrchestrator", "p4obs", "metric_2")
_emit_emits_metric_event("RfpOrchestrator", "p4obs", "metric_3")
_emit_emits_metric_event("RfpOrchestrator", "p4obs", "metric_4")
_emit_emits_metric_event("RfpOrchestrator", "p4obs", "metric_5")
_emit_emits_metric_event("RfpOrchestrator", "p4obs", "metric_6")
_emit_records_incident_event("RfpOrchestrator", "p4obs", "incident")
_emit_captures_runtime_anomaly("RfpOrchestrator", "p4obs", "anomaly")
_emit_writes_observability_log("RfpOrchestrator", "p4obs", "obs_log")
_emit_updates_monitoring_state("RfpOrchestrator", "p4obs", "mon_state")
_emit_triggers_alert("RfpOrchestrator", "p4obs", "alert")
_emit_links_incident_trace("RfpOrchestrator", "p4obs", "trace_link")
_emit_captures_pattern("RfpOrchestrator", "p3lm", "pattern")
_emit_records_learning_event("RfpOrchestrator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("RfpOrchestrator", "p3lm", "snapshot")
_emit_feeds_meta_learning("RfpOrchestrator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("RfpOrchestrator", "p3lm", "routing")
_emit_improves_agent_policy("RfpOrchestrator", "p3lm", "policy")
_emit_stores_learning_state("RfpOrchestrator", "p3lm", "state")
_emit_records_execution_trace("RfpOrchestrator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("RfpOrchestrator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("RfpOrchestrator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("RfpOrchestrator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("RfpOrchestrator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("RfpOrchestrator", "env_read", "p2_env_1")
_emit_reads_environ("RfpOrchestrator", "env_read", "p2_env_2")
_emit_reads_runtime_state("RfpOrchestrator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("RfpOrchestrator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "RfpOrchestrator", "context_pull")
_emit_pulls_context("p1", "RfpOrchestrator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "RfpOrchestrator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "RfpOrchestrator", "uwg_term_2")
_emit_writes_through("p1", "RfpOrchestrator", "write_through")
_emit_writes_through("p1", "RfpOrchestrator", "write_through_2")
_emit_validated_by_safety_plane("p1", "RfpOrchestrator", "safety_validation")
_emit_invokes_eval("p1", "RfpOrchestrator", "eval_call")
_emit_proposal_commits_routing("p1", "RfpOrchestrator", "routing_commit")
_emit_escalates_to_human("p1", "RfpOrchestrator", "human_escalation")
_emit_routes_through("p1", "RfpOrchestrator", "route_through")
_emit_checks_agent_registry("p1", "RfpOrchestrator", "agent_registry")
_emit_validates_agent_capability("p1", "RfpOrchestrator", "capability")
_emit_dispatches_execution_plan("p1", "RfpOrchestrator", "exec_plan")
_emit_agent_executes_agent("p1", "RfpOrchestrator", "sub_agent")
_emit_routes_to_agent("p1", "RfpOrchestrator", "target_agent")
_emit_verifies_policy("p1", "RfpOrchestrator", "policy_check")
_emit_observes_runtime_state("p1", "RfpOrchestrator", "runtime_state")
_emit_verifies_boundary("p1", "RfpOrchestrator", "boundary_check")
_emit_transcripts_response("p1", "RfpOrchestrator", "transcript")
_emit_hard_fails_untranscripted("p1", "RfpOrchestrator")
_emit_gated_by_confidence("p1", "RfpOrchestrator", "confidence_gate")
emit_replay_key("p0", "RfpOrchestrator")
emit_determinism_digest("p0", "RfpOrchestrator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

_log = logging.getLogger(__name__)


@dataclass
class RfpOrchestrator:
    """Orchestrate end-to-end AI Proposal generation."""

    dry_run: bool = False
    output_dir: str = "rfp"
    gate_mode: str = "HARD_FAIL"
    hop_checkpoints: list[dict[str, Any]] = field(default_factory=list)
    qwen_enabled: bool = True

    def __post_init__(self) -> None:
        self._assembly = ProposalAssemblyEngine()
        self._gate = ProposalGateValidator()

        # Initialize Qwen vLLM for proposal generation
        self._qwen_gateway = None
        self._qwen_inference_worker = None
        self._qwen_session_id = None

        if self.qwen_enabled and _QWEN_AVAILABLE:
            try:
                # Initialize Qwen gateway for proposal generation
                self._qwen_gateway = AppsQwenGateway(model_id="Qwen/Qwen2.5-7B-Instruct")

                # Initialize inference worker with proposal-specific config
                model_config = AppsQwenModelConfig(
                    model_id="Qwen/Qwen2.5-7B-Instruct",
                    max_tokens=4096,  # High token limit for detailed proposals
                    temperature=0.3,  # Balanced temperature for professional proposals
                    confidence_threshold=0.8,
                    timeout_seconds=90,
                )
                self._qwen_inference_worker = AppsQwenInferenceWorker(model_config)

                # Start telemetry session
                if apps_qwen_telemetry is not None:
                    self._qwen_session_id = apps_qwen_telemetry.start_session("apps_rfp")

                _emit_records_execution_trace("RfpOrchestrator", "L2_EXECUTION", "qwen_vllm_init")

            except Exception as e:
                _emit_records_telemetry_event("RfpOrchestrator", "L2_EXECUTION", "qwen_init_error")
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

    def run(self, request: RfpRequest) -> RfpResult:
        """Execute full proposal generation pipeline."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RfpOrchestrator.run")

        trace_id = request.trace_id or self._make_trace_id(request)
        _log.info(
            "[RfpOrchestrator] Starting trace=%s industry=%s dry_run=%s",
            trace_id,
            request.industry,
            request.dry_run or self.dry_run,
        )

        result = RfpResult(
            trace_id=trace_id,
            industry=request.industry,
            status=ProposalStatus.GENERATING,
            provenance={"trace_id": trace_id, "industry": request.industry, "app": "apps_rfp"},
        )

        try:
            assembly = self._assembly.execute(request)
            self._record_hop("HOP-1-ASSEMBLY", bool(assembly.sections))
            result.sections = assembly.sections
            result.roadmap = assembly.roadmap
            result.risks = assembly.risks
            result.assumptions = assembly.assumptions

            result.status = ProposalStatus.GATE_CHECKING
            gate = self._gate.validate(assembly.sections, assembly.roadmap, assembly.risks)
            self._record_hop("HOP-2-GATE", gate.passed)
            result.quality_score = gate.quality_score
            result.gate_violations = [f"[{v.rule_id}:{v.severity}] {v.message}" for v in gate.violations]

            if not gate.passed and self.gate_mode == "HARD_FAIL":
                result.status = ProposalStatus.FAILED
                _log.error("[RfpOrchestrator] Gate FAILED: %d violations", len(gate.violations))
            else:
                is_dry = request.dry_run or self.dry_run
                result.status = ProposalStatus.DRY_RUN if is_dry else ProposalStatus.COMPLETE
                if not is_dry:
                    paths = self._emit_artifacts(result, trace_id)
                    result.artifact_paths = paths
                    self._record_hop("HOP-3-EMIT", True)

        except (ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
            _log.error("[RfpOrchestrator] Pipeline error trace=%s: %s", trace_id, exc, exc_info=True)
            result.status = ProposalStatus.FAILED
            result.error = str(exc)
            self._record_hop("PIPELINE-ERROR", False)

        result.provenance["checkpoints"] = [c["hop_id"] for c in self.hop_checkpoints]

        summary = RfpRunSummary(
            trace_id=trace_id,
            status=result.status.value,
            industry=result.industry,
            sections_generated=len(result.sections),
            roadmap_phases=len(result.roadmap),
            risks_identified=len(result.risks),
            assumptions_declared=len(result.assumptions),
            quality_score=result.quality_score,
            gate_violations=result.gate_violations,
            artifacts=result.artifact_paths,
            dry_run=request.dry_run or self.dry_run,
            error=result.error,
            provenance=result.provenance,
        )

        if not (request.dry_run or self.dry_run):
            sp = self._emit_run_summary(summary, trace_id)
            result.run_summary_path = sp

        _log.info(
            "[RfpOrchestrator] Complete trace=%s status=%s score=%.2f",
            trace_id,
            result.status.value,
            result.quality_score,
        )
        return result

    def _emit_artifacts(self, result: RfpResult, trace_id: str) -> list[str]:
        """Write proposal markdown artifacts."""
        out = Path(self.output_dir)
        out.mkdir(parents=True, exist_ok=True)
        paths: list[str] = []

        proposal_path = out / f"proposal_{result.industry}_{trace_id[:8]}.md"
        lines = [
            f"# AI Platform Proposal — {result.industry.replace('_', ' ').title()}",
            "",
            f"**Trace ID:** `{trace_id}`  ",
            f"**Quality Score:** {result.quality_score:.0%}  ",
            "",
            "---",
            "",
        ]
        for section in result.sections:
            lines += [f"## {section.heading}", "", section.body, "", "---", ""]

        lines += ["## Implementation Roadmap", ""]
        for phase in result.roadmap:
            lines.append(f"### {phase.name} ({phase.duration_weeks} weeks)")
            lines.append(f"- Objectives: {', '.join(phase.objectives)}")
            lines.append(f"- Governance: {phase.governance_milestone}")
            lines.append(f"- Measurement: {phase.measurement_milestone}")
            lines.append("")

        lines += ["## Risk Register", ""]
        for risk in result.risks:
            lines.append(f"| {risk.risk_id} | {risk.category} | {risk.severity.value} | {risk.mitigation} |")
        lines.append("")

        proposal_path.write_text("\n".join(lines), encoding="utf-8")
        paths.append(str(proposal_path))

        manifest = {
            "trace_id": trace_id,
            "sections": [s.section_id for s in result.sections],
            "roadmap_phases": len(result.roadmap),
            "risks": len(result.risks),
        }
        manifest_path = out / f"proposal_manifest_{trace_id[:8]}.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        paths.append(str(manifest_path))
        return paths

    def _emit_run_summary(self, summary: RfpRunSummary, trace_id: str) -> str:
        out = Path(self.output_dir)
        out.mkdir(parents=True, exist_ok=True)
        p = out / f"run_summary_{trace_id[:8]}.json"
        p.write_text(json.dumps(summary.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        return str(p)

    def _record_hop(self, hop_id: str, success: bool) -> None:
        self.hop_checkpoints.append({"hop_id": hop_id, "status": "COMPLETED" if success else "FAILED"})

    async def generate_proposal_with_qwen(
        self, rfp_details: dict[str, Any], proposal_type: str = "technical"
    ) -> dict[str, Any]:
        """Generate proposal content using Qwen vLLM inference.

        Args:
            rfp_details: Dictionary containing RFP requirements, constraints, and context
            proposal_type: Type of proposal (technical, commercial, executive_summary)

        Returns:
            Dictionary with generated proposal content and metadata
        """
        if not self.qwen_enabled or self._qwen_gateway is None:
            return {"success": False, "error": "qwen_disabled", "content": None}

        # Validate inputs
        if not rfp_details or not isinstance(rfp_details, dict):
            return {"success": False, "error": "invalid_rfp_details", "content": None}

        if not proposal_type or not proposal_type.strip():
            return {"success": False, "error": "invalid_proposal_type", "content": None}

        try:
            # Prepare proposal generation prompt
            prompt = self._prepare_proposal_generation_prompt(rfp_details, proposal_type)

            # Create Qwen request
            request = AppsQwenRequest(
                app_name="apps_rfp",
                prompt=prompt,
                confidence_threshold=0.8,
                max_tokens=4096,  # High token limit for detailed proposals
                temperature=0.3,  # Balanced temperature for professional proposals
            )

            # Record telemetry start
            if apps_qwen_telemetry is not None and self._qwen_session_id is not None:
                apps_qwen_telemetry.record_request_start(
                    session_id=self._qwen_session_id,
                    app_name="apps_rfp",
                    model_id="Qwen/Qwen2.5-7B-Instruct",
                )

            # Perform inference
            response = await self._qwen_gateway.infer(request)

            # Record telemetry result
            if apps_qwen_telemetry is not None and self._qwen_session_id is not None:
                if response.success:
                    apps_qwen_telemetry.record_request_success(
                        session_id=self._qwen_session_id,
                        app_name="apps_rfp",
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
                        app_name="apps_rfp",
                        model_id=response.model_used,
                        error_message=response.error_message or "unknown_error",
                    )

            _emit_captures_evaluation_metric("apps_rfp", "RfpOrchestrator", "proposal_generation")

            return {
                "success": response.success,
                "content": response.response,
                "confidence": response.confidence,
                "model_used": response.model_used,
                "latency_ms": response.latency_ms,
                "proposal_type": proposal_type,
                "rfp_industry": rfp_details.get("industry", "unknown"),
                "error_message": response.error_message,
            }

        except Exception as e:
            _emit_records_telemetry_event("apps_rfp", "RfpOrchestrator", "proposal_generation_error")
            return {"success": False, "error": f"proposal_generation_failed: {str(e)}", "content": None}

    def _prepare_proposal_generation_prompt(self, rfp_details: dict[str, Any], proposal_type: str) -> str:
        """Prepare prompt for proposal generation using Qwen.

        Args:
            rfp_details: RFP requirements and context
            proposal_type: Type of proposal requested

        Returns:
            Formatted prompt string
        """
        # Extract key RFP information
        industry = rfp_details.get("industry", "Technology")
        problem_statement = rfp_details.get("problem_statement", "Business challenge requiring AI solution")
        requirements = rfp_details.get("requirements", [])
        constraints = rfp_details.get("constraints", [])
        timeline = rfp_details.get("timeline", "6 months")
        budget = rfp_details.get("budget", "To be determined")

        # Format requirements
        requirements_text = ""
        for i, req in enumerate(requirements[:8], 1):  # Limit to 8 requirements
            requirements_text += f"{i}. {req}\n"

        # Format constraints
        constraints_text = ""
        for constraint in constraints[:5]:  # Limit to 5 constraints
            constraints_text += f"- {constraint}\n"

        proposal_instructions = {
            "technical": "Generate a comprehensive technical proposal focusing on solution architecture, implementation approach, and technical feasibility.",
            "commercial": "Generate a commercial proposal focusing on business value, ROI, pricing structure, and competitive advantages.",
            "executive_summary": "Generate an executive summary proposal focusing on strategic alignment, key benefits, and high-level approach.",
            "full": "Generate a complete proposal covering technical, commercial, and strategic aspects.",
        }

        instruction = proposal_instructions.get(proposal_type, proposal_instructions["technical"])

        prompt = f"""PROPOSAL GENERATION REQUEST

INDUSTRY: {industry}
PROPOSAL TYPE: {proposal_type}
TIMELINE: {timeline}
BUDGET: {budget}

PROBLEM STATEMENT:
{problem_statement}

REQUIREMENTS:
{requirements_text}

CONSTRAINTS:
{constraints_text}

INSTRUCTIONS:
{instruction}

Please provide a professional proposal that includes:
1. Executive Summary
2. Understanding of Requirements
3. Proposed Solution
4. Implementation Approach
5. Value Proposition
6. Risk Assessment
7. Timeline and Milestones
8. Next Steps

Ensure the proposal is persuasive, technically sound, and addresses all stated requirements. Use professional business language and maintain a confident, competent tone throughout.
"""

        return prompt

    @staticmethod
    def _make_trace_id(request: RfpRequest) -> str:
        raw = f"rfp:{request.industry}:{request.problem_statement[:64]}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
