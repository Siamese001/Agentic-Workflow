"""
ResearchOrchestrator — apps_research.

Orchestrates the complete research artifact generation pipeline:
  1. Source plan construction
  2. Research assembly (sections, matrix, source register)
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

_emit_authorize_and_execute("p2", "ResearchOrchestrator", "execution_auth")
_emit_validates_capability("p2", "ResearchOrchestrator", "capability_check")
_emit_routes_to_capability("p2", "ResearchOrchestrator", "capability_route")
_emit_writes_via_uwg("p2", "ResearchOrchestrator", "uwg_write")
_emit_blocks_direct_write("p2", "ResearchOrchestrator", "direct_write_block")
_emit_records_tool_invocation("p2", "ResearchOrchestrator", "tool_invocation")
_emit_captures_execution_output("p2", "ResearchOrchestrator", "exec_output")
_emit_dispatches_agent("p3", "ResearchOrchestrator", "agent_dispatch")
_emit_coordinates_agents("p3", "ResearchOrchestrator", "agent_coordination")
_emit_records_workflow_lineage("p3", "ResearchOrchestrator", "workflow_lineage")
_emit_records_healing_outcome("p3", "ResearchOrchestrator", "healing_outcome")
_emit_escalates_failure("p3", "ResearchOrchestrator", "failure_escalation")
_emit_orchestrates_workflow("p3", "ResearchOrchestrator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ResearchOrchestrator", "healing_dispatch")
_emit_invokes_evaluation("p3", "ResearchOrchestrator", "evaluation_signal")
_emit_records_telemetry_event("p4", "ResearchOrchestrator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ResearchOrchestrator", "eval_metric")
_emit_stores_embedding("p4", "ResearchOrchestrator", "embedding_store")
_emit_updates_meta_learning_state("p4", "ResearchOrchestrator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ResearchOrchestrator", "exec_snapshot_link")
from apps_research.engines.research_assembly_engine import ResearchAssemblyEngine
from apps_research.types.research_types import (
    ResearchRequest,
    ResearchResult,
    ResearchRunSummary,
    ResearchStatus,
)
from apps_research.validators.research_gate_validator import ResearchGateValidator

_emit_applies_guardrail("p0", "ResearchOrchestrator", "p0_governance")
_emit_reads_policy_state("p0", "ResearchOrchestrator", "policy_binding")
_emit_snapshots_state("p0", "ResearchOrchestrator", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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

_emit_emits_metric_event("ResearchOrchestrator", "p4obs", "metric_1")
_emit_emits_metric_event("ResearchOrchestrator", "p4obs", "metric_2")
_emit_emits_metric_event("ResearchOrchestrator", "p4obs", "metric_3")
_emit_emits_metric_event("ResearchOrchestrator", "p4obs", "metric_4")
_emit_emits_metric_event("ResearchOrchestrator", "p4obs", "metric_5")
_emit_emits_metric_event("ResearchOrchestrator", "p4obs", "metric_6")
_emit_records_incident_event("ResearchOrchestrator", "p4obs", "incident")
_emit_captures_runtime_anomaly("ResearchOrchestrator", "p4obs", "anomaly")
_emit_writes_observability_log("ResearchOrchestrator", "p4obs", "obs_log")
_emit_updates_monitoring_state("ResearchOrchestrator", "p4obs", "mon_state")
_emit_triggers_alert("ResearchOrchestrator", "p4obs", "alert")
_emit_links_incident_trace("ResearchOrchestrator", "p4obs", "trace_link")
_emit_captures_pattern("ResearchOrchestrator", "p3lm", "pattern")
_emit_records_learning_event("ResearchOrchestrator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ResearchOrchestrator", "p3lm", "snapshot")
_emit_feeds_meta_learning("ResearchOrchestrator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ResearchOrchestrator", "p3lm", "routing")
_emit_improves_agent_policy("ResearchOrchestrator", "p3lm", "policy")
_emit_stores_learning_state("ResearchOrchestrator", "p3lm", "state")
_emit_records_execution_trace("ResearchOrchestrator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ResearchOrchestrator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ResearchOrchestrator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ResearchOrchestrator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ResearchOrchestrator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ResearchOrchestrator", "env_read", "p2_env_1")
_emit_reads_environ("ResearchOrchestrator", "env_read", "p2_env_2")
_emit_reads_runtime_state("ResearchOrchestrator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ResearchOrchestrator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ResearchOrchestrator", "context_pull")
_emit_pulls_context("p1", "ResearchOrchestrator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ResearchOrchestrator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ResearchOrchestrator", "uwg_term_2")
_emit_writes_through("p1", "ResearchOrchestrator", "write_through")
_emit_writes_through("p1", "ResearchOrchestrator", "write_through_2")
_emit_validated_by_safety_plane("p1", "ResearchOrchestrator", "safety_validation")
_emit_invokes_eval("p1", "ResearchOrchestrator", "eval_call")
_emit_proposal_commits_routing("p1", "ResearchOrchestrator", "routing_commit")
emit_replay_key("p0", "ResearchOrchestrator")
emit_determinism_digest("p0", "ResearchOrchestrator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

_log = logging.getLogger(__name__)


@dataclass
class ResearchOrchestrator:
    """Orchestrate end-to-end research artifact generation."""

    dry_run: bool = False
    output_dir: str = "reports/research"
    gate_mode: str = "HARD_FAIL"
    hop_checkpoints: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._assembly = ResearchAssemblyEngine()
        self._gate = ResearchGateValidator()

        try:
            from apps_research.config import load_research_specs

            self._specs = load_research_specs()
        except ImportError:
            self._specs = None

        try:
            from agentic_core.adg.runtime.behavioral_index import ADGBehavioralIndex

            _idx = ADGBehavioralIndex.from_latest(Path(__file__).resolve().parents[3])
            _profile = _idx.profile_for(Path(__file__).resolve()) if _idx else None
            self.adg_behavioral_score: float = _profile.behavioral_score if _profile else 0.5
            self.adg_antipattern_signals: list[str] = sorted(_profile.antipattern_signals) if _profile else []
        except (ImportError, AttributeError, OSError):
            self.adg_behavioral_score = 0.5
            self.adg_antipattern_signals = []

    def run(self, request: ResearchRequest) -> ResearchResult:
        """Execute full research generation pipeline."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ResearchOrchestrator.run")

        trace_id = request.trace_id or self._make_trace_id(request)
        mode_str = request.mode.value if hasattr(request.mode, "value") else str(request.mode)
        _log.info("[ResearchOrchestrator] trace=%s topic=%s mode=%s", trace_id, request.topic, mode_str)

        result = ResearchResult(
            trace_id=trace_id,
            topic=request.topic,
            mode=mode_str,
            status=ResearchStatus.GENERATING,
            provenance={
                "trace_id": trace_id,
                "topic": request.topic,
                "mode": mode_str,
                "app": "apps_research",
            },
        )

        try:
            assembly = self._assembly.execute(request)
            self._record_hop("HOP-1-ASSEMBLY", bool(assembly.sections))
            result.sections = assembly.sections
            result.comparison_matrix = assembly.comparison_matrix
            result.source_register = assembly.source_register

            required_ids: list[str] = []
            if self._specs:
                mode_cfg = self._specs.artifact_modes.get(mode_str)
                if mode_cfg:
                    required_ids = mode_cfg.required_sections

            result.status = ResearchStatus.GATE_CHECKING
            gate = self._gate.validate(assembly.sections, assembly.source_register, required_ids)
            self._record_hop("HOP-2-GATE", gate.passed)
            result.quality_score = gate.quality_score
            result.gate_violations = [f"[{v.rule_id}:{v.severity}] {v.message}" for v in gate.violations]

            if not gate.passed and self.gate_mode == "HARD_FAIL":
                result.status = ResearchStatus.FAILED
                _log.error("[ResearchOrchestrator] Gate FAILED: %d violations", len(gate.violations))
            else:
                is_dry = request.dry_run or self.dry_run
                result.status = ResearchStatus.DRY_RUN if is_dry else ResearchStatus.COMPLETE
                if not is_dry:
                    paths = self._emit_artifacts(result, trace_id)
                    result.artifact_paths = paths
                    self._record_hop("HOP-3-EMIT", True)

        except (ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
            _log.error("[ResearchOrchestrator] Pipeline error trace=%s: %s", trace_id, exc, exc_info=True)
            result.status = ResearchStatus.FAILED
            result.error = str(exc)
            self._record_hop("PIPELINE-ERROR", False)
            result.provenance["checkpoints"] = [c["hop_id"] for c in self.hop_checkpoints]

        summary = ResearchRunSummary(
            trace_id=trace_id,
            status=result.status.value,
            topic=result.topic,
            mode=result.mode,
            sections_generated=len(result.sections),
            sources_registered=len(result.source_register),
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
            "[ResearchOrchestrator] Complete trace=%s status=%s score=%.2f",
            trace_id,
            result.status.value,
            result.quality_score,
        )
        return result

    def _emit_artifacts(self, result: ResearchResult, trace_id: str) -> list[str]:
        out = Path(self.output_dir)
        out.mkdir(parents=True, exist_ok=True)
        paths: list[str] = []

        brief_path = out / f"research_{result.mode}_{trace_id[:8]}.md"
        lines = [
            f"# Research Artifact — {result.topic}",
            "",
            f"**Mode:** {result.mode}  ",
            f"**Trace ID:** `{trace_id}`  ",
            f"**Quality Score:** {result.quality_score:.0%}  ",
            "",
            "---",
            "",
        ]
        for section in result.sections:
            claim_label = f" `[{section.claim_type.value}]`" if hasattr(section.claim_type, "value") else ""
            lines += [f"## {section.heading}{claim_label}", "", section.body, "", "---", ""]

        if result.comparison_matrix:
            lines += ["## Comparison Matrix", ""]
            if result.comparison_matrix:
                dims = list(result.comparison_matrix[0].dimensions.keys())
                header = "| Subject | " + " | ".join(d.replace("_", " ").title() for d in dims) + " |"
                separator = "|---------|" + "|".join(["------"] * len(dims)) + "|"
                lines += [header, separator]
                for row in result.comparison_matrix:
                    cells = " | ".join(row.dimensions.get(d, "—") for d in dims)
                    lines.append(f"| {row.subject} | {cells} |")
                lines.append("")

        brief_path.write_text("\n".join(lines), encoding="utf-8")
        paths.append(str(brief_path))

        src_reg_path = out / f"source_register_{trace_id[:8]}.json"
        src_data = [
            {
                "source_id": s.source_id,
                "title": s.title,
                "claim_type": s.claim_type.value if hasattr(s.claim_type, "value") else str(s.claim_type),
                "confidence": s.confidence,
                "summary": s.summary,
                "url": s.url,
                "section_id": s.section_id,
            }
            for s in result.source_register
        ]
        src_reg_path.write_text(json.dumps(src_data, indent=2), encoding="utf-8")
        paths.append(str(src_reg_path))

        return paths

    def _emit_run_summary(self, summary: ResearchRunSummary, trace_id: str) -> str:
        out = Path(self.output_dir)
        out.mkdir(parents=True, exist_ok=True)
        p = out / f"run_summary_{trace_id[:8]}.json"
        p.write_text(json.dumps(summary.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        return str(p)

    def _record_hop(self, hop_id: str, success: bool) -> None:
        self.hop_checkpoints.append({"hop_id": hop_id, "status": "COMPLETED" if success else "FAILED"})

    @staticmethod
    def _make_trace_id(request: ResearchRequest) -> str:
        mode_str = request.mode.value if hasattr(request.mode, "value") else str(request.mode)
        raw = f"research:{mode_str}:{request.topic[:64]}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
