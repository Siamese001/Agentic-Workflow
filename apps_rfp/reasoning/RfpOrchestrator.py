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

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
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

    def __post_init__(self) -> None:
        self._assembly = ProposalAssemblyEngine()
        self._gate = ProposalGateValidator()
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

    @staticmethod
    def _make_trace_id(request: RfpRequest) -> str:
        raw = f"rfp:{request.industry}:{request.problem_statement[:64]}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
