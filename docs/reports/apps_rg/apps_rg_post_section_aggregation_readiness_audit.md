# apps_rg post-section aggregation readiness audit

**Date:** 2026-05-18  
**Scope:** Read-only audit — no aggregation refactor, no prompt changes, no X2 weakening.  
**Evidence:** `latest_mock_run.json` / `latest_real_run.json` pointers under `artifacts/apps_rg/runtime_proofs/<section>/` (section-scoped paths only).

## Verdict

**STATUS: FAIL** — Not safe to aggregate all seven sections into one resume today without accepting proof-pool/L2 drift on bullet lanes and missing rollup SSOT.

## Aggregation code (exists)

| Component | Path | Role |
|-----------|------|------|
| Section lanes | `apps_rg/runtime/sections/*`, `apps_rg/runtime/dispatch/*` | Per-section L2 + X2 + usage ledger + proof-pool receipt |
| Lane rollup | `apps_rg/runtime/internal/generated_lane_rollup.py` | Filesystem pointers per lane (`latest_successful_real_run.json`) |
| Final assembler | `apps_rg/runtime/internal/final_resume_assembler.py` | Deterministic `final_resume.json` from rollup + locked copy + base resume |
| Assembly X2 | `apps_rg/runtime/assembly/final_resume_x2.py` | Structural/provenance gates (order, snapshots, locked copy) — **no semantic dedup** |
| Package X3 | `apps_rg/runtime/internal/resume_package_disposition.py` | Whole-resume disposition rollup |
| SRFS audit | `apps_rg/audit/srfs_receipt_aggregator.py` | Cross-section SRFS receipt aggregation (audit-only) |
| Modular output | `apps_rg/l2_recipe/modular_rg_output_builder.py` | Alternate `rg_output` path (not same artifact as assembler) |

Prior gap analysis: `docs/reports/apps_rg/apps_rg_post_section_aggregation_gap_20260517.md`

## Section artifact matrix

Evidence run dirs are in `apps_rg_post_section_aggregation_readiness_audit.json`.

| section | output artifact | usage ledger | X2 receipt | proof source | digest match (usage↔receipt) | X2 receipt | X2 gates |
|---------|-----------------|--------------|------------|--------------|------------------------------|------------|----------|
| headline | `headline_output.txt` | yes | yes | `broad_skills_ledger` | yes | PASS | PASS |
| executive_summary | `l2_output.resume_display_text` | yes | yes | `broad_skills_ledger` | yes | PASS | PASS |
| unify_bullets | `l2_output.bullets` | yes | yes | `broad_skills_ledger` | yes | **FAIL** | **FAIL** |
| unify_narrative | `l2_output.narrative_sentence` | yes | yes | `broad_skills_ledger` | yes | PASS | PASS |
| ibm_bullets | `l2_output.bullets` | yes | yes | `broad_skills_ledger` | yes | **FAIL** | **FAIL** |
| ibm_narrative | `l2_output.narrative_sentence` | yes | yes | `broad_skills_ledger` | yes | PASS | PASS |
| competencies | `l2_output.competencies` + `competencies_section_output.json` | yes | yes | `broad_skills_ledger` | yes | PASS | **FAIL** |

All seven sections: `section_input_usage_ledger.json` and `x2_source_fact_pool_receipt.json` present on audited run dirs.  
All seven: `non_proof_inputs` = `["jd_title_company", "briefing"]`; `base_resume_fallback_used` = false on audited runs.

## Proof-pool / aggregation readiness

**Within-section (PASS):** Every section shows matching `proof_pool_digest` on usage ledger vs X2 receipt.

**Cross-section (MAJOR):** Seven distinct `proof_pool_digest` values — one per section ledger slice. Assembler does not bind a single orchestration-scoped proof pool across lanes.

**L2 vs active pool (BLOCKER on bullet lanes):**

- `unify_bullets`: receipt `decisive_reason` = `unsupported_source_fact_ids:bul_unify_001,bul_unify_002` while pool allowlist is ledger-primary (`allowed_source_fact_ids_count`: 2).
- `ibm_bullets`: same pattern for `bul_ibm_*` metric derivatives.

Narrative lanes under ledger-primary cite `fact_*` ids and pass membership gates; bullet mock L2 outputs still use legacy `bul_*` canonical IDs.

## Overlap / redundancy

| category | finding | sections | severity |
|----------|---------|----------|----------|
| source_fact reuse | `fact_engineering_platform_*` appears in 3 sections (headline, exec summary, unify narrative, competencies) | 3 | expected (MAJOR if budget enforced at aggregate) |
| source_fact reuse | No single ID in ≥4 sections | — | none triggered |
| narrative vs bullets | No verbatim bullet sentence found inside unify/ibm narrative text on audited runs | — | none |
| exec vs bullets | No long substring overlap on current exec_summary **real** run vs ibm_bullets mock | — | none on this evidence set |
| metrics | No metric token repeated across ≥3 sections | — | none |
| competencies vs bullets | No competency line duplicated verbatim in bullet text | — | none |

Assembler/`final_resume_x2` do not enforce cross-section semantic dedup today.

## Infrastructure gap

`artifacts/apps_rg/reports/generated_lane_rollup.json` — **missing** on disk. `assemble_final_resume()` cannot run without rollup generation.

## Recommended next wave

1. **Regenerate** `unify_bullets` and `ibm_bullets` offline mock/real runs so L2 `source_fact_ids` ⊆ active ledger pool (receipt PASS).
2. **Generate** `generated_lane_rollup.json` from latest successful real/mock pointers with shared orchestration metadata.
3. **Add** `final_resume_x2` gates: per-lane `x2_source_fact_pool_receipt` PASS, cross-section `source_fact_id` budget, narrative-vs-bullet substring check.

## Non-claims

- Does not claim product ALLOW
- Does not rewrite section outputs
- Does not weaken X2/X3

Machine-readable SSOT: `apps_rg_post_section_aggregation_readiness_audit.json`
