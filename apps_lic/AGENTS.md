# Apps_lic — App Customization Rules

> `apps_lic` owns Life Insurance Commission customization. Follow the shared [App Agent Contract](../apps_shared/APP_AGENT_CONTRACT.md) for ownership, core boundaries, U0 package structure, checklist, and related authority.

## Local ingress

- Ingress contract: `contracts/`, `config/domain_contract/`
- Schemas: `schemas/`
- App tests: `tests/unit/apps_lic/`, `tests/_apps_contract/`

## Existing Core Bindings

`apps_lic` has temporary bindings in `agentic_core/`:

| Binding | Layer | Status | Migration Target |
|---------|-------|--------|------------------|
| `apps_lic_l0_binding.py` | L0 | TEMPORARY_THIN_ADAPTER | Generic L0 + route profile |
| `apps_lic_l1_binding.py` | L1 | TEMPORARY_THIN_ADAPTER | Generic L1 + planning profile |
| `apps_lic_l2_binding.py` | L2 | TEMPORARY_THIN_ADAPTER | Generic L2 + execution profile |
| `apps_lic_l3_binding.py` | L3 | TEMPORARY_THIN_ADAPTER | Generic L3 + workflow profile |
| `apps_lic_c0_binding.py` | C0 | TEMPORARY_THIN_ADAPTER | Generic C0 + retrieval profile |
| `apps_lic_pa_binding.py` | PA | TEMPORARY_THIN_ADAPTER | Generic PA + prompt profile |
| `apps_lic_exit_binding.py` | Exit | TEMPORARY_THIN_ADAPTER | Generic Exit + Exit profile |
| `apps_lic_promo_binding.py` | L6 | TEMPORARY_THIN_ADAPTER | Generic L6 + meta-feedback profile |
| `apps_lic_u0_adapter.py` | U0 | TEMPORARY_THIN_ADAPTER | Generic U0 + ingress contract |
| `u0_apps_lic_binding.py` | U0_Entry | TEMPORARY_THIN_ADAPTER | Generic U0 entry + package |

All bindings have migration receipts at `artifacts/governance/migration_receipts/`.
