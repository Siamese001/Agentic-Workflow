# Runtime Gates — OTEL Live Feed for BaselineRegistry

Plan ID: runtime-gates-otel-live-feed-b5e8a4

## Goal

Keep `BaselineRegistry` baselines fresh by subscribing to completed-span
events from the OTEL collector and pushing observations into the registry
on each completed run.

## Scope

`agentic_core/L5_safety/runtime_gates/otel_feed.py`:

- `OtelBaselineFeed(registry, *, span_to_observation=...)` — subscriber
  that converts an OTEL span dict into a `(task_class, observation)` tuple
  and calls `registry.update()`.
- `default_span_extractor(span)` — extracts `task_class` from
  `span.attributes['task.class']` and metrics from standard OTEL semantic
  conventions (`gen_ai.usage.input_tokens` + `output_tokens`,
  `gen_ai.cost.usd`, span duration).
- `consume_span_stream(feed, stream)` — generator-pump utility for
  iterating any iterable of spans.

Tests cover: standard OTEL attribute mapping, custom extractor, batch
ingestion, malformed-span tolerance, and end-to-end registry update.
