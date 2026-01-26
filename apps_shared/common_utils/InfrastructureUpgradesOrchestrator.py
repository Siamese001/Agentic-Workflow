"""Infrastructure Upgrades Integration - Unified orchestration layer.

This module integrates the Fact Ledger, Global cache, and Brand Voice Enforcer
with the existing hardened infrastructure to provide enhanced consistency,
performance, and brand compliance across all engines.
"""

import logging


logger = logging.getLogger(__name__)


class InfrastructureUpgradesOrchestrator:
    """Orchestrates all infrastructure upgrade components."""

    def __init__(self):
        """Initialize infrastructure upgrades orchestrator."""
        self.fact_ledger: FactLedger | None = None
        self.global_cache: GlobalCache | None = None
        self.tone_enforcer: ToneEnforcer | None = None
        self.infrastructure: InfrastructureOrchestrator | None = None

        self._initialized = False

        logger.info("Initialized InfrastructureUpgradesOrchestrator")

    async def initialize(self) -> None:
        """Initialize all components."""
        if self._initialized:
            return

        logger.info("Initializing infrastructure upgrade components...")

        # Get component instances
        self.fact_ledger = get_fact_ledger()
        self.global_cache = get_global_cache()
        self.tone_enforcer = get_tone_enforcer()

        # Get infrastructure orchestrator
        self.infrastructure = await InfrastructureOrchestrator()

        # Setup event subscriptions
        await self._setup_event_subscriptions()

        self._initialized = True
        logger.info("Infrastructure upgrades initialization complete")

    async def _setup_event_subscriptions(self) -> None:
        """Setup event subscriptions for component coordination."""
        # Subscribe to content generation events for fact checking
        await self.infrastructure.event_bus.subscribe(
            "events.content_generated", self._handle_content_generated
        )

        # Subscribe to cache events
        await self.infrastructure.event_bus.subscribe("events.cache_miss", self._handle_cache_miss)

        # Subscribe to tone violations
        await self.infrastructure.event_bus.subscribe(
            "events.tone_violation", self._handle_tone_violation
        )

        logger.info("Setup infrastructure upgrades event subscriptions")

    async def _handle_content_generated(self, event: SystemEvent) -> None:
        """Handle content generation event for fact checking.

        Args:
            event: Content generated event
        """
        try:
            # Extract content
            payload = event.payload
            content = payload.get("content", "")

            if content:
                # Verify claims in content
                violations = await self._verify_content_facts(content, event.trace_id)

                if violations:
                    # Publish fact violations event
                    await self.infrastructure.event_bus.publish(
                        "events.fact_violations",
                        SystemEvent(
                            type=EventType.ERROR_OCCURRED,
                            trace_id=event.trace_id,
                            source_component="InfrastructureUpgradesOrchestrator",
                            payload={
                                "violations": [v.dict() for v in violations],
                                "content_length": len(content),
                            },
                            causation_id=event.id,
                        ),
                    )

        except Exception as e:
            logger.error(f"Failed to handle content generated: {e}")

    async def _handle_cache_miss(self, event: SystemEvent) -> None:
        """Handle cache miss event.

        Args:
            event: cache miss event
        """
        try:
            # Log cache miss for analytics
            payload = event.payload
            query = payload.get("query", "")
            cache_type = payload.get("cache_type", "unknown")

            logger.debug(f"cache miss for {cache_type}: {query[:50]}...")

            # Could trigger cache warming logic here

        except Exception as e:
            logger.error(f"Failed to handle cache miss: {e}")

    async def _handle_tone_violation(self, event: SystemEvent) -> None:
        """Handle tone violation event.

        Args:
            event: Tone violation event
        """
        try:
            # Extract violations
            payload = event.payload
            violations = payload.get("violations", [])

            # Log violations for analytics
            violation_types = [v.get("type", "unknown") for v in violations]
            logger.info(f"Tone violations detected: {violation_types}")

            # Could trigger adaptive learning here

        except Exception as e:
            logger.error(f"Failed to handle tone violation: {e}")

    async def _verify_content_facts(self, content: str, trace_id: str) -> list[VerificationResult]:
        """Verify facts in generated content.

        Args:
            content: Generated content
            trace_id: Trace ID for tracking

        Returns:
            List of verification results
        """
        # Split content into sentences/claims
        import re

        sentences = re.split(r"[.!?]+", content)
        sentences = [s.strip() for s in sentences if s.strip()]

        violations = []

        for sentence in sentences:
            # Verify each claim
            result = self.fact_ledger.verify_claim(sentence)

            if result.status == "CONFLICT":
                violations.append(result)

                # Publish conflict event
                await self.infrastructure.event_bus.publish(
                    "events.fact_conflict",
                    SystemEvent(
                        type=EventType.ERROR_OCCURRED,
                        trace_id=trace_id,
                        source_component="InfrastructureUpgradesOrchestrator",
                        payload={
                            "claim": sentence,
                            "correction": result.correction_suggestion,
                            "verified_value": result.verified_fact.value
                            if result.verified_fact
                            else None,
                        },
                    ),
                )

        return violations

    async def generate_with_upgrades(
        self,
        task_type: TaskType,
        prompt: str,
        tone_voice: ToneVoice | None = None,
        verify_facts: bool = True,
        enforce_tone: bool = True,
        use_cache: bool = True,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        """Generate content with all infrastructure upgrades.

        Args:
            task_type: Type of task
            prompt: Task prompt
            tone_voice: Voice type to enforce
            verify_facts: Whether to verify facts
            enforce_tone: Whether to enforce tone
            use_cache: Whether to use cache
            trace_id: Trace ID for tracking

        Returns:
            Generated content with metadata
        """
        if not self._initialized:
            await self.initialize()

        # Generate trace ID if not provided
        if not trace_id:
            import uuid

            trace_id = str(uuid.uuid4())

        # Check cache first
        if use_cache:
            cache_key = f"{task_type.value}:{prompt}"
            cached_result = self.global_cache.get(cache_key)

            if cached_result:
                await self.infrastructure.event_bus.publish(
                    "events.cache_hit",
                    SystemEvent(
                        type=EventType.AGENT_THINKING,
                        trace_id=trace_id,
                        source_component="InfrastructureUpgradesOrchestrator",
                        payload={"cache_key": cache_key},
                    ),
                )

                return cached_result

        # Start generation
        await self.infrastructure.event_bus.publish(
            "events.upgraded_generation_started",
            SystemEvent(
                type=EventType.WORKFLOW_STARTED,
                trace_id=trace_id,
                source_component="InfrastructureUpgradesOrchestrator",
                payload={
                    "task_type": task_type.value,
                    "verify_facts": verify_facts,
                    "enforce_tone": enforce_tone,
                },
            ),
        )

        try:
            # Generate base content
            result = await self.infrastructure.execute_with_infrastructure(
                task_type, prompt, complexity_score=5, trace_id=trace_id
            )

            content = result["result"]

            # Apply tone enforcement if requested
            tone_violations = []
            if enforce_tone and tone_voice:
                settings = self.tone_enforcer.get_profile(tone_voice)
                tone_violations = self.tone_enforcer.audit_content(content, settings)

                if tone_violations:
                    await self.infrastructure.event_bus.publish(
                        "events.tone_violation",
                        SystemEvent(
                            type=EventType.ERROR_OCCURRED,
                            trace_id=trace_id,
                            source_component="InfrastructureUpgradesOrchestrator",
                            payload={
                                "violations": [v.dict() for v in tone_violations],
                                "tone_voice": tone_voice.value,
                            },
                        ),
                    )

            # Verify facts if requested
            fact_violations = []
            if verify_facts:
                fact_violations = await self._verify_content_facts(content, trace_id)

            # cache the result
            if use_cache:
                cache_key = f"{task_type.value}:{prompt}"
                self.global_cache.put(
                    cache_key,
                    result,
                    text_for_embedding=prompt,
                    source_engine="InfrastructureUpgrades",
                )

            # Publish completion
            await self.infrastructure.event_bus.publish(
                "events.upgraded_generation_complete",
                SystemEvent(
                    type=EventType.ARTIFACT_GENERATED,
                    trace_id=trace_id,
                    source_component="InfrastructureUpgradesOrchestrator",
                    payload={
                        "content_length": len(content),
                        "tone_violations": len(tone_violations),
                        "fact_violations": len(fact_violations),
                        "cached": use_cache,
                    },
                ),
            )

            return {
                "content": content,
                "trace_id": trace_id,
                "metadata": {
                    "model_used": result["model_used"],
                    "tier": result["tier"],
                    "execution_time": result["execution_time"],
                    "tone_violations": len(tone_violations),
                    "fact_violations": len(fact_violations),
                    "cached": use_cache,
                },
                "violations": {
                    "tone": [v.dict() for v in tone_violations],
                    "facts": [v.dict() for v in fact_violations],
                },
            }

        except Exception as e:
            # Publish error
            await self.infrastructure.event_bus.publish(
                "events.upgraded_generation_failed",
                SystemEvent(
                    type=EventType.ERROR_OCCURRED,
                    trace_id=trace_id,
                    source_component="InfrastructureUpgradesOrchestrator",
                    payload={"error": str(e)},
                    causation_id=trace_id,
                ),
            )

            raise

    async def load_profile_facts(self, profile_data: dict[str, Any]) -> None:
        """Load profile facts into the ledger.

        Args:
            profile_data: Profile data dictionary
        """
        if not self._initialized:
            await self.initialize()

        self.fact_ledger.load_facts(profile_data)
        logger.info(f"Loaded profile facts: {self.fact_ledger.get_stats()['facts_loaded']} facts")

    def get_upgrades_stats(self) -> dict[str, Any]:
        """Get statistics for all upgrade components.

        Returns:
            Statistics dictionary
        """
        return {
            "fact_ledger": self.fact_ledger.get_stats() if self.fact_ledger else {},
            "global_cache": self.global_cache.get_stats() if self.global_cache else {},
            "tone_enforcer": {
                "profiles_loaded": len(self.tone_enforcer.profiles) if self.tone_enforcer else 0
            },
        }


# Global orchestrator
_upgrades_orchestrator: InfrastructureUpgradesOrchestrator | None = None
_orchestrator_lock = None


async def get_infrastructure_upgrades_orchestrator() -> InfrastructureUpgradesOrchestrator:
    """Get global infrastructure upgrades orchestrator.

    Returns:
        InfrastructureUpgradesOrchestrator instance
    """
    global _upgrades_orchestrator, _orchestrator_lock

    if _orchestrator_lock is None:
        import asyncio

        _orchestrator_lock = asyncio.Lock()

    async with _orchestrator_lock:
        if _upgrades_orchestrator is None:
            _upgrades_orchestrator = InfrastructureUpgradesOrchestrator()
            await _upgrades_orchestrator.initialize()

    return _upgrades_orchestrator


# Convenience functions
async def generate_with_consistency(
    task_type: TaskType,
    prompt: str,
    tone_voice: ToneVoice | None = None,
    verify_facts: bool = True,
    enforce_tone: bool = True,
    trace_id: str | None = None,
) -> dict[str, Any]:
    """Generate content with consistency checks.

    Args:
        task_type: Type of task
        prompt: Task prompt
        tone_voice: Voice type to enforce
        verify_facts: Whether to verify facts
        enforce_tone: Whether to enforce tone
        trace_id: Trace ID for tracking

    Returns:
        Generated content with metadata
    """
    orchestrator = await get_infrastructure_upgrades_orchestrator()
    return await orchestrator.generate_with_upgrades(
        task_type, prompt, tone_voice, verify_facts, enforce_tone, True, trace_id
    )


async def verify_claims(content: str) -> list[VerificationResult]:
    """Verify claims in content.

    Args:
        content: Content to verify

    Returns:
        List of verification results
    """
    ledger = get_fact_ledger()

    # Split into claims
    import re

    sentences = re.split(r"[.!?]+", content)
    sentences = [s.strip() for s in sentences if s.strip()]

    results = []
    for sentence in sentences:
        result = ledger.verify_claim(sentence)
        if result.status != "UNVERIFIED":
            results.append(result)

    return results


def audit_tone(text: str, voice: ToneVoice) -> list[ToneViolation]:
    """Audit text for tone compliance.

    Args:
        text: Text to audit
        voice: Voice type to enforce

    Returns:
        List of tone violations
    """
    enforcer = get_tone_enforcer()
    settings = enforcer.get_profile(voice)
    return enforcer.audit_content(text, settings)
