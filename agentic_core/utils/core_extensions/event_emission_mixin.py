import logging
import time
import uuid
import json
import asyncio
import inspect
from typing import Any, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from .context_propagation_mixin import trace_id_var, span_id_var

class SovereignEvent(BaseModel):
    """Standardized schema for all agentic events (Report 4.3)."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    event_type: str
    source_agent: str
    severity: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    payload: Dict[str, Any] = {}
    trace_id: Optional[str] = None

class EventEmissionMixin:
    """
    Phase 2 Observability Infrastructure: Event Emission (Report 4.3).

    Standardizes how agents broadcast internal state changes to L6.
    Features:
    - Structured Event Schema (Pydantic)
    - Automatic Source Attribution
    - Severity-based Filtering
    - Trace ID correlation support
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ee_logger = logging.getLogger(self.__class__.__name__)
        # Buffer for potential batch emission (Report 4.6)
        self._event_buffer = []

    def emit_event(self,
                   event_type: str,
                   payload: Optional[Dict[str, Any]] = None,
                   severity: str = "INFO",
                   trace_id: Optional[str] = None) -> SovereignEvent:
        """
        Broadmosts a structured event for L6 monitoring.

        Args:
            event_type: Category of the event (e.g., 'healing.success')
            payload: Data associated with the event
            severity: Impact level (INFO to CRITICAL)
            trace_id: ID for cross-agent request correlation

        Returns:
            SovereignEvent: The emitted event object
        """
        # Resolve trace_id: Provided arg > contextvar > None
        active_trace = trace_id or trace_id_var.get()
        active_span = span_id_var.get()

        # Add trace/span context to payload for deeper visibility
        event_payload = payload or {}
        if active_trace and "trace_id" not in event_payload:
            event_payload["trace_id"] = active_trace
        if active_span and "span_id" not in event_payload:
            event_payload["span_id"] = active_span

        event = SovereignEvent(
            event_type=event_type,
            source_agent=self.__class__.__name__,
            severity=severity.upper(),
            payload=event_payload,
            trace_id=active_trace
        )

        # 1. Standard Logging Integration
        log_level = getattr(logging, event.severity, logging.INFO)
        self._ee_logger.log(log_level, f"EVENT [{event.event_type}]: {event.payload}")

        # 2. L6 Observability Hook (Placeholder for L6 Central Dispatch)
        # In production, this would send to a centralized event bus or Redis stream
        self._dispatch_to_observability(event)

        return event

    def _dispatch_to_observability(self, event: SovereignEvent):
        """Internal: Routes the event to the L6 monitoring layer."""
        if not hasattr(self, "redis_client") or not self.redis_client:
            return

        async def _dispatch_async() -> None:
            """Hardened: 3 retries + 5s timeout per attempt."""
            MAX_RETRIES = 3
            TIMEOUT_SEC = 5.0
            base_delay = 0.8

            event_data = event.model_dump()
            stream_payload = {"event": json.dumps(event_data)}

            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    result = self.redis_client.xadd(
                        "sovereign_event_stream",
                        stream_payload,
                        maxlen=10000,
                    )

                    if inspect.isawaitable(result):
                        await asyncio.wait_for(result, timeout=TIMEOUT_SEC)
                    else:
                        await asyncio.wait_for(asyncio.to_thread(lambda: result), timeout=TIMEOUT_SEC)

                    self._ee_logger.debug(
                        f"Event dispatched (attempt {attempt}): {event.event_id}"
                    )
                    return
                except asyncio.TimeoutError:
                    self._ee_logger.warning(
                        f"Redis dispatch timeout (attempt {attempt}/{MAX_RETRIES})"
                    )
                except Exception as e:
                    self._ee_logger.warning(
                        f"Redis dispatch failed (attempt {attempt}/{MAX_RETRIES}): {e}"
                    )

                if attempt < MAX_RETRIES:
                    await asyncio.sleep(base_delay * (2 ** (attempt - 1)))

            self._ee_logger.error(
                f"Failed to dispatch event {event.event_id} after {MAX_RETRIES} attempts"
            )

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(_dispatch_async())
        except RuntimeError:
            # No running loop; best-effort single attempt without blocking agent execution.
            try:
                self.redis_client.xadd(
                    "sovereign_event_stream",
                    {"event": json.dumps(event.model_dump())},
                    maxlen=10000,
                )
            except Exception as e:
                self._ee_logger.error(f"Redis Dispatch Failed: {e}")

    @staticmethod
    def observe_execution(event_prefix: str):
        """Decorator to automatically emit start/end events for a method."""
        def decorator(func):
            from functools import wraps
            @wraps(func)
            async def wrapper(self, *args, **kwargs):
                if not isinstance(self, EventEmissionMixin):
                    return await func(self, *args, **kwargs)

                self.emit_event(f"{event_prefix}.started", {"args": str(args)})
                start_time = time.time()

                try:
                    result = await func(self, *args, **kwargs)
                    duration = time.time() - start_time
                    self.emit_event(
                        f"{event_prefix}.completed",
                        {"duration": round(duration, 4), "success": True}
                    )
                    return result
                except Exception as e:
                    self.emit_event(
                        f"{event_prefix}.failed",
                        {"error": str(e), "success": False},
                        severity="ERROR"
                    )
                    raise e
            return wrapper
        return decorator
