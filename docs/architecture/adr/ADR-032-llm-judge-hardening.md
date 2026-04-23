# ADR-032 — LLM-as-Judge Hardening to Anthropic Best Practice

> **Renumber note (2026-04-23)**: originally drafted as ADR-031; renumbered to ADR-032 because ADR-031 was concurrently assigned to priority-scoring-operational-signals. Content unchanged.

- **Status**: Accepted (2026-04-23)
- **Deciders**: Plan owner
- **Related plan**: `.windsurf/plans/llm-as-judge-hardening-anthropic-e7b1a4.md`
- **Impact layers**: L1 (cognition), L5 (safety/evaluation), L6 (observability)
- **Source**: [Anthropic — Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), [Anthropic docs — Develop tests](https://docs.anthropic.com/fr/docs/build-with-claude/develop-tests)

## Context

The pre-existing LLM-as-Judge harness (`agentic_core/evaluation/judges/llm_judge.py`) grades a RAG answer on four dimensions — faithfulness, answer_relevancy, context_precision, groundedness — via a **single prompt** that returns four integers in the 1–5 range plus a short trailing reasoning. Backend was Gemini-only. No Unknown escape hatch. No multi-judge consensus. No calibration against human expert labels. No drift detection.

Anthropic's public engineering guidance for agent evals is specific on several of these gaps:

> *"create clear, structured rubrics to grade each dimension of a task, and then grade each dimension with an **isolated LLM-as-judge** rather than using one to grade all dimensions."* (— *Demystifying evals for AI agents*)
>
> *"Ask the LLM to **think first before deciding a score**, then discard the reasoning."* (— *Develop tests*)
>
> *"To avoid hallucinations, **give the LLM a way out**, like providing an instruction to return 'Unknown' when it doesn't have enough information."* (— *Demystifying evals for AI agents*)
>
> *"LLM-as-judge graders should be **closely calibrated with human experts** to gain confidence that there is little divergence between the human grading and model grading."* (— *Demystifying evals for AI agents*)

Judge output is safety-critical: the confidence engine and runtime-HITL gate (ADR-023) consume judge scores to decide whether to escalate, block, or allow runs. A judge that systematically over-scores is a silent safety failure.

## Decision

Land a hardened judge harness in one architectural change, preserving the existing `LLMJudge` / `JudgeScore` / `NullJudge` / `GeminiJudge` public API. New behaviour:

1. **Per-dimension isolated judges** — `GeminiJudge.score` issues **one prompt per dimension** against the rubric bank in `DIMENSION_RUBRICS`. `per_dimension=False` preserves the legacy single-prompt path for cost-sensitive callers.
2. **CoT-first, score-second** — every per-dimension prompt asks the model to reason inside `<reasoning>...</reasoning>` first, then emit a final `{"score": ..., "unknown_reason": ...}` JSON line. Reasoning is captured in `JudgeScore.per_dim_reasoning` but is **not** hashed into the deterministic digest.
3. **Unknown escape hatch** — judges may return `"score": "Unknown"`. `JudgeScore` stores these as `float('nan')` with an entry in `unknown_reasons`. The `JudgeScore.unknown_rate()` helper surfaces judge abstention as a first-class quality signal; downstream consensus excludes Unknowns from aggregation rather than imputing a value.
4. **Claude-native backend** — new `ClaudeJudge` in `agentic_core/evaluation/judges/claude_judge.py` mirrors `GeminiJudge`'s contract via the Anthropic SDK. Default model `claude-sonnet-4-5`, override via `CLAUDE_JUDGE_MODEL`.
5. **Multi-judge consensus** — new `ConsensusJudge` in `consensus.py` wraps N backends with trimmed-mean aggregation (drop min + max when N ≥ 3), per-dimension disagreement range, and flagged-dimension list for HITL escalation. Exposed both as `.grade()` (full `ConsensusResult`) and `.score()` (protocol-compatible `JudgeScore`).
6. **Pairwise + reference-based protocols** — `PairwiseJudge` with position-swap bias mitigation (swap-on-disagreement → TIE if position bias detected) and `ReferenceJudge` for gold-answer comparisons, both in `pairwise_reference.py`.
7. **Calibration pipeline** — `calibration.py` implements Cohen's κ and Krippendorff's α (ordinal scale with missing-value handling). `summarize_judge_vs_human` loads paired gold / judge jsonl files and emits a `JudgeCalibrationReport`. Gold-set scaffolding + schema at `data/judge_calibration/README.md`.
8. **Drift monitor** — `agentic_core/L6_observability/judge_drift.py` consumes the calibration report and emits `DriftEvent`s when κ/α fall below configurable floors (default 0.60) or when Unknown rate exceeds the dimension's `unknown_budget` in `config/judges/rubrics.yaml`.
9. **Rubric + budget SSOT** — `config/judges/rubrics.yaml` (scoring anchors, weights, thresholds, Unknown budget, consensus policy, capability-vs-regression taxonomy) and `config/judges/budget.yaml` (per-judge cost guards, circuit breaker).

## Author-Gate design decisions (resolved during implementation)

Six decisions the plan called out for Author-Gate were resolved as follows. Each is a default, not a lock — callers may override via kwargs.

| # | Decision | Default chosen | Rationale |
|---|---|---|---|
| 1 | Score scale | Integer 1–5 | Backward compat with existing `JudgeScore` consumers; anchors in `rubrics.yaml` keep grading reproducible. |
| 2 | Unknown semantics | Abstention | Per Anthropic: abstention is a signal, not a failure. Tracked as `unknown_rate`. |
| 3 | Consensus aggregation | Trimmed-mean (drop min + max when N ≥ 3) | Robust to a single-judge outlier without losing sensitivity. |
| 4 | Claude model | `claude-sonnet-4-5` default | Matches current Anthropic product tier; env override kept. |
| 5 | Reasoning storage | Store-and-audit, **not** fed into score math | Anthropic recommendation. `per_dim_reasoning` excluded from deterministic digest. |
| 6 | Position-swap policy | Swap-on-disagreement | Cheap bias check; only pays 2× cost when the verdict is non-TIE/non-Unknown. |

## Consequences

**Positive**:
- Judge quality bias/variance now observable via `unknown_rate`, disagreement range, Cohen's κ, Krippendorff's α, drift events.
- Position bias in pairwise comparisons can no longer silently set a winner.
- A future Claude vs Gemini vs Null ensemble run is a no-code-change configuration.
- Gold-set-vs-judge calibration is repeatable via stdlib-only `calibration.py`.

**Negative**:
- Per-dimension grading is roughly 4× the Gemini inference cost per item vs the legacy single-prompt mode. Mitigated by: `per_dimension=False` escape hatch, consensus-opt-in only for capability (not regression) evals, budget guard in `config/judges/budget.yaml`.
- Gold set requires human annotators. Seed of 3 items shipped in `data/judge_calibration/gold_set.jsonl`; production usage requires the ≥50-item gold set called out in the plan.

**Neutral / deferred**:
- Fine-tuned reward model, RL-from-HITL-feedback, self-consistency N-path voting inside a single judge, crowdsourced annotation UI — all remain deferred per plan ENH5.6 register.

## Compatibility

- `JudgeScore` gains two new optional fields (`unknown_reasons`, `per_dim_reasoning`) with tuple defaults. Existing positional calls to `JudgeScore.create(faithfulness, answer_relevancy, context_precision, groundedness, reasoning, judge_model)` still work.
- `GeminiJudge(gemini_client=None, model=None)` still works; the new `per_dimension` kwarg defaults to `True` — callers that need the legacy single-prompt shape must pass `per_dimension=False`.
- `NullJudge` is unchanged.
- Existing structured-judge system (`llm_judges.py`, `orchestrator.py`, `types.py`) is untouched by this ADR; the hardening applies to the RAG-style `llm_judge.py` harness. A follow-up plan will harmonise the two surfaces.

## Verification

- Unit tests at `tests/unit/agentic_core/evaluation/judges/test_llm_judge_hardened.py` cover: per-dimension scoring, Unknown escape, parse-error fallback, consensus trimmed-mean, consensus flagged dimensions, pairwise position-swap, reference-based grading, Cohen's κ, Krippendorff's α, drift detection below floor.
- Rubric SSOT + budget SSOT validated against schema at `config/judges/rubrics.yaml`.
- Drift monitor output is structured and OTel-emissible.
