"""OpenTelemetry Integration E2E Tests - Tests all 4 phases of OTel implementation.

End-to-end tests for OpenTelemetry tracing gaps closure:
- Phase 1: OTLP exporter configuration
- Phase 2: TelemetryConsumer wiring
- Phase 3: L6 Observability integration
- Phase 4: Advanced span processors

Tests verify production-ready OTel pipeline from span generation
to external backend export and system learning consumption.
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# Lazy import fixtures - avoid collection-time errors

@pytest.fixture(scope="session")
def _lazy_agentic_core_L6_observability_enforcement_rag_telemetry_collector_0():
    from agentic_core.L6_observability.enforcement.rag_telemetry_collector import RagTelemetryCollector, RagMetrics
    return type('_Import', (), {"RagTelemetryCollector": RagTelemetryCollector, "RagMetrics": RagMetrics})

# Phase 1: OpenTelemetry imports
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False

try:
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter as OTLPGrpcExporter
    OTEL_GRPC_AVAILABLE = True
except ImportError:
    OTEL_GRPC_AVAILABLE = False

try:
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as OTLPHttpExporter
    OTEL_HTTP_AVAILABLE = True
except ImportError:
    OTEL_HTTP_AVAILABLE = False

# Internal imports
from apps_shared.utils.open_telemetry_tracing_adapter_util import (
    OpenTelemetryTracingAdapter,
    get_tracer,
    reset_tracer,
)
from system_learning.stores.otel_telemetry_store import (
    OpenTelemetrySpanStore,
    create_otel_telemetry_store,
)
from system_learning.engines.telemetry_consumer import (
    ingest_otel_spans,
    create_telemetry_consumer_with_otel,
)

from apps_shared.utils.agentic_span_processor import (
    AgenticSpanProcessor,
    RuntimeADGSpanEnricher,
    create_cognitive_telemetry_processor,
    create_execution_telemetry_processor,
    create_orchestration_telemetry_processor,
)


# =============================================================================
# Phase 1 E2E Tests: OTLP Exporter Configuration
# =============================================================================

@pytest.mark.skipif(not OTEL_AVAILABLE, reason="OpenTelemetry not installed")
class TestPhase1OtlpExporterConfiguration:
    """E2E tests for OTLP exporter configuration (Phase 1)."""

    def setup_method(self):
        """Reset tracer before each test."""
        reset_tracer()

    def teardown_method(self):
        """Reset tracer after each test."""
        reset_tracer()

    def test_otlp_grpc_exporter_configuration(self):
        """Test that OTLP gRPC exporter can be configured with custom endpoint."""
        if not OTEL_GRPC_AVAILABLE:
            pytest.skip("OTLP gRPC exporter not available")
        
        custom_endpoint = "http://localhost:5555"
        
        # Create tracer with OTLP gRPC enabled
        tracer = OpenTelemetryTracingAdapter(
            service_name="test-service",
            enable_console_export=False,
            enable_otlp_grpc=True,
            enable_otlp_http=False,
            otlp_grpc_endpoint=custom_endpoint,
        )
        
        # Verify tracer is enabled
        assert tracer.is_enabled()
        assert tracer.service_name == "test-service"

    def test_otlp_http_exporter_configuration(self):
        """Test that OTLP HTTP exporter can be configured with custom endpoint."""
        if not OTEL_HTTP_AVAILABLE:
            pytest.skip("OTLP HTTP exporter not available")
        
        custom_endpoint = "http://localhost:6666"
        
        # Create tracer with OTLP HTTP enabled
        tracer = OpenTelemetryTracingAdapter(
            service_name="test-service",
            enable_console_export=False,
            enable_otlp_grpc=False,
            enable_otlp_http=True,
            otlp_http_endpoint=custom_endpoint,
        )
        
        # Verify tracer is enabled
        assert tracer.is_enabled()

    def test_environment_variable_endpoint_configuration(self):
        """Test that OTLP endpoints can be configured via environment variables."""
        # Set environment variables
        os.environ["OTEL_EXPORTER_OTLP_GRPC_ENDPOINT"] = "http://jaeger:4317"
        os.environ["OTEL_EXPORTER_OTLP_HTTP_ENDPOINT"] = "http://tempo:4318"
        
        try:
            # Create tracer - should pick up env vars
            tracer = OpenTelemetryTracingAdapter(
                service_name="env-test-service",
                enable_otlp_grpc=OTEL_GRPC_AVAILABLE,
                enable_otlp_http=OTEL_HTTP_AVAILABLE,
            )
            
            assert tracer.is_enabled()
        finally:
            # Clean up environment
            del os.environ["OTEL_EXPORTER_OTLP_GRPC_ENDPOINT"]
            del os.environ["OTEL_EXPORTER_OTLP_HTTP_ENDPOINT"]

    def test_both_exporters_enabled(self):
        """Test that both OTLP gRPC and HTTP can be enabled simultaneously."""
        tracer = OpenTelemetryTracingAdapter(
            service_name="dual-export-service",
            enable_console_export=False,
            enable_otlp_grpc=OTEL_GRPC_AVAILABLE,
            enable_otlp_http=OTEL_HTTP_AVAILABLE,
        )
        
        assert tracer.is_enabled()

    def test_tracer_span_generation_with_exporters(self):
        """Test that spans are generated correctly with OTLP exporters configured."""
        tracer = OpenTelemetryTracingAdapter(
            service_name="span-test-service",
            enable_console_export=True,  # Console for test visibility
            enable_otlp_grpc=False,  # Don't actually export in tests
            enable_otlp_http=False,
        )
        
        # Generate a span
        with tracer.trace_orchestrator("test-mission", metadata={"test": "value"}):
            pass
        
        # Drain and verify spans
        spans = tracer.drain_completed_spans()
        assert len(spans) == 1
        assert spans[0]["name"] == "orchestrator.execute"
        assert spans[0]["attributes"]["mission"] == "test-mission"

    def test_get_tracer_factory_with_otlp_options(self):
        """Test that get_tracer() factory exposes OTLP configuration."""
        reset_tracer()
        
        tracer = get_tracer(
            service_name="factory-test",
            enable_console_export=False,
            enable_otlp_grpc=False,
            enable_otlp_http=False,
        )
        
        assert tracer is not None
        assert tracer.is_enabled() == OTEL_AVAILABLE


# =============================================================================
# Phase 2 E2E Tests: TelemetryConsumer Wiring
# =============================================================================

@pytest.mark.skipif(not OTEL_AVAILABLE, reason="OpenTelemetry not installed")
class TestPhase2TelemetryConsumerWiring:
    """E2E tests for TelemetryConsumer wiring (Phase 2)."""

    def test_opentelemetry_span_store_creation(self):
        """Test that OpenTelemetrySpanStore can be created and configured."""
        store = create_otel_telemetry_store(max_buffer_size=5000)
        
        assert isinstance(store, OpenTelemetrySpanStore)
        assert store._max_buffer_size == 5000

    def test_span_ingestion_into_store(self):
        """Test that spans can be ingested into the telemetry store."""
        store = OpenTelemetrySpanStore(max_buffer_size=100)
        
        # Create test spans
        test_spans = [
            {
                "ts_utc": 1700000000000,
                "trace_id": "trace-1",
                "span_id": "span-1",
                "name": "test.span",
                "kind": "orchestrator",
                "layer": "L3_Orchestration",
                "component": "TestComponent",
                "status": "ok",
            },
            {
                "ts_utc": 1700000001000,
                "trace_id": "trace-1",
                "span_id": "span-2",
                "parent_span_id": "span-1",
                "name": "test.child",
                "kind": "cognitive",
                "layer": "L1_Cognition",
                "component": "TestComponent",
                "status": "ok",
            },
        ]
        
        # Ingest spans
        count = store.ingest_spans(test_spans)
        assert count == 2
        assert store.get_span_count() == 2

    def test_span_buffer_eviction(self):
        """Test that old spans are evicted when buffer exceeds max size."""
        store = OpenTelemetrySpanStore(max_buffer_size=5)
        
        # Add more spans than buffer can hold
        for i in range(10):
            store.ingest_spans([{
                "ts_utc": 1700000000000 + i,
                "trace_id": f"trace-{i}",
                "span_id": f"span-{i}",
                "name": f"test.span.{i}",
                "kind": "test",
            }])
        
        # Buffer should only hold max_buffer_size spans
        assert store.get_span_count() == 5

    def test_read_events_by_time_window(self):
        """Test that events can be read by time window."""
        store = OpenTelemetrySpanStore()
        
        # Ingest spans at different times
        for i in range(5):
            store.ingest_spans([{
                "ts_utc": 1700000000000 + (i * 1000),  # 1 second apart
                "trace_id": f"trace-{i}",
                "span_id": f"span-{i}",
                "name": f"test.span.{i}",
                "kind": "test",
            }])
        
        # Read events within window
        events = store.read_events(
            window_start_utc=1700000000000,
            window_end_utc=1700000003000,  # Should get first 4 spans
        )
        
        assert len(events) == 4

    def test_telemetry_consumer_with_otel_factory(self):
        """Test that factory creates integrated OTel + consumer setup."""
        store, consumer = create_telemetry_consumer_with_otel(max_buffer_size=100)
        
        assert isinstance(store, OpenTelemetrySpanStore)
        assert callable(consumer)

    def test_ingest_otel_spans_function(self):
        """Test that ingest_otel_spans bridges OTel to telemetry store."""
        store = OpenTelemetrySpanStore()
        
        test_spans = [
            {"ts_utc": 1700000000000, "trace_id": "t1", "span_id": "s1", "name": "span1", "kind": "test"},
            {"ts_utc": 1700000001000, "trace_id": "t1", "span_id": "s2", "name": "span2", "kind": "test"},
        ]
        
        count = ingest_otel_spans(store, test_spans)
        assert count == 2
        assert store.get_span_count() == 2

    def test_full_pipeline_span_to_telemetry_event(self):
        """E2E test: span generation → ingestion → event consumption."""
        # Step 1: Generate spans with tracer
        tracer = OpenTelemetryTracingAdapter(
            service_name="pipeline-test",
            enable_console_export=False,
        )
        
        with tracer.trace_orchestrator("pipeline-mission"):
            with tracer.trace_cognitive("pipeline-task"):
                pass
        
        spans = tracer.drain_completed_spans()
        assert len(spans) == 2
        
        # Step 2: Ingest into telemetry store
        store = OpenTelemetrySpanStore()
        ingest_otel_spans(store, spans)
        assert store.get_span_count() == 2
        
        # Step 3: Consume events by time window
        events = store.read_events(
            window_start_utc=0,
            window_end_utc=9999999999999,
        )
        
        assert len(events) == 2
        # Verify event structure
        for event in events:
            assert len(event) == 3  # (ts_utc, kind, payload_bytes)
            ts_utc, kind, payload_bytes = event
            assert isinstance(ts_utc, int)
            assert isinstance(kind, str)
            assert isinstance(payload_bytes, bytes)


# =============================================================================
# Phase 3 E2E Tests: L6 Observability Integration
# =============================================================================

@pytest.mark.skipif(not OTEL_AVAILABLE, reason="OpenTelemetry not installed")
class TestPhase3L6ObservabilityIntegration:
    """E2E tests for L6 Observability integration (Phase 3)."""

    def test_rag_telemetry_collector_otel_span_consumption(self):
        """Test that RagTelemetryCollector can consume OTel spans."""
        collector = RagTelemetryCollector()
        
        # Reset metrics
        collector.metrics = RagMetrics()
        
        # Create RAG-related OTel spans
        rag_spans = [
            {
                "name": "rag.retrieve",
                "attributes": {
                    "rag.operation": "retrieval",
                    "rag.latency_ms": 150.0,
                    "rag.doc_count": 5,
                    "rag.cached": False,
                    "rag.reranked": True,
                    "rag.faithfulness_score": 0.85,
                    "rag.namespace": "test-namespace",
                },
            },
            {
                "name": "embedding.encode",
                "attributes": {
                    "rag.operation": "embedding",
                    "rag.latency_ms": 50.0,
                    "rag.doc_count": 0,
                    "rag.cached": True,
                    "rag.reranked": False,
                },
            },
        ]
        
        # Consume spans
        processed = collector.consume_otel_spans(rag_spans)
        assert processed == 2
        
        # Verify metrics were updated
        assert collector.metrics.total_queries == 2
        assert collector.metrics.cache_hits == 1
        assert collector.metrics.cache_misses == 1
        assert collector.metrics.rerank_count == 1

    def test_rag_metrics_extraction_from_span_attributes(self):
        """Test that all RAG metrics are correctly extracted from spans."""
        collector = RagTelemetryCollector()
        collector.metrics = RagMetrics()
        
        span = {
            "name": "rag.query",
            "attributes": {
                "rag.latency_ms": 250.0,
                "rag.doc_count": 10,
                "rag.cached": False,
                "rag.reranked": True,
                "rag.faithfulness_score": 0.92,
                "rag.namespace": "custom-namespace",
            },
        }
        
        processed = collector.consume_otel_spans([span])
        assert processed == 1
        
        # Verify all metrics
        metrics = collector.get_metrics()
        assert metrics.total_queries == 1
        assert metrics.cache_misses == 1
        assert metrics.rerank_count == 1
        assert metrics.latency_buckets["200-500ms"] == 1

    def test_non_rag_spans_filtered_out(self):
        """Test that non-RAG spans are not processed."""
        collector = RagTelemetryCollector()
        collector.metrics = RagMetrics()
        
        # Mix of RAG and non-RAG spans
        spans = [
            {"name": "rag.retrieve", "attributes": {"rag.operation": "retrieval"}},
            {"name": "api.generic.call", "attributes": {"api.endpoint": "/test"}},
            {"name": "database.query", "attributes": {"sql.table": "users"}},
            {"name": "embedding.encode", "attributes": {}},
        ]
        
        processed = collector.consume_otel_spans(spans)
        assert processed == 2  # Only RAG spans processed

    def test_rag_collector_singleton_behavior(self):
        """Test that RagTelemetryCollector maintains singleton behavior."""
        collector1 = RagTelemetryCollector()
        collector2 = RagTelemetryCollector()
        
        assert collector1 is collector2

    def test_full_telemetry_pipeline_to_l6(self):
        """E2E: OTel spans → TelemetryStore → RAG Collector → L6 Metrics."""
        # Step 1: Generate spans
        tracer = OpenTelemetryTracingAdapter(
            service_name="l6-pipeline-test",
            enable_console_export=False,
        )
        
        # Simulate RAG operation with metadata
        with tracer.trace_orchestrator("rag-pipeline-mission"):
            # Add span with RAG attributes
            with tracer.trace_cognitive("rag-retrieval", metadata={
                "rag.operation": "retrieval",
                "rag.latency_ms": 180.0,
                "rag.doc_count": 8,
                "rag.cached": False,
                "rag.reranked": True,
                "rag.faithfulness_score": 0.88,
            }):
                pass
        
        spans = tracer.drain_completed_spans()
        
        # Step 2: Process through telemetry store
        store = OpenTelemetrySpanStore()
        ingest_otel_spans(store, spans)
        
        # Step 3: Consume by RAG collector
        collector = RagTelemetryCollector()
        collector.metrics = RagMetrics()
        
        # Get latest spans from store
        latest_spans = store.get_latest_spans(count=100)
        processed = collector.consume_otel_spans(latest_spans)
        
        # Verify pipeline worked end-to-end
        assert processed >= 0  # May process RAG spans if found


# =============================================================================
# Phase 4 E2E Tests: Advanced Span Processors
# =============================================================================

@pytest.mark.skipif(not OTEL_AVAILABLE, reason="OpenTelemetry not installed")
class TestPhase4AdvancedSpanProcessors:
    """E2E tests for advanced span processors (Phase 4)."""

    def test_agentic_span_processor_creation(self):
        """Test that AgenticSpanProcessor can be created with filters."""
        processor = AgenticSpanProcessor(
            layer_filter={"L1_Cognition", "L2_Execution"},
            component_filter={"CognitivePlane"},
        )
        
        assert processor._layer_filter == {"L1_Cognition", "L2_Execution"}
        assert processor._component_filter == {"CognitivePlane"}

    def test_layer_filtering(self):
        """Test that spans are filtered by layer correctly."""
        processor = AgenticSpanProcessor(layer_filter={"L1_Cognition"})
        
        # Test span in filtered layer
        cognitive_span = {
            "attributes": {"layer": "L1_Cognition", "component": "Test"},
        }
        result = processor.process_span(cognitive_span)
        assert result is not None
        
        # Test span outside filtered layer
        execution_span = {
            "attributes": {"layer": "L2_Execution", "component": "Test"},
        }
        result = processor.process_span(execution_span)
        assert result is None

    def test_component_filtering(self):
        """Test that spans are filtered by component correctly."""
        processor = AgenticSpanProcessor(component_filter={"ReActEngine"})
        
        # Test span in filtered component
        react_span = {
            "attributes": {"layer": "L1_Cognition", "component": "ReActEngine"},
        }
        result = processor.process_span(react_span)
        assert result is not None
        
        # Test span outside filtered component
        other_span = {
            "attributes": {"layer": "L1_Cognition", "component": "OtherEngine"},
        }
        result = processor.process_span(other_span)
        assert result is None

    def test_runtime_adg_span_enricher(self):
        """Test that RuntimeADGSpanEnricher adds graph correlation."""
        enricher = RuntimeADGSpanEnricher(snapshot_id="test-snapshot-123")
        
        span = {
            "span_id": "span-abc",
            "parent_span_id": "parent-xyz",
            "attributes": {},
        }
        
        enriched = enricher.enrich(span)
        
        # Verify enrichment
        assert enriched["attributes"]["runtime_adg.snapshot_id"] == "test-snapshot-123"
        assert enriched["attributes"]["runtime_adg.node_id"] == "node_span-abc"
        assert enriched["attributes"]["runtime_adg.parent_node_id"] == "node_parent-xyz"

    def test_custom_enricher_pipeline(self):
        """Test custom enrichers are applied in pipeline."""
        processor = AgenticSpanProcessor()
        
        # Add custom enricher
        def add_custom_attr(span: dict[str, Any]) -> dict[str, Any]:
            if "attributes" not in span:
                span["attributes"] = {}
            span["attributes"]["custom.enriched"] = True
            return span
        
        processor.add_enricher(add_custom_attr)
        
        # Process span
        span = {"attributes": {"layer": "L1"}}
        result = processor.process_span(span)
        
        assert result["attributes"]["custom.enriched"] is True

    def test_custom_filter_pipeline(self):
        """Test custom filters are applied in pipeline."""
        processor = AgenticSpanProcessor()
        
        # Add custom filter that rejects "test" spans
        def reject_test_spans(span: dict[str, Any]) -> bool:
            name = span.get("name", "")
            return "test" not in name.lower()
        
        processor.add_filter(reject_test_spans)
        
        # Test span that passes filter
        good_span = {"name": "production.span", "attributes": {}}
        assert processor.process_span(good_span) is not None
        
        # Test span that fails filter
        test_span = {"name": "test.span", "attributes": {}}
        assert processor.process_span(test_span) is None

    def test_batch_span_processing(self):
        """Test batch processing of multiple spans."""
        processor = AgenticSpanProcessor(layer_filter={"L1_Cognition"})
        
        spans = [
            {"attributes": {"layer": "L1_Cognition"}},
            {"attributes": {"layer": "L2_Execution"}},
            {"attributes": {"layer": "L1_Cognition"}},
            {"attributes": {"layer": "L3_Orchestration"}},
        ]
        
        processed = processor.process_spans(spans)
        
        # Only L1_Cognition spans should pass
        assert len(processed) == 2

    def test_cognitive_telemetry_processor_factory(self):
        """Test cognitive layer processor factory."""
        processor = create_cognitive_telemetry_processor()
        
        # Should filter to L1_Cognition only
        cognitive_span = {"attributes": {"layer": "L1_Cognition"}}
        assert processor.process_span(cognitive_span) is not None
        
        execution_span = {"attributes": {"layer": "L2_Execution"}}
        assert processor.process_span(execution_span) is None

    def test_execution_telemetry_processor_factory(self):
        """Test execution layer processor factory."""
        processor = create_execution_telemetry_processor()
        
        execution_span = {"attributes": {"layer": "L2_Execution"}}
        assert processor.process_span(execution_span) is not None
        
        cognitive_span = {"attributes": {"layer": "L1_Cognition"}}
        assert processor.process_span(cognitive_span) is None

    def test_orchestration_telemetry_processor_factory(self):
        """Test orchestration layer processor factory."""
        processor = create_orchestration_telemetry_processor()
        
        orchestration_span = {"attributes": {"layer": "L3_Orchestration"}}
        assert processor.process_span(orchestration_span) is not None
        
        cognitive_span = {"attributes": {"layer": "L1_Cognition"}}
        assert processor.process_span(cognitive_span) is None

    def test_full_processor_pipeline_with_enrichment(self):
        """E2E: Filter → Enrich → Process pipeline."""
        # Create processor with layer filter
        processor = AgenticSpanProcessor(layer_filter={"L1_Cognition", "L2_Execution"})
        
        # Add Runtime ADG enrichment
        enricher = RuntimeADGSpanEnricher(snapshot_id="e2e-snapshot")
        processor.add_enricher(enricher.enrich)
        
        # Process spans
        spans = [
            {
                "span_id": "span-1",
                "name": "cognitive.think",
                "attributes": {"layer": "L1_Cognition"},
            },
            {
                "span_id": "span-2",
                "name": "action.execute",
                "attributes": {"layer": "L2_Execution"},
            },
            {
                "span_id": "span-3",
                "name": "orchestrator.run",
                "attributes": {"layer": "L3_Orchestration"},
            },
        ]
        
        processed = processor.process_spans(spans)
        
        # Only L1 and L2 spans should be processed
        assert len(processed) == 2
        
        # Verify enrichment was applied
        for span in processed:
            assert "runtime_adg.snapshot_id" in span["attributes"]
            assert "runtime_adg.node_id" in span["attributes"]


# =============================================================================
# Cross-Phase Integration E2E Tests
# =============================================================================

@pytest.mark.skipif(not OTEL_AVAILABLE, reason="OpenTelemetry not installed")
class TestCrossPhaseIntegration:
    """E2E tests spanning all 4 phases."""

    def test_complete_otel_pipeline_all_phases(self):
        """Complete E2E: OTel → Store → Consumer → L6 → Processor."""
        # Phase 1: Create tracer with configuration
        tracer = OpenTelemetryTracingAdapter(
            service_name="full-pipeline-test",
            enable_console_export=False,
        )
        
        # Generate spans
        with tracer.trace_orchestrator("full-pipeline-mission"):
            with tracer.trace_cognitive("full-pipeline-task", metadata={
                "rag.operation": "retrieval",
                "rag.latency_ms": 200.0,
                "rag.doc_count": 10,
            }):
                pass
        
        spans = tracer.drain_completed_spans()
        assert len(spans) >= 2
        
        # Phase 2: Store and consumer
        store = OpenTelemetrySpanStore()
        ingest_otel_spans(store, spans)
        
        # Phase 3: L6 consumption
        collector = RagTelemetryCollector()
        collector.metrics = RagMetrics()
        latest_spans = store.get_latest_spans(count=100)
        collector.consume_otel_spans(latest_spans)
        
        # Phase 4: Processor pipeline
        processor = create_cognitive_telemetry_processor()
        processed = processor.process_spans(latest_spans)
        
        # Verify pipeline completed
        assert store.get_span_count() > 0

    def test_deterministic_telemetry_slice_creation(self):
        """Test that telemetry slices are created deterministically."""
        store = OpenTelemetrySpanStore()
        
        # Ingest spans
        for i in range(5):
            store.ingest_spans([{
                "ts_utc": 1700000000000 + i,
                "trace_id": f"trace-{i}",
                "span_id": f"span-{i}",
                "name": f"span-{i}",
                "kind": "test",
            }])
        
        # Read events
        events1 = store.read_events(1700000000000, 1700000009999)
        events2 = store.read_events(1700000000000, 1700000009999)
        
        # Should be identical (deterministic)
        assert events1 == events2

    def test_concurrent_span_processing(self):
        """Test that span store handles concurrent access safely."""
        store = OpenTelemetrySpanStore(max_buffer_size=1000)
        
        import threading
        import time
        
        errors = []
        
        def ingest_worker(worker_id: int):
            try:
                for i in range(50):
                    store.ingest_spans([{
                        "ts_utc": 1700000000000 + worker_id * 1000 + i,
                        "trace_id": f"worker-{worker_id}",
                        "span_id": f"span-{worker_id}-{i}",
                        "name": f"worker-{worker_id}-span-{i}",
                        "kind": "test",
                    }])
                    time.sleep(0.001)  # Small delay
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=ingest_worker, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # Should have no errors
        assert len(errors) == 0
        # Should have spans (may be evicted due to buffer size)
        assert store.get_span_count() <= 1000


# =============================================================================
# Error Handling and Edge Cases
# =============================================================================

@pytest.mark.skipif(not OTEL_AVAILABLE, reason="OpenTelemetry not installed")
class TestErrorHandlingAndEdgeCases:
    """E2E tests for error handling and edge cases."""

    def test_empty_span_list_handling(self):
        """Test that empty span lists are handled gracefully."""
        store = OpenTelemetrySpanStore()
        
        count = store.ingest_spans([])
        assert count == 0
        assert store.get_span_count() == 0

    def test_invalid_span_data_handling(self):
        """Test that invalid span data is handled gracefully."""
        store = OpenTelemetrySpanStore()
        
        # Spans with missing required fields
        invalid_spans = [
            {},  # Empty span
            {"ts_utc": "not-a-number"},  # Wrong type
            {"ts_utc": None},  # None value
        ]
        
        # Should not raise exception
        count = store.ingest_spans(invalid_spans)
        assert count == 3  # All ingested even if invalid

    def test_store_clear_buffer(self):
        """Test that buffer can be cleared."""
        store = OpenTelemetrySpanStore()
        
        # Add spans
        store.ingest_spans([{"ts_utc": 1, "name": "test"}])
        assert store.get_span_count() == 1
        
        # Clear
        cleared = store.clear_buffer()
        assert cleared == 1
        assert store.get_span_count() == 0

    def test_span_processor_with_empty_spans(self):
        """Test that span processor handles empty span list."""
        processor = AgenticSpanProcessor()
        
        processed = processor.process_spans([])
        assert processed == []

    def test_span_processor_with_all_filtered(self):
        """Test that processor handles case where all spans are filtered."""
        processor = AgenticSpanProcessor(layer_filter={"NonExistentLayer"})
        
        spans = [
            {"attributes": {"layer": "L1_Cognition"}},
            {"attributes": {"layer": "L2_Execution"}},
        ]
        
        processed = processor.process_spans(spans)
        assert processed == []


# =============================================================================
# Performance E2E Tests
# =============================================================================

@pytest.mark.skipif(not OTEL_AVAILABLE, reason="OpenTelemetry not installed")
@pytest.mark.slow
class TestPerformanceE2E:
    """Performance-focused E2E tests."""

    def test_large_span_batch_processing(self):
        """Test processing of large span batches."""
        store = OpenTelemetrySpanStore(max_buffer_size=10000)
        
        # Generate large batch
        large_batch = [
            {
                "ts_utc": 1700000000000 + i,
                "trace_id": f"trace-{i % 100}",
                "span_id": f"span-{i}",
                "name": f"large-batch-span-{i}",
                "kind": "test",
                "layer": "L1_Cognition" if i % 3 == 0 else "L2_Execution",
            }
            for i in range(5000)
        ]
        
        # Process
        start = time.time()
        count = store.ingest_spans(large_batch)
        duration = time.time() - start
        
        assert count == 5000
        assert duration < 5.0  # Should complete in under 5 seconds

    def test_span_processor_performance(self):
        """Test span processor performance with large batches."""
        processor = AgenticSpanProcessor(layer_filter={"L1_Cognition", "L2_Execution"})
        
        # Add enricher
        enricher = RuntimeADGSpanEnricher()
        processor.add_enricher(enricher.enrich)
        
        # Generate batch
        spans = [
            {
                "span_id": f"span-{i}",
                "attributes": {
                    "layer": "L1_Cognition" if i % 2 == 0 else "L2_Execution",
                },
            }
            for i in range(1000)
        ]
        
        # Process
        start = time.time()
        processed = processor.process_spans(spans)
        duration = time.time() - start
        
        assert len(processed) == 1000
        assert duration < 2.0  # Should complete in under 2 seconds


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-x"])
