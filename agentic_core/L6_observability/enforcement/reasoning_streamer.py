from __future__ import annotations

"""
L5 Streamer - Live Reasoning Broadcast System

Implements non-blocking JSONL streaming of agent thoughts and actions
to observability/audit/live_stream.jsonl for real-time monitoring.

Features:
- Non-blocking asyncio.Queue based streaming
- WebSocket server for real-time browser updates
- Reasoning extraction from LLM responses
- Agent lifecycle broadcasts
- Graceful shutdown with queue drain
"""
import asyncio
import json
import logging
import re
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

if sys.platform == "win32":
    sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)
Logger: Any = logging.getLogger(__name__)
try:
    import websockets
    from websockets.server import WebSocketServerProtocol

    WEBSOCKETS_AVAILABLE: Any = True
except ImportError:
    WEBSOCKETS_AVAILABLE: Any = False
    LOGGER.warning("websockets not available - live browser updates disabled")


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
        if self._streamer_initialized:
            return
        self.stream_dir.mkdir(parents=True, exist_ok=True)
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
                    with open(self.log_path, "a", encoding="utf-8") as f:
                        f.write(json.dumps(payload) + "\n")
                    if self._websocket_clients:
                        message = json.dumps(payload)
                        disconnected = set()
                        for client in self._websocket_clients:
                            try:
                                asyncio.run_coroutine_threadsafe(
                                    client.send(message),
                                    asyncio.get_event_loop(),
                                ).result(timeout=1.0)
                            # guardian: allow-silent-swallow
                            except Exception:
                                disconnected.add(client)
                        self._websocket_clients -= disconnected
                finally:
                    self.stream_queue.task_done()
            except asyncio.CancelledError:
                break
            # guardian: allow-silent-swallow
            except Exception as e:
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
                        },
                    ),
                )
                await websocket.wait_closed()
            # guardian: allow-silent-swallow
            except Exception as e:
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
            # guardian: allow-silent-swallow
            except Exception as e:
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
                asyncio.run_coroutine_threadsafe(client.close(), asyncio.get_event_loop()).result(timeout=1.0)
            # guardian: allow-silent-swallow
            except Exception:
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
