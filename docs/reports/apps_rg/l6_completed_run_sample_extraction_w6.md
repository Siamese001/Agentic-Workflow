# L6 Completed-Run Sample Extraction — W6 Report

**Report date:** 2026-05-18  
**Status:** PASS (extraction); reviewer export **EMPTY** (all `pending_review`)  
**proof_eligible:** false  

---

## Extraction strategy

- Source: [apps_rg_live_section_proof_results.json](apps_rg_live_section_proof_results.json) indexed REAL_LLM artifact dirs (`--index-only`, default).
- Tool: [extract_completed_run_samples.py](../../ops_scripts/apps_rg/l6_benchmarks/extract_completed_run_samples.py)
- Reads completed-run bundles (`run_manifest.json`, `l2_output.json`, `x3_disposition.json`, `section_input_usage_ledger.json`) **without mutating** source proofs.

## Section mapping

| section_id | section_group |
|------------|---------------|
| headline | positioning |
| executive_summary | executive_summary |
| competencies | competencies |
| unify_bullets, ibm_bullets | bullet |
| unify_narrative, ibm_narrative | narrative |

## Quality-status classification

| Status | Meaning |
|--------|---------|
| `x2_pass_x3_allow` | X2 PASS + X3 ALLOW (none in live wave 2 index) |
| `x2_pass_x3_review` | X2 PASS + X3 REVIEW* (1: executive_summary) |
| `x2_fail_x3_block` | X2 FAIL + X3 BLOCK (6 sections) |
| `incomplete_or_ineligible` | Missing artifacts or non-REAL_LLM |

`proof_eligible` in `collection_metadata` is **false** for all extracted samples (no certification claim).

## X2/X3 preservation

Stored under `collection_metadata` on each sample: `x2_product_quality_status`, `x2_failed_gates`, `x3_disposition`, `proof_eligible`, `skills_authority_source_type`, `claim_evidence_source_type`, `unsupported_source_fact_ids`, plus `x2_receipt_refs` / `x1d_judge_refs`.

## PII behavior

- Heuristic scan (email/phone/ssn-like); no redaction in W6.
- All 7 samples: `pii_status=pending_review`.
- Reviewer export: **0 packets** (`empty_reason=all_samples_pending_review_excluded`).

## Split behavior

- Seeded hash 60/20/20 via [assign_benchmark_splits.py](../../ops_scripts/apps_rg/l6_benchmarks/assign_benchmark_splits.py).
- Paths: `collected/<section_group>/<split>/<benchmark_id>.json`

## Drift holdout

- [drift_holdout_manifest_w6.json](../../artifacts/apps_rg/benchmarks/collected/_manifests/drift_holdout_manifest_w6.json) lists reserved IDs; **not** used for first-pass calibration.

## Counts (live wave 2)

| Metric | Value |
|--------|------:|
| samples_collected | 7 |
| samples_skipped | 0 |
| pii_pending_review | 7 |
| pii_cleared | 0 |
| reviewer_export_count | 0 |
| drift_holdout_count | 0 |

## Non-claims

- No public datasets ingested
- No human labels collected
- No judge promotion
- No Spearman / Cohen kappa computed
- No runtime behavior changed
- No calibration complete

## Next wave

1. PII review → set `pii_status=cleared` on approved rows  
2. Re-run [export_reviewer_packets.py](../../ops_scripts/apps_rg/l6_benchmarks/export_reviewer_packets.py)  
3. Human scoring ingest (future)  
4. Calibration report job (future)

## Receipt

[l6_completed_run_sample_extraction_w6_receipt.md](l6_completed_run_sample_extraction_w6_receipt.md) · [manifest](l6_completed_run_sample_extraction_w6_manifest.json)
