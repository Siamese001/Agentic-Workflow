from __future__ import annotations

from agentic_core.L2_execution.utils import write_gateway as _wg
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
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
    # noqa: E402
    record_execution_trace,
)

"\nL5 Streamer - Live Reasoning Broadcast System\n\nImplements non-blocking JSONL streaming of agent thoughts and actions\nto observability/audit/live_stream.jsonl for real-time monitoring.\n\nFeatures:\n- Non-blocking asyncio.Queue based streaming\n- WebSocket server for real-time browser updates\n- Reasoning extraction from LLM responses\n- Agent lifecycle broadcasts\n- Graceful shutdown with queue drain\n"
import asyncio
import json
import logging
import re
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import DEFAULT_TIMEOUT

if sys.platform == "win32":
    sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)
Logger: Any = logging.getLogger(__name__)
try:
    import websockets
    from websockets.server import WebSocketServerProtocol

    WEBSOCKETS_AVAILABLE: Any = True
except ImportError:  # guardian: allow-silent-swallow
    WEBSOCKETS_AVAILABLE: Any = False
    LOGGER.warning("websockets not available - live browser updates disabled")
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_snapshots_state,
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

record_execution_trace("reasoning_streamer", "reasoning_streamer_trace")


class L5Streamer:
    """
    Live reasoning broadcast system for L5+ autonomy.

    Provides non-blocking streaming of agent thoughts to both
    file (JSONL) and WebSocket clients for real-time monitoring.
    """

    def __init__(self, stream_dir: str = "observability/audit"):
        """
        Initialize the L5 streamer.

        Args:
            stream_dir: Directory for live_stream.jsonl output
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "L5Streamer.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "L5Streamer.__init__", "p0_governance")
        self.stream_dir = Path(stream_dir)
        self.log_path = self.stream_dir / "live_stream.jsonl"
        self.stream_queue: asyncio.Queue = asyncio.Queue()
        self.stream_task: asyncio.Task | None = None
        self._streamer_initialized: bool = False
        self._current_agent: str = "System"
        self._websocket_server: Any | None = None
        self._websocket_clients: set[WebSocketServerProtocol] = set()
        self._websocket_task: threading.Thread | None = None
        self.signals: set[str] = set()
        LOGGER.info(f"L5Streamer initialized with output: {self.log_path}")

    async def start_streamer(self) -> Any:
        """Initialize the non-blocking stream worker and WebSocket server."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L6_OBSERVABILITY, "L5Streamer.start_streamer")

        if self._streamer_initialized:
            return
        _wg.ensure_dir(self.stream_dir)
        if not self.stream_task or self.stream_task.done():
            self.stream_task = asyncio.create_task(self._stream_worker())
            self._streamer_initialized = True
        if WEBSOCKETS_AVAILABLE and (not self._websocket_server):
            self._websocket_task = threading.Thread(target=self._run_websocket_server, daemon=True)
            self._websocket_task.start()
        await self.broadcast("L5 Streamer initialized and operational", level="SYSTEM")
        LOGGER.info("L5 Streamer started")

    async def _stream_worker(self):
        """Background worker to drain queue to JSONL without blocking execution."""
        while True:
            try:
                payload = await self.stream_queue.get()
                try:
                    _wg.append_text(self.log_path, json.dumps(payload) + "\n")
                    if self._websocket_clients:
                        message = json.dumps(payload)
                        disconnected = set()
                        for client in self._websocket_clients:
                            try:
                                asyncio.run_coroutine_threadsafe(
                                    client.send(message), asyncio.get_event_loop()
                                ).result(timeout=DEFAULT_TIMEOUT)
                            except (ValueError, TypeError, RuntimeError) as e:
                                raise
                                disconnected.add(client)
                        self._websocket_clients -= disconnected
                finally:
                    self.stream_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                raise
                LOGGER.error(f"Streamer error writing to stream: {e}")

    def _run_websocket_server(self):
        """Run WebSocket server in a separate thread with its own event loop."""

        async def handle_client(websocket: WebSocketServerProtocol, path: str):
            """Handle new WebSocket client connections."""
            self._websocket_clients.add(websocket)
            LOGGER.info(f"WebSocket client connected: {websocket.remote_address}")
            try:
                await websocket.send(
                    json.dumps(
                        {
                            "type": "connected",
                            "message": "Connected to L5 Stream",
                            "agent": self._current_agent,
                        }
                    )
                )
                await websocket.wait_closed()
            except Exception as e:
                raise
                LOGGER.error(f"WebSocket client error: {e}")
            finally:
                self._websocket_clients.discard(websocket)
                LOGGER.info("WebSocket client disconnected")

        async def server_main():
            """Main WebSocket server coroutine."""
            try:
                async with websockets.serve(handle_client, "127.0.0.1", 8765):
                    LOGGER.info("🌐 WebSocket server started at ws://127.0.0.1:8765")
                    await asyncio.Future()
            except Exception as e:
                raise
                LOGGER.error(f"WebSocket server error: {e}")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(server_main())

    async def broadcast(self, message: str, agent: str = None, level: str = "INFO") -> Any:
        """
        Queue a message for live stream in non-blocking manner.

        Args:
            message: Message content to broadcast
            agent: Agent name (defaults to current agent)
            level: Log level (INFO, THOUGHT, AGENT_START, AGENT_END, ERROR)
        """
        payload: Any = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent or self._current_agent,
            "level": level,
            "content": message,
            "signals": list(self.signals),
        }
        await self.stream_queue.put(payload)

    async def broadcast_reasoning(self, response_text: str, agent: str = None) -> Any:
        """
        Extract and broadcast reasoning blocks from LLM responses.

        Args:
            response_text: Full LLM response text
            agent: Agent name (defaults to current agent)

        Returns:
            Extracted reasoning text or None
        """
        reasoning_match: Any = re.search("<reasoning>(.*?)</reasoning>", response_text, re.DOTALL)
        if reasoning_match:
            reasoning: Any = reasoning_match.group(1).strip()
            await self.broadcast(f"REASONING: {reasoning}", agent=agent, level="THOUGHT")
            return reasoning
        return None

    async def broadcast_agent_start(self, agent_name: str, message: str = None) -> Any:
        """Broadcast agent activation event."""
        self.set_current_agent(agent_name)
        msg: Any = message or f"ACTIVATED: {agent_name} starting execution"
        await self.broadcast(msg, agent=agent_name, level="AGENT_START")

    async def broadcast_agent_complete(self, agent_name: str, message: str = None) -> Any:
        """Broadcast agent completion event."""
        msg: Any = message or f"COMPLETED: {agent_name} finished execution"
        await self.broadcast(msg, agent=agent_name, level="AGENT_END")

    async def broadcast_agent_error(self, agent_name: str, error: str) -> Any:
        """Broadcast agent error event."""
        await self.broadcast(f"ERROR: {error}", agent=agent_name, level="ERROR")

    def set_current_agent(self, agent_name: str) -> Any:
        """Set the current agent for broadcast context."""
        self._current_agent = agent_name

    def add_signal(self, signal: str) -> Any:
        """Add a signal to current context."""
        self.signals.add(signal)

    def remove_signal(self, signal: str) -> Any:
        """Remove a signal from current context."""
        self.signals.discard(signal)

    async def stop_streamer(self) -> Any:
        """Gracefully stop the stream worker and WebSocket server."""
        if not self._streamer_initialized:
            return
        if self.stream_task and (not self.stream_task.done()):
            await self.stream_queue.join()
            self.stream_task.cancel()
            try:
                await self.stream_task
            except asyncio.CancelledError:
                pass
            self.stream_task = None
        for client in list(self._websocket_clients):
            try:
                asyncio.run_coroutine_threadsafe(client.close(), asyncio.get_event_loop()).result(
                    timeout=DEFAULT_TIMEOUT
                )
            except (ValueError, TypeError, RuntimeError) as e:
                raise
                pass
        self._websocket_clients.clear()
        self._streamer_initialized = False
        LOGGER.info("L5 Streamer stopped")


_l5_streamer: L5Streamer | None = None


def get_l5_streamer(stream_dir: str = "observability/audit") -> L5Streamer:
    """Get or create the global L5 streamer instance."""
    global _l5_streamer
    if _l5_streamer is None:
        _l5_streamer = L5Streamer(stream_dir)
    return _l5_streamer


async def start_l5_stream() -> Any:
    """Start the global L5 streamer."""
    streamer: Any = get_l5_streamer()
    await streamer.start_streamer()


async def broadcast(message: str, agent: str = None, level: str = "INFO") -> Any:
    """Broadcast a message via the global L5 streamer."""
    streamer: Any = get_l5_streamer()
    await streamer.broadcast(message, agent, level)


async def broadcast_reasoning(response_text: str, agent: str = None) -> Any:
    """Broadcast reasoning from LLM response via the global L5 streamer."""
    streamer: Any = get_l5_streamer()
    return await streamer.broadcast_reasoning(response_text, agent)


async def stop_l5_stream() -> Any:
    """Stop the global L5 streamer."""
    streamer: Any = get_l5_streamer()
    await streamer.stop_streamer()
