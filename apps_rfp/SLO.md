# SLO — apps_rfp (AI Proposal / RFP Generator)

> **Status:** TARGETS, not yet measured. Wave 4.3 (cost/latency telemetry rollup) closes the loop.
> **Owner:** see `CODEOWNERS`
> **Last reviewed:** 2026-04-29

## Architecture Note

apps_rfp generates competitive proposals. Its SLOs prioritize **bid-window deadlines** over sub-minute latency: a proposal must be ready an hour before deadline, every time, even if a single run takes 20 minutes.

## Service Level Objectives

| Dimension | p50 | p95 | p99 | Hard ceiling | Error budget |
|---|---:|---:|---:|---:|---:|
| **Proposal assembly (full)** | 45s | 3min | 8min | 20min (gate) | 2% / 30d |
| **RFP ingestion + parse** | 5s | 20s | 60s | 120s | 1% / 30d |
| **Proposal-retrieval (similar past bids)** | 300ms | 1.5s | 5s | 15s | 1% / 30d |
| **Risk-item generation** | 2s | 8s | 20s | 60s | 1% / 30d |
| **Section-by-section assembly** | 4s | 15s | 35s | 90s | 1% / 30d |

## Bid-Quality SLOs

| Dimension | Target |
|---|---|
| **Pricing-bound coverage** (bid stays within configured $ envelope) | 100% (gate, not target) |
| **Scope-creep detection** (added line items vs. RFP scope) | 100% flagged |
| **Win-rate vs. baseline** (regression detector against historical bids) | ≥ 0.85× baseline |
| **Section completeness** (every required RFP section addressed) | 100% (gate, not target) |

## Cost Ceiling

| Workload | Per-call (USD) | Per-day budget |
|---|---:|---:|
| Proposal assembly (multi-call, ~25K tokens) | $0.020 | $40 |
| Retrieval (cached, vector DB) | $0.0001 | $0.50 |
| Risk-item generation | $0.0024 | $5 |
| Total ceiling | — | **$60/day**, alert at 80% |

## Freshness

- **Win-rate baseline** rebuilt monthly from historical proposal outcomes.
- **Pricing reference data** must be ≤ 7 days old; staler triggers `gate_violations=["PRICING_STALE"]`.
- **Competitor intelligence** (if used) ≤ 30 days.

## Failure Modes (top-3 — see RUNBOOK.md for response)

1. **Pricing-bound violation** → REFUSE to render, emit `gate_violations=["PRICING_OUT_OF_BOUNDS"]`. Pricing is the one thing that cannot be silently corrected post-render.
2. **Section-completeness check fails** (missing required section) → render with explicit "MISSING SECTION" placeholder; do NOT silently omit. Auditable.
3. **Win-rate regression detector flags >0.15 drop** → halt promotion, alert; manual review of the assembly engine before further bids.

## Architectural Differentiation

apps_rfp is the only in-portfolio app with:
- **Pricing-bound enforcement** as a hard gate (not just a warning)
- **Win-rate-anchored regression** evaluation (not just structural quality)
- **Scope-creep detection** comparing rendered scope to ingested RFP scope

These are **W2.1 contract-test seed targets** — each must have a passing test by end of W2.

## Out of Scope (for THIS app's SLO)

- Bid submission / portal integration
- Contract negotiation post-award
- Compliance review of legal terms (separate workflow)

## How These Numbers Were Derived

- p50/p95: 5–8 section proposal × 4–6s/section ≈ 30–60s warm; outliers at p99 driven by retrieval cold-cache.
- 20min hard ceiling: typical bid window pre-deadline buffer.
- Win-rate target 0.85× — derived from 2025-2026 historical proposals; below this implies a regression worth pausing.

## Measurement Plan (W4.3)

- OTEL span per-section + per-pricing-check with `app=apps_rfp`, `section_id`, `pricing_within_bound` (bool), `scope_drift_score`.
- Win-rate rollup nightly; weekly delta posted to Notion ADR Registry.
- Pricing audit log preserved indefinitely (financial auditability).
