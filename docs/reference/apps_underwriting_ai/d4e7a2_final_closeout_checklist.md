# d4e7a2 Final Closeout Checklist

## Current truth

W1 is not blocked by missing data anymore. W1 is provenance pending until a qualified underwriting owner completes the attestation file.

## Closeout gates

| Gate | Requirement | Status when done |
|---|---|---|
| W1 schema | `rationale_judge_holdout.yaml` has 100 examples, 20 per dimension, required fields, unique IDs, score range, no obvious PII | `W1_SCHEMA_VALID` |
| W1 provenance | `rationale_judge_holdout_provenance.yaml` is completed by a qualified underwriting owner | `W1_COMPLETE` |
| W2 API key | `ANTHROPIC_API_KEY` configured in CI secrets and local .env — **already done** | `W2_EXECUTABLE` ✅ |
| W2 judge run | LLM judge produces model scores against holdout examples | `W2_SCORED` |
| W5 report | weekly report populates holdout_comparison using human vs model scores | `W5_HOLDOUT_COMPARISON_POPULATED` |

## Human attestation fields that must be completed

File: `apps_underwriting_ai/holdout/rationale_judge_holdout_provenance.yaml`

Required changes:

```yaml
holdout_dataset_status: VERIFIED_ANALYST_ATTESTED

attestation:
  attestation_owner: "<full name or approved internal alias>"
  attestation_owner_role: "Qualified underwriting analyst / credit risk SME / approved reviewer"
  attestation_date: "YYYY-MM-DD"
  independent_human_review_confirmed: true
  qualified_underwriting_analyst_confirmed: true
  no_pii_confirmed: true
  no_real_applicant_data_confirmed: true
  no_live_lender_thresholds_confirmed: true
  no_llm_or_cascade_authored_labels_confirmed: true
  analyst_labeling_or_review_method: "<short description of who reviewed/authored labels and how>"
  calibration_method: "<short description of score rubric/calibration method>"
  limitations: "<honest limitations, e.g. realistic/anonymized training examples, not lender-production decisions>"
```

## Commands

Schema only:

```bash
python scripts/validate_underwriting_holdout.py \
  --holdout apps_underwriting_ai/holdout/rationale_judge_holdout.yaml
```

Schema plus provenance:

```bash
python scripts/validate_underwriting_holdout.py \
  --holdout apps_underwriting_ai/holdout/rationale_judge_holdout.yaml \
  --provenance apps_underwriting_ai/holdout/rationale_judge_holdout_provenance.yaml \
  --require-provenance
```

Tests:

```bash
pytest tests/apps_underwriting_ai/test_holdout_provenance_gate.py -q
```

## Required CI behavior

- Pull request should pass schema-only validation.
- Main/protected branch should require provenance validation before W1 can be marked complete.
- W2 jobs should be skipped or fail closed unless W1 provenance validation passes.
  - `ANTHROPIC_API_KEY` is already configured in CI secrets and local `.env` — not a gate.

## Status language

Before attestation:

```text
W1 = W1_PROVENANCE_PENDING. Holdout schema is valid, but qualified underwriting provenance attestation is incomplete.
W2 = BLOCKED. Requires W1_COMPLETE. (ANTHROPIC_API_KEY is already configured.)
```

After attestation and key availability:

```text
W1 = COMPLETE. Holdout schema and qualified underwriting provenance attestation passed.
W2 = READY_TO_RUN. LLM-as-judge scoring can execute against the analyst-attested holdout. (ANTHROPIC_API_KEY already present.)
```
