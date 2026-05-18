# SRFS-active representative proof — R1 + R2 (unify_bullets)

**Binding diagnosis:** `srfs_real_receipt_fallback_diagnosis_w1_w2.md`  
**Proof level:** `REPRESENTATIVE_SRFS_ACTIVE_RECEIPT_ONLY`  
**Date:** 2026-05-18

---

## R1 — Seven-section SRFS SSOT

**Selected path:** `artifacts/apps_rg/test_fixtures/srfs_w7/w7_realistic_nested_facts.json`  
**Shape:** `nested_facts`  
**SHA256:** `30ac00cbcbe55f761afaba28685015081d83228efc2b8c6759c302f22b99b50f`  
**SSOT record:** `docs/reports/apps_rg/srfs_active_rerun_ssot_r1.json`

| Section | Fact count |
|---------|------------|
| headline | 1 |
| executive_summary | 2 |
| unify_bullets | 6 |
| unify_narrative | 2 |
| ibm_bullets | 5 |
| ibm_narrative | 1 |
| competencies | 2 |

**Reason selected:** Nested `selected_facts_by_section` matches production inventory shape and W7 contract tests; all seven slices non-empty. Bare-list twin has identical counts but was not pinned to avoid dual-SSOT drift for R3.

**Not used:** `selected_role_fact_set_20260518T181200Z_exec_summary_srfs_cli_proof.json` (exec-only facts in non-exec slices).

---

## R2 — Representative lane run

**Lane:** `unify_bullets`  
**Run dir:** `artifacts/apps_rg/runtime_proofs/unify_bullets/real/unify_bullets_20260518_191249`  
**Receipt:** `.../section_metric_receipt.json`

### Governed command

```text
python -m apps_rg --section unify_bullets \
  --selected-role-fact-set artifacts/apps_rg/test_fixtures/srfs_w7/w7_realistic_nested_facts.json \
  --provider qwen_vllm --mock-judges --allow-test-mock-judges --allow-non-allow-exit-zero
```

Same structural-proof flag surface as the prior fallback run; **with** SRFS path added.

### Proof checks (required)

| Check | Result |
|-------|--------|
| `run_manifest` includes `--selected-role-fact-set` with SSOT path | **PASS** |
| `section_metric_receipt.json` exists | **PASS** |
| `proof_pool_type == selected_role_fact_set` | **PASS** |
| `selected_role_fact_set_used == true` | **PASS** |
| `fallback_used == false` | **PASS** |
| `fallback_reason` empty | **PASS** |
| `srfs_section_id == unify_bullets` | **PASS** |
| `x2_srfs_gate_status` in PASS\|FAIL (not NOT_APPLICABLE / UNKNOWN) | **PASS** (`FAIL`) |
| `prompt_hash` non-empty | **PASS** (`d5badab7051c09c4`) |
| `full_resume_srfs_supported == false` | **PASS** |

**SRFS-active receipt verdict:** **PASS** — receipt is SRFS-active; X2 SRFS gate **FAIL** is expected quality enforcement (out-of-slice fact id `bul_w7_unify_ 006` spacing typo in model output), not fallback.

### Contrast with prior fallback run

| Field | Prior (`unify_bullets_20260518_182346`) | R2 (`unify_bullets_20260518_191249`) |
|-------|----------------------------------------|--------------------------------------|
| CLI SRFS flag | absent | present |
| `proof_pool_type` | `base_resume_fallback` | `selected_role_fact_set` |
| `x2_srfs_gate_status` | `NOT_APPLICABLE` | `FAIL` |

### Operator notes (non-claims)

- Process exit 0 with `--allow-non-allow-exit-zero`; X3 `X3_BLOCK` for unrelated X2 gates.
- `runtime_generation_status`: **REAL_LLM** (local Qwen probe passed). Not offline stub; mock judges only. Does not claim live judge quality or certification.
- No lane code changes; no aggregator run.

---

## R3 readiness

**`can_start_r3_batch`:** **true** — hypothesis confirmed: supplying `--selected-role-fact-set` with seven-section SSOT produces SRFS-active receipts. Remaining five lanes can batch with the same SSOT path and CLI template.

**Avoid for R3:** exec-summary-only SRFS file; `latest_successful_*` receipt pointers; weakening X2/PASS guard.
