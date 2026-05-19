# Live section proof — execution results (Wave 2)

**STATUS: PARTIAL**

## Summary

| Dimension | Result |
|-----------|--------|
| Non-mock product path (`REAL_LLM`) | **7 / 7** |
| `skills_authority_source_type=augmented_skills_graph` + `PASS` | **7 / 7** |
| `claim_evidence_source_type=candidate_fact_ledger` | **7 / 7** |
| X2 source-fact pool boundary (`unsupported_source_fact_ids=[]`) | **7 / 7** |
| X2 product quality PASS | **1 / 7** (executive_summary) |
| X3 ALLOW / certification `proof_eligible` | **0 / 7** |

All seven canonical sections ran through **`--provider qwen_vllm`** with vLLM healthy at `http://localhost:8000/v1`. Augmented skills graph remained skills authority; candidate fact ledger remained claim evidence. No mock or offline stub paths were used for these runs.

Certification-grade proof (X3 ALLOW + `proof_eligible`) was **not** achieved for any section. That gap is quality/judge disposition, not source-authority regression.

## Per-section results

| Section | Artifact dir | Gen | Skills auth | Claim evidence | X2 pool | X3 | X2 PQ |
|---------|--------------|-----|-------------|----------------|---------|-----|-------|
| headline | `.../headline_20260518_215544` | REAL_LLM | PASS (graph) | candidate_fact_ledger | PASS | X3_BLOCK | FAIL |
| executive_summary | `.../exec_summary_20260518_215708` | REAL_LLM | PASS (graph) | candidate_fact_ledger | PASS | X3_REVIEW_JUDGE_SOFT_FAIL | PASS |
| competencies | `.../competencies_20260518_215820` | REAL_LLM | PASS (graph) | candidate_fact_ledger | PASS | X3_BLOCK | FAIL |
| unify_bullets | `.../unify_bullets_20260518_220036` | REAL_LLM | PASS (graph) | candidate_fact_ledger | PASS | X3_BLOCK | FAIL |
| unify_narrative | `.../unify_narrative_20260518_220149` | REAL_LLM | PASS (graph) | candidate_fact_ledger | PASS | X3_BLOCK | FAIL |
| ibm_bullets | `.../ibm_bullets_20260518_220226` | REAL_LLM | PASS (graph) | candidate_fact_ledger | PASS | X3_BLOCK | FAIL |
| ibm_narrative | `.../ibm_narrative_20260518_220332` | REAL_LLM | PASS (graph) | candidate_fact_ledger | PASS | X3_BLOCK | FAIL |

Base paths: `artifacts/apps_rg/runtime_proofs/<section>/real/<run_id>/`.

### Representative X2 failures (gates not weakened)

- **headline**: `x2_headline_word_count_10_to_13`
- **competencies**: `x2_structured_term_primary_facts`, `x2_competency_terms_canonical_structured`, …
- **unify_bullets**: `x2_unify_protected_bullet_preserved_or_justified`, `x2_claim_ledger_coverage_100`, …
- **unify_narrative**: `x2_unify_narrative_exactly_one_sentence`, `x2_unify_narrative_source_supported`, …
- **ibm_bullets**: `x2_ibm_metrics_preserved`, `x2_claim_ledger_coverage_100`, …
- **ibm_narrative**: `x2_ibm_narrative_source_supported`, `x2_claim_ledger_source_fact_ids_allow_list`, …

### executive_summary (closest to certification)

- X2 deterministic gates: **PASS**
- X3: **X3_REVIEW_JUDGE_SOFT_FAIL** (gemini_pro, openai_chatgpt, anthropic_claude below threshold)
- `x2_source_fact_pool_receipt.json`: `skills_authority_x2_boundary=PASS`, `unsupported_source_fact_ids=[]`

## Mock vs live classification

| Class | Sections |
|-------|----------|
| **REAL_LLM** (product-path generation) | All 7 |
| **MOCK_ONLY** | None in Wave 2 |
| **BLOCKED** | None (vLLM available) |
| **Certification proof_eligible** | None |

Prior mock receipt refresh (`--provider mock`) remains **MOCK_ONLY** and is excluded from this proof.

## Dual-source boundary (verified on all bundles)

- `section_input_usage_ledger.json` present on all 7 runs
- `skills_authority_source_type` = `augmented_skills_graph`
- `skills_authority_status` = `PASS`
- `claim_evidence_source_type` = `candidate_fact_ledger`
- `legacy_broad_skills_ledger_skills_authority` = `false`
- `x2_source_fact_pool_receipt.json`: `skills_authority_source_type=augmented_skills_graph`, `legacy_broad_skills_ledger_skills_authority=false`, `proof_source=broad_skills_ledger` (legacy claim-pool label only)

## Tests

| Command | Result |
|---------|--------|
| Scoped augmented-skills contract trio | **48 passed** |
| Broader `-k "augmented_skills_graph or source_authority or proof_pool"` | **80 passed, 2 failed** (`test_w9_judge_eval_harness` — out of scope) |

## Wave 1 readiness

See `apps_rg_live_section_proof_readiness.md` / `.json`.

## Machine-readable receipt

[apps_rg_live_section_proof_results.json](apps_rg_live_section_proof_results.json)
