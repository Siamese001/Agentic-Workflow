"""Resume Enhancement Integration - Unified orchestration layer.

This module integrates the Persona router, Evidence Injector, and Competitor
Recon with the existing hardened infrastructure to provide enhanced
resume generation capabilities.
"""

import logging

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

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
            "events.resume_generation_started", self._handle_resume_generation_started
        )
        await self.infrastructure.event_bus.subscribe(
            "events.persona_analyzed", self._handle_persona_analyzed
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
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to handle resume generation started: {e}")

    async def _handle_persona_analyzed(self, event: SystemEvent) -> None:
        """Handle persona analyzed event.

        Args:
            event: Persona analyzed event
        """
        try:
            payload = event.payload
            logger.info(f"Persona analyzed: {payload.get('persona_title')} ({payload.get('archetype')})")
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to handle persona analyzed: {e}")

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
        _emit_records_execution_trace(trace_id, LayerSegment.L3_ORCHESTRATION, "ResumeEnhancementOrchestrator.generate_enhanced_resume")
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
        except Exception as e:
            raise
            await self.infrastructure.event_bus.publish(
                "events.resume_enhancement_failed",
                SystemEvent(
                    type=EventType.ERROR_OCCURRED,
                    trace_id=trace_id,
                    source_component="ResumeEnhancementOrchestrator",
                    payload={"error": str(e)},
                    causation_id=trace_id,
                ),
            )
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
        job_description, candidate_history, resume_bullets, evidence_library_path, trace_id
    )
