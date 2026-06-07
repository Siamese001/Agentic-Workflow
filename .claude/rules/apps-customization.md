
<!-- Converted from `.claude/rules/apps-customization.md`. Original Cursor trigger: `model_decision`. -->

# Apps_* Customization Guidance

> App-specific behavior belongs in `apps_lic/`, `apps_rg/`, `apps_qna/`, `apps_research/` — never in shared `agentic_core/`.

## App Ownership Model

| Component | Where It Belongs | NOT In Core |
|-----------|------------------|-------------|
| Ingress contract | `apps_*/config/domain_contract/` | ❌ `agentic_core/runtime/contracts/` |
| JSON schema | `apps_*/schemas/` | ❌ `agentic_core/schemas/` |
| Field map | `apps_*/config/domain_contract/` | ❌ `agentic_core/config/` |
| Route profile | `apps_*/config/domain_contract/l0_route_profile.yaml` | ❌ `agentic_core/L0_routing/` |
| Retrieval profile | `apps_*/config/domain_contract/c0_retrieval_profile.yaml` | ❌ `agentic_core/runtime/c0/` |
| Prompt profile | `apps_*/config/domain_contract/prompt_profile.yaml` | ❌ `agentic_core/prompt_governance/` |
| Cache policy | `apps_*/config/domain_contract/cache_policy.yaml` | ❌ `agentic_core/cache/` |
| Exit profile | `apps_*/config/domain_contract/exit_profile.yaml` | ❌ `agentic_core/runtime/exit/` |
| Judge/eval rubric | `apps_*/config/domain_contract/judge_rubric.yaml` | ❌ `agentic_core/L3_orchestration/exit_eval/` |
| Threshold profile | `apps_*/config/domain_contract/threshold_profile.yaml` | ❌ `agentic_core/config/` |
| Meta-feedback profile | `apps_*/config/domain_contract/meta_feedback_profile.yaml` | ❌ `agentic_core/L6_observability/` |
| App tests | `tests/unit/apps_*/`, `tests/_apps_contract/` | ❌ `tests/unit/agentic_core/` |

## U0 Runtime Customization Package

The **only** canonical path for app behavior to enter the governed spine:

```yaml
# apps_<name>/config/domain_contract/runtime_customization_package.yaml
package_version: "1.0"
package_digest: "sha256:..."

refs:
  # Intake
  ingress_contract: "apps_<name>/config/domain_contract/ingress_contract.yaml"
  schema: "apps_<name>/schemas/ingress_payload.json"
  field_map: "apps_<name>/config/domain_contract/field_map.yaml"
  
  # Layer profiles
  route_profile: "apps_<name>/config/domain_contract/l0_route_profile.yaml"
  retrieval_profile: "apps_<name>/config/domain_contract/c0_retrieval_profile.yaml"
  prompt_profile: "apps_<name>/config/domain_contract/prompt_profile.yaml"
  cache_policy: "apps_<name>/config/domain_contract/cache_policy.yaml"
  
  # Exit/eval
  exit_profile: "apps_<name>/config/domain_contract/exit_profile.yaml"
  judge_rubric: "apps_<name>/config/domain_contract/judge_rubric.yaml"
  threshold_profile: "apps_<name>/config/domain_contract/threshold_profile.yaml"
  
  # Learning
  meta_feedback_profile: "apps_<name>/config/domain_contract/meta_feedback_profile.yaml"
```

## What Stays in apps_*

**App-specific logic** (correct location):
- U0 intake validation (`apps_qna/u0_intake.py`)
- L0 route selection (`apps_qna/l0_router.py`)
- L1 planning (`apps_qna/l1_planner.py`)
- Prompt assembly templates
- Domain-specific validators
- App-specific egress logic
- App-specific judge implementations

**Never in apps_***:
- X3 Exit emission (only `agentic_core` Exit)
- Direct L4 writes (must go through UWG)
- Generic enforcement engines
- Cross-app contract propagation

## Adding New App Behavior

When adding new `apps_<name>` behavior:

1. **Profile First**: Define in `config/domain_contract/`
2. **Schema Second**: Update JSON schema if ingress changes
3. **Field Map Third**: Map fields for downstream layers
4. **Package Fourth**: Recalculate digest
5. **Tests Fifth**: Add to `tests/unit/apps_<name>/` or `tests/_apps_contract/`
6. **Receipt Sixth**: If touching core boundaries, update migration receipt
7. **Audit Seventh**: Run `/core-boundary-audit` workflow

## Forbidden in apps_*

These violate the spine:
- Implementing separate Exit layer
- Emitting X3 dispositions directly
- Writing to L4 state directly
- Direct side effects without Exit clearance
- Copy-pasting core enforcement logic

## Related

- `apps_lic/AGENTS.md`, `apps_rg/AGENTS.md`, etc. — App-specific rules
- Root `AGENTS.md` — Architecture law
- `.claude/rules/agentic-core-static.md` — Core guidance
- `/u0-customize-app` workflow — Canonical customization procedure
