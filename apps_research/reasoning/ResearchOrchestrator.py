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

from apps_research._telemetry import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
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

from apps_research.types.research_types import (
    ResearchRequest,
    ResearchResult,
    ResearchRunSummary,
    ResearchStatus,
)
from apps_research._telemetry import (
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

_log = logging.getLogger(__name__)


@dataclass
class ResearchOrchestrator:
    """Orchestrate end-to-end research artifact generation."""

    dry_run: bool = False
    output_dir: str = "artifacts/apps_research"
    gate_mode: str = "HARD_FAIL"
    stage_checkpoints: list[dict[str, Any]] = field(default_factory=list)  # renamed from hop_checkpoints; back-compat alias below

    def __post_init__(self) -> None:
        self._assembly = None
        self._gate = None
        self._bootstrap_error: str | None = None
        try:
            from apps_research.engines.research_assembly_engine import ResearchAssemblyEngine
            from apps_research.validators.research_gate_validator import ResearchGateValidator

            self._assembly = ResearchAssemblyEngine()
            self._gate = ResearchGateValidator()
        except ImportError as exc:  # guardian: allow-log-and-swallow -- apps_research runtime is optional; bootstrap error recorded for later diagnostics
            self._bootstrap_error = f"apps_research runtime dependency unavailable: {exc}"
            _log.warning(self._bootstrap_error)

        try:
            from apps_research.config import load_research_specs

            self._specs = load_research_specs()
        except ImportError:  # guardian: allow-silent-swallow -- Optional research specs dependency; not critical for core functionality
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

    async def run(self, request: ResearchRequest) -> ResearchResult:
        """Execute full research generation pipeline."""
        trace_id = request.trace_id or self._make_trace_id(request)
        _emit_records_execution_trace(trace_id, LayerSegment.L3_ORCHESTRATION, "ResearchOrchestrator.run")
        if self._bootstrap_error is not None:
            raise RuntimeError(self._bootstrap_error)
        if self._assembly is None or self._gate is None:
            raise RuntimeError("ResearchOrchestrator bootstrap incomplete")
        mode_str = request.mode.value if hasattr(request.mode, "value") else str(request.mode)
        _log.info("[ResearchOrchestrator] trace=%s topic=%s mode=%s", trace_id, request.topic, mode_str)

        result = ResearchResult(
            trace_id=trace_id,
            topic=request.topic,
            mode=mode_str,
            status="generating",
            provenance={
                "trace_id": trace_id,
                "topic": request.topic,
                "mode": mode_str,
                "app": "apps_research",
            },
        )

        try:
            assembly = self._assembly.execute(request)
            self._record_hop("STAGE-ASSEMBLY", bool(assembly.sections))
            result.sections = assembly.sections
            result.comparison_matrix = assembly.comparison_matrix
            result.source_register = assembly.source_register

            required_ids: list[str] = []
            if self._specs:
                mode_cfg = self._specs.artifact_modes.get(mode_str)
                if mode_cfg:
                    required_ids = mode_cfg.required_sections

            result.status = "gate_checking"
            gate = self._gate.validate(assembly.sections, assembly.source_register, required_ids)
            self._record_hop("STAGE-GATE", gate.passed)
            result.quality_score = gate.quality_score
            result.gate_violations = [f"[{v.rule_id}:{v.severity}] {v.message}" for v in gate.violations]

            if not gate.passed and self.gate_mode == "HARD_FAIL":
                result.status = "failed"
                _log.error("[ResearchOrchestrator] Gate FAILED: %d violations", len(gate.violations))
            else:
                is_dry = request.dry_run or self.dry_run
                result.status = "dry_run" if is_dry else "complete"
                if not is_dry:
                    paths = self._emit_artifacts(result, trace_id)
                    result.artifact_paths = paths
                    self._record_hop("STAGE-EMIT", True)

        except (ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
            _log.error("[ResearchOrchestrator] Pipeline error trace=%s: %s", trace_id, exc, exc_info=True)
            result.status = "failed"
            result.error = str(exc)
            self._record_hop("PIPELINE-ERROR", False)
            result.provenance["checkpoints"] = [c["hop_id"] for c in self.stage_checkpoints]

        summary = ResearchRunSummary(
            trace_id=trace_id,
            status=result.status,
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
            result.status,
            result.quality_score,
        )
        return result

    def _emit_artifacts(self, result: ResearchResult, trace_id: str) -> list[str]:
        out = self._resolve_output_dir()
        paths: list[str] = []

        brief_path = out / f"research_{result.mode}_{trace_id[:8]}.md"
        lines = [
            f"# Research Artifact — {self._safe_markdown(result.topic)}",
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
            lines += [
                f"## {self._safe_markdown(section.heading)}{claim_label}",
                "",
                self._safe_markdown(section.body),
                "",
                "---",
                "",
            ]

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
        src_reg_path.write_text(
            json.dumps(src_data, indent=2, sort_keys=True, ensure_ascii=False),
            encoding="utf-8",
        )
        paths.append(str(src_reg_path))

        return paths

    def _emit_run_summary(self, summary: ResearchRunSummary, trace_id: str) -> str:
        out = self._resolve_output_dir()
        p = out / f"run_summary_{trace_id[:8]}.json"
        p.write_text(
            json.dumps(summary.to_dict(), indent=2, sort_keys=True, ensure_ascii=False),
            encoding="utf-8",
        )
        return str(p)

    def _resolve_output_dir(self) -> Path:
        out = Path(self.output_dir).expanduser().resolve()
        if out.exists() and not out.is_dir():
            raise ValueError(f"output_dir must be a directory, got file: {out}")
        out.mkdir(parents=True, exist_ok=True)
        return out

    @staticmethod
    def _safe_markdown(value: str) -> str:
        return value.replace("\x00", "").replace("\r\n", "\n").replace("```", "``\u200b`").strip()

    def _record_hop(self, hop_id: str, success: bool) -> None:
        self.stage_checkpoints.append({"hop_id": hop_id, "status": "COMPLETED" if success else "FAILED"})

    @property
    def hop_checkpoints(self) -> list[dict[str, Any]]:
        """Back-compat alias for stage_checkpoints."""
        return self.stage_checkpoints

    @staticmethod
    def _make_trace_id(request: ResearchRequest) -> str:
        mode_str = request.mode.value if hasattr(request.mode, "value") else str(request.mode)
        raw = f"research:{mode_str}:{request.topic[:64]}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
