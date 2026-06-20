# Apps_qna — App Customization Rules

> `apps_qna` owns domain customization for Interview Q&A support. All app-specific behavior lives here; `agentic_core` provides generic enforcement engines.

## App Ownership

`apps_qna` **owns**:
- Ingress contract (`contracts/`, `config/domain_contract/`)
- JSON schemas (`schemas/`)
- Field maps (`config/domain_contract/`)
- runtime_customization_package refs
- Route/retrieval/prompt profiles
- Cache policy profiles
- Runtime gate profiles
- Exit profiles
- Judge/eval/rubric profiles
- Threshold profiles
- Forbidden action/send policy
- Consent/compliance policy
- Write policy
- Learning/meta-feedback profiles
- Tests (`tests/unit/apps_qna/`, `tests/_apps_contract/`)
- Migration receipts for any core bindings

## Core Boundaries

`apps_qna` **must NOT**:

1. **Implement separate Exit** — only `agentic_core` Exit emits X3
2. **Emit X3 directly** — use Exit profile (data), not Exit implementation
3. **Write L4 directly** — all durable writes go through Exit X3C → CommitRequest → UWG → L4
4. **Send directly or perform forbidden side effects** — must route through governed spine and clear Exit
5. **Add app-specific code to `agentic_core`** — use U0 package refs instead

## U0 Runtime Customization Package

`apps_qna` behavior enters `agentic_core` **only** through:

```
apps_qna/
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
      judge_rubric.yaml            → Eval consumes
      threshold_profile.yaml       → Exit gates consume
      meta_feedback_profile.yaml   → L6 consumes
```

### Package Structure

```yaml
# runtime_customization_package.yaml
package_version: "1.0"
package_digest: "sha256:..."

refs:
  ingress_contract: "apps_qna/config/domain_contract/ingress_contract.yaml"
  schema: "apps_qna/schemas/ingress_payload.json"
  field_map: "apps_qna/config/domain_contract/field_map.yaml"
  
  route_profile: "apps_qna/config/domain_contract/l0_route_profile.yaml"
  retrieval_profile: "apps_qna/config/domain_contract/c0_retrieval_profile.yaml"
  prompt_profile: "apps_qna/config/domain_contract/prompt_profile.yaml"
  cache_policy: "apps_qna/config/domain_contract/cache_policy.yaml"
  
  exit_profile: "apps_qna/config/domain_contract/exit_profile.yaml"
  judge_rubric: "apps_qna/config/domain_contract/judge_rubric.yaml"
  threshold_profile: "apps_qna/config/domain_contract/threshold_profile.yaml"
  
  meta_feedback_profile: "apps_qna/config/domain_contract/meta_feedback_profile.yaml"
```

## Core Bindings Status

`apps_qna` currently has **no temporary bindings** in `agentic_core/`. All customization happens through:
- `apps_qna/u0_intake.py` — U0-level intake (app-owned)
- `apps_qna/l0_router.py` — L0 routing (app-owned)
- `apps_qna/l1_planner.py` — L1 planning (app-owned)
- `apps_qna/cert/fec_producer.py` — FEC production (app-owned)

This is the **target state** — app logic stays in `apps_qna/`, core provides generic enforcement.

## Customization Checklist

When adding new `apps_qna` behavior:

- [ ] Profile defined in `config/domain_contract/`
- [ ] Schema updated if ingress changes
- [ ] Field map updated for new fields
- [ ] Package digest recalculated
- [ ] Tests added to `tests/unit/apps_qna/` or `tests/_apps_contract/`
- [ ] Receipt created if touching core boundaries
- [ ] Boundary audit passes (see workflow `/core-boundary-audit`)

## Related

- Root `AGENTS.md` — Architecture law
- `agentic_core/AGENTS.md` — Core boundary rules
- `.codex/rules/apps-customization.md` — App customization guidance
- `.codex/rules/boundary-audit-required.md` — Audit triggers
