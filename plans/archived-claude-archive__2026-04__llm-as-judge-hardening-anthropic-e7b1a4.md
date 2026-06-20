---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-04\\llm-as-judge-hardening-anthropic-e7b1a4.md'
original_relative_path: '_archive\\2026-04\\llm-as-judge-hardening-anthropic-e7b1a4.md'
source_sha256: 9f75c488469fb9db1a28fa4b636aecc630a97f1e55cd5349dafaf94b90bd1845
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: LLM-as-Judge Hardening — Anthropic Best Practice Alignment

- **Slug**: `llm-as-judge-hardening-anthropic-e7b1a4`
- **Tier**: T3 (cross-layer, L5 evaluation + L1 cognition + L6 observability)
- **Status**: Todo — backlog enhancement (do NOT implement yet)
- **Source**: [Anthropic — Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) and [Anthropic docs — Develop tests / grader prompt](https://docs.anthropic.com/fr/docs/build-with-claude/develop-tests)

## Current Implementation Review

**Files**:
- `@c:/Git/Agentic-Workflow/agentic_core/evaluation/judges/llm_judge.py` — main `GeminiJudge` + `NullJudge` + `JudgeScore`
- `@c:/Git/Agentic-Workflow/agentic_core/evaluation/judges/llm_judges.py` — secondary wrappers
- `@c:/Git/Agentic-Workflow/agentic_core/evaluation/judges/orchestrator.py` — judge orchestrator
- `@c:/Git/Agentic-Workflow/system_learning/confidence/llm_judge.py` — confidence-engine judge
- `@c:/Git/Agentic-Workflow/agentic_core/evaluation/judges/scorecard.py` — score aggregation

**What it does today** (`GeminiJudge.score`, llm_judge.py:289-305):
- Single prompt with single rubric (`_RUBRIC`, line 169) scoring **4 dimensions at once**: faithfulness, answer_relevancy, context_precision, groundedness
- Temperature=0.0 for determinism (good)
- Reasoning field is **trailing** (asked for after scores — weakens CoT)
- Parse-fail retry strips markdown fences once
- Single judge backend (Gemini only)
- Deterministic digest via SHA256 over canonical JSON (good)
- `NullJudge` deterministic stub for CI (good)

## Gap Analysis vs Anthropic Best Practice

| # | Anthropic Best Practice | Current State | Gap Severity |
|---|---|---|---|
| 1 | **Isolated LLM-as-judge per dimension** ("grade each dimension with an isolated LLM-as-judge rather than using one to grade all dimensions") | Single prompt grades 4 dimensions at once | **HIGH** |
| 2 | **Reasoning BEFORE score, then discard reasoning** ("Ask the LLM to think first before deciding a score, then discard the reasoning") | Reasoning requested after/alongside score | **HIGH** |
| 3 | **"Give the LLM a way out"** — allow `"Unknown"` / `"insufficient evidence"` response | No Unknown escape; forced 1-5 integer | **HIGH** |
| 4 | **Human-expert calibration** — close alignment with human graders + inter-annotator agreement | No calibration dataset; no IAA tracking | **HIGH** |
| 5 | **Multi-judge consensus** — ensemble across judges to reduce single-model bias | Single judge, single model | **MEDIUM** |
| 6 | **Pairwise comparison** mode (A-vs-B) as a grader type | Not available | **MEDIUM** |
| 7 | **Reference-based evaluation** when gold answer exists | Not available | **MEDIUM** |
| 8 | **Bias mitigation** — position bias, verbosity bias, self-enhancement bias | None | **MEDIUM** |
| 9 | **Capability vs. Regression eval separation** | No taxonomy | **MEDIUM** |
| 10 | **Partial credit** for multi-component tasks | Scores are scalar 1-5 only | **MEDIUM** |
| 11 | **Grader-resistance-to-hacks** (agent cannot game the eval) | Not tested | **MEDIUM** |
| 12 | **Isolated environment per trial** ("start from clean environment") | Not enforced for judge invocations | **LOW** |
| 13 | **Structured rubric with scoring anchors** (what 1 vs 3 vs 5 means per dimension) | Only one-line rubric per dimension | **MEDIUM** |
| 14 | **Multiple backend judges** (Claude-native + Gemini + local) for diversity | Gemini only | **MEDIUM** |
| 15 | **Drift detection** — grader output distribution drift over time | Not tracked | **LOW** |

## Goal

Ship a hardened LLM-as-Judge harness that mirrors Anthropic-recommended structure:

1. **Per-dimension isolated judges** — one judge call per dimension, each with its own structured rubric.
2. **CoT-first, score-second** — rubric asks LLM to reason first, then produce final score; reasoning is stored but not used for downstream math.
3. **Unknown escape hatch** — every judge may return `"Unknown"` / `NaN` with reason code; scorecard aggregator handles explicit unknowns rather than hallucinated numbers.
4. **Calibration pipeline** — gold-standard dataset, human-expert labels, inter-annotator-agreement (Cohen's κ / Krippendorff's α) tracking, grader-drift alerts.
5. **Multi-judge consensus + ensemble** — N judges (Claude + Gemini + null sentinel) with quorum aggregation.
6. **Pairwise + reference-based + rubric-based modes** — protocol-level judge types.
7. **Bias mitigation** — position-swap for pairwise, length-normalization, judge-identity masking.
8. **Capability vs Regression taxonomy** — each judge emits a tag; scorecard distinguishes hill-climb vs backsliding signals.
9. **Claude-native backend** — add `ClaudeJudge` alongside `GeminiJudge` for diversity and Anthropic alignment.

## Scope

| In Scope | Out of Scope |
|---|---|
| Refactor of `agentic_core/evaluation/judges/` | Test harness for `system_learning/confidence/*` (separate plan) |
| `ClaudeJudge` (Anthropic SDK) + `GeminiJudge` + `NullJudge` | Training a custom reward model |
| Per-dimension isolated judges + rubric bank (`config/judges/rubrics.yaml`) | Human-annotation tooling UI (deferred) |
| Pairwise + reference-based + rubric-based judge protocols | Crowdsourced grading pipeline |
| Calibration dataset + IAA tracking + drift monitors | Live A/B testing of judges in production |
| Multi-judge consensus aggregator | |

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| W1 | ENH5.1 | ADG + review audit + gap register (this plan's review) | 3000 | Todo | Evidence report at `docs/reports/plans/llm-judge-audit.md` with ranked gaps |
| W2 | ENH5.2 | Per-dimension rubric bank + CoT-first prompt template + Unknown escape | 4000 | Todo | `config/judges/rubrics.yaml` + template; `JudgeScore` gains `unknown_reasons: dict[dim, str\|None]` |
| W3 | ENH5.3 | `ClaudeJudge` backend (Anthropic SDK) + multi-judge consensus aggregator | 5000 | Todo | `ClaudeJudge` passes parity tests vs `GeminiJudge`; consensus aggregator with quorum + disagreement emission |
| W4 | ENH5.4 | Pairwise + reference-based judge protocols + bias mitigation (position swap, length norm) | 4000 | Todo | `PairwiseJudge`, `ReferenceJudge` protocols; position-swap variance test passes |
| W5 | ENH5.5 | Calibration dataset + IAA tracking + drift monitors | 3000 | Todo | Gold-set of ≥50 items with 2+ human annotators; Cohen's κ report; OTel drift spans |
| W6 | ENH5.6 | Capability-vs-regression taxonomy + ADR + migration guide | 2000 | Todo | ADR drafted; existing callsites migrated to per-dim judges; regression gate wired |

## Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| ENH5.1 | Audit + gap register | `agentic_core/evaluation/judges/**`, `system_learning/confidence/llm_judge.py` | Multiple judge implementations — consolidation risk | 3000 | Todo |
| ENH5.2 | Rubric bank + CoT-first + Unknown | `config/judges/`, `agentic_core/evaluation/judges/` | Rubric anchor calibration is subjective | 4000 | Todo |
| ENH5.3 | ClaudeJudge + consensus | `agentic_core/evaluation/judges/`, `infrastructure/sdks_mcps/` | Anthropic SDK dependency; quorum policy design | 5000 | Todo |
| ENH5.4 | Pairwise + reference + bias mitigation | `agentic_core/evaluation/judges/` | Position-swap doubles inference cost | 4000 | Todo |
| ENH5.5 | Calibration + IAA + drift | `data/judge_calibration/` (new), `agentic_core/L6_observability/` | Requires human-annotated gold set | 3000 | Todo |
| ENH5.6 | Capability/regression + ADR | `docs/architecture/adr/`, migration of callsites | — | 2000 | Todo |

## Concrete Design Decisions (Author-Gate during W2)

1. **Score scale**: keep 1–5 integer vs move to 0.0–1.0 float per dimension. Recommendation: float with discrete anchor values (0.0, 0.25, 0.5, 0.75, 1.0); Unknown = NaN.
2. **Unknown semantics**: is a dimension returning Unknown a **fail**, **abstention**, or **neutral**? Recommendation: abstention — scorecard tracks `unknown_rate` per judge as a quality signal.
3. **Consensus aggregation**: mean / median / majority-vote / trimmed-mean. Recommendation: trimmed-mean (drop top and bottom) + disagreement flag when range > 0.3.
4. **Claude model selection** for `ClaudeJudge`: claude-sonnet-4-5 vs claude-opus-4-5. Recommendation: sonnet-4-5 default, opus-4-5 override via env.
5. **Reasoning storage**: store-and-discard (Anthropic recommended for grading accuracy) vs store-and-audit. Recommendation: store for audit, **do not** feed into score math.
6. **Position-swap policy**: always-swap (2× cost) vs swap-on-disagreement vs never. Recommendation: swap-on-disagreement (cheap bias check).

Each of the 6 decisions above emits an Author-Gate packet during W2/W3 — not pre-committed.

## Dependencies

- **ENH1** (`cot-reflexion-self-consistency-config-7a3f1c`) — judge CoT prompts consume the complexity→reasoning-strategy resolver.
- **ENH2** (`prompt-assembly-few-shot-exemplars-9c4e2b`) — per-dimension rubrics slot in exemplars from the golden-context bank.
- **ADR-023** (runtime HITL exit control) — high-disagreement consensus outputs escalate via runtime-HITL.

## ADG_HOTSPOT_REPORT (to be filled in ENH5.1)

| Callsite | Layer | Archetype | Fan-in | Surface | Impact |
|---|---|---|---|---|---|
| TBD — `GeminiJudge.score` | L5 | SAFETY_GATEKEEPER | TBD | Security | TBD |
| TBD — `llm_judges.orchestrator` | L5 | ORCHESTRATOR | TBD | Security | TBD |
| TBD — `system_learning/confidence/llm_judge.py` | L1 | STATE_NODE | TBD | State | TBD |

## ADG_GRAPH_LAYER_EVIDENCE (to be filled in ENH5.1)

- **MVs**: `mv_hotspot_centrality`, `mv_graph_reverse_dependency_hotspots`, `mv_exemptions_near_critical_paths`
- **Semantic edges**: `calls`, `flows_to`, `emits_side_effect`
- **P-views**: L5 safety P-views, L1 cognition P-views

## Risks

| Risk | Mitigation |
|---|---|
| Per-dimension judges multiply inference cost ~4× | Start with high-value dimensions; cache judge outputs by (query, context, answer) hash |
| Multi-judge consensus doubles cost again | Make consensus opt-in via capability/regression tag; regression suite uses single judge |
| Gold-standard dataset creation is slow | Start with 50 items; grow incrementally; reuse ADR-023 HITL packets as seed |
| Judge drift detected but no remediation path | Drift alert → re-calibration workflow; part of ENH5.5 |
| Anthropic SDK token/cost overruns | Per-judge budget in `config/judges/budget.yaml`; circuit breaker on cost |

## Non-Goals

- Replacing judges with fine-tuned reward models (separate R&D effort)
- Crowdsourced annotation platform UI
- Production A/B shadow deployment of new judges (post-hardening plan)

## Deferred Items (for ENH5.6 register)

1. Fine-tuned reward model for high-volume dimensions
2. Self-consistency voting across N samples of the same judge (ties into ENH1)
3. Judge explanation quality evaluation (meta-judging)
4. Auto-rubric refinement from human annotator disagreement patterns
5. Cross-lingual judge calibration
