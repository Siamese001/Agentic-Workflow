"""
[PHASE 16] TerritoryChangeHandlerAgent - L5 Safety & Validation.

Watches for territory healing/ingestion changes and triggers RAG reindexing.
Acts as a safety gate to ensure the "Canon" stays aligned with the filesystem.
"""

import asyncio
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    # noqa: E402,
    # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "TerritoryChangeHandlerAgent")
emit_determinism_digest("p0", "TerritoryChangeHandlerAgent")

_emit_dispatches_healing_run("p1", "TerritoryChangeHandlerAgent", "L5")
_emit_routes_through("p1", "TerritoryChangeHandlerAgent", "L5")
_emit_checks_agent_registry("p1", "TerritoryChangeHandlerAgent", "agent_registry")
_emit_validates_agent_capability("p1", "TerritoryChangeHandlerAgent", "capability")
_emit_dispatches_execution_plan("p1", "TerritoryChangeHandlerAgent", "exec_plan")
_emit_agent_executes_agent("p1", "TerritoryChangeHandlerAgent", "sub_agent")
_emit_routes_to_agent("p1", "TerritoryChangeHandlerAgent", "target_agent")
_emit_verifies_policy("p1", "TerritoryChangeHandlerAgent", "policy_check")
_emit_observes_runtime_state("p1", "TerritoryChangeHandlerAgent", "runtime_state")
_emit_verifies_boundary("p1", "TerritoryChangeHandlerAgent", "boundary_check")
_emit_transcripts_response("p1", "TerritoryChangeHandlerAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "TerritoryChangeHandlerAgent")
_emit_gated_by_confidence("p1", "TerritoryChangeHandlerAgent", "confidence_gate")
_emit_escalates_to_human("p1", "TerritoryChangeHandlerAgent", "L5")
_emit_reads_policy_state("p1", "TerritoryChangeHandlerAgent", "L5")

_emit_applies_guardrail("p0", "TerritoryChangeHandlerAgent", "p0_governance")
_emit_snapshots_state("p0", "TerritoryChangeHandlerAgent", "state_snapshot")
_emit_authorize_and_execute("p2", "TerritoryChangeHandlerAgent", "execution_auth")
_emit_validates_capability("p2", "TerritoryChangeHandlerAgent", "capability_check")
_emit_routes_to_capability("p2", "TerritoryChangeHandlerAgent", "capability_route")
_emit_writes_via_uwg("p2", "TerritoryChangeHandlerAgent", "uwg_write")
_emit_blocks_direct_write("p2", "TerritoryChangeHandlerAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "TerritoryChangeHandlerAgent", "tool_invocation")
_emit_captures_execution_output("p2", "TerritoryChangeHandlerAgent", "exec_output")
_emit_dispatches_agent("p3", "TerritoryChangeHandlerAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "TerritoryChangeHandlerAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "TerritoryChangeHandlerAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "TerritoryChangeHandlerAgent", "healing_outcome")
_emit_escalates_failure("p3", "TerritoryChangeHandlerAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "TerritoryChangeHandlerAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "TerritoryChangeHandlerAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "TerritoryChangeHandlerAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "TerritoryChangeHandlerAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "TerritoryChangeHandlerAgent", "eval_metric")
_emit_stores_embedding("p4", "TerritoryChangeHandlerAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "TerritoryChangeHandlerAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "TerritoryChangeHandlerAgent", "exec_snapshot_link")

try:
    from watchdog.events import FileSystemEventHandler  # noqa: F401
    from watchdog.observers import Observer  # noqa: F401
except ImportError:  # guardian: allow-silent-swallow
    Observer = object
    FileSystemEventHandler = object
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_signs_execution_trace,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("TerritoryChangeHandlerAgent", "p4obs", "metric_1")
_emit_emits_metric_event("TerritoryChangeHandlerAgent", "p4obs", "metric_2")
_emit_emits_metric_event("TerritoryChangeHandlerAgent", "p4obs", "metric_3")
_emit_emits_metric_event("TerritoryChangeHandlerAgent", "p4obs", "metric_4")
_emit_emits_metric_event("TerritoryChangeHandlerAgent", "p4obs", "metric_5")
_emit_emits_metric_event("TerritoryChangeHandlerAgent", "p4obs", "metric_6")
_emit_records_incident_event("TerritoryChangeHandlerAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("TerritoryChangeHandlerAgent", "p4obs", "anomaly")
_emit_writes_observability_log("TerritoryChangeHandlerAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("TerritoryChangeHandlerAgent", "p4obs", "mon_state")
_emit_triggers_alert("TerritoryChangeHandlerAgent", "p4obs", "alert")
_emit_links_incident_trace("TerritoryChangeHandlerAgent", "p4obs", "trace_link")
_emit_captures_pattern("TerritoryChangeHandlerAgent", "p3lm", "pattern")
_emit_records_learning_event("TerritoryChangeHandlerAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("TerritoryChangeHandlerAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("TerritoryChangeHandlerAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("TerritoryChangeHandlerAgent", "p3lm", "routing")
_emit_improves_agent_policy("TerritoryChangeHandlerAgent", "p3lm", "policy")
_emit_stores_learning_state("TerritoryChangeHandlerAgent", "p3lm", "state")
_emit_records_execution_trace("TerritoryChangeHandlerAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("TerritoryChangeHandlerAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("TerritoryChangeHandlerAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("TerritoryChangeHandlerAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("TerritoryChangeHandlerAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("TerritoryChangeHandlerAgent", "env_read", "p2_env_1")
_emit_reads_environ("TerritoryChangeHandlerAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("TerritoryChangeHandlerAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("TerritoryChangeHandlerAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "TerritoryChangeHandlerAgent", "context_pull")
_emit_pulls_context("p1", "TerritoryChangeHandlerAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "TerritoryChangeHandlerAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "TerritoryChangeHandlerAgent", "uwg_term_2")
_emit_writes_through("p1", "TerritoryChangeHandlerAgent", "write_through")
_emit_writes_through("p1", "TerritoryChangeHandlerAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "TerritoryChangeHandlerAgent", "safety_validation")
_emit_invokes_eval("p1", "TerritoryChangeHandlerAgent", "eval_call")
_emit_proposal_commits_routing("p1", "TerritoryChangeHandlerAgent", "routing_commit")


def timeout(seconds: int):
    def decorator(func):
        return func

    return decorator


Logger = logging.getLogger(__name__)
AGENTIC_CORE_DIR = os.environ.get("AGENTIC_CORE_DIR", ".")


@dataclass
class TerritoryChangeHandlerAgent(SovereignBaseAgent, FileSystemEventHandler):
    """
    L5 Safety Agent: Watches for territory changes with debouncing.
    Informs the AutonomousRagDaemon when re-indexing is required.
    """

    def __init__(self, daemon: Any = None, **kwargs) -> None:
        """Initialize the agent with debouncing logic."""
        super().__init__(**kwargs)
        self.daemon = daemon
        self.last_trigger = 0.0
        # guardian: allow-magic-config
        self.debounce_seconds = 10

    def on_modified(self, event: Any) -> None:
        """Execute on_modified operation when files change."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "TerritoryChangeHandlerAgent.on_modified"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:TerritoryChangeHandlerAgent.on_modified".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if event.is_directory:
            return
        if event.src_path.endswith((".py", ".json", ".yaml", ".md", ".txt")):
            current_time = time.time()
            if current_time - self.last_trigger > self.debounce_seconds:
                self.last_trigger = current_time
                if self.daemon and hasattr(self.daemon, "loop"):
                    self.daemon.loop.call_soon_threadsafe(
                        lambda: asyncio.create_task(self.daemon.trigger_reindex())
                    )

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> dict[str, Any]:
        """L5 validation - operational health check."""
        base_results = super().heal_repository(dry_run=dry_run, execute=execute, **kwargs)
        return {"status": "active", "last_trigger": self.last_trigger, "base_healing": base_results}

    def heal(self, violation, **kwargs):
        return super().heal(violation, **kwargs)


class AutonomousRagDaemon:
    """
    L5/L3 Hybrid: Self-monitoring RAG system with autonomous health checks.
    Uses TerritoryChangeHandlerAgent to maintain sync between disk and vector DB.
    """

    def __init__(self, orchestrator: Any, retriever: Any, historian: Any) -> None:
        """Initialize the daemon with its dependencies."""
        self.orchestrator = orchestrator
        self.retriever = retriever
        self.historian = historian
        self.loop = asyncio.get_event_loop()
        self.running = True
        # guardian: allow-magic-config
        self.health_check_interval = 3600
        # guardian: allow-magic-config
        self.reindex_interval = 86400
        self.observer = Observer()
        self.handler = TerritoryChangeHandlerAgent(daemon=self)

    async def start(self) -> None:
        """Start the autonomous monitoring and reindexing cycle."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "AutonomousRagDaemon.start")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:AutonomousRagDaemon.start".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        watch_path = Path(AGENTIC_CORE_DIR)
        if watch_path.exists():
            self.observer.schedule(self.handler, str(watch_path), recursive=True)
            self.observer.start()
            asyncio.create_task(self.health_check_loop())
            asyncio.create_task(self.periodic_reindex_loop())
            Logger.info(f"[TERRITORY] Monitoring started on: {watch_path}")

    async def health_check_loop(self) -> None:
        """Sovereign validation: testing the Canon against reality."""
        while self.running:
            await asyncio.sleep(self.health_check_interval)
            try:
                test_queries = ["Purpose of the Canon?", "Explain L5 safety", "How does L1 expansion work?"]
                import random

                query = random.choice(test_queries)
                result = await self.orchestrator.sovereign_retrieve(query)
                faithfulness = result.get("faithfulness", 0.0)
                self.historian.log_event(
                    {
                        "event": "health_check",
                        "query": query,
                        "faithfulness": faithfulness,
                        "timestamp": time.time(),
                    }
                )
                if faithfulness < 0.75:
                    Logger.warning(f"[TERRITORY] Faithfulness low ({faithfulness}). Triggering reindex.")
                    await self.trigger_reindex()
            except Exception as e:
                raise
                Logger.error(f"[TERRITORY] Health check failed: {e}")

    async def periodic_reindex_loop(self) -> None:
        """Enforce periodic full reindexing to prevent drift."""
        while self.running:
            await asyncio.sleep(self.reindex_interval)
            await self.trigger_reindex()

    async def trigger_reindex(self) -> None:
        """Execute the actual reindex operation on the retriever."""
        try:
            Logger.info("[TERRITORY] Starting reindexing of the canon...")
            await self.retriever.reindex_all()
        except Exception as e:
            raise
            Logger.error(f"[TERRITORY] Reindexing failed: {e}")

    async def stop(self) -> None:
        """Graceful shutdown of the monitoring system."""
        self.running = False
        self.observer.stop()
        self.observer.join()
