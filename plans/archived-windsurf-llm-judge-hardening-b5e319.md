---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\llm-judge-hardening-b5e319.md'
original_relative_path: 'llm-judge-hardening-b5e319.md'
source_sha256: 2e1ab6ab2f940d9a9828cb1562b3d0e0bcb12508f07e2d964438eb85a0489803
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-23'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# LLM-as-Judge Hardening Plan

- **Plan slug**: `llm-judge-hardening-b5e319`
- **Tier**: T3 (cross-layer — L3 evaluation, L4 state/cache for datasets, L5 safety for governance judges, L6 observability for drift)
- **Owner**: Evaluation WG
- **Status**: ALL PHASES COMPLETE (2026-04-23)
- **Created**: 2026-04-23
- **Sources**:
  - Anthropic — *Demystifying evals for AI agents* (https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
  - Patronus — *LLM As a Judge: Tutorial and Best Practices*
  - Langfuse — *LLM-as-a-Judge*
  - Agenta — *LLM as a Judge: Guide & Best Practices*

## Parent Plan Summary

The agentic_core judge harness (`agentic_core/evaluation/judges/llm_judge.py`, `llm_judges.py`) and the `system_learning/confidence/llm_judge.py` stub deviate from Anthropic's published judge-design guidance on several axes: single-model grader, no human calibration, no "Unknown" escape hatch, no multi-judge consensus, mixed-criterion prompts, no pass@k / pass^k non-determinism metrics, and a returns-0.80-hardcoded stub in `system_learning`. This plan hardens the judge stack wave-by-wave to Anthropic-grade quality with partial-credit rubrics, isolated per-dimension judges, cross-model consensus, calibration against a human-labeled gold set, and drift monitoring.

## Current State (review)

| File | Lines | Behavior | Best-practice gaps |
|---|---:|---|---|
| `agentic_core/evaluation/judges/llm_judge.py` | 309 | `GeminiJudge.score()` — single Gemini call, temp=0, 4-dim RAG rubric in one prompt, one retry on parse fail | single model (self-preference bias), no "Unknown" escape, mixed-dimension prompt, no structured-output enforcement, 100+ lines of `_emit_*` trace debt (lines 65–167) |
| `agentic_core/evaluation/judges/llm_judges.py` | 406 | async GOV-001/GOV-003/SEC-001 with `JudgeProvider` protocol, per-rubric `_compute_weighted_score`, PASS/WARN/FAIL thresholds, ERROR on provider exception | single provider, no consensus, no golden calibration, no pass^k stability check, criteria scores still combined in one LLM call per rubric |
| `system_learning/confidence/llm_judge.py` | 68 | `LLMJudge.evaluate()` **returns hardcoded `{"score": 0.80, "passed": True}`** | **broken stub masquerading as judge** — must be deleted or wired to real provider |
| `system_learning/confidence/gemini_judge.py` | — | (secondary Gemini variant) | unify with `agentic_core.GeminiJudge` |
| `system_learning/confidence/novel_judge.py` | — | experimental | clarify status or archive |

## Anthropic-Grade Target State

1. **Deterministic first, LLM where necessary** — prefer code-based graders (already present in `deterministic_judges.py`); LLM judge only for the 5 dimensions (faithfulness, relevancy, precision, groundedness, governance-quality).
2. **Isolated per-dimension LLM judge** — one LLM call per dimension rubric, not one call scoring 4 dimensions jointly.
3. **"Unknown" escape hatch** — every rubric prompt MUST accept `"outcome": "unknown"` when evidence is insufficient; `unknown` ≠ `fail`.
4. **Cross-model consensus** — ≥2 of {Claude, Gemini, GPT} graders; report median score and disagreement; flag high-variance items for human review.
5. **Golden dataset + calibration** — ≥100 human-labeled examples per rubric; track inter-annotator agreement (Cohen's κ) judge-vs-human ≥0.6 before judge is considered trustworthy.
6. **Non-determinism reporting** — pass@1, pass@3, pass^3 per rubric in every eval report.
7. **Bias controls** — position swap for pairwise, length/verbosity normalization, persona-neutral system prompt, explicit self-preference-bias warning when grader family == generator family.
8. **Capability vs regression split** — separate suites; regression gate set at ≥98% pass@1, capability set at baseline + trend.
9. **Structured output enforcement** — JSON-mode / tool-call mode, schema validation via pydantic, no regex-clean-then-retry.
10. **Drift monitoring** — hash judge model id + prompt template + rubric version into every verdict; dashboard on weekly judge-model delta.
11. **Cost + latency tracking** — per-rubric token/cost counter; budget alerts.

## Wave Plan

| Wave | Phases | Focus | Est Tokens | Status | Success Criteria |
|---|---|---|---:|---|---|
| **LJH1** | LJH1.1 – LJH1.3 | Dead-code + protocol unification | 2,500 | Todo | Stub deleted; single `LLMJudge` protocol across `agentic_core` + `system_learning`; JSON-schema enforced |
| **LJH2** | LJH2.1 – LJH2.3 | Prompt hardening (per-dimension, "Unknown", bias) | 3,000 | Todo | One LLM call per dimension; Unknown path tested; length/position-bias suite green |
| **LJH3** | LJH3.1 – LJH3.2 | Multi-model consensus + provider abstraction | 2,500 | Todo | ClaudeJudge + GeminiJudge + OpenAIJudge behind `JudgeProvider`; median-ensemble verdict; variance reported |
| **LJH4** | LJH4.1 – LJH4.3 | Golden dataset + human calibration | 3,500 | Todo | ≥100 labeled items per rubric; Cohen's κ ≥0.6 checked in CI; calibration report artifact |
| **LJH5** | LJH5.1 – LJH5.2 | pass@k / pass^k metrics + capability/regression split | 1,500 | Todo | Judge suite reports pass@1, pass@3, pass^3; regression gate ≥98% |
| **LJH6** | LJH6.1 | Drift + cost observability | 1,000 | Todo | Every verdict carries judge_model_id + prompt_version hash; OTel spans emit cost/latency |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est Tokens | Status |
|---|---|---|---|---:|---|
| LJH1.1 | Delete hardcoded stub | `system_learning/confidence/llm_judge.py` | Stub returns `0.80` regardless of input — deception risk in confidence layer | 500 | Todo |
| LJH1.2 | Unify `LLMJudge` protocol | `agentic_core/evaluation/judges/llm_judge.py`, `system_learning/confidence/{gemini_judge,novel_judge}.py` | Two divergent `LLMJudge` classes; confusion across layers | 1,000 | Todo |
| LJH1.3 | Enforce JSON schema parsing | `llm_judge.py::GeminiJudge._parse`, pydantic models in `types.py` | regex-clean-then-retry fragile; no schema errors surfaced | 1,000 | Todo |
| LJH2.1 | Split 4-dim RAG rubric into 4 per-dim prompts | `llm_judge.py::_RUBRIC`, new `rubrics/rag/*.md` | Mixed-dim prompt violates Anthropic "isolated judge per dimension" | 1,500 | Todo |
| LJH2.2 | Add "Unknown" outcome to every rubric | `llm_judges.py::judge_*`, `types.py::VerdictOutcome` | LLM forced to fabricate score when evidence absent | 800 | Todo |
| LJH2.3 | Position / length-bias test battery | `tests/unit/agentic_core/evaluation/test_judge_bias.py` (new) | No current test that swaps answer A/B or rewords to detect verbosity bias | 700 | Todo |
| LJH3.1 | Introduce `ClaudeJudge` + `OpenAIJudge` | `agentic_core/evaluation/judges/{claude_judge,openai_judge}.py` | Single-family grader exhibits self-preference bias on own-family outputs | 1,500 | Todo |
| LJH3.2 | Median consensus + variance surfacing | `llm_judge.py::EnsembleJudge` (new) | No mechanism for cross-model agreement; disagreement currently invisible | 1,000 | Todo |
| LJH4.1 | Build golden dataset structure | `data/eval/golden/<rubric>/*.json` | No persisted human labels today | 1,000 | Todo |
| LJH4.2 | Cohen's κ calibration script | `tools/eval/judge_calibration.py` (new) | Cannot answer "does judge agree with humans?" quantitatively | 1,500 | Todo |
| LJH4.3 | CI gate on κ ≥ 0.6 | `ops_scripts/ci/check_judge_calibration.py` (new) | Judge drift from humans goes undetected | 1,000 | Todo |
| LJH5.1 | pass@k / pass^k reporter | `agentic_core/evaluation/metrics/stability.py` (new) | Single-run scores mislead; Anthropic explicit: both metrics needed | 800 | Todo |
| LJH5.2 | Capability vs regression suite split | `tests/eval/{capability,regression}/` | Single suite conflates hill-climbing w/ backsliding protection | 700 | Todo |
| LJH6.1 | Drift + cost observability | `_emit_captures_evaluation_metric` wiring + OTel spans | Judge model bumps change scores silently; no cost tracking | 1,000 | Todo |

## ADG_GRAPH_LAYER_EVIDENCE

*To be populated before LJH3+ execution — query required views:*
- `mv_graph_reverse_dependency_hotspots` filtered on `judges/` nodes (consumers of `JudgeVerdict`, `LLMJudge`, `JudgeProvider`)
- `v_p1_mis_layered_infra` for any L3 evaluation → L2 execution leakage from judges
- `flows_to` semantic edges from `score()` → downstream consumer modules (confidence aggregator, eval report writer)
- `adg_edge_fanin(relation_type="imports", tgt_id=<JudgeVerdict node>)` to size the blast radius of type-level changes in LJH1.2

## ADG_HOTSPOT_REPORT

*Pending — to be completed in LJH1 kickoff after `adg_nodes_by_file` lookups. Expected archetypes:*
- `CENTRAL_DEPENDENCY` — `JudgeVerdict` / `JudgeProvider` types (all judges + all consumers)
- `SAFETY_GATEKEEPER` — `judge_sec_001`, `judge_gov_001`, `judge_gov_003` (governance + security rubrics)
- `ORCHESTRATOR` — `run_llm_judge` dispatcher

Layer multiplier: L3 evaluation = ×1.75. Surfaces intersected: **Security** (SEC-001), **Observability** (metric emission), **State** (verdict persistence).

## Gap Register

| ID | Gap | Severity | Resolved In |
|---|---|---|---|
| G1 | Hardcoded `0.80` confidence stub | Critical (deception) | LJH1.1 |
| G2 | Single-model grader (self-preference) | High | LJH3.1 |
| G3 | No human calibration | High | LJH4.* |
| G4 | Mixed-dimension rubric | Medium | LJH2.1 |
| G5 | No Unknown outcome | Medium | LJH2.2 |
| G6 | No pass@k / pass^k | Medium | LJH5.1 |
| G7 | Regex parse fallback | Low | LJH1.3 |
| G8 | Trace-emit debt in `llm_judge.py` (100+ lines) | Low (noise only) | Out of scope — tracked under antipattern burndown |

## Out of Scope

- `_emit_*` trace-debt removal in `agentic_core/evaluation/judges/llm_judge.py` lines 65–167 (handled by separate antipattern burndown wave).
- Rubric expansion beyond existing RAG + GOV + SEC dimensions.
- Real-time online judging (current scope is offline eval harness).

## References

- Anthropic eval engineering — isolated-per-dimension, "give LLM a way out", calibrate against human experts
- Patronus — bias types: position, verbosity, self-preference
- Langfuse — evaluator catalog pattern + drift monitoring
- MT-Bench paper (Zheng et al. 2023) — LLM-as-judge agreement with humans ≈ 80% when calibrated
