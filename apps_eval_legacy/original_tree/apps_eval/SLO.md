# SLO — apps_eval (Evaluation Lab)

> **Status:** TARGETS, not yet measured. Wave 4.3 (cost/latency telemetry rollup) closes the loop.
> **Owner:** see `CODEOWNERS`
> **Last reviewed:** 2026-04-29

## Service Level Objectives

| Dimension | p50 | p95 | p99 | Hard ceiling | Error budget |
|---|---:|---:|---:|---:|---:|
| **Single-scenario eval latency** | 800ms | 3.0s | 8.0s | 30s (gate) | 1% / 30d |
| **Suite of 50 scenarios** | 12s | 45s | 120s | 5min (gate) | 1% / 30d |
| **Regression-detection turnaround** (commit → verdict) | 90s | 4min | 10min | 30min | 2% / 30d |
| **HITL decision-quality engine call** | 200ms | 800ms | 2.0s | 10s | 1% / 30d |
| **Scorecard render → markdown** | 50ms | 200ms | 500ms | 2s | <0.5% / 30d |

## Cost Ceiling

| Workload | Per-call (USD) | Per-day budget |
|---|---:|---:|
| Local Qwen 2.5 inference (default judge) | $0.0008 | $30 |
| External LLM judge (sanity-check, ≤5% sample) | $0.012 | $5 |
| Total ceiling | — | **$50/day**, alert at 80% |

## Freshness

- **Eval baselines** must be ≤ 30 days old or judge must abstain (constitutional §promote-only-on-fresh-baseline).
- **Test fixture corpus** rebaseline cadence: weekly.
- **Regression baseline retention:** 90 days (rolling), then archived.

## Failure Modes (top-3 — see RUNBOOK.md for response)

1. **Judge model unavailable** (Qwen down) → degrade to deterministic-only scenarios; skip LLM-judged dimensions; mark `verdict=DEGRADED`.
2. **Regression false-positive storm** (>10 verdict=REGRESSION in one suite) → halt promotion gate; alert; manual review required.
3. **Scorecard latency >2s** → indicates deserialization stall; check `scorecard_engine.py` artifact-cache hit rate.

## Out of Scope (for THIS app's SLO)

- LLM model latency itself (owned by `agentic_core/L3_orchestration/inference/`)
- ADG snapshot freshness (owned by `tools/generate_full_adg.py`)
- Promotion gate Wilson-CI thresholds (owned by `agentic_core/L6_observability/promotion_gates.py`)

## How These Numbers Were Derived

- p50/p95: deterministic scenarios → CPU-bound JSON-schema validation (~50–200ms baseline) + judge call latency band from `BaseEvalEngine.evaluate_with_qwen` typical ~600ms warm-path.
- Error budget: matches the 1%/30d SLO floor used by `agentic_core/L6_observability/promotion_gates.py` for promotion-eligible signals.
- Cost: $0.0008/call from observed Qwen 2.5 7B local inference (~1.5K tokens × 0.5¢/1K tokens local-amortized).

## Measurement Plan (W4.3)

- Per-call OTEL span with `app=apps_eval`, `dimension`, `latency_ms`, `judge_model`, `tokens`, `usd_estimate`.
- Daily rollup: `ops_scripts/calibration/apps_eval_slo_rollup.py` (TODO W4.3).
- Weekly delta vs. SLO posted to Notion ADR Registry as a measurement-debt entry.
