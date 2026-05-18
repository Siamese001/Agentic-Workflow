# SRFS aggregator real-receipt trial v2 — R4

**Wave:** R4 only  
**Proof level:** `SECTION_SRFS_STRUCTURAL_AUDIT_ONLY` (aggregator)  
**Date:** 2026-05-18

---

## Summary

| Item | Result |
|------|--------|
| Executive_summary W7 SSOT rerun | SRFS-active receipt |
| Seven-section manifest | Built (explicit paths) |
| Aggregator deterministic status | **PASS** |
| Aggregator advisory judge | NOT_RUN |
| Contract tests | 20 passed |

---

## SRFS SSOT

- **Path:** `artifacts/apps_rg/test_fixtures/srfs_w7/w7_realistic_nested_facts.json`
- **SHA256:** `30ac00cbcbe55f761afaba28685015081d83228efc2b8c6759c302f22b99b50f`

---

## R4 executive_summary rerun

**Command:**

```text
python -m apps_rg --section executive_summary \
  --selected-role-fact-set artifacts/apps_rg/test_fixtures/srfs_w7/w7_realistic_nested_facts.json \
  --provider qwen_vllm --mock-judges --allow-test-mock-judges --allow-non-allow-exit-zero
```

| Field | Value |
|-------|-------|
| Exit code | 0 (inspection override; X3_BLOCK) |
| Run dir | `artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260518_195206` |
| Receipt | `.../section_metric_receipt.json` |
| `proof_pool_type` | `selected_role_fact_set` |
| `x2_srfs_gate_status` | PASS |
| X3 | X3_BLOCK (product quality; not aggregate criteria) |

---

## Trial v2 manifest

**Path:** `artifacts/apps_rg/audit/srfs_section_aggregation/real_receipt_trial_v2/real_section_receipt_manifest_v2.json`

| Section | Source | Receipt path |
|---------|--------|--------------|
| headline | R3 | `.../headline/real/headline_20260518_192606/section_metric_receipt.json` |
| executive_summary | R4 | `.../executive_summary/real/exec_summary_20260518_195206/section_metric_receipt.json` |
| unify_bullets | R2 | `.../unify_bullets/real/unify_bullets_20260518_191249/section_metric_receipt.json` |
| unify_narrative | R3 | `.../unify_narrative/real/unify_narrative_20260518_192624/section_metric_receipt.json` |
| ibm_bullets | R3 | `.../ibm_bullets/plumbing/ibm_bullets_20260518_192636/section_metric_receipt.json` |
| ibm_narrative | R3 | `.../ibm_narrative/real/ibm_narrative_20260518_192700/section_metric_receipt.json` |
| competencies | R3 | `.../competencies/real/competencies_20260518_192715/section_metric_receipt.json` |

All seven: SRFS-active per receipt proof checks (`sections_srfs_active_count: 7`).

---

## Aggregator run

```text
python -m apps_rg.audit.srfs_receipt_aggregator \
  --receipt-manifest artifacts/apps_rg/audit/srfs_section_aggregation/real_receipt_trial_v2/real_section_receipt_manifest_v2.json \
  --manifest docs/reports/apps_rg/srfs_per_section_w1_w7_closeout_manifest.json \
  --out artifacts/apps_rg/audit/srfs_section_aggregation/real_receipt_trial_v2
```

**CLI output:**

```text
report_path=artifacts\apps_rg\audit\srfs_section_aggregation\real_receipt_trial_v2\apps_rg_srfs_audit_report.json
deterministic_status=PASS
proof_level=SECTION_SRFS_STRUCTURAL_AUDIT_ONLY
advisory_judge_status=NOT_RUN
advisory_judge_mocked_or_live=not_run
```

Exit code: 0

**Cross-section:** `any_section_x2_srfs_fail: true` (unify_bullets only) — informational; does not fail PASS guard.

---

## Section matrix (aggregator-normalized)

| Section | srfs_active | x2_srfs | pass_guard | x3 (info) |
|---------|-------------|---------|------------|-----------|
| headline | true | PASS | [] | X3_REVIEW_MOCKED_PLUMBING_ONLY |
| executive_summary | true | PASS | [] | X3_BLOCK |
| unify_bullets | true | FAIL | [] | X3_BLOCK |
| unify_narrative | true | PASS | [] | X3_BLOCK |
| ibm_bullets | true | PASS | [] | X3_BLOCK |
| ibm_narrative | true | PASS | [] | X3_BLOCK |
| competencies | true | PASS | [] | X3_BLOCK |

**Deterministic verdict:** PASS  
**Advisory verdict:** NOT_RUN (disabled)

---

## Non-claims

- Not runtime certification, product ALLOW, release signoff, or live judge quality proof.
- W7 fixture SRFS; not production fact_inventory homogeneity claim beyond structural audit.
- REAL_LLM + mock judges on section runs; unify_bullets x2_srfs FAIL noted but PASS guard satisfied.
