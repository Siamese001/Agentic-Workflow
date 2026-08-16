# Shared App Agent Contract

> Read this contract with the root `AGENTS.md` and the local `apps_<name>/AGENTS.md`. It is the canonical contract for all application packages; each local file supplies only its domain-specific ownership and binding status.

## App ownership

Every `apps_<name>` package owns its ingress contract, JSON schemas, field maps, runtime-customization-package references, route/retrieval/prompt profiles, cache and runtime-gate profiles, Exit, judge/evaluation/rubric, threshold, forbidden-action/send, consent/compliance, write, and learning/meta-feedback profiles. It also owns its app and shared-contract tests, plus migration receipts for any core bindings.

## Core boundaries

An app must not:

1. Implement a separate Exit; only `agentic_core` Exit emits X3.
2. Emit X3 directly; use Exit-profile data rather than an Exit implementation.
3. Write L4 directly; durable writes flow through Exit X3C → CommitRequest → UWG → L4.
4. Send directly or perform forbidden side effects; route them through the governed spine and clear Exit.
5. Add app-specific code to `agentic_core`; use U0 package references unless a migration receipt authorizes the boundary change.

## U0 runtime customization package

App behavior enters `agentic_core` only through a package rooted in its own directory:

```
apps_<name>/
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

```yaml
# runtime_customization_package.yaml
package_version: "1.0"
package_digest: "sha256:..."

refs:
  ingress_contract: "apps_<name>/config/domain_contract/ingress_contract.yaml"
  schema: "apps_<name>/schemas/ingress_payload.json"
  field_map: "apps_<name>/config/domain_contract/field_map.yaml"

  route_profile: "apps_<name>/config/domain_contract/l0_route_profile.yaml"
  retrieval_profile: "apps_<name>/config/domain_contract/c0_retrieval_profile.yaml"
  prompt_profile: "apps_<name>/config/domain_contract/prompt_profile.yaml"
  cache_policy: "apps_<name>/config/domain_contract/cache_policy.yaml"

  exit_profile: "apps_<name>/config/domain_contract/exit_profile.yaml"
  judge_rubric: "apps_<name>/config/domain_contract/judge_rubric.yaml"
  threshold_profile: "apps_<name>/config/domain_contract/threshold_profile.yaml"

  meta_feedback_profile: "apps_<name>/config/domain_contract/meta_feedback_profile.yaml"
```

## Customization checklist

When adding app behavior:

- [ ] Define the profile in `config/domain_contract/`.
- [ ] Update schema if ingress changes.
- [ ] Update the field map for new fields.
- [ ] Recalculate the package digest.
- [ ] Add tests under `tests/unit/apps_<name>/` or `tests/_apps_contract/`.
- [ ] Create or update the migration receipt when touching a core boundary.
- [ ] Pass the boundary audit (workflow `/core-boundary-audit`).

## Related authority

- Root `AGENTS.md` — architecture law
- `agentic_core/AGENTS.md` — core boundary rules
- `.codex/rules/apps-customization.md` — app customization guidance
- `.codex/rules/boundary-audit-required.md` — audit triggers
