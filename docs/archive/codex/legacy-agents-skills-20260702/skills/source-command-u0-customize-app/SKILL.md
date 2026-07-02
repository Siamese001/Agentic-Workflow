---
name: "source-command-u0-customize-app"
description: "|"
---

# source-command-u0-customize-app

Use this skill when the user asks to run the migrated source command `u0-customize-app`.

## Command Template

# /u0-customize-app Workflow

## Slash-Command Purpose

Add or update app-specific behavior through the U0 runtime_customization_package. This is the canonical procedure for app customization that keeps app logic in `apps_*/` and uses generic core engines.

## Ordered Steps

### Step 1: App Audit

Read existing app structure:
```python
app_structure = {
    'config/domain_contract/': list_files(f'{app_name}/config/domain_contract/'),
    'schemas/': list_files(f'{app_name}/schemas/'),
    'existing_package': f'{app_name}/config/domain_contract/runtime_customization_package.yaml'
}
```

Verify package exists or create new.

### Step 2: Add or Update Profile

Create/update profile based on customization type:

**Route Profile:**
```yaml
# {app_name}/config/domain_contract/l0_route_profile.yaml
profile_version: "1.0"
profile_digest: "sha256:..."

route_policy:
  default_route: "<route_id>"
  conditional_routes:
    - condition: "<expression>"
      route: "<route_id>"
      gate_profile: "<gate_id>"
      
cache_policy_refs:
  r1a_bypass: "<profile_ref>"
  r1b_semantic: "<profile_ref>"
```

**Exit Profile:**
```yaml
# {app_name}/config/domain_contract/exit_profile.yaml
profile_version: "1.0"

exit_gates:
  - gate_id: "G21_CONTENT_SAFETY"
    required: true
    threshold: 0.85
    rubric: "<rubric_ref>"
  - gate_id: "G22_BRAND_VOICE"
    required: true
    threshold: 0.75

forbidden_actions:
  - action: "linkedin_send"
    exception_conditions: []
  - action: "email_outbox_send"
    exception_conditions: ["user_consented"]
```

**Threshold Profile:**
```yaml
# {app_name}/config/domain_contract/threshold_profile.yaml
profile_version: "1.0"

dimensions:
  - dim_id: "executive_positioning"
    grader_type: "llm_as_judge"
    min_required_score: 0.75
    weight: 1.0
    judge_retry_on_low: true
    
intentional_zero_dims: []
intentional_failopen_dims: []
```

### Step 3: Preserve U0 as Carrier Only

Ensure U0 implementation:
- Validates ingress contract
- Preserves field map
- Does NOT route, retrieve, execute, or approve
- Hands off to generic core engines

Verify U0 code pattern:
```python
def u0_intake(payload: dict) -> ValidatedRequest:
    """U0: Validate and preserve only."""
    # Validate
    validate(payload, load_schema(app_name))
    
    # Preserve
    field_map = load_field_map(app_name)
    
    # Package (do not route/execute)
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
  ingress_contract: "{app_name}/config/domain_contract/ingress_contract.yaml"
  schema: "{app_name}/schemas/ingress_payload.json"
  field_map: "{app_name}/config/domain_contract/field_map.yaml"
  
  # Updated/additional refs
  route_profile: "{app_name}/config/domain_contract/l0_route_profile.yaml"
  retrieval_profile: "{app_name}/config/domain_contract/c0_retrieval_profile.yaml"
  prompt_profile: "{app_name}/config/domain_contract/prompt_profile.yaml"
  cache_policy: "{app_name}/config/domain_contract/cache_policy.yaml"
  exit_profile: "{app_name}/config/domain_contract/exit_profile.yaml"
  judge_rubric: "{app_name}/config/domain_contract/judge_rubric.yaml"
  threshold_profile: "{app_name}/config/domain_contract/threshold_profile.yaml"
  meta_feedback_profile: "{app_name}/config/domain_contract/meta_feedback_profile.yaml"
```

