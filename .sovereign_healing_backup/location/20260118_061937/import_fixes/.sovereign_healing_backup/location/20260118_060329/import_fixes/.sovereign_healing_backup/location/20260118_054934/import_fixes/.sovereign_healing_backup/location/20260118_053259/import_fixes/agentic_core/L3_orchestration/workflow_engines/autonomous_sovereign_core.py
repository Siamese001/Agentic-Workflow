from __future__ import annotations
"""
L3 Orchestration: Autonomous Sovereign Core
Cross-layer orchestrator that coordinates autonomous responses across L1-L5.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)



# NAMING FIXED: TerritoryWatcher → TerritoryWatcher
class TerritoryWatcher(FileSystemEventHandler):
    """Watches the entire territory for changes and feeds L3 Orchestration Executive"""
    
    def __init__(self, core):
        self.core = core
        super().__init__()

    def on_modified(self, event):
        if event.is_directory or any(x in event.src_path for x in ["pycache", ".git", ".idx"]):
            return
        # Thread-safe handoff to the L3 Executive Queue
        self.core.loop.call_soon_threadsafe(
            self.core.event_queue.put_nowait, 
            {"path": event.src_path, "type": "modify"}
        )


# NAMING FIXED: AutonomousSovereignCore → AutonomousSovereignCore
class AutonomousSovereignCore:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.event_queue = asyncio.Queue()
        self.running = True
        
        # Import autonomous improvements
        from agentic_core.L1_cognition.thought_engine.AdaptiveLearningEngine import (
            create_adaptive_learning_engine,
        )
        from agentic_core.L2_execution.ToolRegistry.ProactiveResourceManagerAgent import (
            create_proactive_resource_manager,
        )
        from agentic_core.L3_orchestration.workflow_engines.autonomous_execution_engine import (
            create_autonomous_execution_engine,
        )
        from agentic_core.L3_orchestration.workflow_engines.SelfRecoveringOrchestratorAgent import (
            create_self_recovering_orchestrator,
        )
        # GRAVITY FIXED: Dynamic imports for autonomous components
        try:
            from agentic_core.L4_state.checkpoint_manager import create_autonomous_checkpoint_manager
        except ImportError:
            create_autonomous_checkpoint_manager = lambda: None
        try:
            from agentic_core.L4_state.state_guardian import create_autonomous_state_guardian
        except ImportError:
            create_autonomous_state_guardian = lambda: None
        try:
            from agentic_core.L5_safety.guardrails.self_updating_safety_engine import create_self_updating_safety_engine
        except ImportError:
            create_self_updating_safety_engine = lambda: None

        # Initialize all autonomous layers
        self.l1_learning = create_adaptive_learning_engine(autonomous_mode=True)
        self.l2_resource = create_proactive_resource_manager()
        self.l3_orchestrator = create_self_recovering_orchestrator()
        self.l3_execution = create_autonomous_execution_engine()
        self.l4_checkpoint = create_autonomous_checkpoint_manager()
        self.l4_guardian = create_autonomous_state_guardian()
        self.l5_safety = create_self_updating_safety_engine()
        
        print(f"\n[ETERNAL SOVEREIGN CORE AWAKENED] {datetime.now()}")
        print(f"   L1 Adaptive Learning: Online")
        print(f"   L2 Resource Manager: Online")
        print(f"   L3 Self-Recovery: Online")
        print(f"   L3 Execution Engine: Online")
        print(f"   L4 Checkpoint Manager: Online")
        print(f"   L4 State Guardian: Online")
        print(f"   L5 Safety Engine: Online")
        
        # Awaken autonomous loops with dependency injection
        self.l1_learning.awaken()
        self.l2_resource.awaken(learner_instance=self.l1_learning)  # Inject L1 wisdom into L2
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
                
                # Priority 1: L5 Safety Review
                if "safety" in path or "guardrail" in path:
                    detection = await self.l5_safety.detect_threats(
                        Path(path).read_text(encoding='utf-8', errors='ignore')
                    )
                    if detection.detected:
                        print(f"   [L5] Threat detected: {detection.ThreatLevel}")
                
                # Priority 2: L4 Checkpoint
                await self.l4_checkpoint.auto_checkpoint_if_needed(
                    state={"event": event["type"], "path": path},
                    files_to_track=[path]
                )
                
                # Priority 3: L2 Resource Refresh
                status = self.l2_resource.get_resource_status()
                if status['global_budget_remaining'] < 10:
                    print(f"   [L2] Low resource budget: {status['global_budget_remaining']}")
                
            except Exception as e:
                print(f"   [!] Executive Worker Error: {e}")
            finally:
                self.event_queue.task_done()

    async def eternal_watch(self):
        """L3: Eternal monitoring loop"""
        # Launch background daemons and the Executive Worker
        asyncio.create_task(self.sovereign_executive_worker())
        
        # Set up file system watcher
        observer = Observer()
        handler = TerritoryWatcher(self)
        observer.schedule(handler, str(Path.cwd()), recursive=True)
        observer.start()
        
        print(f"   [L3] Territory watcher active on: {Path.cwd()}")
        
        try:
            while self.running:
                await asyncio.sleep(1)
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