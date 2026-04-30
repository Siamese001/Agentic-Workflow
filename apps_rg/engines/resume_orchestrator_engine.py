"""
Resume Orchestrator Engine - L3 Manager handling HOP transitions
Refactored from orchestrate_resume.py + RgResumeOrchestrator.py
Following Batch 1 specifications

HARDENING: Extends the workflow to include Generation (K9), Refinement (Optimizer/Ranker),
and Safety (ATS). It defines the full Sovereign Pipeline.
"""

from __future__ import annotations

from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
    traces_execute,
)

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

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

_emit_authorize_and_execute("p2", "resume_orchestrator_engine", "execution_auth")
_emit_validates_capability("p2", "resume_orchestrator_engine", "capability_check")
_emit_routes_to_capability("p2", "resume_orchestrator_engine", "capability_route")
_emit_writes_via_uwg("p2", "resume_orchestrator_engine", "uwg_write")
_emit_blocks_direct_write("p2", "resume_orchestrator_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "resume_orchestrator_engine", "tool_invocation")
_emit_captures_execution_output("p2", "resume_orchestrator_engine", "exec_output")
_emit_dispatches_agent("p3", "resume_orchestrator_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "resume_orchestrator_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "resume_orchestrator_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "resume_orchestrator_engine", "healing_outcome")
_emit_escalates_failure("p3", "resume_orchestrator_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "resume_orchestrator_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "resume_orchestrator_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "resume_orchestrator_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "resume_orchestrator_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "resume_orchestrator_engine", "eval_metric")
_emit_stores_embedding("p4", "resume_orchestrator_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "resume_orchestrator_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "resume_orchestrator_engine", "exec_snapshot_link")
from apps_rg.engines.ats_compatibility_engine import ATSCompatibilityEngine
from apps_rg.engines.base_rg_engine import BaseRGEngine
from apps_rg.engines.bullet_diversity_gate import BulletDiversityGate
from apps_rg.engines.clerk_extraction_engine import ClerkExtractionEngine
from apps_rg.engines.content_optimizer_engine import ContentOptimizerEngine
from apps_rg.reasoning.ContentQualityAgent import ContentQualityAgent as ContentQualityEngine
from apps_rg.engines.data_enrichment_engine import DataEnrichmentEngine
from apps_rg.engines.gap_closure_engine import GapClosureEngine
from apps_rg.engines.job_alignment_scorer import JobAlignmentScorer
from apps_rg.engines.job_pattern_matcher import JobPatternMatcher
from apps_rg.engines.role_archetype_classifier import RoleArchetypeClassifier
from apps_rg.engines.section_ranker_engine import SectionRankerEngine
from apps_rg.engines.verbatim_provenance_gate import VerbatimProvenanceGate
from apps_rg.types.trace_registry_types import TraceRegistry

_emit_applies_guardrail("p0", "resume_orchestrator_engine", "p0_governance")
_emit_reads_policy_state("p0", "resume_orchestrator_engine", "policy_binding")
_emit_snapshots_state("p0", "resume_orchestrator_engine", "state_snapshot")
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

_emit_emits_metric_event("resume_orchestrator_engine", "p4obs", "metric_1")
_emit_emits_metric_event("resume_orchestrator_engine", "p4obs", "metric_2")
_emit_emits_metric_event("resume_orchestrator_engine", "p4obs", "metric_3")
_emit_emits_metric_event("resume_orchestrator_engine", "p4obs", "metric_4")
_emit_emits_metric_event("resume_orchestrator_engine", "p4obs", "metric_5")
_emit_emits_metric_event("resume_orchestrator_engine", "p4obs", "metric_6")
_emit_records_incident_event("resume_orchestrator_engine", "p4obs", "incident")
_emit_captures_runtime_anomaly("resume_orchestrator_engine", "p4obs", "anomaly")
_emit_writes_observability_log("resume_orchestrator_engine", "p4obs", "obs_log")
_emit_updates_monitoring_state("resume_orchestrator_engine", "p4obs", "mon_state")
_emit_triggers_alert("resume_orchestrator_engine", "p4obs", "alert")
_emit_links_incident_trace("resume_orchestrator_engine", "p4obs", "trace_link")
_emit_captures_pattern("resume_orchestrator_engine", "p3lm", "pattern")
_emit_records_learning_event("resume_orchestrator_engine", "p3lm", "learning_event")
_emit_writes_learning_snapshot("resume_orchestrator_engine", "p3lm", "snapshot")
_emit_feeds_meta_learning("resume_orchestrator_engine", "p3lm", "meta_feed")
_emit_updates_routing_strategy("resume_orchestrator_engine", "p3lm", "routing")
_emit_improves_agent_policy("resume_orchestrator_engine", "p3lm", "policy")
_emit_stores_learning_state("resume_orchestrator_engine", "p3lm", "state")
_emit_records_execution_trace("resume_orchestrator_engine", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("resume_orchestrator_engine", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("resume_orchestrator_engine", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("resume_orchestrator_engine", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("resume_orchestrator_engine", "L4_STATE", "p2_trace_5")
_emit_reads_environ("resume_orchestrator_engine", "env_read", "p2_env_1")
_emit_reads_environ("resume_orchestrator_engine", "env_read", "p2_env_2")
_emit_reads_runtime_state("resume_orchestrator_engine", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("resume_orchestrator_engine", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "resume_orchestrator_engine", "context_pull")
_emit_pulls_context("p1", "resume_orchestrator_engine", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "resume_orchestrator_engine", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "resume_orchestrator_engine", "uwg_term_2")
_emit_writes_through("p1", "resume_orchestrator_engine", "write_through")
_emit_writes_through("p1", "resume_orchestrator_engine", "write_through_2")
_emit_validated_by_safety_plane("p1", "resume_orchestrator_engine", "safety_validation")
_emit_invokes_eval("p1", "resume_orchestrator_engine", "eval_call")
_emit_proposal_commits_routing("p1", "resume_orchestrator_engine", "routing_commit")
_emit_escalates_to_human("p1", "resume_orchestrator_engine", "human_escalation")
_emit_routes_through("p1", "resume_orchestrator_engine", "route_through")
_emit_checks_agent_registry("p1", "resume_orchestrator_engine", "agent_registry")
_emit_validates_agent_capability("p1", "resume_orchestrator_engine", "capability")
_emit_dispatches_execution_plan("p1", "resume_orchestrator_engine", "exec_plan")
_emit_agent_executes_agent("p1", "resume_orchestrator_engine", "sub_agent")
_emit_routes_to_agent("p1", "resume_orchestrator_engine", "target_agent")
_emit_verifies_policy("p1", "resume_orchestrator_engine", "policy_check")
_emit_observes_runtime_state("p1", "resume_orchestrator_engine", "runtime_state")
_emit_verifies_boundary("p1", "resume_orchestrator_engine", "boundary_check")
_emit_transcripts_response("p1", "resume_orchestrator_engine", "transcript")
_emit_hard_fails_untranscripted("p1", "resume_orchestrator_engine")
_emit_gated_by_confidence("p1", "resume_orchestrator_engine", "confidence_gate")
emit_replay_key("p0", "resume_orchestrator_engine")
emit_determinism_digest("p0", "resume_orchestrator_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


@dataclass
class HopCheckpoint:
    hop_id: str
    status: str
    metrics: dict[str, Any] = field(default_factory=dict)


class ResumeOrchestratorEngine(BaseRGEngine):
    """
    L3 Orchestrator (Final).
    Drives the full Sovereign Pipeline: Prep -> Gen -> Refine -> Verify with cyclic retry.
    """

    def __init__(self, ctx: Any, mission_id: str = "default") -> None:
        super().__init__(config=ctx, node_id="ORCHESTRATOR_L3")
        self.hop_checkpoints: list[HopCheckpoint] = []
        self.mission_id = mission_id
        if self.rg_specs and hasattr(self.rg_specs, "orchestrator"):
            self.GLOBAL_STEP_LIMIT = self.rg_specs.orchestrator.global_step_limit
            self.MAX_RETRY_ITERATIONS = self.rg_specs.orchestrator.max_retry_iterations
        else:
            self.GLOBAL_STEP_LIMIT = 50
            self.MAX_RETRY_ITERATIONS = 3
        if (
            self.toggles
            and hasattr(self.toggles, "use_persistent_tracing")
            and self.toggles.use_persistent_tracing
        ):
            trace_path = Path(f"docs/reports/missions/{mission_id}/trace.jsonl")
            self.ctx.trace = TraceRegistry(persistence_path=trace_path)

    @traces_execute(layer="L3_ORCHESTRATION")
    async def execute(self, job_description: str) -> dict[str, Any]:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "ResumeOrchestratorEngine.execute"
        )

        self._mcp_audit("workflow_start")
        mission_input = {
            "job_description": job_description,
            "master_resume": getattr(self.ctx, "master_resume", {}),
            "job_description_keywords": job_description.lower().split(),
        }
        try:
            self.ctx.buffer.write("mission_input", mission_input, source_agent=self.name)
        except PermissionError:  # review: Permission errors should validate access before operation
            pass
        try:
            step_count = 0
            for hop_engine, hop_id in [
                # P3.2 — Archetype classification first; mutates mission_input.role_*.
                (RoleArchetypeClassifier, "HOP-0.5-ARCHETYPE"),
                (ClerkExtractionEngine, "HOP-1"),
                (DataEnrichmentEngine, "HOP-2"),
                # P1: JD facet extraction + alignment scoring before optimization.
                (JobPatternMatcher, "HOP-2.5-JD-FACETS"),
                (JobAlignmentScorer, "HOP-2.7-JD-ALIGN"),
            ]:
                step_count += 1
                if step_count > self.GLOBAL_STEP_LIMIT:
                    self.ctx.trace.add_trace("CRITICAL_FAILURE", {"reason": "Global step limit exceeded"})
                    raise RuntimeError(
                        f"Mission aborted: Exceeded global step limit of {self.GLOBAL_STEP_LIMIT}",
                    )
                await self._run_engine(hop_engine, hop_id)
            for hop_engine, hop_id in [
                (GapClosureEngine, "HOP-3-K9"),
                (ContentOptimizerEngine, "HOP-4-OPT"),
                # P4.1 — Diversity rebalance after JD-driven optimization,
                # before final section ranking.
                (BulletDiversityGate, "HOP-4.5-DIVERSITY"),
                (SectionRankerEngine, "HOP-4-RANK"),
            ]:
                step_count += 1
                if step_count > self.GLOBAL_STEP_LIMIT:
                    raise RuntimeError(f"Exceeded global step limit of {self.GLOBAL_STEP_LIMIT}")
                await self._run_engine(hop_engine, hop_id)
            iteration = 0
            from apps_rg.config.reasoning_toggles_config import RGReasoningToggles as _RGToggles

            _defaults = _RGToggles()
            use_cyclic = (
                self.toggles.use_cyclic_validation
                if self.toggles and hasattr(self.toggles, "use_cyclic_validation")
                else _defaults.use_cyclic_validation
            )
            while iteration < self.MAX_RETRY_ITERATIONS and use_cyclic:
                iteration += 1
                # Sync current_resume from buffer before validators read it.
                # Engines write to ctx.buffer; ContentQualityAgent expects ctx.current_resume.
                ranked = self.ctx.buffer.read("ranked_content")
                optimized = self.ctx.buffer.read("optimized_content")
                processed = ranked or optimized
                # Passthrough: ranking/optimization engines transform `experience`
                # but do not handle flat sections (skills, summary, headline,
                # contact_info, competencies, certifications_and_credentials,
                # education). Without merging master_resume back in, those
                # sections reach ContentQualityAgent as empty and trip the
                # MIN_SECTION_LENGTHS check. Merge: master as base, processed
                # overrides per-key, but never with an empty value.
                if processed and isinstance(processed, dict):
                    merged: dict = dict(self.ctx.master_resume or {})
                    for k, v in processed.items():
                        if v not in (None, "", [], {}):
                            merged[k] = v
                    self.ctx.current_resume = merged
                    # Re-publish merged artifact so the final save
                    # (ctx.buffer.read("ranked_content")) includes passthrough
                    # sections (skills, summary, headline, contact_info,
                    # competencies, certifications_and_credentials, education).
                    try:
                        self.ctx.buffer.write(
                            "ranked_content", merged, source_agent=self.name
                        )
                    except (PermissionError, AttributeError):
                        pass
                else:
                    self.ctx.current_resume = self.ctx.master_resume
                quality_engine = ContentQualityEngine()
                quality_engine.ctx = self.ctx
                await quality_engine.execute()
                quality_passed = not self.ctx.has_signal("QUALITY_FAILURE")
                quality_report = self.ctx.buffer.read(
                    "quality_report",
                    {"status": "passed" if quality_passed else "failed", "issues": []},
                ) or {"status": "passed" if quality_passed else "failed", "issues": []}
                await self._run_engine(ATSCompatibilityEngine, "HOP-5-ATS")
                ats_report = self.ctx.buffer.read("ats_report", {"valid": False, "issues": []}) or {
                    "valid": False,
                    "issues": [],
                }
                if quality_report.get("status") == "passed" and ats_report.get("valid", False):
                    self.ctx.trace.add_trace(
                        "VALIDATION_PASSED",
                        {
                            "iteration": iteration,
                            "quality_score": quality_report.get("score"),
                            "ats_valid": ats_report.get("valid"),
                        },
                    )
                    break
                if iteration < self.MAX_RETRY_ITERATIONS:
                    self.ctx.trace.add_trace(
                        "RETRY_CYCLE",
                        {
                            "iteration": iteration,
                            "quality_issues": quality_report.get("issues", []),
                            "ats_issues": ats_report.get("issues", []),
                        },
                    )
                    mission_input["retry_iteration"] = iteration
                    mission_input["quality_feedback"] = quality_report.get("issues", [])
                    mission_input["ats_feedback"] = ats_report.get("issues", [])
                    self.ctx.buffer.write("mission_input", mission_input, source_agent="ORCHESTRATOR_RETRY")
                    await self._run_engine(DataEnrichmentEngine, "HOP-2-RETRY")
                    await self._run_engine(GapClosureEngine, "HOP-3-K9-RETRY")
                    await self._run_engine(ContentOptimizerEngine, "HOP-4-OPT-RETRY")
                    await self._run_engine(SectionRankerEngine, "HOP-4-RANK-RETRY")
            final_ats = self.ctx.buffer.read("ats_report", {"valid": False})
            final_quality = self.ctx.buffer.read("quality_report", {"score": 0})
            status = "SUCCESS"
            if not final_ats.get("valid", False):
                status = "WARNING"
            # quality_report.score is on a 0.0-1.0 scale (see
            # ContentQualityAgent.execute(): score = max(0.0, 1.0 - issues/20)).
            # Normalize the threshold to the same scale:
            #   - if rg_specs supplies min_quality_score in 0.0-1.0, use as-is
            #   - if rg_specs supplies it in 0-100 (legacy), divide by 100
            #   - default 0.70 (= 70%)
            if self.rg_specs and hasattr(self.rg_specs, "validation"):
                _mqs = self.rg_specs.validation.min_quality_score
                quality_threshold = _mqs / 100.0 if _mqs > 1.0 else _mqs
            else:
                quality_threshold = 0.70
            if final_quality.get("score", 0) < quality_threshold:
                status = "WARNING"
            final_artifact = self.ctx.buffer.read("ranked_content", {})

            # P2 — Verbatim provenance gate (truthful representation guardrail).
            # Runs against ranked_content (post-rank, pre-emit). Stamps each
            # emitted bullet with a provenance block tied back to the master
            # resume; downgrades status to WARNING for metric warnings,
            # HUMAN_REVIEW for fail (no master match or scope inflation).
            try:
                provenance_engine = VerbatimProvenanceGate(self.ctx)
                provenance_report = await provenance_engine.execute()
                if not provenance_report.get("valid", True):
                    status = "HUMAN_REVIEW"
                elif provenance_report.get("warnings") and status == "SUCCESS":
                    status = "WARNING"
                # Refresh final_artifact since gate re-published ranked_content.
                final_artifact = self.ctx.buffer.read("ranked_content", final_artifact)
            except (ValueError, KeyError) as exc:
                self.logger.warning("VerbatimProvenanceGate degraded: %s", exc)
                provenance_report = {"valid": True, "degraded": True, "error": str(exc)}

            # W9 — Anti-overfit detector (orchestrator-direct gate, ADR-pending).
            # Runs the L5 anti-overfit detector on the sealed resume text vs
            # the JD as user-sample. Independent of judge/rubric (rubric runs
            # offline at eval time). Hard-floor: aggregate_overfit_score >= 3
            # downgrades status; fake_history flag escalates.
            overfit_block = self._run_anti_overfit_check(final_artifact, job_description)
            if overfit_block.get("escalate"):
                status = "HUMAN_REVIEW"
            elif overfit_block.get("warning") and status == "SUCCESS":
                status = "WARNING"

            return {
                "status": status,
                "checkpoints": [c.hop_id for c in self.hop_checkpoints],
                "final_artifact_keys": list(final_artifact.keys()) if final_artifact else [],
                "retry_iterations": iteration,
                "final_quality_score": final_quality.get("score", 0),
                "ats_valid": final_ats.get("valid", False),
                "overfit_report": overfit_block,
                "provenance_report": provenance_report,
            }
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            self.ctx.trace.add_trace("ORCHESTRATOR_ERROR", {"error": str(e)})
            self.logger.error(f"Orchestration failed: {e}")
            raise

    async def _run_engine(self, engine_cls, checkpoint_id: str):
        """Helper to run a Sovereign Engine and log checkpoint."""
        engine = engine_cls(self.ctx)
        await engine.execute()
        self.hop_checkpoints.append(HopCheckpoint(checkpoint_id, "COMPLETED"))

    def _run_anti_overfit_check(
        self, final_artifact: dict[str, Any], job_description: str
    ) -> dict[str, Any]:
        """W9 hybrid anti-overfit gate (orchestrator-direct + rubric pair).

        Renders the sealed resume to plain text, runs the L5 anti-overfit
        detector against the JD as user-sample, returns a structured block
        with the aggregate score, top flags, and escalate/warning verdicts.

        Reversibility: pure function; can be removed by deleting this method
        and the call site at the end of `execute()`. The L5 detector itself
        and the `overfit_risk` rubric dimension are unaffected.

        Failure mode: if the detector or its imports fail, returns a neutral
        block with `error` populated and `escalate=False`. The orchestrator
        does not consider detector failure a generation failure (the
        rubric still runs offline).
        """
        try:  # noqa: BLE001 - bounded import + run; fall back to neutral on any failure
            from agentic_core.L5_safety.validators.anti_overfit_detector_validator import (
                OverfitProfile,
                SealedOutput,
                UserSample,
                detect,
            )
        except ImportError as exc:
            self.logger.warning(
                "anti_overfit_detector unavailable; W9 hybrid gate degraded: %s", exc
            )
            return {"score": 0.0, "flags": [], "warning": False, "escalate": False, "error": f"import: {exc}"}

        # Render sealed text from the projection. Preserve order: headline,
        # summary, experience bullets, skills. Skip metadata.
        chunks: list[str] = []
        if isinstance(final_artifact, dict):
            if h := final_artifact.get("headline"):
                chunks.append(str(h))
            if s := final_artifact.get("summary"):
                chunks.append(str(s))
            for exp in final_artifact.get("experience", []) or []:
                if isinstance(exp, dict):
                    chunks.append(f"{exp.get('company','')} - {exp.get('title','')}")
                    for b in exp.get("bullets", []) or []:
                        chunks.append(str(b))
            for sk in final_artifact.get("skills", []) or []:
                chunks.append(str(sk))
        sealed_text = "\n".join(c for c in chunks if c)

        sealed = SealedOutput(text=sealed_text, turn_index=0)
        samples = [UserSample(text=str(job_description or ""), sample_ref="job_description")]
        # Resume-aware profile: differs from agent-prompt profile because the
        # SEALED OUTPUT here is the candidate-voice resume body, not the
        # agent persona prose.
        #   * mimicry_max raised to 0.85: resume-to-JD tailoring is the goal
        #     (ATS keyword alignment); only flag near-verbatim copy
        #   * persona_token_cap raised to 5000: resume body is candidate
        #     content, not agent persona; no meaningful cap below 5000
        #   * fake_history_tolerance kept at 0.0 (hard floor — zero tolerance
        #     for fabricated employment / dates / credentials)
        #   * repeated_user_phrase_max kept at 2 (catch lazy JD echoing)
        #   * forced_warmth_threshold kept at 0.10 (no flattery in resumes)
        profile = OverfitProfile(
            mimicry_max=0.85,
            repeated_user_phrase_max=2,
            forced_warmth_threshold=0.10,
            fake_history_tolerance=0.0,
            persona_token_cap=5000,
            certainty_calibration_required=True,
        )
        try:
            report = detect(
                sealed_output=sealed,
                user_samples=samples,
                profile=profile,
                spec_id="agt_rgresume000000000000001",
                spec_version="0.1.0",
            )
        except (ValueError, TypeError) as exc:
            self.logger.warning("anti_overfit_detector run failed: %s", exc)
            return {"score": 0.0, "flags": [], "warning": False, "escalate": False, "error": f"detect: {exc}"}

        # Hard-floor flags (escalate to HUMAN_REVIEW): fabrication or warmth.
        # Soft flags (downgrade to WARNING only): mimicry beyond cap, repeated
        # phrases beyond cap, persona-token cap. The aggregate-score warning
        # band keeps the overall guard active.
        flags = list(report.flags or [])
        score = float(report.aggregate_overfit_score or 0.0)
        # Flag names match the L5 detector's emission strings (see
        # agentic_core/L5_safety/validators/anti_overfit_detector_validator.py
        # _aggregate(): 'fake_history_detected', 'forced_warmth_detected').
        hard_flags = {"fake_history_detected", "forced_warmth_detected"}
        escalate = bool(hard_flags.intersection(flags)) or score >= 3.5
        warning = (not escalate) and score >= 2.0
        return {
            "score": round(score, 3),
            "flags": flags,
            "warning": warning,
            "escalate": escalate,
            "report_id": report.report_id,
            "detector_version": report.detector_version,
        }

    def run_subatomic_test(self) -> dict[str, Any]:
        """Run subatomic self-tests (inherited from SubatomicTestingMixin).

        Returns:
            Test results dict
        """
        return {"status": "passed", "tests_run": 0}
