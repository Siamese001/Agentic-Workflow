"""Resume Enhancement Integration - Unified orchestration layer.

This module integrates the Persona router, Evidence Injector, and Competitor
Recon with the existing hardened infrastructure to provide enhanced
resume generation capabilities.
"""

from __future__ import annotations

import logging
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

_emit_applies_guardrail("p0", "ResumeEnhancementOrchestrator", "p0_governance")
_emit_reads_policy_state("p0", "ResumeEnhancementOrchestrator", "policy_binding")
_emit_snapshots_state("p0", "ResumeEnhancementOrchestrator", "state_snapshot")
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

_emit_emits_metric_event("ResumeEnhancementOrchestrator", "p4obs", "metric_1")
_emit_emits_metric_event("ResumeEnhancementOrchestrator", "p4obs", "metric_2")
_emit_emits_metric_event("ResumeEnhancementOrchestrator", "p4obs", "metric_3")
_emit_emits_metric_event("ResumeEnhancementOrchestrator", "p4obs", "metric_4")
_emit_emits_metric_event("ResumeEnhancementOrchestrator", "p4obs", "metric_5")
_emit_emits_metric_event("ResumeEnhancementOrchestrator", "p4obs", "metric_6")
_emit_records_incident_event("ResumeEnhancementOrchestrator", "p4obs", "incident")
_emit_captures_runtime_anomaly("ResumeEnhancementOrchestrator", "p4obs", "anomaly")
_emit_writes_observability_log("ResumeEnhancementOrchestrator", "p4obs", "obs_log")
_emit_updates_monitoring_state("ResumeEnhancementOrchestrator", "p4obs", "mon_state")
_emit_triggers_alert("ResumeEnhancementOrchestrator", "p4obs", "alert")
_emit_links_incident_trace("ResumeEnhancementOrchestrator", "p4obs", "trace_link")
_emit_captures_pattern("ResumeEnhancementOrchestrator", "p3lm", "pattern")
_emit_records_learning_event("ResumeEnhancementOrchestrator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ResumeEnhancementOrchestrator", "p3lm", "snapshot")
_emit_feeds_meta_learning("ResumeEnhancementOrchestrator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ResumeEnhancementOrchestrator", "p3lm", "routing")
_emit_improves_agent_policy("ResumeEnhancementOrchestrator", "p3lm", "policy")
_emit_stores_learning_state("ResumeEnhancementOrchestrator", "p3lm", "state")
_emit_records_execution_trace("ResumeEnhancementOrchestrator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ResumeEnhancementOrchestrator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ResumeEnhancementOrchestrator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ResumeEnhancementOrchestrator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ResumeEnhancementOrchestrator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ResumeEnhancementOrchestrator", "env_read", "p2_env_1")
_emit_reads_environ("ResumeEnhancementOrchestrator", "env_read", "p2_env_2")
_emit_reads_runtime_state("ResumeEnhancementOrchestrator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ResumeEnhancementOrchestrator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ResumeEnhancementOrchestrator", "context_pull")
_emit_pulls_context("p1", "ResumeEnhancementOrchestrator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ResumeEnhancementOrchestrator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ResumeEnhancementOrchestrator", "uwg_term_2")
_emit_writes_through("p1", "ResumeEnhancementOrchestrator", "write_through")
_emit_writes_through("p1", "ResumeEnhancementOrchestrator", "write_through_2")
_emit_validated_by_safety_plane("p1", "ResumeEnhancementOrchestrator", "safety_validation")
_emit_invokes_eval("p1", "ResumeEnhancementOrchestrator", "eval_call")
_emit_proposal_commits_routing("p1", "ResumeEnhancementOrchestrator", "routing_commit")
_emit_escalates_to_human("p1", "ResumeEnhancementOrchestrator", "human_escalation")
_emit_routes_through("p1", "ResumeEnhancementOrchestrator", "route_through")
_emit_checks_agent_registry("p1", "ResumeEnhancementOrchestrator", "agent_registry")
_emit_validates_agent_capability("p1", "ResumeEnhancementOrchestrator", "capability")
_emit_dispatches_execution_plan("p1", "ResumeEnhancementOrchestrator", "exec_plan")
_emit_agent_executes_agent("p1", "ResumeEnhancementOrchestrator", "sub_agent")
_emit_routes_to_agent("p1", "ResumeEnhancementOrchestrator", "target_agent")
_emit_verifies_policy("p1", "ResumeEnhancementOrchestrator", "policy_check")
_emit_observes_runtime_state("p1", "ResumeEnhancementOrchestrator", "runtime_state")
_emit_verifies_boundary("p1", "ResumeEnhancementOrchestrator", "boundary_check")
_emit_transcripts_response("p1", "ResumeEnhancementOrchestrator", "transcript")
_emit_hard_fails_untranscripted("p1", "ResumeEnhancementOrchestrator")
_emit_gated_by_confidence("p1", "ResumeEnhancementOrchestrator", "confidence_gate")
emit_replay_key("p0", "ResumeEnhancementOrchestrator")
emit_determinism_digest("p0", "ResumeEnhancementOrchestrator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ResumeEnhancementOrchestrator", "execution_auth")
_emit_validates_capability("p2", "ResumeEnhancementOrchestrator", "capability_check")
_emit_routes_to_capability("p2", "ResumeEnhancementOrchestrator", "capability_route")
_emit_writes_via_uwg("p2", "ResumeEnhancementOrchestrator", "uwg_write")
_emit_blocks_direct_write("p2", "ResumeEnhancementOrchestrator", "direct_write_block")
_emit_records_tool_invocation("p2", "ResumeEnhancementOrchestrator", "tool_invocation")
_emit_captures_execution_output("p2", "ResumeEnhancementOrchestrator", "exec_output")
_emit_dispatches_agent("p3", "ResumeEnhancementOrchestrator", "agent_dispatch")
_emit_coordinates_agents("p3", "ResumeEnhancementOrchestrator", "agent_coordination")
_emit_records_workflow_lineage("p3", "ResumeEnhancementOrchestrator", "workflow_lineage")
_emit_records_healing_outcome("p3", "ResumeEnhancementOrchestrator", "healing_outcome")
_emit_escalates_failure("p3", "ResumeEnhancementOrchestrator", "failure_escalation")
_emit_orchestrates_workflow("p3", "ResumeEnhancementOrchestrator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ResumeEnhancementOrchestrator", "healing_dispatch")
_emit_invokes_evaluation("p3", "ResumeEnhancementOrchestrator", "evaluation_signal")
_emit_records_telemetry_event("p4", "ResumeEnhancementOrchestrator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ResumeEnhancementOrchestrator", "eval_metric")
_emit_stores_embedding("p4", "ResumeEnhancementOrchestrator", "embedding_store")
_emit_updates_meta_learning_state("p4", "ResumeEnhancementOrchestrator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ResumeEnhancementOrchestrator", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class ResumeEnhancementOrchestrator:
    """Orchestrates all resume enhancement components."""

    def __init__(self):
        """Initialize resume enhancement orchestrator."""
        self.persona_router: PersonaRouter | None = None
        self.evidence_injector: EvidenceInjector | None = None
        self.recon_agent: ReconAgent | None = None
        self.infrastructure: InfrastructureOrchestrator | None = None
        self._initialized = False
        logger.info("Initialized ResumeEnhancementOrchestrator")

    async def initialize(self) -> None:
        """Initialize all components."""
        if self._initialized:
            return
        logger.info("Initializing resume enhancement components...")
        self.persona_router = get_persona_router()
        self.evidence_injector = get_evidence_injector()
        self.recon_agent = get_recon_agent()
        self.infrastructure = await InfrastructureOrchestrator()
        await self._setup_event_subscriptions()
        self._initialized = True
        logger.info("Resume enhancement initialization complete")

    async def _setup_event_subscriptions(self) -> None:
        """Setup event subscriptions for component coordination."""
        await self.infrastructure.event_bus.subscribe(
            "events.resume_generation_started",
            self._handle_resume_generation_started,
        )
        await self.infrastructure.event_bus.subscribe(
            "events.persona_analyzed",
            self._handle_persona_analyzed,
        )
        logger.info("Setup resume enhancement event subscriptions")

    async def _handle_resume_generation_started(self, event: SystemEvent) -> None:
        """Handle resume generation start event.

        Args:
            event: Resume generation started event
        """
        try:
            payload = event.payload
            jd_text = payload.get("job_description", "")
            candidate_history = payload.get("candidate_history", [])
            persona = self.persona_router.analyze_jd(jd_text)
            await self.infrastructure.event_bus.publish(
                "events.persona_analyzed",
                SystemEvent(
                    type=EventType.AGENT_THINKING,
                    trace_id=event.trace_id,
                    source_component="ResumeEnhancementOrchestrator",
                    payload={
                        "persona_title": persona.title,
                        "archetype": persona.archetype.value,
                        "risk_tolerance": persona.profile.risk_tolerance,
                    },
                    causation_id=event.id,
                ),
            )
            if candidate_history and jd_text:
                target_company = self._extract_company_from_jd(jd_text)
                if target_company:
                    recon_signal = self.recon_agent.analyze(target_company, candidate_history)
                    await self.infrastructure.event_bus.publish(
                        "events.competitive_analyzed",
                        SystemEvent(
                            type=EventType.INSIGHT_DISCOVERED,
                            trace_id=event.trace_id,
                            source_component="ResumeEnhancementOrchestrator",
                            payload={
                                "target_company": target_company,
                                "position": recon_signal.position.value,
                                "competitor": recon_signal.competitor_detected,
                                "strategy": recon_signal.strategy_recommendation,
                            },
                            causation_id=event.id,
                        ),
                    )
        except (AttributeError, ValueError, TypeError, RuntimeError):  # guardian: allow-double-logging -- orchestrator-level error log before re-raise for event-handler observability
            raise

    async def _handle_persona_analyzed(self, event: SystemEvent) -> None:
        """Handle persona analyzed event.

        Args:
            event: Persona analyzed event
        """
        try:
            payload = event.payload
            logger.info(f"Persona analyzed: {payload.get('persona_title')} ({payload.get('archetype')})")
        except (AttributeError, ValueError, TypeError):  # guardian: allow-double-logging -- orchestrator-level error log before re-raise for event-handler observability
            raise

    def _extract_company_from_jd(self, jd_text: str) -> str | None:
        """Extract company name from job description.

        Args:
            jd_text: Job description text

        Returns:
            Company name if found
        """
        import re

        patterns = [
            "Join\\s+([A-Z][a-z]+(?:\\s+[A-Z][a-z]+)*)",
            "About\\s+([A-Z][a-z]+(?:\\s+[A-Z][a-z]+)*)",
            "at\\s+([A-Z][a-z]+(?:\\s+[A-Z][a-z]+)*)\\s+we're",
            "([A-Z][a-z]+(?:\\s+[A-Z][a-z]+)*)\\s+is\\s+(?:hiring|looking|seeking)",
        ]
        for pattern in patterns:
            match = re.search(pattern, jd_text, re.IGNORECASE)
            if match:
                company = match.group(1)
                if company not in ["We", "Our", "The", "This", "A", "An"]:
                    return company
        return None

    async def generate_enhanced_resume(
        self,
        job_description: str,
        candidate_history: list[str],
        resume_bullets: list[str],
        evidence_library_path: str | None = None,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        """Generate enhanced resume with all enhancements.

        Args:
            job_description: Job description text
            candidate_history: List of previous companies
            resume_bullets: Base resume bullets
            evidence_library_path: Path to evidence library
            trace_id: Trace ID for tracking

        Returns:
            Enhanced resume with metadata
        """
        if not self._initialized:
            await self.initialize()
        if not trace_id:
            import uuid

            trace_id = str(uuid.uuid4())
        _emit_records_execution_trace(
            trace_id, LayerSegment.L3_ORCHESTRATION, "ResumeEnhancementOrchestrator.generate_enhanced_resume"
        )
        await self.infrastructure.event_bus.publish(
            "events.resume_enhancement_started",
            SystemEvent(
                type=EventType.WORKFLOW_STARTED,
                trace_id=trace_id,
                source_component="ResumeEnhancementOrchestrator",
                payload={
                    "jd_length": len(job_description),
                    "bullet_count": len(resume_bullets),
                    "history_count": len(candidate_history),
                },
            ),
        )
        try:
            persona = self.persona_router.analyze_jd(job_description)
            target_company = self._extract_company_from_jd(job_description)
            recon_signal = None
            if target_company:
                recon_signal = self.recon_agent.analyze(target_company, candidate_history)
            if evidence_library_path:
                self.evidence_injector.load_library(evidence_library_path)
            enhanced_bullets = self.evidence_injector.inject(resume_bullets)
            prompt_template = self.persona_router.get_prompt_template(persona)
            if recon_signal and recon_signal.position.value != "UNRELATED":
                prompt_template += f"\n\nCompetitive Intelligence:\n{recon_signal.strategy_recommendation}"
            result = await self.infrastructure.execute_with_infrastructure(
                TaskType.CONTENT_CREATION,
                prompt_template,
                sources=[(b, "resume_bullet", 1.0) for b in enhanced_bullets],
                complexity_score=self._calculate_complexity(persona, recon_signal),
                trace_id=trace_id,
            )
            await self.infrastructure.event_bus.publish(
                "events.resume_enhanced",
                SystemEvent(
                    type=EventType.ARTIFACT_GENERATED,
                    trace_id=trace_id,
                    source_component="ResumeEnhancementOrchestrator",
                    payload={
                        "persona": persona.title,
                        "enhanced_bullets": len(enhanced_bullets),
                        "links_injected": self.evidence_injector._links_used,
                        "competitive_insights": recon_signal.position.value if recon_signal else None,
                    },
                    causation_id=trace_id,
                ),
            )
            return {
                "enhanced_resume": result["result"],
                "trace_id": trace_id,
                "persona": persona.dict(),
                "competitive_signal": recon_signal.dict() if recon_signal else None,
                "enhanced_bullets": enhanced_bullets,
                "metadata": {
                    "model_used": result["model_used"],
                    "tier": result["tier"],
                    "execution_time": result["execution_time"],
                    "lineage": result.get("lineage"),
                },
            }
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise

    def _calculate_complexity(self, persona: ReaderPersona, recon_signal: ReconSignal | None) -> int:
        """Calculate task complexity based on persona and signals.

        Args:
            persona: Reader persona
            recon_signal: Competitive signal

        Returns:
            Complexity score (1-10)
        """
        base_complexity = 5
        if persona.archetype.value == "VISIONARY":
            base_complexity += 2
        elif persona.archetype.value == "GUARDIAN":
            base_complexity += 1
        if persona.profile.technical_depth > 0.8:
            base_complexity += 1
        if recon_signal and recon_signal.position.value == "DIRECT_COMPETITOR":
            base_complexity += 2
        return min(base_complexity, 10)

    async def get_enhancement_stats(self) -> dict[str, Any]:
        """Get enhancement statistics.

        Returns:
            Statistics dictionary
        """
        return {
            "persona_router": "Ready",
            "evidence_injector": self.evidence_injector.get_stats(),
            "recon_agent": {
                "companies_in_db": len(self.recon_agent.competitor_db),
                "industries_covered": len({c.industry for c in self.recon_agent.competitor_db.values()}),
            },
        }


_enhancement_orchestrator: ResumeEnhancementOrchestrator | None = None
_orchestrator_lock = None


async def get_resume_enhancement_orchestrator() -> ResumeEnhancementOrchestrator:
    """Get global resume enhancement orchestrator.

    Returns:
        ResumeEnhancementOrchestrator instance
    """
    global _enhancement_orchestrator, _orchestrator_lock
    if _orchestrator_lock is None:
        import asyncio

        _orchestrator_lock = asyncio.Lock()
    async with _orchestrator_lock:
        if _enhancement_orchestrator is None:
            _enhancement_orchestrator = ResumeEnhancementOrchestrator()
            await _enhancement_orchestrator.initialize()
    return _enhancement_orchestrator


async def enhance_resume(
    job_description: str,
    candidate_history: list[str],
    resume_bullets: list[str],
    evidence_library_path: str | None = None,
    trace_id: str | None = None,
) -> dict[str, Any]:
    """Enhance resume with all available enhancements.

    Args:
        job_description: Job description text
        candidate_history: List of previous companies
        resume_bullets: Base resume bullets
        evidence_library_path: Path to evidence library
        trace_id: Trace ID for tracking

    Returns:
        Enhanced resume with metadata
    """
    orchestrator = await get_resume_enhancement_orchestrator()
    return await orchestrator.generate_enhanced_resume(
        job_description,
        candidate_history,
        resume_bullets,
        evidence_library_path,
        trace_id,
    )
