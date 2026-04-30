# SLO — apps_lic (LinkedIn / Lead Intelligence & Composition)

> **Status:** TARGETS, not yet measured. Wave 4.3 (cost/latency telemetry rollup) closes the loop.
> **Owner:** see `CODEOWNERS`
> **Last reviewed:** 2026-04-29

## Architecture Note

apps_lic is the largest in-portfolio app: **97 files, 882KB**, with a multi-stage hop registry (`hop_stage_registry.py`) and a 22KB retry-policy module. Its SLOs are **per-hop** because end-to-end latency is dominated by the slowest hop, not the median.

## Service Level Objectives — Per Hop

| Hop / Stage | p50 | p95 | p99 | Hard ceiling | Error budget |
|---|---:|---:|---:|---:|---:|
| **Archetype indicator** (input shape detect) | 50ms | 200ms | 500ms | 2s | <0.5% / 30d |
| **Knowledge-base lookup** | 80ms | 300ms | 800ms | 3s | 1% / 30d |
| **Voice-profile match** | 30ms | 100ms | 300ms | 1s | <0.5% / 30d |
| **Message-body composer** (LLM) | 1.2s | 4s | 10s | 30s | 1% / 30d |
| **Validator pass** | 60ms | 200ms | 500ms | 2s | <0.5% / 30d |
| **End-to-end (full hop chain)** | 3s | 8s | 20s | 60s (gate) | 2% / 30d |

## Service Level Objectives — Control Plane

| Dimension | Target |
|---|---|
| **Retry success rate** (transient failure → success) | ≥ 92% |
| **Per-hop circuit-breaker trip rate** | ≤ 0.5% / 30d |
| **HITL escalation rate** (low-confidence path → human) | ≤ 8% of runs |
| **Determinism digest match rate** (replay verifies) | ≥ 99.5% |

## Cost Ceiling

| Workload | Per-call (USD) | Per-day budget |
|---|---:|---:|
| Message-body composer LLM (default Qwen) | $0.0016 | $40 |
| Voice-profile match (deterministic) | $0 | $0 |
| Knowledge-base lookup (cached) | $0.00005 | $1 |
| Total ceiling | — | **$60/day**, alert at 80% |

## Freshness

- **Voice profile** must be ≤ 30 days old or hop chain refuses.
- **Knowledge base** must be ≤ 7 days old; staleness fires `gate_violations=["KB_STALE"]`.
- **Sender corpus** weekly refresh.

## Failure Modes (top-3 — see RUNBOOK.md for response)

1. **Hop chain stalls at message-body composer (>30s)** → cancel run, emit `gate_violations=["LLM_HOP_TIMEOUT"]`, increment retry counter; on retry exhaustion → HITL escalation.
2. **Determinism digest mismatch on replay** → freeze the run, capture full state, alert; never auto-recover (data integrity > availability).
3. **Validator chain emits >2 violations on the same hop** → escalate to HITL; do NOT auto-modify the message body.

## Architectural Differentiation

apps_lic is the only in-portfolio app with:
- **A formal hop registry** with per-stage SLOs and retry policy
- **HITL fallback** wired into the validator chain (not just into L5 runtime)
- **Determinism digests** for full replay parity

These are the "what's hard about this domain" elements that distinguish it from apps_exec / apps_research / apps_rfp.

## Out of Scope (for THIS app's SLO)

- Outbound delivery infrastructure (post-render)
- A/B testing of voice profiles (W4 stretch)
- Reply tracking / engagement loop

## How These Numbers Were Derived

- p50/p95 per-hop: instrumented locally with `apps_lic._telemetry` debug log dumps over 100 sample runs (2026-04 sample, NOT continuous measurement — see GAP-1).
- 60s end-to-end ceiling: matches user-perceived "is it done yet" boundary for batch composition workflows.
- Determinism ≥99.5%: derived from `emit_determinism_digest` replay tests (passing currently per `tests/test_determinism.py`).

## Measurement Plan (W4.3)

- OTEL span per-hop with `app=apps_lic`, `hop_id`, `stage`, `latency_ms`, `attempt`, `circuit_breaker_state`.
- Hop-chain aggregation under one parent `trace_id` to assert end-to-end p95.
- Determinism replay job nightly; verdict feeds Wave/Phase Convergence as a freshness signal.
