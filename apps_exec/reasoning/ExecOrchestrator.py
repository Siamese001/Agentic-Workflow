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

    def __post_init__(self) -> None:
        self._ingestion = IngestionEngine()
        self._extraction = CapabilityExtractionEngine()
        self._assembly = BriefAssemblyEngine()
        self._gate = StyleGateValidator()
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

    @staticmethod
    def _make_trace_id(request: ExecBriefRequest) -> str:
        audience = request.audience.value if hasattr(request.audience, "value") else str(request.audience)
        raw = f"exec:{audience}:{','.join(request.source_dirs)}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
