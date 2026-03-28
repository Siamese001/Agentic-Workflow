observability/
│
├── logging/                           # L4 Logs (event, state, error)
│   ├── sinks/                         # -1  Concrete output destinations
│   │   ├── console_logger.py
│   │   ├── file_logger.py
│   │   └── structured_json_logger.py
│   │
│   ├── formatters/                    # -1  Formatting logic for log events
│   │   ├── base_formatter.py
│   │   ├── json_formatter.py
│   │   └── color_formatter.py
│   │
│   ├── processors/                    # -1  Interceptors, enrichers, scrubbers
│   │   ├── pii_sanitizer.py
│   │   ├── metadata_enricher.py
│   │   └── sampling_processor.py
│   │
│   ├── core/                          # -1  Core logging interfaces
│   │   ├── logger.py
│   │   ├── log_event.py
│   │   └── log_config.py
│   │
│   └── adapters/                      # -1  External adapter integrations
│       ├── openai_logger_adapter.py
│       ├── mcp_tool_logger.py
│       └── http_api_logger.py
│
├── metrics/                           # L4 Metrics (counters, timers, gauges)
│   ├── collectors/                    # -1  Concrete metric collectors
│   │   ├── base_collector.py
│   │   ├── runtime_metrics_collector.py
│   │   └── pipeline_metrics_collector.py
│   │
│   ├── exporters/                     # -1  Output channels for metrics
│   │   ├── prometheus_exporter.py
│   │   ├── json_exporter.py
│   │   └── in_memory_exporter.py
│   │
│   ├── instruments/                   # -1  Metric primitives
│   │   ├── counter.py
│   │   ├── gauge.py
│   │   └── histogram.py
│   │
│   ├── registries/                    # -1 Metric registry objects
│   │   ├── metric_registry.py
│   │   └── metric_config.py
│   │
│   └── adapters/                      # -1 Third-party metrics hooks
│       ├── opentelemetry_adapter.py
│       └── cloudwatch_adapter.py
│
├── tracing/                           # L4 Distributed Tracing
│   ├── spans/                         # -1 Span models
│   │   ├── span.py
│   │   ├── span_context.py
│   │   └── span_config.py
│   │
│   ├── propagators/                   # -1 Context propagation
│   │   ├── w3c_trace_context.py
│   │   └── baggage_propagator.py
│   │
│   ├── samplers/                      # -1 Sampling strategies
│   │   ├── always_on_sampler.py
│   │   ├── probabilistic_sampler.py
│   │   └── parent_based_sampler.py
│   │
│   ├── exporters/                     # -1  Trace exporters
│   │   ├── otlp_exporter.py
│   │   ├── json_trace_exporter.py
│   │   └── console_trace_exporter.py
│   │
│   └── adapters/                      # -1  Third-party tracing bridges
│       ├── opentelemetry_tracing_adapter.py
│       └── jaeger_adapter.py
│
├── audits/                            # L5 Compliance + tamper-proof trails
│   ├── event_log/                     # -1  Immutable audit event objects
│   │   ├── audit_event.py
│   │   └── audit_schema.json
│   │
│   ├── stores/                        # -1  Where audit logs persist
│   │   ├── sqlite_audit_store.py
│   │   ├── file_audit_store.py
│   │   └── append_only_store.py
│   │
│   ├── verifiers/                     # -1  Integrity verification
│   │   ├── hash_chain_verifier.py
│   │   ├── signature_verifier.py
│   │   └── tamper_detector.py
│   │
│   └── processors/                    # -1  Pre-store transformations
│       ├── pii_redaction.py
│       └── audit_event_normalizer.py
│
└── diagnostics/                       # Internal debugging & health surfaces
    ├── health_checks/                 # -1  Liveness + readiness checks
    │   ├── cpu_check.py
    │   ├── memory_check.py
    │   └── dependency_check.py
    │
    ├── profilers/                     # -1  Perf & latency profiling
    │   ├── time_profiler.py
    │   ├── async_profiler.py
    │   └── cost_profiler.py
    │
    ├── inspectors/                    # -1  Attach-at-runtime introspection
    │   ├── state_inspector.py
    │   ├── token_budget_inspector.py
    │   └── dag_runtime_inspector.py
    │
    └── snapshots/                     # -1  Periodic snapshots
        ├── runtime_snapshot.py
        ├── planning_snapshot.py
        └── execution_snapshot.py


### Directory Structure

```plaintext
├── agentic_core.md
├── apps.md
├── config.md
├── data.md
├── observability.md
├── prompt_governance.md
├── runtime.md
├── schemas.md
├── scripts.md
├── tests.md
└── update_markdown_trees.py
```
