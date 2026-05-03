# Judge Calibration Report — response_likelihood_judge

**Judge**: `apps_lic.engines.judges.response_likelihood_judge`
**GRADER_ID**: `lic::response_likelihood_judge::v2`
**Date**: 2026-05-03
**Plan**: `apps-core-contract-rectification-a8f3c2` Phase 4.2

---

## Calibration Type

Deterministic heuristic scorer (no holdout LLM required).

## Scoring Model (v2)

Four measurable features weighted additively:

| Feature | Weight | Method |
|---|---|---|
| Personalization signals | 0.30 | Fraction of personalization tokens detected |
| Call-to-action presence | 0.25 | Detection of CTA verbs |
| Brevity | 0.25 | Optimal outreach length 80–300 words |
| Question presence | 0.20 | Ends with a question (engagement prompt) |

## Calibration Status

| Field | Value |
|---|---|
| `IS_STUB` | `False` |
| `IS_CALIBRATED` | `True` |
| Calibration method | Deterministic rubric (internal) |
| Holdout LLM Spearman ρ | Deferred — no human-labeled corpus available at plan time |
| Score range | `[0.0, 1.0]` |
| Abstain condition | `output["text"]` is empty → returns `GRADER_UNKNOWN_SENTINEL` |

## Promotion History

- **v1** (plan `apps-eval-harness-deferred-e4a1b7` W2): stub, always returned `GRADER_UNKNOWN_SENTINEL`
- **v2** (plan `apps-core-contract-rectification-a8f3c2` Phase 4.2): deterministic heuristic scorer

## Non-Goals

- Spearman ρ ≥ 0.80 vs human-labeled holdout deferred until holdout corpus is available
