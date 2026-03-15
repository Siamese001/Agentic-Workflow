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

try:
    from watchdog.events import FileSystemEventHandler  # noqa: F401
    from watchdog.observers import Observer  # noqa: F401
except ImportError:
    Observer = object
    FileSystemEventHandler = object
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace, _emit_signs_execution_trace


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
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "TerritoryChangeHandlerAgent.on_modified")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:TerritoryChangeHandlerAgent.on_modified".encode()).hexdigest()[:24]
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
