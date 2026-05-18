# unify_bullets SRFS X2 fix — Q1–Q3

**Date:** 2026-05-18  
**Proof level:** `SECTION_SRFS_STRUCTURAL_AUDIT_ONLY`

---

## Q1 — Diagnosis

**Failing receipt (before):** `artifacts/apps_rg/runtime_proofs/unify_bullets/real/unify_bullets_20260518_191249/section_metric_receipt.json`

| Field | Value |
|-------|-------|
| `x2_srfs_gate_status` | FAIL |
| `out_of_slice_fact_ids` | `["bul_w7_unify_ 006"]` (space before `006`) |
| Primary SRFS gate | `x2_unify_bullets_source_fact_ids_within_srfs_slice` FAIL |

**Root cause:** Qwen emitted a whitespace typo in the sixth bullet / claim_ledger row: `bul_w7_unify_ 006` instead of fixture id `bul_w7_unify_006`. SRFS slice and `selected_fact_plan` were correct; failure was **model output fact-id formatting**, not missing CLI SRFS input or fixture error.

**Evidence:**
- `raw_model_output.txt` line 76: `"source_fact_ids": ["bul_w7_unify_ 006"]`
- `w7_realistic_nested_facts.json` unify_bullets facts use `bul_w7_unify_001` … `bul_w7_unify_006` (no spaces)
- Other X2 gates also failed on that run (metrics, scope, etc.); **SRFS-specific** failure isolated to the spaced id

**Gates changed in Q2:** None weakened. Added lane **output normalization** only (same pattern as `ibm_bullets_lane._canonicalize_bul_ibm_source_fact_id`).

---

## Q2 — Fix

**File:** `apps_rg/runtime/sections/unify_bullets_lane.py`

- `_canonicalize_bul_w7_unify_source_fact_id` — strip whitespace inside `bul_w7_unify*` ids
- `_normalize_unify_source_fact_id_list` / `_normalize_unify_claim_ledger`
- Applied in `normalize_unify_parsed_without_ledger_synthesis` on bullets + claim_ledger

**Test:** `tests/_apps_contract/test_unify_bullets_section_pipeline.py::test_canonicalize_bul_w7_unify_whitespace_source_fact_id`

---

## Q3 — Rerun + aggregator v3

**Rerun command:**

```text
python -m apps_rg --section unify_bullets \
  --selected-role-fact-set artifacts/apps_rg/test_fixtures/srfs_w7/w7_realistic_nested_facts.json \
  --provider qwen_vllm --mock-judges --allow-test-mock-judges --allow-non-allow-exit-zero
```

| | Before | After |
|---|--------|-------|
| Run dir | `.../unify_bullets_20260518_191249` | `.../unify_bullets_20260518_195618` |
| Receipt | `.../191249/section_metric_receipt.json` | `.../195618/section_metric_receipt.json` |
| `x2_srfs_gate_status` | FAIL | **PASS** |
| `out_of_slice_fact_ids` | `["bul_w7_unify_ 006"]` | `[]` |
| `x2_unify_bullets_source_fact_ids_within_srfs_slice` | FAIL | **PASS** |

Product X2 may still FAIL (`x2_claim_ledger_coverage_100`, etc.); not required for SRFS gate PASS.

**Manifest v3:** `artifacts/apps_rg/audit/srfs_section_aggregation/real_receipt_trial_v3/real_section_receipt_manifest_v3.json`

**Aggregator v3:** `deterministic_status=PASS`, `any_section_x2_srfs_fail: false`, all seven sections `x2_srfs_gate_status: PASS`

---

## Non-claims

- Not certification, product ALLOW, live judge quality, or full résumé SRFS.
- Normalization fixes typo ids only; does not relax slice membership rules.
