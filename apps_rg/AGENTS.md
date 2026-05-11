# Apps_rg — App Customization Rules

> `apps_rg` owns domain customization for Resume Generation. All app-specific behavior lives here; `agentic_core` provides generic enforcement engines.

## App Ownership

`apps_rg` **owns**:
- Ingress contract (`contracts/`, `config/domain_contract/`)
- JSON schemas (`schemas/`)
- Field maps (`config/domain_contract/`)
- runtime_customization_package refs
- Route/retrieval/prompt profiles
- Cache policy profiles
- Runtime gate profiles
- Exit profiles
- Judge/eval/rubric profiles (e.g., `executive_positioning`)
- Threshold profiles
- Forbidden action/send policy
- Consent/compliance policy
- Write policy
- Learning/meta-feedback profiles
- Tests (`tests/unit/apps_rg/`, `tests/_apps_contract/`)
- Migration receipts for core bindings

## Core Boundaries

`apps_rg` **must NOT**:

1. **Implement separate Exit** — only `agentic_core` Exit emits X3
2. **Emit X3 directly** — use Exit profile (data), not Exit implementation
3. **Write L4 directly** — all durable writes go through Exit X3C → CommitRequest → UWG → L4
4. **Send directly or perform forbidden side effects** — must route through governed spine and clear Exit
5. **Add app-specific code to `agentic_core`** — use U0 package refs instead

## U0 Runtime Customization Package

`apps_rg` behavior enters `agentic_core` **only** through:

```
apps_rg/
  config/domain_contract/
    ingress_contract.yaml          → U0 validates
    schema/*.json                  → U0 validates
    field_map.yaml                 → U0 preserves
    runtime_customization_package/
      route_profile.yaml           → L0 consumes
      retrieval_profile.yaml       → C0 consumes
      prompt_profile.yaml          → PA consumes
      cache_policy.yaml            → Cache layer consumes
      exit_profile.yaml            → Exit consumes
      judge_rubric.yaml            → Eval consumes (executive_positioning)
      threshold_profile.yaml       → Exit gates consume
      meta_feedback_profile.yaml   → L6 consumes
```

### Package Structure

```yaml
# runtime_customization_package.yaml
package_version: "1.0"
package_digest: "sha256:..."

refs:
  ingress_contract: "apps_rg/config/domain_contract/ingress_contract.yaml"
  schema: "apps_rg/schemas/ingress_payload.json"
  field_map: "apps_rg/config/domain_contract/field_map.yaml"
  
  route_profile: "apps_rg/config/domain_contract/l0_route_profile.yaml"
  retrieval_profile: "apps_rg/config/domain_contract/c0_retrieval_profile.yaml"
  prompt_profile: "apps_rg/config/domain_contract/prompt_profile.yaml"
  cache_policy: "apps_rg/config/domain_contract/cache_policy.yaml"
  
  exit_profile: "apps_rg/config/domain_contract/exit_profile.yaml"
  judge_rubric: "apps_rg/config/domain_contract/judge_rubric.yaml"
  threshold_profile: "apps_rg/config/domain_contract/threshold_profile.yaml"
  
  meta_feedback_profile: "apps_rg/config/domain_contract/meta_feedback_profile.yaml"
```

## Existing Core Bindings

`apps_rg` has temporary bindings in `agentic_core/`:

| Binding | Layer | Status | Migration Target |
|---------|-------|--------|------------------|
| `apps_rg_l0_binding.py` | L0 | TEMPORARY_THIN_ADAPTER | Generic L0 + route profile |
| `apps_rg_l1_binding.py` | L1 | TEMPORARY_THIN_ADAPTER | Generic L1 + planning profile |
| `apps_rg_l2_binding.py` | L2 | TEMPORARY_THIN_ADAPTER | Generic L2 + execution profile |
| `apps_rg_c0_binding.py` | C0 | TEMPORARY_THIN_ADAPTER | Generic C0 + retrieval profile |
| `apps_rg_pa_binding.py` | PA | TEMPORARY_THIN_ADAPTER | Generic PA + prompt profile |
| `apps_rg_exit_binding.py` | Exit | TEMPORARY_THIN_ADAPTER | Generic Exit + Exit profile |
| `apps_rg_u0_adapter.py` | U0 | TEMPORARY_THIN_ADAPTER | Generic U0 + ingress contract |
| `u0_apps_rg_binding.py` | U0_Entry | TEMPORARY_THIN_ADAPTER | Generic U0 entry + package |

All bindings have migration receipts at `artifacts/governance/migration_receipts/`.

## Customization Checklist

When adding new `apps_rg` behavior:

- [ ] Profile defined in `config/domain_contract/`
- [ ] Schema updated if ingress changes
- [ ] Field map updated for new fields
- [ ] Package digest recalculated
- [ ] Tests added to `tests/unit/apps_rg/` or `tests/_apps_contract/`
- [ ] Receipt updated if touching core boundaries
- [ ] Boundary audit passes (see workflow `/core-boundary-audit`)

## Related

- Root `AGENTS.md` — Architecture law
- `agentic_core/AGENTS.md` — Core boundary rules
- `.windsurf/rules/apps-customization.md` — App customization guidance
- `.windsurf/rules/boundary-audit-required.md` — Audit triggers
