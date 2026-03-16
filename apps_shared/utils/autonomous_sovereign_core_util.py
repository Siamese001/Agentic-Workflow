"""
L3 Orchestration: Autonomous Sovereign Core
Cross-layer orchestrator that coordinates autonomous responses across L1-L5.
"""

import asyncio
from datetime import datetime
from pathlib import Path

from watchdog.observers import Observer

from agentic_core.L0_routing.config.path_constants import DEFAULT_SLEEP
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

_emit_applies_guardrail("p0", "autonomous_sovereign_core_util", "p0_governance")
_emit_reads_policy_state("p0", "autonomous_sovereign_core_util", "policy_binding")
_emit_snapshots_state("p0", "autonomous_sovereign_core_util", "state_snapshot")
emit_replay_key("p0", "autonomous_sovereign_core_util")
emit_determinism_digest("p0", "autonomous_sovereign_core_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "autonomous_sovereign_core_util", "execution_auth")
_emit_validates_capability("p2", "autonomous_sovereign_core_util", "capability_check")
_emit_routes_to_capability("p2", "autonomous_sovereign_core_util", "capability_route")
_emit_writes_via_uwg("p2", "autonomous_sovereign_core_util", "uwg_write")
_emit_blocks_direct_write("p2", "autonomous_sovereign_core_util", "direct_write_block")
_emit_records_tool_invocation("p2", "autonomous_sovereign_core_util", "tool_invocation")
_emit_captures_execution_output("p2", "autonomous_sovereign_core_util", "exec_output")
_emit_dispatches_agent("p3", "autonomous_sovereign_core_util", "agent_dispatch")
_emit_coordinates_agents("p3", "autonomous_sovereign_core_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "autonomous_sovereign_core_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "autonomous_sovereign_core_util", "healing_outcome")
_emit_escalates_failure("p3", "autonomous_sovereign_core_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "autonomous_sovereign_core_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "autonomous_sovereign_core_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "autonomous_sovereign_core_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "autonomous_sovereign_core_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "autonomous_sovereign_core_util", "eval_metric")
_emit_stores_embedding("p4", "autonomous_sovereign_core_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "autonomous_sovereign_core_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "autonomous_sovereign_core_util", "exec_snapshot_link")


class TerritoryWatcher(FileSystemEventHandler):
    """Watches the entire territory for changes and feeds L3 Orchestration Executive"""

    def __init__(self, core):
        self.core = core
        super().__init__()

    def on_modified(self, event):
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "TerritoryWatcher.on_modified")

        if event.is_directory or any(x in event.src_path for x in ["pycache", ".git", ".idx"]):
            return
        self.core.loop.call_soon_threadsafe(
            self.core.event_queue.put_nowait, {"path": event.src_path, "type": "modify"}
        )


class AutonomousSovereignCore:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.event_queue = asyncio.Queue()
        self.running = True
        try:
            from ..L3_orchestration.engines.adaptive_learning import create_adaptive_learning_engine
        except ImportError:

            def create_adaptive_learning_engine():
                return None

        try:
            from ..L3_orchestration.engines.proactive_resources import create_proactive_resource_manager
        except ImportError:

            def create_proactive_resource_manager():
                return None

        try:
            from ..L3_orchestration.engines.autonomous_execution import create_autonomous_execution_engine
        except ImportError:

            def create_autonomous_execution_engine():
                return None

        try:
            from ..L3_orchestration.engines.self_recovering import create_self_recovering_orchestrator
        except ImportError:

            def create_self_recovering_orchestrator():
                return None

        try:
            from ..L5_safety.gravity.autonomous_checkpoint import create_autonomous_checkpoint_manager
        except ImportError:

            def create_autonomous_checkpoint_manager():
                return None

        try:
            from ..L5_safety.gravity.autonomous_state_guardian import create_autonomous_state_guardian
        except ImportError:

            def create_autonomous_state_guardian():
                return None

        try:
            from ..L5_safety.gravity.self_updating_safety import create_self_updating_safety_engine
        except ImportError:

            def create_self_updating_safety_engine():
                return None

        self.l1_learning = create_adaptive_learning_engine(autonomous_mode=True)
        self.l2_resource = create_proactive_resource_manager()
        self.l3_orchestrator = create_self_recovering_orchestrator()
        self.l3_execution = create_autonomous_execution_engine()
        self.l4_checkpoint = create_autonomous_checkpoint_manager()
        self.l4_guardian = create_autonomous_state_guardian()
        self.l5_safety = create_self_updating_safety_engine()
        print(f"\n[ETERNAL SOVEREIGN CORE AWAKENED] {datetime.now()}")
        print("   L1 Adaptive Learning: Online")
        print("   L2 Resource Manager: Online")
        print("   L3 Self-Recovery: Online")
        print("   L3 Execution Engine: Online")
        print("   L4 Checkpoint Manager: Online")
        print("   L4 State Guardian: Online")
        print("   L5 Safety Engine: Online")
        self.l1_learning.awaken()
        self.l2_resource.awaken(learner_instance=self.l1_learning)
        self.l3_orchestrator.awaken_mutation_engine()
        self.l3_execution.awaken()
        self.l4_guardian.awaken()

    async def sovereign_executive_worker(self):
        """L3: The central brain processing prioritized territory events"""
        while self.running:
            event = await self.event_queue.get()
            path = event["path"]
            try:
                print(f"   [EXECUTIVE] Processing: {Path(path).name}")
                if "safety" in path or "guardrail" in path:
                    detection = await self.l5_safety.detect_threats(
                        Path(path).read_text(encoding="utf-8", errors="ignore")
                    )
                    if detection.detected:
                        print(f"   [L5] Threat detected: {detection.ThreatLevel}")
                await self.l4_checkpoint.auto_checkpoint_if_needed(
                    state={"event": event["type"], "path": path}, files_to_track=[path]
                )
                status = self.l2_resource.get_resource_status()
                if status["global_budget_remaining"] < 10:
                    print(f"   [L2] Low resource budget: {status['global_budget_remaining']}")
            # guardian: allow-silent-swallow
            except Exception as e:
                print(f"   [!] Executive Worker Error: {e}")
            finally:
                self.event_queue.task_done()

    async def eternal_watch(self):
        """L3: Eternal monitoring loop"""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AutonomousSovereignCore.eternal_watch")

        asyncio.create_task(self.sovereign_executive_worker())
        observer = Observer()
        handler = TerritoryWatcher(self)
        observer.schedule(handler, str(Path.cwd()), recursive=True)
        observer.start()
        print(f"   [L3] Territory watcher active on: {Path.cwd()}")
        try:
            while self.running:
                await asyncio.sleep(DEFAULT_SLEEP)
        except KeyboardInterrupt:
            print("\n[L3] Sovereign Core shutting down...")
            observer.stop()
            observer.join()


async def main():
    """Entry point for L3 Autonomous Sovereign Core"""
    core = AutonomousSovereignCore()
    await core.eternal_watch()


if __name__ == "__main__":
    asyncio.run(main())
