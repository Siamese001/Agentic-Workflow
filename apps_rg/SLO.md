# SLO — apps_rg (AI Résumé Generator)

> **Status:** TARGETS, not yet measured. Per-engine cost telemetry pending.
> **Owner:** see `CODEOWNERS`
> **Last reviewed:** 2026-05-02

## Architecture Note

apps_rg generates targeted résumés. Its SLOs prioritize **fabrication-zero** and **ATS-coverage discipline** over sub-second latency: a résumé must be ATS-survivable and trustworthy, even if generation takes 2-3 minutes.

## Service Level Objectives

| Dimension | p50 | p95 | p99 | Hard ceiling | Error budget |
|---|---:|---:|---:|---:|---:|
| **Résumé generation (full)** | 30s | 90s | 3min | 5min (gate) | 2% / 30d |
| **Profile ingestion + parse** | 2s | 8s | 20s | 60s | 1% / 30d |
| **Achievement prioritization** | 4s | 15s | 35s | 90s | 1% / 30d |
| **ATS coverage check** | 200ms | 1s | 3s | 10s | 1% / 30d |
| **Per-section assembly** | 3s | 10s | 25s | 60s | 1% / 30d |

## Quality SLOs

| Dimension | Target |
|---|---|
| **Fabrication rate** (claims with no profile evidence) | **0** (gate, not target) |
| **ATS coverage** (keyword coverage vs target role) | ≥ 80% (gate, not target) |
| **Evidence density** (evidence-per-claim) | ≥ 1.0 |
| **Length compliance** (within page bounds for tier) | 100% (gate) |
| **Section completeness** (every required section addressed) | 100% (gate) |

## Cost Ceiling

| Workload | Per-call (USD) | Per-day budget |
|---|---:|---:|
| Résumé generation (multi-call, ~15K tokens) | $0.012 | $24 |
| Retrieval (candidate-history vector index) | $0.0001 | $0.30 |
| ATS keyword check (cached) | $0.0002 | $0.50 |
| Total ceiling | — | **$30/day**, alert at 80% |

## Freshness

- **Candidate profile** must be ≤ 30 days old at generation time; staler triggers `gate_violations=["PROFILE_STALE"]`.
- **ATS keyword corpora** rebuilt monthly per industry.
- **Industry-specific evaluator rubrics** rebuilt quarterly.

## Failure Modes (top-3 — see RUNBOOK.md for response)

1. **Fabrication violation** → REFUSE to render, emit `gate_violations=["FABRICATION:<claim>"]`. Fabrication is the one thing that cannot be silently corrected post-render.
2. **ATS coverage below 80%** → render with explicit `[ATS_GAP]` markers; do NOT auto-pad with fabricated keywords.
3. **Anti-overfitting flag (evidence density < 1.0)** → halt generation, flag for re-prioritization.

## Architectural Differentiation

apps_rg is the only in-portfolio app with:
- **Fabrication-zero enforcement** as a hard gate (not just a warning)
- **ATS-coverage gate** as a structural quality floor (not just an aesthetic)
- **Anti-overfitting evidence-density check** comparing claims-to-evidence ratio
- **52 specialist engines** for per-domain résumé component generation

## Out of Scope (for THIS app's SLO)

- Application portal submission
- Recruiter follow-up workflow
- Cover letter generation (separate workflow under apps_lic)

## How These Numbers Were Derived

- p50/p95: 5-section résumé × 4-6s/section ≈ 20-40s warm; outliers at p99 driven by retrieval cold-cache.
- 5min hard ceiling: typical interactive-tool patience window.
- ATS coverage 80% — derived from 2025-2026 successful-application historical data; below this implies high screening-rejection risk.

## Measurement Plan

- OTEL span per-section + per-fabrication-check with `app=apps_rg`, `section_id`, `fabrication_clean` (bool), `ats_coverage_pct`.
- ATS coverage rollup nightly; weekly delta in observability dashboard.
- Fabrication audit log preserved indefinitely (candidate-trust auditability).
