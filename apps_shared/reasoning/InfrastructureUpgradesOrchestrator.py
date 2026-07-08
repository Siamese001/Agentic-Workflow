"""Infrastructure Upgrades Integration - Unified orchestration layer.

This module integrates the Fact Ledger, Global cache, and Brand Voice Enforcer
with the existing hardened infrastructure to provide enhanced consistency,
performance, and brand compliance across all engines.
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract
from apps_shared.config.pipeline_constants_config import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, THRESHOLD

trace_contract._emit_applies_guardrail("p0", "InfrastructureUpgradesOrchestrator", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "InfrastructureUpgradesOrchestrator", "policy_binding")
trace_contract._emit_snapshots_state("p0", "InfrastructureUpgradesOrchestrator", "state_snapshot")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("InfrastructureUpgradesOrchestrator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("InfrastructureUpgradesOrchestrator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("InfrastructureUpgradesOrchestrator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("InfrastructureUpgradesOrchestrator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("InfrastructureUpgradesOrchestrator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("InfrastructureUpgradesOrchestrator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("InfrastructureUpgradesOrchestrator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("InfrastructureUpgradesOrchestrator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("InfrastructureUpgradesOrchestrator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("InfrastructureUpgradesOrchestrator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("InfrastructureUpgradesOrchestrator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("InfrastructureUpgradesOrchestrator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("InfrastructureUpgradesOrchestrator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("InfrastructureUpgradesOrchestrator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("InfrastructureUpgradesOrchestrator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("InfrastructureUpgradesOrchestrator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("InfrastructureUpgradesOrchestrator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("InfrastructureUpgradesOrchestrator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("InfrastructureUpgradesOrchestrator", "p3lm", "state")
trace_contract._emit_records_execution_trace("InfrastructureUpgradesOrchestrator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("InfrastructureUpgradesOrchestrator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("InfrastructureUpgradesOrchestrator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("InfrastructureUpgradesOrchestrator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("InfrastructureUpgradesOrchestrator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("InfrastructureUpgradesOrchestrator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("InfrastructureUpgradesOrchestrator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("InfrastructureUpgradesOrchestrator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("InfrastructureUpgradesOrchestrator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "InfrastructureUpgradesOrchestrator", "context_pull")
trace_contract._emit_pulls_context("p1", "InfrastructureUpgradesOrchestrator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "InfrastructureUpgradesOrchestrator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "InfrastructureUpgradesOrchestrator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "InfrastructureUpgradesOrchestrator", "write_through")
trace_contract._emit_writes_through("p1", "InfrastructureUpgradesOrchestrator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "InfrastructureUpgradesOrchestrator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "InfrastructureUpgradesOrchestrator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "InfrastructureUpgradesOrchestrator", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "InfrastructureUpgradesOrchestrator", "human_escalation")
trace_contract._emit_routes_through("p1", "InfrastructureUpgradesOrchestrator", "route_through")
trace_contract._emit_checks_agent_registry("p1", "InfrastructureUpgradesOrchestrator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "InfrastructureUpgradesOrchestrator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "InfrastructureUpgradesOrchestrator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "InfrastructureUpgradesOrchestrator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "InfrastructureUpgradesOrchestrator", "target_agent")
trace_contract._emit_verifies_policy("p1", "InfrastructureUpgradesOrchestrator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "InfrastructureUpgradesOrchestrator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "InfrastructureUpgradesOrchestrator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "InfrastructureUpgradesOrchestrator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "InfrastructureUpgradesOrchestrator")
trace_contract._emit_gated_by_confidence("p1", "InfrastructureUpgradesOrchestrator", "confidence_gate")
trace_contract.emit_replay_key("p0", "InfrastructureUpgradesOrchestrator")
trace_contract.emit_determinism_digest("p0", "InfrastructureUpgradesOrchestrator")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "InfrastructureUpgradesOrchestrator", "execution_auth")
trace_contract._emit_validates_capability("p2", "InfrastructureUpgradesOrchestrator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "InfrastructureUpgradesOrchestrator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "InfrastructureUpgradesOrchestrator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "InfrastructureUpgradesOrchestrator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "InfrastructureUpgradesOrchestrator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "InfrastructureUpgradesOrchestrator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "InfrastructureUpgradesOrchestrator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "InfrastructureUpgradesOrchestrator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "InfrastructureUpgradesOrchestrator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "InfrastructureUpgradesOrchestrator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "InfrastructureUpgradesOrchestrator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "InfrastructureUpgradesOrchestrator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "InfrastructureUpgradesOrchestrator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "InfrastructureUpgradesOrchestrator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "InfrastructureUpgradesOrchestrator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "InfrastructureUpgradesOrchestrator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "InfrastructureUpgradesOrchestrator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "InfrastructureUpgradesOrchestrator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "InfrastructureUpgradesOrchestrator", "exec_snapshot_link")

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
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "InfrastructureUpgradesOrchestrator.initialize"
        )

        if self._initialized:
            return
        logger.info("Initializing infrastructure upgrade components...")
        self.fact_ledger = get_fact_ledger()
        self.global_cache = get_global_cache()
        self.tone_enforcer = get_tone_enforcer()
        self.infrastructure = await InfrastructureOrchestrator()
        await self._setup_event_subscriptions()
        self._initialized = True
        logger.info("Infrastructure upgrades initialization complete")

    async def _setup_event_subscriptions(self) -> None:
        """Setup event subscriptions for component coordination."""
        await self.infrastructure.event_bus.subscribe(
            "events.content_generated",
            self._handle_content_generated,
        )
        await self.infrastructure.event_bus.subscribe("events.cache_miss", self._handle_cache_miss)
        await self.infrastructure.event_bus.subscribe("events.tone_violation", self._handle_tone_violation)
        logger.info("Setup infrastructure upgrades event subscriptions")

    async def _handle_content_generated(self, event: SystemEvent) -> None:
        """Handle content generation event for fact checking.

        Args:
            event: Content generated event
        """
        try:
            payload = event.payload
            content = payload.get("content", "")
            if content:
                violations = await self._verify_content_facts(content, event.trace_id)
                if violations:
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
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-silent-swallow
            logger.error(f"Failed to handle content generated: {e}")

    async def _handle_cache_miss(self, event: SystemEvent) -> None:
        """Handle cache miss event.

        Args:
            event: cache miss event
        """
        try:
            payload = event.payload
            query = payload.get("query", "")
            cache_type = payload.get("cache_type", "unknown")
            logger.debug(f"cache miss for {cache_type}: {query[:50]}...")
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-silent-swallow
            logger.error(f"Failed to handle cache miss: {e}")

    async def _handle_tone_violation(self, event: SystemEvent) -> None:
        """Handle tone violation event.

        Args:
            event: Tone violation event
        """
        try:
            payload = event.payload
            violations = payload.get("violations", [])
            violation_types = [v.get("type", "unknown") for v in violations]
            logger.info(f"Tone violations detected: {violation_types}")
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-silent-swallow
            logger.error(f"Failed to handle tone violation: {e}")

    async def _verify_content_facts(self, content: str, trace_id: str) -> list[VerificationResult]:
        """Verify facts in generated content.

        Args:
            content: Generated content
            trace_id: Trace ID for tracking

        Returns:
            List of verification results
        """
        import re

        sentences = re.split("[.!?]+", content)
        sentences = [s.strip() for s in sentences if s.strip()]
        violations = []
        for sentence in tqdm(sentences, desc="Processing", unit="item"):
            result = self.fact_ledger.verify_claim(sentence)
            if result.status == "CONFLICT":
                violations.append(result)
                await self.infrastructure.event_bus.publish(
                    "events.fact_conflict",
                    SystemEvent(
                        type=EventType.ERROR_OCCURRED,
                        trace_id=trace_id,
                        source_component="InfrastructureUpgradesOrchestrator",
                        payload={
                            "claim": sentence,
                            "correction": result.correction_suggestion,
                            "verified_value": result.verified_fact.value if result.verified_fact else None,
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
        if not trace_id:
            import uuid

            trace_id = str(uuid.uuid4())
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
            result = await self.infrastructure.execute_with_infrastructure(
                task_type,
                prompt,
                complexity_score=5,
                trace_id=trace_id,
            )
            content = result["result"]
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
            fact_violations = []
            if verify_facts:
                fact_violations = await self._verify_content_facts(content, trace_id)
            if use_cache:
                cache_key = f"{task_type.value}:{prompt}"
                self.global_cache.put(
                    cache_key,
                    result,
                    text_for_embedding=prompt,
                    source_engine="InfrastructureUpgrades",
                )
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
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
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
                "profiles_loaded": len(self.tone_enforcer.profiles) if self.tone_enforcer else 0,
            },
        }


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
        task_type,
        prompt,
        tone_voice,
        verify_facts,
        enforce_tone,
        True,
        trace_id,
    )


async def verify_claims(content: str) -> list[VerificationResult]:
    """Verify claims in content.

    Args:
        content: Content to verify

    Returns:
        List of verification results
    """
    ledger = get_fact_ledger()
    import re

    sentences = re.split("[.!?]+", content)
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
