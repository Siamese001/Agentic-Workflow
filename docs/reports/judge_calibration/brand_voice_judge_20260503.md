# Judge Calibration Report — brand_voice_judge

**Judge**: `apps_lic.engines.judges.brand_voice_judge`
**GRADER_ID**: `lic::brand_voice_judge::v2`
**Date**: 2026-05-03
**Plan**: `apps-core-contract-rectification-a8f3c2` Phase 4.3

---

## Calibration Type

Deterministic heuristic scorer (no holdout LLM required).

## Scoring Model (v2)

Four measurable features weighted additively against an optional `brand_voice_profile`:

| Feature | Weight | Method |
|---|---|---|
| Preferred lexicon coverage | 0.30 | Fraction of preferred_lexicon terms present |
| Forbidden lexicon cleanliness | 0.30 | 1.0 iff none of forbidden_lexicon appear; linear penalty per hit |
| Register match | 0.25 | Formal/casual/neutral register detection vs declared register |
| Length variance | 0.15 | Sentence-length coefficient of variation (high variance = informal) |

Default professional-register heuristic applied when no `brand_voice_profile` provided.

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
- **v2** (plan `apps-core-contract-rectification-a8f3c2` Phase 4.3): deterministic heuristic scorer

## Non-Goals

- Spearman ρ ≥ 0.80 vs human-labeled holdout deferred until holdout corpus is available
