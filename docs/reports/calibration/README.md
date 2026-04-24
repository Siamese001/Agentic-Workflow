# L0 Routing Calibration Reports (W0 baseline)

Plan: `.windsurf/plans/l0-routing-calibration-gap-audit-b3c9d4.md`
Generated: 2026-04-23 (W0 initial run)

## How to regenerate

```bash
python -m tools.calibration --all
```

## Baseline summary (shipped fixtures)

Five path fixtures, ~12–16 samples each. These are **seed** fixtures for
harness validation; production calibration requires ≥500 samples per path
per namespace from real traces (see plan §W0.P1 Assumptions A-1).

| Path  | Signal                       | Samples | Optimal threshold (max F1) | Current repo literal                 | Observation                                         |
|-------|------------------------------|--------:|---------------------------:|:--------------------------------------|:-----------------------------------------------------|
| R1A   | `freshness_ratio`            | 12      | 0.650                      | n/a — gate not implemented           | Plan §G1 confirmed: no R1A gate in code.            |
| R1B   | `cosine_similarity`          | 16      | 0.930                      | `similarity_threshold = 0.98`         | ~5pp too conservative on seed data; calibrate per-ns. |
| R3    | `grounding_need_prediction`  | 12      | 0.720                      | n/a — no prediction score emitted    | Matches Vertex default 0.7 within tolerance.        |
| R5    | `aggregate_confidence` (inv) | 13      | 0.490                      | `DEFAULT_ABSTAIN_THRESHOLD = 0.50`    | Essentially aligned on seed data.                    |
| C0    | `evidence_coverage`          | 11      | 0.620                      | n/a — coverage not scored            | Matches plan §C0.6 suggested 0.6 floor.             |

## Interpretation caveats

- **Small sample sizes.** Per-threshold confusion counts move sharply with
  small fixtures. These numbers are **harness smoke-test output**, not
  production thresholds. Do NOT flip the repo literal `0.98` to `0.93` on
  the basis of 16 samples.
- **Vertex objective** (`vertex_default`) surfaces the 0.7 fixed threshold
  point for R1B/R3/R5 so we can see what Vertex's default would do on each
  path's signal. Not directly applicable to R1A/C0.
- **R5 uses `invert_score=true`.** A low score means "abstain." The harness
  inverts the comparison automatically; thresholds reported for R5 are on
  the same [0,1] axis but fire when the observed score is at or BELOW
  threshold.

## Deferred scope

W1 / W1b / W2 / W3 / W4 remain deferred per plan §Next Author-Gate.
None of the calibrated thresholds in this directory are wired into live
routing code yet.
