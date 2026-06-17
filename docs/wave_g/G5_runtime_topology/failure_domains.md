# G5 — Failure Domains and Blast Radius Grouping

wave: G5
produced_at: 2026-04-18
adg_snapshot: artifacts/adg/adg_indexed_04182026_0814.sqlite
upstream_artefacts:
  - docs/wave_g/G2_service_wiring/boundary_violations.md
  - docs/wave_g/G2b_provider_gateway/egress_points.yaml
  - docs/wave_g/G3_pipelines/pipeline_catalogue.yaml
  - docs/wave_g/G4_storage_infra/storage_catalogue.yaml
  - docs/wave_g/G4b_control_plane/kill_switches_and_risk.md

ADG snapshot timestamp used: `04182026_0814`.

## Domain FD-01 — Core app runtime and orchestration

- Scope: `apps_*` runtime entrypoints + `agentic_core` execution/orchestration layers.
- Typical failures: bootstrap import failures, route/handoff gate failures, healing exhaustion.
- Blast radius: app-local to cross-app depending on shared `agentic_core` module touched.
- Key probes: app startup logs, ADG bootstrap report summary, pipeline-specific traces.

## Domain FD-02 — ADG canonical graph service

- Scope: ADG sqlite snapshot generation, ADG MCP serving, graph projection state.
- Typical failures: stale snapshot, lock contention, cache/snapshot mismatch.
- Blast radius: all ADG-first analysis and any workflow dependent on structural graph correctness.
- Key probes: `adg_health`, `adg_status`, `adg_runtime_info`, `adg_stale_guard.py`.

## Domain FD-03 — Redis bridge/cache domain

- Scope: local Redis daemon + ADG hot cache + runtime cache namespaces.
- Typical failures: Redis down/cold, namespace drift, db mismatch, stale hot cache.
- Blast radius: ADG acceleration, memory import path, cache-backed orchestration and MCP redis tooling.
- Key probes: `redis_health`, `redis_namespace_stats`, `adg_redis_ingest --check`.

## Domain FD-04 — Vector retrieval and embedding domain

- Scope: vector_db MCP, vector_service singleton, Chroma embedded store, embedding model runtime.
- Typical failures: cold model latency, Chroma path lock/contention, warmup timeout, external model-download path leakage.
- Blast radius: retrieval-heavy app flows and semantic search operations.
- Key probes: `readiness`, `vector_stats`, per-query timing logs.

## Domain FD-05 — Observability/runtime-ADG domain

- Scope: `otel_mcp`, runtime ADG ingest/query services, dashboard aggregates, optional metrics sidecar.
- Typical failures: stale server process, ingest write failures, missing runtime ADG artifacts.
- Blast radius: telemetry visibility, anomaly detection, policy-decision traceability.
- Key probes: `otel_status`, `otel_server_info`, dashboard `degraded_component_flags`, sidecar `/metrics`.

## Domain FD-06 — MCP transport and launcher domain

- Scope: legacy editor MCP lifecycle, stdio protocol hygiene, filesystem launcher watchdog, external endpoint bridges.
- Typical failures: subprocess startup timeout, stdout protocol pollution, zombie duplicate MCP processes.
- Blast radius: tool-specific outages up to full IDE tooling degradation.
- Key probes: MCP tool responsiveness, launcher readiness marker, server-specific health tools.

## Domain FD-07 — External endpoint domain

- Scope: DeepWiki endpoint, Notion API, provider APIs, Git hosting APIs through GitKraken, optional HF model download.
- Typical failures: network outage, auth token expiry, remote service degradation.
- Blast radius: bounded to dependent tools/pipelines, but can block operator workflows.
- Key probes: connectivity tests (`enhanced_http`), per-tool API failures, auth validation errors.

## Domain FD-08 — Governance/hook/CI enforcement domain

- Scope: `.claude/settings.json` gate chain, operator workflows, GitHub Actions runtime posture workflows.
- Typical failures: over-blocking gate, stale gate logic, CI gate regressions.
- Blast radius: can halt deployment flow or tool execution despite healthy runtime services.
- Key probes: hook script exit diagnostics, workflow job statuses, gate artifact outputs.

## Cross-domain high-risk coupling points

1. **Redis coupling**: FD-02 (ADG) ↔ FD-03 (Redis) ↔ FD-04/FD-05 (vector/otel/memory imports).
2. **Import-time config coupling**: FD-01/FD-04 sensitive to process-start/import-time knobs from G4b.
3. **MCP lifecycle coupling**: FD-06 impacts all MCP-backed operator capabilities.
4. **Kill-switch coupling**: per-call policy bypasses (`EGRESS_GUARD_DISABLED`, `DISABLE_RUNTIME_MUTATION_GUARD`) can magnify impact from local domain failures into governance incidents.

## Fast triage order

1. Validate FD-02/FD-03 first (`adg_health`, `adg_status`, `redis_health`).
2. Validate FD-06 MCP process integrity (tool responsiveness + launcher/server_info checks).
3. Validate domain-specific readiness (`readiness` for vector, `otel_status`/`otel_server_info` for observability).
4. Validate FD-07 external endpoint reachability only after internal domains are green.
5. Review FD-08 hooks/CI gates when runtime appears healthy but actions are blocked.

## Unknowns explicitly retained

- Exact auto-recovery behavior for all Node/binary MCP bridges is external-tool-owned.
- External provider retry/circuit-breaker internals for Notion/GitKraken/DeepWiki are partially opaque.
