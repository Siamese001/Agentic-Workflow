---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\llm-judge-hardening-followups-f2c8e1.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\llm-judge-hardening-followups-f2c8e1.md'
source_sha256: 0d50877d8f509041a9b392ef6e30f3d662cb985942f5ffc38c42518366fd3852
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
> SUPERSEDED 2026-05-02 - Notion status flipped to Superseded. Burndown/backlog/followup/deferred framing retired in favor of ratcheting CI gates (where applicable) or absorption into successor plans. Daily-drift counts are stale by design and not plan-tracked. Kept on disk for archive only.

# Plan: LLM-as-Judge Hardening — Follow-Ups

- **Slug**: `llm-judge-hardening-followups-f2c8e1`
- **Tier**: T2 (scoped, L5 evaluation + L6 observability)
- **Status**: Todo — backlog
- **Parent**: `llm-as-judge-hardening-anthropic-e7b1a4` (ADR-031 landed 2026-04-23)
- **Parent Plan Summary**: ENH5 delivered per-dim judges, CoT-first + Unknown escape, ClaudeJudge, consensus with disagreement flagging, pairwise position-swap, reference-based grading, calibration (κ + α), drift monitor, rubric/budget SSOT, and 21 passing unit tests. This follow-up closes residual items explicitly deferred in ADR-031 §Deferred Items and §Consequences.

## Residual Items (from ADR-031 + implementation review)

| # | Item | Severity | Why Now |
|---|---|---|---|
| 1 | Populate gold set to ≥50 annotated items (seeded with 3) | **HIGH** | Calibration metrics are mathematically valid but statistically weak at n=3. |
| 2 | Migrate live callsites from combined rubric to per-dim judges | **HIGH** | Default behaviour already changed, but consumers via legacy `_score_legacy` still pay quality tax. |
| 3 | Wire `ConsensusResult.flagged_dimensions` to runtime-HITL escalation (ADR-023) | **HIGH** | High-disagreement judge output should trigger HITL escalation rather than silently aggregate. |
| 4 | Integration tests with real Gemini + Claude clients (behind env-gated pytest marker) | **MEDIUM** | Unit tests use stubs; need one live-backed smoke test per backend. |
| 5 | Self-consistency N-path voting inside a single judge | **MEDIUM** | Ties into ENH1 (CoT/ToT/Reflexion config); judge can sample N times at T=0 and vote. |
| 6 | Meta-judging (judge grades judge's reasoning quality) | **MEDIUM** | Detects shallow/superficial CoT that still lands on a plausible score. |
| 7 | Auto-rubric refinement from human annotator disagreement patterns | **LOW** | Anchors in `rubrics.yaml` are hand-authored; human disagreement signals where anchors need sharpening. |
| 8 | Cross-lingual judge calibration | **LOW** | All rubrics currently assume English query/context/answer. |
| 9 | Crowdsourced annotation UI | **LOW** | Operational concern; current scaffold supports jsonl hand-editing. |
| 10 | Production A/B shadow deployment of ClaudeJudge vs GeminiJudge | **MEDIUM** | Consensus aggregator is ready; needs a shadow-mode runner to collect comparison data. |

## Goal

Close items 1–4 in this plan's scope (highest severity). Items 5–10 are tracked as sub-waves with clear entry criteria but do not block plan closure.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| W1 | ENH5.7A | Gold-set expansion to ≥50 items (3 annotators per item target) | 4000 | Todo | `data/judge_calibration/gold_set.jsonl` ≥50 lines; Krippendorff's α between annotators ≥ 0.6 per dimension |
| W2 | ENH5.7B | Callsite migration inventory + retrofit | 3000 | Todo | ADG fan-in report of `GeminiJudge` consumers; all production callsites use `per_dimension=True` (default); `_score_legacy` marked deprecated with warning |
| W3 | ENH5.7C | Wire consensus disagreement to runtime-HITL | 3000 | Todo | `ConsensusResult.flagged_dimensions` escapes to ADR-023 runtime-HITL adapter; HITL packet carries the per-judge breakdown |
| W4 | ENH5.7D | Integration-test suite (live backends, env-gated) | 2000 | Todo | `tests/integration/evaluation/judges/test_live_backends.py` with `pytest.mark.live` marker; skipped by default; docs in README |
| W5 | ENH5.7E | Shadow A/B runner for ClaudeJudge vs GeminiJudge | 3000 | Todo | `tools/eval/judge_shadow_ab.py` emits per-item comparison rows to `data/judge_calibration/shadow_runs/`; weekly summary in Notion |

Items 5–9 held as sub-waves pending evidence from W1–W5.

## Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| ENH5.7A | Gold-set expansion | `data/judge_calibration/` | Human-annotator scheduling | 4000 | Todo |
| ENH5.7B | Callsite migration | All `GeminiJudge(...)` consumers | Multiple consumers; cost impact per-call | 3000 | Todo |
| ENH5.7C | HITL escalation wiring | `consensus.py`, `L5_safety/enforcement/hitl/**` | ADR-023 packet shape | 3000 | Todo |
| ENH5.7D | Live integration tests | `tests/integration/evaluation/judges/` | API cost guard | 2000 | Todo |
| ENH5.7E | Shadow A/B runner | `tools/eval/` | Storage layout for comparisons | 3000 | Todo |

## Dependencies

- **ADR-023** (runtime-HITL exit control) — for W3 escalation wiring
- **ENH1** (`cot-reflexion-self-consistency-config-7a3f1c`) — for item 5 (self-consistency N-paths inside a judge)
- **Item 3 (HITL wiring)** blocks nothing downstream; item 2 (callsite migration) blocks closure of ADR-031's stated deprecation path for `_score_legacy`.

## Risks

| Risk | Mitigation |
|---|---|
| Gold-set annotator disagreement signals a broken rubric, not judge failure | Use inter-annotator α < 0.6 as a signal to refine `rubrics.yaml` anchors before proceeding (item 7) |
| Migration of callsites triples inference cost | Budget guard in `config/judges/budget.yaml` already configured; monitor `per_eval_hard_limit_usd` breaches in OTel |
| HITL storm from noisy disagreement flag | Threshold in `rubrics.yaml:consensus.disagreement_threshold` tunable; start conservatively at 1.5, adjust based on data |

## ADG_GRAPH_LAYER_EVIDENCE (to be filled in ENH5.7A)

- MVs: `mv_hotspot_centrality`, `mv_graph_reverse_dependency_hotspots`
- Semantic edges: `calls`, `reads_from`
- P-views: L5 safety P-views
