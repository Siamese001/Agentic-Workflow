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

# guardian: allow-silent-degradation -- Qwen vLLM is optional for research synthesis; graceful fallback to manual processing
try:
    from agentic_core.L3_orchestration.inference.qwen_vllm import (
        AppsQwenGateway,
        AppsQwenRequest,
        apps_qwen_telemetry,
    )

    _QWEN_AVAILABLE = True
except ImportError:
    AppsQwenGateway = None  # type: ignore[assignment]
    AppsQwenRequest = None  # type: ignore[assignment]
    apps_qwen_telemetry = None  # type: ignore[assignment]
    _QWEN_AVAILABLE = False

from apps_research._telemetry import (
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
from tqdm import tqdm

_log = logging.getLogger(__name__)


@dataclass
class ResearchOrchestrator:
    """Orchestrate end-to-end research artifact generation."""

    dry_run: bool = False
    output_dir: str = "reports/research"
    gate_mode: str = "HARD_FAIL"
    hop_checkpoints: list[dict[str, Any]] = field(default_factory=list)
    qwen_enabled: bool = True

    def __post_init__(self) -> None:
        self._assembly = None
        self._gate = None
        self._bootstrap_error: str | None = None
        try:
            from apps_research.engines.research_assembly_engine import ResearchAssemblyEngine
            from apps_research.validators.research_gate_validator import ResearchGateValidator

            self._assembly = ResearchAssemblyEngine()
            self._gate = ResearchGateValidator()
        except ImportError as exc:
            self._bootstrap_error = f"apps_research runtime dependency unavailable: {exc}"
            _log.warning(self._bootstrap_error)

        # Initialize Qwen vLLM for research synthesis
        self._qwen_gateway = None
        self._qwen_session_id = None
        self._qwen_init_error: str | None = None

        if self.qwen_enabled and _QWEN_AVAILABLE:
            try:
                self._qwen_gateway = AppsQwenGateway(model_id="Qwen/Qwen2.5-7B-Instruct")

                if apps_qwen_telemetry is not None:
                    self._qwen_session_id = apps_qwen_telemetry.start_session("apps_research")

                _emit_records_execution_trace("ResearchOrchestrator", "L2_EXECUTION", "qwen_vllm_init")

            except Exception as e:  # guardian: allow-broad-exception -- gateway init raises heterogeneous errors (aiohttp, ImportError, RuntimeError); all recorded and surfaced via _qwen_init_error
                _emit_records_telemetry_event("ResearchOrchestrator", "L2_EXECUTION", "qwen_init_error")
                _log.error("Qwen vLLM init failed — run() will raise if LOCAL_VLLM is selected: %s", e)
                self._qwen_init_error = str(e)

        try:
            from apps_research.config import load_research_specs

            self._specs = load_research_specs()
        # guardian: allow-silent-swallow -- Optional research specs dependency; not critical for core functionality
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

        # --- Local-first Qwen routing (Phase 1 + adapter enforcement) ---
        from agentic_core.L2_execution.types.vllm_gateway_adapter_types import (  # noqa: PLC0415
            VLLMGatewayAdapter,
        )
        from agentic_core.L2_execution.types.local_first_disposition import (  # noqa: PLC0415
            LocalFirstDisposition,
        )
        from agentic_core.L4_state.config.vllm_routing_predicates import (  # noqa: PLC0415
            Provider,
            evaluate as evaluate_routing,
        )

        # requires_policy_read / iteration_count / invalid_ast: repair-domain predicates.
        # Generation apps are single-pass pipelines with no policy-read concept, no retry
        # iterations, and no AST output — False/0/100 are semantically correct here, not
        # placeholders.  Wire these only if a retry loop or policy-read path is introduced.
        routing_ctx: dict[str, object] = {
            "requires_policy_read": False,
            "iteration_count": 0,
            "max_iterations": 100,
            "invalid_ast": False,
            "routing_version": "1",
        }
        routing_decision = evaluate_routing(routing_ctx)
        _dsp: LocalFirstDisposition | None = None

        if routing_decision.provider == Provider.LOCAL_VLLM:
            if self._qwen_init_error is not None:
                _dsp = LocalFirstDisposition.for_fail_init(
                    orchestrator="ResearchOrchestrator",
                    run_id=trace_id,
                    predicate_hash=routing_decision.predicate_evaluation_hash,
                    init_error=self._qwen_init_error,
                )
                _log.info("LOCAL_FIRST_DISPOSITION %s", json.dumps(_dsp.as_dict()))
                raise RuntimeError(f"LOCAL_VLLM selected but Qwen init failed: {self._qwen_init_error}")
            if self._qwen_gateway is not None:
                # Adapter enforces token budget, backpressure, and circuit breaker
                _adapter = VLLMGatewayAdapter()
                _prompt_preview = request.topic[:512]
                _adapter_result = _adapter.evaluate(
                    prompt=_prompt_preview,
                    task_class="research_synthesis",
                    severity="medium",
                )
                _telem = _adapter_result.telemetry.as_dict() if _adapter_result.telemetry is not None else {}
                if _adapter_result.route_to_gemini:
                    _dsp = LocalFirstDisposition.for_escalate(
                        orchestrator="ResearchOrchestrator",
                        run_id=trace_id,
                        predicate_hash=routing_decision.predicate_evaluation_hash,
                        telem=_telem,
                    )
                    _log.info("LOCAL_FIRST_DISPOSITION %s", json.dumps(_dsp.as_dict()))
                    _emit_records_telemetry_event(
                        "ResearchOrchestrator",
                        "L2_EXECUTION",
                        "adapter_escalate",
                    )
                else:
                    _emit_records_telemetry_event(
                        "ResearchOrchestrator",
                        "L2_EXECUTION",
                        "adapter_allow",
                    )
                    try:
                        qwen_result = await self.synthesize_research_with_qwen(
                            research_topic=request.topic,
                            sources=[],
                        )
                        _adapter.record_local_success(severity="medium")
                    except Exception as _exc:  # guardian: allow-broad-exception -- Qwen inference raises heterogeneous network/runtime errors; failure recorded in circuit breaker
                        _adapter.record_local_failure(severity="medium")
                        _dsp = LocalFirstDisposition.for_fail_exec(
                            orchestrator="ResearchOrchestrator",
                            run_id=trace_id,
                            predicate_hash=routing_decision.predicate_evaluation_hash,
                            telem=_telem,
                            exc=_exc,
                        )
                        _log.info("LOCAL_FIRST_DISPOSITION %s", json.dumps(_dsp.as_dict()))
                        raise
                    result.qwen_inference_result = qwen_result
                    _dsp = LocalFirstDisposition.for_allow(
                        orchestrator="ResearchOrchestrator",
                        run_id=trace_id,
                        predicate_hash=routing_decision.predicate_evaluation_hash,
                        telem=_telem,
                        qwen_result_present=qwen_result is not None,
                    )
                    _log.info("LOCAL_FIRST_DISPOSITION %s", json.dumps(_dsp.as_dict()))
                    _emit_records_execution_trace(
                        trace_id,
                        LayerSegment.L3_ORCHESTRATION,
                        "ResearchOrchestrator.run.qwen_local",
                    )
            else:
                _dsp = LocalFirstDisposition.for_skip(
                    orchestrator="ResearchOrchestrator",
                    run_id=trace_id,
                    provider_value="LOCAL_VLLM",
                    predicate_hash=routing_decision.predicate_evaluation_hash,
                    reason_code="gateway_not_initialized",
                )
                _log.info("LOCAL_FIRST_DISPOSITION %s", json.dumps(_dsp.as_dict()))
        else:
            _dsp = LocalFirstDisposition.for_skip(
                orchestrator="ResearchOrchestrator",
                run_id=trace_id,
                provider_value=routing_decision.provider.value,
                predicate_hash=routing_decision.predicate_evaluation_hash,
                reason_code="predicate_selected_opus",
            )
            _log.info("LOCAL_FIRST_DISPOSITION %s", json.dumps(_dsp.as_dict()))
        result.local_first_disposition = _dsp.as_dict() if _dsp is not None else None

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

            result.status = "gate_checking"
            gate = self._gate.validate(assembly.sections, assembly.source_register, required_ids)
            self._record_hop("HOP-2-GATE", gate.passed)
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
                    self._record_hop("HOP-3-EMIT", True)

        except (ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
            _log.error("[ResearchOrchestrator] Pipeline error trace=%s: %s", trace_id, exc, exc_info=True)
            result.status = "failed"
            result.error = str(exc)
            self._record_hop("PIPELINE-ERROR", False)
            result.provenance["checkpoints"] = [c["hop_id"] for c in self.hop_checkpoints]

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
        self.hop_checkpoints.append({"hop_id": hop_id, "status": "COMPLETED" if success else "FAILED"})

    async def synthesize_research_with_qwen(
        self,
        research_topic: str,
        sources: list[dict[str, Any]],
        synthesis_type: str = "comprehensive",
    ) -> dict[str, Any]:
        """Synthesize research content using Qwen vLLM inference.

        Args:
            research_topic: Main research topic/question
            sources: List of source materials with titles, content, and metadata
            synthesis_type: Type of synthesis (comprehensive, comparative, analytical)

        Returns:
            Dictionary with synthesized research content and metadata
        """
        if not self.qwen_enabled:
            return {"success": False, "error": "qwen_disabled", "content": None}

        if self._qwen_gateway is None or AppsQwenRequest is None:
            return {"success": False, "error": "qwen_gateway_unavailable", "content": None}

        if apps_qwen_telemetry is None or self._qwen_session_id is None:
            return {"success": False, "error": "qwen_telemetry_unavailable", "content": None}

        # Validate inputs
        if not research_topic or not research_topic.strip():
            return {"success": False, "error": "empty_research_topic", "content": None}

        if not sources or not isinstance(sources, list):
            return {"success": False, "error": "invalid_sources", "content": None}

        try:
            # Prepare research synthesis prompt
            prompt = self._prepare_research_synthesis_prompt(research_topic, sources, synthesis_type)

            # Create Qwen request
            request = AppsQwenRequest(
                app_name="apps_research",
                prompt=prompt,
                confidence_threshold=0.75,
                max_tokens=3072,  # Higher token limit for research synthesis
                temperature=0.4,  # Moderate temperature for creative synthesis
            )

            # Record telemetry start
            if apps_qwen_telemetry is not None and self._qwen_session_id is not None:
                apps_qwen_telemetry.record_request_start(
                    session_id=self._qwen_session_id,
                    app_name="apps_research",
                    model_id="Qwen/Qwen2.5-7B-Instruct",
                )

            # Perform inference
            response = await self._qwen_gateway.infer(request)

            # Record telemetry result
            if apps_qwen_telemetry is not None and self._qwen_session_id is not None:
                if response.success:
                    apps_qwen_telemetry.record_request_success(
                        session_id=self._qwen_session_id,
                        app_name="apps_research",
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
                        app_name="apps_research",
                        model_id=response.model_used,
                        error_message=response.error_message or "unknown_error",
                    )

            _emit_captures_evaluation_metric("apps_research", "ResearchOrchestrator", "research_synthesis")

            return {
                "success": response.success,
                "content": response.response,
                "confidence": response.confidence,
                "model_used": response.model_used,
                "latency_ms": response.latency_ms,
                "synthesis_type": synthesis_type,
                "sources_count": len(sources),
                "error_message": response.error_message,
            }

        except Exception as e:  # guardian: allow-broad-exception -- Qwen inference raises heterogeneous network/runtime errors; failure logged and returned as error dict
            _emit_records_telemetry_event("apps_research", "ResearchOrchestrator", "research_synthesis_error")
            return {"success": False, "error": f"synthesis_failed: {str(e)}", "content": None}

    def _prepare_research_synthesis_prompt(
        self,
        research_topic: str,
        sources: list[dict[str, Any]],
        synthesis_type: str,
    ) -> str:
        """Prepare prompt for research synthesis using Qwen.

        Args:
            research_topic: Main research topic
            sources: List of source materials
            synthesis_type: Type of synthesis requested

        Returns:
            Formatted prompt string
        """
        # Format sources for the prompt
        sources_text = ""
        for i, source in tqdm(
            enumerate(sources[:10], 1), desc="Processing", unit="item"
        ):  # Limit to 10 sources for token limits
            sources_text += f"\nSOURCE {i}:\n"
            sources_text += f"Title: {source.get('title', 'Untitled')}\n"
            sources_text += (
                f"Content: {source.get('content', source.get('summary', 'No content available'))[:500]}...\n"
            )
            if source.get("author"):
                sources_text += f"Author: {source['author']}\n"
            if source.get("date"):
                sources_text += f"Date: {source['date']}\n"
            sources_text += "---\n"

        synthesis_instructions = {
            "comprehensive": "Provide a comprehensive synthesis that integrates all sources, identifies key themes, and presents a holistic view of the research topic.",
            "comparative": "Compare and contrast the sources, identifying similarities, differences, and unique contributions of each source.",
            "analytical": "Analyze the sources critically, identifying strengths, weaknesses, biases, and research gaps.",
            "meta": "Provide a meta-analysis of the research landscape, identifying trends, controversies, and future directions.",
        }

        instruction = synthesis_instructions.get(synthesis_type, synthesis_instructions["comprehensive"])

        prompt = f"""RESEARCH SYNTHESIS REQUEST

TOPIC: {research_topic}
SYNTHESIS TYPE: {synthesis_type}

SOURCES:
{sources_text}

INSTRUCTIONS:
{instruction}

Please provide a well-structured synthesis that includes:
1. Executive Summary
2. Key Themes and Findings
3. Source Analysis
4. Critical Insights
5. Research Gaps or Future Directions
6. Conclusions

Ensure proper academic tone, cite sources appropriately, and maintain objectivity throughout the synthesis.
"""

        return prompt

    @staticmethod
    def _make_trace_id(request: ResearchRequest) -> str:
        mode_str = request.mode.value if hasattr(request.mode, "value") else str(request.mode)
        raw = f"research:{mode_str}:{request.topic[:64]}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
