# SLO — apps_research (Autonomous Research Engine)

> **Status:** TARGETS, not yet measured. Wave 4.3 (cost/latency telemetry rollup) closes the loop.
> **Owner:** see `CODEOWNERS`
> **Last reviewed:** 2026-04-29

## Architecture Note

apps_research is the deepest engine in the portfolio (`research_assembly_engine.py` = 32KB). Its SLOs reflect the reality that good research is **latency-tolerant but quality-sensitive** — users wait 30s gladly for cited, contradiction-aware output and reject 2s output that hallucinates.

## Service Level Objectives

| Dimension | p50 | p95 | p99 | Hard ceiling | Error budget |
|---|---:|---:|---:|---:|---:|
| **Single-topic research run** | 25s | 90s | 240s | 600s (gate) | 2% / 30d |
| **Source credibility validation** | 100ms | 400ms | 1.0s | 5s | 1% / 30d |
| **Section assembly call** | 4s | 15s | 35s | 90s | 1% / 30d |
| **Citation grounding pass** | 200ms | 800ms | 2.0s | 8s | 1% / 30d |
| **Contradiction-resolution pass** | 300ms | 1.0s | 3.0s | 10s | 1% / 30d |

## Quality SLOs (more important than latency)

| Dimension | Target |
|---|---|
| **Citation rate** (claims with at least 1 source) | ≥ 95% |
| **Source confidence ≥ 0.7** (per `SourceEntry.confidence`) | ≥ 80% of cited sources |
| **Contradiction detection** (when sources disagree, system flags it) | 100% (zero silent suppression) |
| **Hallucination rate** (manual audit, monthly) | ≤ 1% |

## Cost Ceiling

| Workload | Per-call (USD) | Per-day budget |
|---|---:|---:|
| Section assembly (multi-call, ~15K tokens total) | $0.012 | $60 |
| Source validation (deterministic + cached) | $0.0001 | $1 |
| Citation grounding (1 LLM call ~2K tokens) | $0.0016 | $8 |
| Total ceiling | — | **$80/day**, alert at 80% |

## Freshness

- **Cited sources** must include retrieval timestamp; sources >180 days old emit a freshness warning in the rendered output.
- **Contradiction-resolution policy** versioned; changes require ADR.

## Failure Modes (top-3 — see RUNBOOK.md for response)

1. **Citation rate drops below 95%** → halt render, emit `gate_violations=["LOW_CITATION_RATE"]`. Better to fail than ship uncited research.
2. **Sources contradict and resolution policy abstains** → render the contradiction explicitly in the output (do NOT silently pick a side). User decides.
3. **Section assembly stalls >90s** → kill the section, emit `gate_violations=["SECTION_TIMEOUT"]`, render partial output with explicit gap notice.

## Architectural Differentiation

apps_research is the only in-portfolio app with:
- **First-class contradiction handling** — sources that disagree are surfaced, not silenced
- **Per-claim provenance** (gap: only per-section today; per-claim is a NEXT_STEP)
- **Confidence-aware source registry** with bounded `[0,1]` confidence scores

## Out of Scope (for THIS app's SLO)

- Web crawling / source discovery beyond local SearXNG search
- Long-term knowledge persistence (handled by `vector_db` MCP)
- Translation / localization

## How These Numbers Were Derived

- p50/p95: typical 4–6 section research run = 4 × 4s assembly + ~5s grounding + ~2s overhead ≈ 25s warm.
- 600s hard ceiling: tolerant ceiling for "thorough research" workflow; users typically background the task and check back.
- Quality SLOs ground-truthed against `data/research_brief_*.md` historical outputs.

## Depth-Profile SLO Thresholds

Per-profile retrieval SLOs enforced by the C0 PA gate (`_evaluate_c0_pa_gate`).

| Profile | min_sources | min_citation_anchors | max_queries | gate_weak_floor | p99 ceiling |
|---|---:|---:|---:|---:|---:|
| COMPANY_BRIEF_LIGHT | 5 | 8 | 3 | 0.40 | 60s |
| COMPANY_BRIEF_STANDARD | 10 | 18 | 6 | 0.58 | 120s |
| COMPANY_BRIEF_DEEP | 18 | 30 | 10 | 0.60 | 180s |
| COMPANY_BRIEF_DOSSIER | 25 | 45 | 15 | 0.75 | 300s |
| **COMPANY_BRIEF_COMPETITIVE_SCAN** | **20** | **35** | **12** | **0.65** | **240s** |
| **COMPANY_BRIEF_FORENSIC** | **35** | **60** | **20** | **0.80** | **480s** |

> DS-5 W5 (`apps-research-deferred-scope-b7e3d2`): COMPETITIVE_SCAN targets competitive-intelligence use cases (market share, win/loss, competitive-landscape depth); FORENSIC targets regulatory due-diligence and legal-risk analysis. Both are background-task profiles; FORENSIC p99 ceiling is 480s (users background the run and check back).

### DOSSIER SLO Baseline (W3 — apps-research-spine-deferred-followup-9c3e1a)

- **Status:** TARGETS — first live run with `SEARXNG_BASE_URL` establishes concrete baseline.
- **Measurement:** `tests/e2e/test_apps_research_live.py::TestAppsResearchDossierLive` (skipped without `SEARXNG_BASE_URL`).
- **Artifacts:** Emitted to `artifacts/slo/apps_research_dossier_<run_id>.json` per live run.
- **Verified mocked (P3.1):** 25 stub URL sources → `gate_verdict` in {PASS, WEAK_WITH_CAVEATS}.

## Measurement Plan (W4.3)

- Per-section OTEL span with `app=apps_research`, `section_id`, `latency_ms`, `source_count`, `citation_count`, `contradiction_count`.
- Monthly hallucination audit (manual sample, 50 runs/month) tracked in `data/judge_calibration/`.
- Citation rate measured at render time; rolled up daily.