### Step 5: Update Schema and Field Map

If ingress contract changes:
1. Update JSON schema
2. Update field map
3. Recalculate package digest

### Step 6: Add Tests

Create tests in canonical surfaces:

```python
# tests/unit/{app_name}/test_{customization}.py
def test_profile_loads():
    profile = load_profile(f'{app_name}/config/domain_contract/{type}_profile.yaml')
    assert profile['profile_version'] == '1.0'

def test_package_digest_validates():
    package = load_package(f'{app_name}/config/domain_contract/runtime_customization_package.yaml')
    assert verify_digest(package)

def test_core_consumes_profile():
    validated = u0_intake(test_payload, app_name='{app_name}')
    result = generic_engine.process(validated)  # Uses profile internally
    assert result is not None
```

### Step 7: Run Boundary Audit

Execute `/core-boundary-audit` workflow:
- Verify app logic stays in `apps_*/`
- Verify core remains generic
- Verify no leakage

### Step 8: Write Receipt

Generate customization receipt:

```json
{
  "receipt_version": "1.0",
  "workflow": "/u0-customize-app",
  "timestamp": "<ISO8601>",
  "app_name": "<app_name>",
  "customization_type": "route|exit|threshold|...",
  
  "files_created": [
    "{app_name}/config/domain_contract/{type}_profile.yaml"
  ],
  "files_modified": [
    "{app_name}/config/domain_contract/runtime_customization_package.yaml"
  ],
  
  "package_digest": "sha256:...",
  "new_digest_calculated": true,
  
  "tests_added": [
    "tests/unit/{app_name}/test_{customization}.py"
  ],
  
  "boundary_audit": {
    "outcome": "ALLOW",
    "receipt_path": "artifacts/governance/boundary_receipts/..."
  },
  
  "known_gaps": []
}
```

## Files Inspected

| File Pattern | Purpose |
|--------------|---------|
| `{app_name}/config/domain_contract/*.yaml` | App profiles |
| `{app_name}/config/domain_contract/runtime_customization_package.yaml` | Package |
| `{app_name}/schemas/*.json` | Schemas |
| `{app_name}/u0_intake.py` or equivalent | U0 implementation |
| `agentic_core/**/package_driven_*.py` | Generic engines |

## Classification Categories

Categories applied:

- `APPS_DECLARATIVE_CONFIG` — Created profiles
- `APPS_CONTRACT` — Ingress contracts
- `APPS_TEST` — Added tests
- `GENERIC_CORE_RUNTIME` — Generic engines (verified)
- `DOC_ALLOWED` — Documentation

## Expected Receipt

Path:
```
artifacts/governance/customization_receipts/<timestamp>_<app_name>_<type>.json
```

## Stop Conditions

This workflow **STOPS** when:

- U0 layer attempts routing/execution (not just validation)
- Profile fails schema validation
- Package digest mismatch
- Boundary audit detects leakage
- Missing required profile refs
- Core modification attempted

## Success Criteria

- [ ] Profile created in `config/domain_contract/`
- [ ] U0 layer validates and preserves only
- [ ] Package digest recalculated
- [ ] All required refs present
- [ ] Schema and field map updated if needed
- [ ] Tests added
- [ ] Boundary audit passes
- [ ] Receipt written

## Output

```
U0_CUSTOMIZE_APP: app=<app>, type=<type>, outcome=success, receipt=<path>
```

## Related

- Skill: `u0-app-customization`
- Skill: `runtime-package-verifier` (Step 4-5 verification)
- Skill: `core-boundary-audit` (Step 7)
- Workflow: `/core-boundary-audit`

## MANUAL MIGRATION REQUIRED

Migrated from source command `u0-customize-app` into a Codex skill. Invoke it as `$source-command-u0-customize-app` and manually rewrite any slash-command behavior that depended on provider-specific runtime expansion.

Review unsupported command metadata manually: `slash_command`, `tier`, `version`, `workflow_id`.
