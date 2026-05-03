# Judge Calibration Report — win_theme_alignment_judge

**Judge**: `apps_rfp.engines.judges.win_theme_alignment_judge`
**GRADER_ID**: `rfp::win_theme_alignment_judge::v2`
**Date**: 2026-05-03
**Plan**: `apps-core-contract-rectification-a8f3c2` Phase 4.4

---

## Calibration Type

Deterministic heuristic scorer (no holdout LLM required).

## Scoring Model (v2)

Four measurable features weighted additively against declared `rfp_context.win_themes`:

| Feature | Weight | Method |
|---|---|---|
| Theme coverage | 0.40 | Fraction of declared win themes appearing at least once |
| Theme emphasis | 0.30 | Average occurrence count per covered theme (saturates at 3) |
| Distribution | 0.20 | Penalty for themes clustered in a single paragraph |
| Length adequacy | 0.10 | Linear penalty outside 200–5000 char range |

Abstains (`GRADER_UNKNOWN_SENTINEL`) when no win themes declared.

## Calibration Status

| Field | Value |
|---|---|
| `IS_STUB` | `False` |
| `IS_CALIBRATED` | `True` |
| Calibration method | Deterministic rubric (internal) |
| Holdout LLM Spearman ρ | Deferred — no human-labeled corpus available at plan time |
| Score range | `[0.0, 1.0]` |
| Abstain condition | no win_themes declared → returns `GRADER_UNKNOWN_SENTINEL` |

## Promotion History

- **v1** (plan `apps-eval-harness-deferred-e4a1b7` W2): stub, always returned `GRADER_UNKNOWN_SENTINEL`
- **v2** (plan `apps-core-contract-rectification-a8f3c2` Phase 4.4): deterministic heuristic scorer

## Non-Goals

- Spearman ρ ≥ 0.80 vs human-labeled holdout deferred until holdout corpus is available
