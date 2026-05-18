# SRFS-active five-lane batch — R3

**Binding SSOT:** `docs/reports/apps_rg/srfs_active_rerun_ssot_r1.json`  
**Proof level:** `FIVE_LANE_SRFS_ACTIVE_RECEIPT_BATCH_ONLY`  
**Date:** 2026-05-18

---

## Scope

Batch rerun of five previously fallback lanes with pinned seven-section SRFS:

`artifacts/apps_rg/test_fixtures/srfs_w7/w7_realistic_nested_facts.json`

**Not rerun:** `unify_bullets` (R2), `executive_summary` (out of R3 success criteria).

---

## Governed command (all five lanes)

```text
python -m apps_rg --section <lane> \
  --selected-role-fact-set artifacts/apps_rg/test_fixtures/srfs_w7/w7_realistic_nested_facts.json \
  --provider qwen_vllm --mock-judges --allow-test-mock-judges --allow-non-allow-exit-zero
```

Mock judges only; `REAL_LLM` generation with local Qwen probe (same surface as R2).

---

## Lane results

| Lane | Run dir | Placement | SRFS-active receipt | `x2_srfs_gate_status` | X3 / product quality |
|------|---------|-----------|---------------------|-------------------------|----------------------|
| headline | `.../headline/real/headline_20260518_192606` | real | **yes** | PASS | X3_REVIEW_MOCKED; X2 product PASS |
| unify_narrative | `.../unify_narrative/real/unify_narrative_20260518_192624` | real | **yes** | PASS | X3_BLOCK; product FAIL |
| ibm_bullets | `.../ibm_bullets/plumbing/ibm_bullets_20260518_192636` | plumbing | **yes** | PASS | X3_BLOCK; product FAIL |
| ibm_narrative | `.../ibm_narrative/real/ibm_narrative_20260518_192700` | real | **yes** | PASS | X3_BLOCK; product FAIL |
| competencies | `.../competencies/real/competencies_20260518_192715` | real | **yes** | PASS | X3_BLOCK; product FAIL |

All five: `proof_pool_type=selected_role_fact_set`, `selected_role_fact_set_used=true`, `fallback_used=false`, `srfs_section_id` matches lane, non-empty `prompt_hash`, `full_resume_srfs_supported=false`.

**Note:** `ibm_bullets` artifacts under `plumbing/` bucket (runtime placement); receipt and `run_manifest` still include SRFS flag and SRFS-active fields.

---

## Seven-lane inventory for R4 (informational)

| Lane | SRFS-active receipt source |
|------|---------------------------|
| executive_summary | Prior trial (`exec_summary_20260518_173654`, exec-only SRFS file) — **different SSOT** |
| unify_bullets | R2 (`unify_bullets_20260518_191249`, W7 nested SSOT) |
| headline | R3 (`headline_20260518_192606`) |
| unify_narrative | R3 (`unify_narrative_20260518_192624`) |
| ibm_bullets | R3 (`ibm_bullets_20260518_192636`, plumbing) |
| ibm_narrative | R3 (`ibm_narrative_20260518_192700`) |
| competencies | R3 (`competencies_20260518_192715`) |

R4 aggregator trial v2 should use an **explicit manifest** with these paths. Optional: rerun `executive_summary` with W7 nested SSOT for SSOT consistency across all seven receipts.

---

## Verdict

**R3 status: PASS** — all five lanes emit SRFS-active `section_metric_receipt.json` with SRFS gate engaged (PASS or FAIL acceptable; all five show PASS on SRFS gate).

**Non-claims:** No product ALLOW, certification, live judge quality, or full résumé SRFS proof. Aggregator not run in this wave.
