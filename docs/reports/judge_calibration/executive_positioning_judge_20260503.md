# Judge Calibration Report — executive_positioning_judge

**Judge**: `apps_rg.engines.judges.executive_positioning_judge`
**GRADER_ID**: `rg::executive_positioning_judge::v2`
**Date**: 2026-05-03
**Plan**: `apps-core-contract-rectification-a8f3c2` Phase 4.1

---

## Calibration Type

Deterministic heuristic scorer (no holdout LLM required).

## Scoring Model (v2)

Four measurable features weighted additively:

| Feature | Weight | Method |
|---|---|---|
| Executive lexicon density | 0.35 | Fraction of exec-vocab terms in output text |
| Structural coherence | 0.25 | Presence of numbered lists, headings, or section markers |
| Action-orientation | 0.20 | Density of imperative/modal verbs |
| Length adequacy | 0.20 | Linear penalty outside 50–2000 char range |

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
- **v2** (plan `apps-core-contract-rectification-a8f3c2` Phase 4.1): deterministic heuristic scorer

## Non-Goals

- Spearman ρ ≥ 0.80 vs human-labeled holdout deferred until holdout corpus is available
- LLM-backed secondary scoring deferred (separate plan)
