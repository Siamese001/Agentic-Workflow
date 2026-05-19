# Augmented skills graph — X2 / proof-source boundary (Wave 1)

**Status: PASS** for scoped dual-source boundary work.

## Split semantics

| Role | `*_source_type` | Artifact |
|------|-----------------|----------|
| Claim evidence | `candidate_fact_ledger` (or `selected_role_fact_set` / `base_resume_fallback`) | Candidate fact JSON / SRFS / base resume |
| Skills authority | `augmented_skills_graph` | `master_skills_arsenal_ledger.json` (W4A) |

Legacy `proof_pool_type` / `proof_source` values are **unchanged** for existing X2 claim-id gates. Receipts and INPUT_AUTHORITY prompts state explicitly that `broad_skills_ledger` is **claim evidence only**, not skills authority.

## X2 hardening

- `proof_pool_source_fact_validation` receipts include `skills_authority_source_type`, `skills_authority_status`, `skills_authority_x2_boundary`.
- If `legacy_broad_skills_ledger_skills_authority` is true or skills type is `broad_skills_ledger`, boundary is **NOT_PASS**.
- Missing graph → `skills_authority_status=BLOCKED`, `skills_authority_x2_boundary=NOT_PASS` (never PASS).

## Competencies

- `build_verified_skill_inventory_projection()` supplies graph-backed scaffolding.
- `verified_skill_inventory_deprecated` documents that base-resume `facts.skills` is not SSOT.
- Competencies PA injects `VERIFIED_SKILL_INVENTORY_PROJECTION` into C0 when graph loads.

## unify_bullets edge

- Resolver now includes `unify_bullets` in company-hint fallback (`unify` lane) when SRFS allocation slice is empty, avoiding spurious `base_resume_fallback` when the candidate ledger is loadable.

Machine-readable: `augmented_skills_graph_x2_source_boundary.json`.
