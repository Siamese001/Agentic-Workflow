# apps_rg X2 ledger-primary source_fact hardening

## Scope

Harden deterministic X2 `source_fact_id` validation for **SRFS**, **broad_skills_ledger**, and **explicit base_resume_fallback** proof pools — without weakening gates or treating JD/briefing as proof.

## Shared helper

`apps_rg/runtime/validators/proof_pool_source_fact_validation.py`

- `validate_active_proof_pool_source_fact_ids` — membership + non-proof rejection
- `evaluate_proof_pool_source_fact_gate` — X2 gate envelope + receipt fields
- `write_x2_source_fact_pool_receipt` — persists `x2_source_fact_pool_receipt.json` under the run artifact dir
- `scope_ids_membership_only` — IBM/Unify scope without legacy `bul_*` prefix when ledger/SRFS is active

Receipt fields: `section`, `proof_source`, `proof_pool_ref`, `proof_pool_digest`, `allowed_source_fact_ids_count`, `source_fact_ids_checked`, `unsupported_source_fact_ids`, `rejected_non_proof_source_ids`, `jd_or_briefing_ids_rejected`, `x2_source_fact_pool_status`, `decisive_reason`, `validator_name`.

## Section updates

| Section | X2 changes |
|---------|------------|
| competencies | Proof-pool gate; mock output uses active pool IDs for ledger; `x2_all_terms_source_fact_ids` threshold text |
| unify_bullets | Membership scope + coverage when ledger/SRFS; proof-pool gate |
| ibm_bullets | Same pattern as unify |

Lanes activate proof-pool X2 when `proof_pool_metadata.proof_pool_type` is set (all three modes).

## Tests

- `tests/_apps_contract/test_apps_rg_x2_ledger_primary_source_facts.py`
- Updated SRFS w4/w6/w7 expectations where default pool is now ledger-primary

## Non-claims

- No product ALLOW
- No live Qwen quality proof in this wave
- X2 gates not weakened (membership enforced; JD/briefing still rejected)
