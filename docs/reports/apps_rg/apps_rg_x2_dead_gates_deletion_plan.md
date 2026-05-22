# apps_rg X2 dead / deprecated gates — deletion plan (review copy)

**Plan SSOT:** [.cursor/plans/apps-rg-x2-dead-gates-burndown-c4e8f2.md](../../.cursor/plans/apps-rg-x2-dead-gates-burndown-c4e8f2.md)  
**Generated for review:** 2026-05-22  
**Status:** W1–W3 complete (2026-05-22); W4 pending approval  
**Receipts:** [w1_w2](apps_rg_x2_dead_gates_w1_w2_receipt.md) · [w3](apps_rg_x2_dead_gates_w3_receipt.md)

---

## Executive summary

Seven generated sections carry overlapping X2 gate catalogs. On the **product golden path** (`augmented_skills_graph`), many gates still appear in `x2_gate_outputs.json` as **PASS with skip** (`skipped_no_selected_role_fact_set`, `MOCKED_runtime_plumbing`, `skipped_not_real_llm`). Registry and audit layers also reference **retired gate IDs** that runtime no longer emits.

Recommended burndown: **four waves**, safest first (registry/audit) → retired SRFS repair stack → legacy proof-pool IDs → optional SRFS skip-PASS removal after live proof.

---

## Wave overview

| Wave | Risk | What changes |
|------|------|----------------|
| **W1** | Low | `lane_registry`, declarative contracts, audit scripts — rename/remove ghosts |
| **W2** | Low | Delete release-disabled exec-summary SRFS repair; align tests |
| **W3** | Medium | Collapse `*_within_srfs_slice` → `*_active_proof_pool_source_fact_ids` (7 validators) |
| **W4** | Medium–High | Stop emitting SRFS skip-PASS gates on default path; live qwen proof |

---

## Section inventory (deletion safety)

### headline

| Item | Skipped? | Safe to delete? |
|------|----------|-----------------|
| `x2_*_within_srfs_slice` (legacy branch) | No on product path | Conditional (W3) |
| `x2_headline_claim_ledger_no_silent_row_drop` | No | **No** — live gate |
| `x2_headline_text_claim_coverage_integrity` | No | **No** — live gate |

### executive_summary

| Item | Skipped? | Safe to delete? |
|------|----------|-----------------|
| `x2_srfs_*` (5 gates) | Yes when SRFS envelope inactive | Conditional (W4) |
| `x2_source_sensitive_phrases_supported` | Yes when no `selected_facts` | Conditional (W4) |
| `x2_exec_summary_sentence_count_2_3` | Old proofs only | **Yes** (W2) |
| `x2_exec_summary_srfs_density_word_count` | Not emitted | **Yes** (W2) |
| `x2_exec_summary_srfs_sentence_count_4_5` | Not emitted | **Yes** (W2) |
| `x2_exec_summary_paragraph_word_bounds` | Registry ghost | **Yes** (W1) → use `paragraph_max_words` |
| SRFS repair modules | N/A | **Yes** (W2) if release-disabled |

### competencies

| Item | Skipped? | Safe to delete? |
|------|----------|-----------------|
| Style gates (`skipped_not_real_llm`) | Yes when not REAL_LLM | **No** — mock discipline |
| SRFS slice gate branch | No on product path | Conditional (W3) |

### unify_bullets / ibm_bullets

No designed permanent skip-noops. “Absent in proof bundle” = enumeration gap, not deprecation.

### unify_narrative

| Item | Skipped? | Safe to delete? |
|------|----------|-----------------|
| `x2_unify_narrative_requires_finalized_bullets` | MOCKED path | **No** |
| `x2_no_metric_repetition_unless_justified` | No companion | Conditional |
| `x2_no_companion_ngram_copy` | No companion text | Conditional |

### ibm_narrative

| Item | Skipped? | Safe to delete? |
|------|----------|-----------------|
| `x2_ibm_narrative_requires_finalized_bullets` | MOCKED / standalone | **No** / conditional |
| `x2_no_mock_or_plumbing_language_in_real_l2_output` | offline stub | **No** |
| `x2_claim_ledger_source_fact_ids_allow_list` | `skipped_no_runtime_allow_list` | **No** |

---

## What NOT to delete

- **C0 gates** (`x2_c0_metrics_artifact_present`, `x2_c0_support_status_gate`) — live, augmented at write time
- **Competencies** `skipped_not_real_llm` style hygiene
- **Narrative** `MOCKED_runtime_plumbing` companion dependency skips
- **Active product gates** (`sentence_count_4_5`, `paragraph_max_words`, claim coverage, metric anchors)

---

## Proof commands (per wave)

```bash
# W1
python ops_scripts/apps_rg/section_complexity_reduction_audit.py
python -m pytest tests/unit/apps_rg/section_rigor/ -q --override-ini=addopts= -p no:xdist -p pytest_timeout

# W2
python -m pytest tests/_apps_contract/test_executive_summary_x2_x1d_alignment.py tests/_apps_contract/test_exec_summary_runtime_slice.py -q --override-ini=addopts= -p no:xdist -p pytest_timeout

# W3
python -m pytest tests/_apps_contract/test_apps_rg_x2_ledger_primary_source_facts.py tests/unit/apps_rg/test_product_evidence_authority_contract.py -q --override-ini=addopts= -p no:xdist -p pytest_timeout

# W4 (live — provider required)
python -m apps_rg --section executive_summary --provider qwen_vllm --allow-non-allow-exit-zero
```

---

## Related artifacts

- [apps_rg_section_complexity_reduction_audit.json](apps_rg_section_complexity_reduction_audit.json)
- [section_authority_convergence_audit.json](section_authority_convergence_audit.json)
- [SIMPLIFICATION_REDESIGN.md](SIMPLIFICATION_REDESIGN.md)
- [apps_rg_x2_remaining_lanes_active_proof_pool.json](apps_rg_x2_remaining_lanes_active_proof_pool.json)

---

## Your review checklist

1. Approve **W1+W2** as no-brainer safe deletions?
2. Approve **W3** proof-pool ID collapse on product path only?
3. Confirm **W4** — is SRFS structural X2 officially retired on golden path, or still needed for some targeting runs?
4. Any section where skip-PASS gates should remain for operator visibility?
