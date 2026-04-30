# SLO — apps_exec (Executive Brief Generator)

> **Status:** TARGETS, not yet measured. Wave 4.3 (cost/latency telemetry rollup) closes the loop.
> **Owner:** see `CODEOWNERS`
> **Last reviewed:** 2026-04-29

## Service Level Objectives

| Dimension | p50 | p95 | p99 | Hard ceiling | Error budget |
|---|---:|---:|---:|---:|---:|
| **Single brief generation (ingest → render)** | 6s | 18s | 35s | 90s (gate) | 1% / 30d |
| **Capability extraction call** | 400ms | 1.2s | 3.0s | 10s | 1% / 30d |
| **Style validation pass** | 80ms | 250ms | 600ms | 3s | <0.5% / 30d |
| **HTML render** | 30ms | 120ms | 300ms | 1s | <0.5% / 30d |
| **Markdown render** | 20ms | 80ms | 200ms | 1s | <0.5% / 30d |

**Justification — why exec briefs need <90s ceiling:** Exec briefs are typically requested in-meeting or in-session. >90s breaks the user's interactive flow. The hard ceiling is more important than the median.

## Cost Ceiling

| Workload | Per-call (USD) | Per-day budget |
|---|---:|---:|
| Brief assembly (1 LLM call, ~3K tokens) | $0.0024 | $24 |
| Capability extraction (1 LLM call, ~1.5K tokens) | $0.0012 | $12 |
| Style validator (deterministic, no LLM) | $0 | $0 |
| Total ceiling | — | **$40/day**, alert at 80% |

## Freshness

- **Capability evidence anchors** must reference artifacts ≤ 90 days old; older sources flagged in `gate_violations`.
- **Style template** updated only via ADR — frozen otherwise.

## Failure Modes (top-3 — see RUNBOOK.md for response)

1. **Brief assembly hangs > 90s** → almost always upstream LLM stall, not local. Check `agentic_core/L3_orchestration/inference/qwen_vllm.py` heartbeat. Fall through to deterministic skeleton.
2. **Style validator fires >3 violations** → reject brief, surface to user; do NOT auto-rewrite (constitutional anti-silent-rewrite).
3. **Capability extraction returns empty** → emit `gate_violations=["NO_CAPABILITIES_EXTRACTED"]` and refuse render. Better to fail visibly than ship an empty brief.

## Out of Scope (for THIS app's SLO)

- Audience-segmentation routing (decided upstream by L0)
- Document persistence (handled by `infrastructure/sdks_mcps/` consumers)

## How These Numbers Were Derived

- p50/p95: typical 3K-token Qwen call ~3–6s warm; brief assembly = 1 LLM + 1 capability + style + render ≈ 6–12s warm path.
- Cost: 3K tokens × $0.0008/1K tokens local-amortized ≈ $0.0024.
- 90s hard ceiling: human-interactive UX boundary (>90s the user disengages).

## Measurement Plan (W4.3)

- OTEL span with `app=apps_exec`, `phase` ∈ {`ingest`, `capability`, `assembly`, `style`, `render`}, latencies measured per-phase.
- Brief-level aggregation by `trace_id` to assert end-to-end p95.
- Reader-engagement loop (W4 stretch): track which sections users actually read; feed back as eval signal.
