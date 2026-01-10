from __future__ import annotations
"""
TracingAgent: Sovereign Distributed Tracing System

Provides Span-based tracing for compliance missions and agent operations.
Features:
- Trace and Span ID generation (UUID4)
- Hierarchical parent-child spans
- Start/end timing with duration calculation
- Status tracking (SUCCESS/ERROR)
- Attribute and event recording
- Span sampling configuration (probability + head-based root sampling)
- File export of completed traces (JSON, timestamped or single file)

Designed for integration with:
- ComplianceOrchestratorAgent (root Span)
- Individual agents (child spans)
- ReportingAgent (future trace visualization)

Placed in observability/tracing per SSOT semantic registry:
  "Span tracing, context propagation, and distributed trace ids"

Depth: agentic_core/observability/tracing/tracing_agent.py
      → root/L1/L2/file.py → exactly 4 parts → Canon Key 3/12 compliant

Sovereign tracing Provider:
- Default: Pure mock (no deps)
- Optional: OpenTelemetry + OTLP export (if OTEL_EXPORTER_OTLP_ENDPOINT set)
"""
import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from agentic_core.utils.core_extensions.timeout_decorator import timeoutAny
from threading import Lock
from datetime import datetime
import uuid
import random
import json
from contextlib import contextmanager

Logger = logging.getLogger(__name__)


class Span:
    """Represents a single tracing Span."""

    def __init__(
        self,
        name: str,
        trace_id: str,
        span_id: str,
        parent_span_id: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_span_id = parent_span_id
        self.attributes = attributes or {}
        self.events: List[Dict[str, Any]] = []
        self.start_time: Optional[str] = None
        self.end_time: Optional[str] = None
        self.status: str = "IN_PROGRESS"

    def start(self) -> None:
        self.start_time = datetime.now().isoformat(timespec="milliseconds")

    def end(self, status: str = "SUCCESS") -> None:
        self.end_time = datetime.now().isoformat(timespec="milliseconds")
        self.status = status

    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        event = {
            "name": name,
            "timestamp": datetime.now().isoformat(timespec="milliseconds"),
            "attributes": attributes or {}
        }
        self.events.append(event)

    def set_attribute(self, key: str, value: Any) -> None:
        """Set a Span attribute."""
        self.attributes[key] = value

    def to_dict(self) -> Dict[str, Any]:
        duration_ms = 0.0
        if self.start_time and self.end_time:
            start = datetime.fromisoformat(self.start_time)
            end = datetime.fromisoformat(self.end_time)
            duration_ms = round((end - start).total_seconds() * 1000, 3)

        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": duration_ms,
            "status": self.status,
            "attributes": self.attributes,
            "events": self.events
        }


# Uppercase alias for backward compatibility
Span = Span

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.mixins import SubatomicTestingMixin

class TracingAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """
    Autonomous distributed tracing agent.
    Manages trace context and Span lifecycle.
    
    Sovereign tracing Provider:
    - Default: Pure mock (no deps)
    - Optional: OpenTelemetry + OTLP export (if OTEL_EXPORTER_OTLP_ENDPOINT set)
    """

    def __init__(
        self,
        project_root: Optional[Path] = None,
        export_path: Optional[Path] = None,
        timestamped_exports: bool = True,
        auto_export_on_mission_end: bool = True
    ):
        self.project_root = project_root.resolve() if project_root else None
        self._lock = Lock()
        self._spans: Dict[str, Span] = {}  # Standard Span dict
        self._trace_map: Dict[str, List[str]] = {}  # trace_id → [span_ids]
        self._sample_probability: float = 1.0  # Default: sample everything
        self._always_sample_traces: set = set()  # trace_ids to force-sample

        # Export configuration
        self.export_path = export_path.resolve() if export_path else None
        self.timestamped_exports = timestamped_exports
        self.auto_export_on_mission_end = auto_export_on_mission_end
        self._ensure_export_dir()

        if self.export_path:
            Logger.info(f"[TracingAgent] File export enabled: {self.export_path} (timestamped={timestamped_exports})")
        
        # Sovereign tracing Provider setup
        self.tracer = self._setup_sovereign_tracer()

    def _setup_sovereign_tracer(self) -> Any:
        """Setup mock tracer + optional OTLP export."""
        # 1. Internal Mock Provider (Zero-Dependency Fallback)
        class MockSpan:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def set_attribute(self, *args): pass
            def set_status(self, *args): pass
            def record_exception(self, *args): pass
            def add_event(self, *args, **kwargs): pass
            def end(self): pass

        class MockTracer:
            def start_as_current_span(self, name): return MockSpan()
            def start_span(self, name): return MockSpan()

        tracer = MockTracer()

        # 2. Optional OpenTelemetry/OTLP Integration
        try:
            from opentelemetry import trace as otel_trace
            from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            from opentelemetry.trace import set_tracer_provider

            endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
            if endpoint:
                resource = Resource(attributes={
                    SERVICE_NAME: "sovereign-agentic",
                    SERVICE_VERSION: "v2.9"
                })
                Provider = TracerProvider(resource=resource)
                processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, insecure=True))
                Provider.add_span_processor(processor)
                set_tracer_provider(Provider)
                tracer = otel_trace.get_tracer("sovereign.tracing")
                Logger.info(f"[TracingAgent] OTLP export enabled: {endpoint}")
            else:
                Logger.info("[TracingAgent] Using mock Provider (OTEL_EXPORTER_OTLP_ENDPOINT not set)")
        except Exception as e:
            Logger.warning(f"[TracingAgent] OTLP setup failed — using mock tracer: {e}")

        return tracer

    def get_tracer(self) -> Any:
        """Expose tracer for external mission use."""
        return self.tracer

    def _ensure_export_dir(self) -> None:
        """Create export directory if configured."""
        if self.export_path and self.export_path.suffix == "":
            # It's a directory
            try:
                self.export_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                Logger.error(f"[TracingAgent] Failed to create export directory {self.export_path}: {e}")
                self.export_path = None

    def _get_export_filepath(self, trace_id: Optional[str] = None) -> Optional[Path]:
        """Resolve actual export file path."""
        if not self.export_path:
            return None

        if self.timestamped_exports:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"trace_{timestamp}_{trace_id or 'batch'}.json"
            return self.export_path / filename if self.export_path.is_dir() else self.export_path.parent / filename
        else:
            return self.export_path

    def export_trace_to_file(self, trace_id: Optional[str] = None) -> bool:
        """
        Export one or all completed traces to file.

        Args:
            trace_id: Specific trace to export; if None, export all

        Returns:
            True if export succeeded
        """
        if not self.export_path:
            return False

        try:
            traces = {trace_id: self.get_trace(trace_id)} if trace_id else self.get_all_traces()
            if not traces or (trace_id and not traces.get(trace_id)):
                Logger.debug(f"[TracingAgent] No completed trace to export: {trace_id or 'all'}")
                return False

            export_data = list(traces.values()) if trace_id else list(traces.values())
            filepath = self._get_export_filepath(trace_id)

            if not filepath:
                return False

            mode = "a" if not self.timestamped_exports else "w"
            with open(filepath, mode, encoding="utf-8") as f:
                if not self.timestamped_exports:
                    # Append with comma separation for JSON array
                    if filepath.exists() and filepath.stat().st_size > 0:
                        f.write(",\nfrom agentic_core.utils.mixins import SubatomicTestingMixin\nfrom agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin\n")
                    else:
                        f.write("[\n")
                json.dump(export_data[0] if trace_id else export_data, f, indent=2)
                if not self.timestamped_exports:
                    f.write("\n]")

            Logger.info(f"[TracingAgent] Trace exported to {filepath}")
            return True

        except Exception as e:
            Logger.error(f"[TracingAgent] Failed to export trace to file: {e}")
            return False

    def set_sample_probability(self, probability: float) -> None:
        """
        Configure Span sampling rate.

        Args:
            probability: 0.0 (none) to 1.0 (all). Values outside clamped.
        """
        if not 0.0 <= probability <= 1.0:
            Logger.warning(f"[TracingAgent] Sampling probability {probability} out of range, clamping to [0.0, 1.0]")
            probability = max(0.0, min(1.0, probability))

        with self._lock:
            old = self._sample_probability
            self._sample_probability = probability

        Logger.info(f"[TracingAgent] Span sampling rate updated: {old:.2%} → {probability:.2%}")

    def force_sample_trace(self, trace_id: str) -> None:
        """Force all spans in a trace to be sampled (e.g., compliance mission root)."""
        with self._lock:
            self._always_sample_traces.add(trace_id)

    @contextmanager
    def create_span(
        self,
        name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None
    ):
        """
        Context manager for creating and completing a Span.

        Usage:
            with tracing_agent.create_span("location_validation") as Span:
                Span.set_attribute("file_count", 150)
                # do work
        """
        if not trace_id:
            trace_id = str(uuid.uuid4())

        # Sampling decision
        sample = True
        with self._lock:
            if trace_id in self._always_sample_traces:
                sample = True
            elif self._sample_probability < 1.0:
                sample = random.random() < self._sample_probability

        if not sample:
            # No-op Span: yield dummy to avoid breaking caller
            class NoOpSpan:
                def set_attribute(self, *args): pass
                def add_event(self, *args): pass
            yield NoOpSpan()
            return

        span_id = str(uuid.uuid4())
        new_span = Span(name, trace_id, span_id, parent_span_id, attributes)
        new_span.start()

        with self._lock:
            self._spans[span_id] = new_span
            self._trace_map.setdefault(trace_id, []).append(span_id)

        try:
            yield new_span
            new_span.end("SUCCESS")
        except Exception as e:
            new_span.end("ERROR")
            new_span.add_event("exception", {"error": str(e)})
            raise

    def set_attribute(self, span_id: str, key: str, value: Any) -> None:
        with self._lock:
            if span_id in self._spans:
                self._spans[span_id].attributes[key] = value

    def add_event(self, span_id: str, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        with self._lock:
            if span_id in self._spans:
                self._spans[span_id].add_event(name, attributes)

    def get_trace(self, trace_id: str) -> List[Dict[str, Any]]:
        """Return all spans for a trace, ordered by start time."""
        with self._lock:
            span_ids = self._trace_map.get(trace_id, [])
            spans = [self._spans[sid] for sid in span_ids if sid in self._spans]
            spans.sort(key=lambda s: s.start_time or "")
            return [s.to_dict() for s in spans]

    def get_all_traces(self) -> Dict[str, List[Dict[str, Any]]]:
        """Return all completed traces."""
        with self._lock:
            result = {}
            for trace_id, span_ids in self._trace_map.items():
                spans = []
                for sid in span_ids:
                    if sid in self._spans:
                        current_span = self._spans[sid]
                        if current_span.end_time:  # Only completed spans
                            spans.append(current_span.to_dict())
                if spans:
                    spans.sort(key=lambda s: s["start_time"])
                    result[trace_id] = spans
            return result

    def export_traces_json(self) -> str:
        """Export all traces as JSON string."""
        import json
        return json.dumps(self.get_all_traces(), indent=2)

    # === Compliance Mission Helpers ===

    @contextmanager
    def trace_compliance_mission(self, mission_id: str = "manual"):
        """High-level context for full compliance mission."""
        trace_id = str(uuid.uuid4())
        # Force sampling for root mission trace
        self.force_sample_trace(trace_id)

        attributes = {"mission_id": mission_id, "agent": "ComplianceOrchestratorAgent"}
        with self.create_span("full_compliance_mission", trace_id, attributes=attributes) as root_span:
            try:
                yield root_span, trace_id
            finally:
                # Auto-export on mission completion if enabled
                if self.auto_export_on_mission_end and self.export_path:
                    self.export_trace_to_file(trace_id)

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """Observability agent - invoke shared healing chain."""
        if _call_path is None:
            _call_path = set()
        # Invoke shared HealerMixin chain for diagnostics, rollback, MCP hardening
        super().heal_repository(dry_run=dry_run, execute=execute, depth=depth, max_depth=max_depth, _call_path=_call_path)
        print(f"[{self.__class__.__name__}] Observability agent - healing chain invoked")
        return {"skipped": 1}


# PascalCase is now the canonical name
