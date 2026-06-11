---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\runtime-gates-otel-live-feed-b5e8a4.md'
original_relative_path: 'runtime-gates-otel-live-feed-b5e8a4.md'
source_sha256: 1871601d5376699940e7275932cbc9beb5ae9bd7636d559d78f6bad707c51b23
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
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
