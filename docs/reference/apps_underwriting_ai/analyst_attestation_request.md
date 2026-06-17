# Analyst Attestation Request for DS-R1 / W1 Holdout

## Purpose

We need a qualified underwriting analyst or credit risk SME to attest whether the holdout labels in `apps_underwriting_ai/holdout/rationale_judge_holdout.yaml` are acceptable as a human/SME benchmark for rationale judge calibration.

This is not a production lending decision file. The attestation confirms review quality, labeling provenance, and data safety posture.

## What the analyst should review

1. Confirm the holdout contains 100 examples and 20 examples per rubric dimension.
2. Confirm each rationale_text is realistic enough to test the judge.
3. Confirm each human_score is a reasonable human/SME score for that dimension.
4. Confirm labeler aliases map to actual qualified reviewers or an approved offline compliance mapping.
5. Confirm there is no PII, real applicant data, or live lender thresholds.
6. Confirm labels were not authored solely by Codex or an LLM.

## Required output

Complete this file:

`apps_underwriting_ai/holdout/rationale_judge_holdout_provenance.yaml`

Set:

```yaml
holdout_dataset_status: VERIFIED_ANALYST_ATTESTED
```

And fill all attestation fields with non-null values and true confirmations.

## Important limitation language

Use honest language. If the examples are realistic/anonymized rather than production-derived, say that. Do not represent demo, synthetic, Codex-authored, or LLM-authored labels as independent human labels.
