# OTEL Collector Infrastructure Hardening — Best-Practice Upgrades

> **Plan slug**: `otel-collector-infra-hardening-a6f3b2`
> **Plan path**: `.windsurf/plans/otel-collector-infra-hardening-a6f3b2.md`
> **Parent plan**: `otel-collector-cert-receipt-b4d2e6` (pre-execution infra hardening)
> **Status**: Completed — 2026-05-03

PLAN_CREATED: slug=otel-collector-infra-hardening-a6f3b2 path=.windsurf/plans/otel-collector-infra-hardening-a6f3b2.md

## 1. Background

Web research (2025 best practices from opentelemetry.io, Dash0, SigNoz, Multiplayer,
OneUptime, Last9) identified five actionable gaps in the freshly-authored OTEL collector
infrastructure for the parent plan `otel-collector-cert-receipt-b4d2e6`. This plan lands
the high-value upgrades before the cert probe executes, so the collector is
production-shape and the probe exits cleanly.

## 2. Scope

### 2.1 In scope — upgrades applied

| # | Upgrade | Rationale | Source |
|---|---|---|---|
| H1 | Add `memory_limiter` as **first** processor in both pipelines | Spec: prevents OOM, must precede `batch` so backpressure reaches receivers | opentelemetry.io spec; Dash0; SigNoz; Multiplayer |
| H2 | Strip `http://` prefix from OTLP gRPC endpoint in probe | gRPC exporter expects `host:port`, not URL | OTel Python SDK docs |
| H3 | Tune `BatchSpanProcessor` with `schedule_delay_millis=1000`, `max_export_batch_size=512` | Faster `force_flush()` → shorter probe runtime | CNCF best-practices, OTel spec |
| M1 | Add `restart: unless-stopped` + `mem_limit: 512m` to collector service | Resilience + host memory protection | OneUptime production guide |
| M2 | Add compose `healthcheck` + `condition: service_healthy` pattern ready for future app containers | Ensures collector-first startup for sidecar pattern | opentelemetry.io security guide |

### 2.2 Out of scope

- TLS/mTLS on receivers — cert probe is local-only, `insecure: true` is correct here
- PII scrubbing — synthetic cert-probe spans have no PII
- Retry/queue on exporters — file + Prometheus are terminal exporters
- Docker Desktop restart — user infrastructure, not this plan's scope

## 3. Files In Scope

### Edit
- `docker-compose.otel.yml` — add restart policy + mem_limit
- `config/otel/collector-config.yaml` — add `memory_limiter` processor, reorder pipelines
- `tools/cert/run_otel_collector_probe.py` — strip `http://`, tune BSP

### Read
- parent plan `otel-collector-cert-receipt-b4d2e6.md`

## 4. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| W1 | P1.1 | Apply H1 + H2 + H3 + M1 + M2 to the three files | ~3k | Completed | Files updated; yaml/python parses; `python -c` import check passes |

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1.1 | Apply best-practice upgrades | 3 files above | Preserve all verifier-contract fields (exporter_status, status, probe_run_id); do not break file schema | ~3k | Completed |

## 6. Success Criteria

- [x] `config/otel/collector-config.yaml` has `memory_limiter` as first processor in both `traces` and `metrics` pipelines.
- [x] `docker-compose.otel.yml` has `restart: unless-stopped` and `mem_limit: 512m`.
- [x] Probe uses `localhost:4317` (no `http://` prefix).
- [x] Probe's BatchSpanProcessor configured with `schedule_delay_millis=1000`, `max_export_batch_size=512`.
- [x] `python -c "import tools.cert.run_otel_collector_probe"` passes without syntax error.
- [x] `python -c "import yaml; yaml.safe_load(open('config/otel/collector-config.yaml'))"` passes.

## 7. References

- Parent plan `otel-collector-cert-receipt-b4d2e6`
- opentelemetry.io/docs/security/config-best-practices/
- opentelemetry.io/docs/specs/otel/trace/sdk/ (ForceFlush + Shutdown contract)
- Dash0 "Mastering OpenTelemetry Memory Limiter Processor"
- SigNoz "OpenTelemetry Processors Explained"
