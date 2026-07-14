---
name: u0-app-customization
description: |
  Invoke when creating, revising, or validating an app's U0 runtime_customization_package or
  its route, retrieval, prompt, exit, judge, threshold, cache, meta-feedback, ingress, schema,
  field-map, and profile-reference contracts. Enforce declarative app ownership and the
  carrier-only U0 boundary.
---

# U0 App Customization Skill

## Purpose

Guide the canonical procedure for adding or updating `apps_*` behavior through the U0 runtime_customization_package, ensuring app-specific logic stays in `apps_*/` and uses profile refs rather than hardcoding in core.

## When to Use

Invoke this skill when:
- Adding new app-specific behavior
- Updating existing app profiles
- Creating new route/retrieval/prompt/exit profiles
- Modifying app ingress contracts
- `/u0-customize-app` workflow is triggered
- Need to verify U0 package structure

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `app_name` | str | Yes | e.g., "apps_lic", "apps_rg" |
| `customization_type` | Enum | Yes | route, retrieval, prompt, exit, judge, threshold, cache, meta_feedback |
| `existing_package_path` | str | No | Path to existing runtime_customization_package.yaml |
| `new_profile_content` | Dict | Yes | Profile specification |

## Steps

### Step 1: Audit Existing App Contracts

Read existing app structure:
```
apps_<name>/
  config/domain_contract/
    runtime_customization_package.yaml
    <profile_type>_profile.yaml
    ingress_contract.yaml
    field_map.yaml
  schemas/
    *.json
```

Verify package exists and is valid.

### Step 2: Add or Update Profile

Create/update profile in correct location:

```yaml
# apps_<name>/config/domain_contract/<type>_profile.yaml
profile_version: "1.0"
profile_digest: "sha256:..."

refs:
  # Profile-specific configuration
  # (varies by profile type)

# Route profile example:
route_policy:
  default_route: "R1_STANDARD"
  conditional_routes:
    - condition: "payload.type == 'managed_draft'"
      route: "R4_MANAGED_DRAFT"
      gate_profile: "final_draft_pre_publish"

# Exit profile example:
exit_gates:
  - gate_id: "G21_CONTENT_SAFETY"
    required: true
    threshold: 0.85
  - gate_id: "G22_BRAND_VOICE"
    required: true
    threshold: 0.75
```

### Step 3: Preserve U0 as Carrier Only

Ensure U0 layer:
- Validates ingress contract
- Preserves field map
- Does NOT route, retrieve, execute, or approve
- Hands off to generic core engines

U0 code should look like:
```python
def u0_intake(payload: dict) -> ValidatedRequest:
    # Validate against schema
    validate(payload, ingress_schema)
    
    # Preserve field map
    field_map = load_field_map(app_name)
    
    # Package for core
    return ValidatedRequest(
        app_payload=payload,
        field_map=field_map,
        package_digest=calculate_digest(payload)
    )
```

### Step 4: Add Profile Refs and Digests

Update `runtime_customization_package.yaml`:

```yaml
package_version: "1.0"
package_digest: "sha256:<recalculate>"

refs:
  ingress_contract: "apps_<name>/config/domain_contract/ingress_contract.yaml"
  schema: "apps_<name>/schemas/ingress_payload.json"
  field_map: "apps_<name>/config/domain_contract/field_map.yaml"
  
  # Updated refs
  route_profile: "apps_<name>/config/domain_contract/l0_route_profile.yaml"
  retrieval_profile: "apps_<name>/config/domain_contract/c0_retrieval_profile.yaml"
  prompt_profile: "apps_<name>/config/domain_contract/prompt_profile.yaml"
  cache_policy: "apps_<name>/config/domain_contract/cache_policy.yaml"
  exit_profile: "apps_<name>/config/domain_contract/exit_profile.yaml"
  judge_rubric: "apps_<name>/config/domain_contract/judge_rubric.yaml"
  threshold_profile: "apps_<name>/config/domain_contract/threshold_profile.yaml"
  meta_feedback_profile: "apps_<name>/config/domain_contract/meta_feedback_profile.yaml"
```

### Step 5: Update Schema and Field Map

If ingress contract changes:
- Update JSON schema
- Update field map for downstream layers
- Recalculate package digest

### Step 6: Add Tests

Create tests in canonical surfaces:
- `tests/unit/apps_<name>/` — Unit tests
- `tests/_apps_contract/` — Contract tests

Tests must verify:
- Profile loads correctly
- Package digest validates
- Core engines consume profile
- No leakage to core

### Step 7: Run Boundary Audit

Invoke `/core-boundary-audit` workflow to verify:
- App logic stays in `apps_*/`
- Core remains generic
- No leakage detected

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `updated_package_path` | str | Path to updated package |
| `new_profile_paths` | List[str] | Created/updated profiles |
| `new_digest` | str | SHA256 of package |
| `test_paths` | List[str] | Test files created |
| `boundary_audit_passed` | bool | Audit result |

## Blocking Conditions

This skill **BLOCKS** when:
- Attempting to add app-specific logic to `agentic_core/`
- U0 layer tries to route/retrieve/execute (not just validate/preserve)
- Profile digest mismatch
- Schema validation fails
- Boundary audit detects leakage
- Missing required profile refs

## Required Receipt Path

Customization receipt:
```
artifacts/governance/customization_receipts/<timestamp>_<app_name>_<type>.json
```

Receipt includes:
- App name
- Customization type
- Files created/modified
- Package digest
- Test coverage
- Boundary audit result

## Acceptance Criteria

- [ ] Profile created in `apps_<name>/config/domain_contract/`
- [ ] U0 layer validates and preserves only (no routing/execution)
- [ ] Package digest recalculated
- [ ] All required refs present in package
- [ ] Schema and field map updated if needed
- [ ] Tests added to canonical surfaces
- [ ] Boundary audit passes
- [ ] Receipt written

## Classification Categories Used

- `APPS_DECLARATIVE_CONFIG` — Profile YAML files
- `APPS_CONTRACT` — Ingress contracts
- `APPS_TEST` — Test files
- `DOC_ALLOWED` — Documentation
- `GENERIC_CORE_RUNTIME` — Core remains generic

## Related

- Workflow: `/u0-customize-app`
- Rule: `.codex/rules/apps-customization.md`
- Skill: `core-boundary-audit` (Step 7)
