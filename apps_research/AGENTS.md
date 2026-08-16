# Apps_research — App Customization Rules

> `apps_research` owns Company Research Brief customization. Follow the shared [App Agent Contract](../apps_shared/APP_AGENT_CONTRACT.md) for ownership, core boundaries, U0 package structure, checklist, and related authority.

## Local ingress

- Ingress contract: `config/domain_contract/`
- Schemas: `schemas/`
- App tests: `tests/unit/apps_research/`, `tests/_apps_contract/`

## Existing Core Bindings

`apps_research` has temporary bindings in `agentic_core/`:

| Binding | Layer | Status | Migration Target |
|---------|-------|--------|------------------|
| `apps_research_l0_binding.py` | L0 | TEMPORARY_THIN_ADAPTER | Generic L0 + route profile |
| `apps_research_l0_binding_v2.py` | L0 | TEMPORARY_THIN_ADAPTER | Consolidate with v1 first |
| `apps_research_l1_binding.py` | L1 | TEMPORARY_THIN_ADAPTER | Generic L1 + planning profile |
| `apps_research_l1_binding_v2.py` | L1 | TEMPORARY_THIN_ADAPTER | Consolidate with v1 first |
| `apps_research_l2_binding.py` | L2 | TEMPORARY_THIN_ADAPTER | Generic L2 + execution profile |
| `apps_research_c0_binding.py` | C0 | TEMPORARY_THIN_ADAPTER | Generic C0 + retrieval profile |
| `apps_research_pa_binding.py` | PA | TEMPORARY_THIN_ADAPTER | Generic PA + prompt profile |
| `apps_research_exit_binding.py` | Exit | TEMPORARY_THIN_ADAPTER | Generic Exit + Exit profile |
| `u0_apps_research_binding.py` | U0_Entry | TEMPORARY_THIN_ADAPTER | Generic U0 entry + package |
| `u0_apps_research_binding_v2.py` | U0_Entry | TEMPORARY_THIN_ADAPTER | Consolidate with v1 first |

**Note**: Versioned bindings (v2) indicate ongoing consolidation. Merge v1/v2 before migration to generic engines.
