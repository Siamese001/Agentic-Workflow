# apps_rg input wiring remediation — proof pool resolver (W1)

## Scope

Narrow remediation wave: shared proof-pool resolution for all seven canonical section lanes (`headline`, `executive_summary`, `unify_bullets`, `unify_narrative`, `ibm_bullets`, `ibm_narrative`, `competencies`).

## Resolution order (implemented)

1. **SRFS** when `--selected-role-fact-set` is supplied → `proof_source=srfs`
2. **Broad skills ledger** (default SSOT: `artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json`, override via `APPS_RG_BROAD_SKILLS_LEDGER_PATH`) → `proof_source=broad_skills_ledger`
3. **Base resume employment bullets** (explicit fallback) → `proof_source=base_resume_fallback`

JD/title/company and briefing remain **targeting/context only** (non-proof). Base resume JSON is labeled `BASE_RESUME_SOURCE` when ledger or SRFS is primary.

## Key modules

| Module | Role |
|--------|------|
| `apps_rg/runtime/proof_pool_resolver.py` | `resolve_section_proof_pool`, `SectionProofPool`, usage-ledger extension |
| `apps_rg/runtime/proof_pool_lane_integration.py` | `load_section_proof_for_lane`, `apply_proof_pool_to_usage_ledger` |
| `apps_rg/runtime/dispatch/input_authority_prompt_block.py` | CLAIM SUPPORT POOL vs TARGETING INPUTS in compiled prompts |
| Section lanes + PA modules | Per-lane wiring and `proof_pool_mode` in prompts |

## `--resume` forwarding

`canonical_dispatch` passes `base_resume_ref=str(resume_path)` into lane args. `load_section_proof_for_lane` records `base_resume_override_used` in receipts.

## Company-hint ledger slices

When role allocation returns an empty slice for `ibm_bullets`, `ibm_narrative`, or `unify_narrative`, resolver selects HIGH ledger rows whose company/claim text matches `ibm` or `unify` hints (bounded slice).

## Proof status

Contract tests pass for resolver behavior, usage-ledger fields, mock CLI runs, and competencies ledger slice. **No product ALLOW claim** — mock/offline-stub paths only unless a separate real provider run is executed.

## Gaps remaining

- Full U0 ingress redesign not in scope; section-only CLI still bypasses U0 package assembly.
- Ledger slices for IBM/Unify narrative may not map to canonical `bul_ibm_*` / employment fact IDs until SRFS or base fallback; mock paths remap indices for offline stub.
- Live Qwen quality proof not re-run in this wave.
