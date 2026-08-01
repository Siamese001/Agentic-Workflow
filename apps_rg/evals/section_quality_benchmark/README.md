# Section quality benchmark

This package evaluates completed, sealed Apps RG section artifacts and completed
offline reviews. It does not generate resume content, invoke a judge, mutate the
runtime, or authorize release.

## Supported lanes

- `headline`
- `executive_summary`
- `competencies`
- `unify_bullets`
- `ibm_bullets`

The original `*.schema.json` files in this directory remain compatibility
scaffolds for historical W14 label rows. Runnable v1 contracts live under
`schemas/`; governed scoring rules live under `rubrics/`.

## Inputs and review authority

The CLI consumes two independently sealed JSON files:

1. `apps_rg.section_quality_input.v1` freezes the five lane artifacts, target,
   prompt, contract, grounding status, and absolute or pairwise mode.
2. `apps_rg.section_quality_review.v1` binds every completed review to the exact
   input-bundle, candidate, baseline, and rubric digests.

Pairwise reviewers score opaque `VARIANT_A` and `VARIANT_B` identities. The
sealed input privately binds those labels to candidate and baseline artifacts;
unblinded pairwise inputs are rejected as `UNKNOWN`.

Each dimension score carries a reason and evidence references. Human and model
judge results are aggregated separately. Human coverage is preferred when it is
complete for a lane; otherwise complete model-only coverage remains explicitly
`MODEL_JUDGE_ADVISORY`. Neither classification authorizes release or current-run
mutation. This wave does not calibrate model judges against human labels, and
the report records that fact explicitly.

## Run

```text
python -m apps_rg.evals.section_quality_benchmark \
  --input sealed-section-input.json \
  --reviews sealed-section-reviews.json \
  --output section-quality-report.json
```

Exit codes are `0` for advisory `PASS`, `1` for `FAIL`, `2` for `UNKNOWN` or
`NOT_MEASURED`, and `3` for file or JSON errors.

All five lanes must be supplied for the report to pass. Missing lanes remain
`NOT_MEASURED`; invalid or incomplete evidence is `UNKNOWN`; failed grounding
cannot be overridden by high quality scores. Absolute scores and blinded
pairwise preferences remain distinct, and no blended overall score is emitted.

Synthetic scores under `fixtures/` are controlled test data only. They are not
production benchmark labels, calibration evidence, or release authority.
