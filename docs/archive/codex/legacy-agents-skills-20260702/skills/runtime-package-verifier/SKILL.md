---
name: "runtime-package-verifier"
description: "|"
---

# Runtime Package Verifier Skill

## Purpose

Verify that a `apps_*` runtime_customization_package is complete, valid, and ready for handoff to `agentic_core` generic engines. Ensures required refs exist, digest is current, schema validates, and no pointers are dropped.

## When to Use

Invoke this skill when:
- Before U0 hands off to core
- After modifying any app profile
- `/u0-customize-app` workflow verification step
- Pre-commit verification
- CI validation step

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `package_path` | str | Yes | Path to runtime_customization_package.yaml |
| `app_name` | str | Yes | e.g., "apps_lic" |
| `validate_digests` | bool | No | If True, verify all referenced file digests |

## Steps

### Step 1: Verify Required Refs

Check all required refs present in package:

```yaml
required_refs:
  - ingress_contract
  - schema
  - field_map
  - route_profile
  - retrieval_profile
  - prompt_profile
  - cache_policy
  - exit_profile
  - judge_rubric
  - threshold_profile
  - meta_feedback_profile
```

For each ref:
- Verify path is non-empty
- Verify file exists at referenced path
- Verify file is readable

### Step 2: Verify Package Digest

Calculate expected digest:
```python
import hashlib
import json

# Load all referenced files
files_content = {}
for ref_name, ref_path in package['refs'].items():
    with open(ref_path) as f:
        files_content[ref_name] = f.read()

# Calculate package digest
package_str = json.dumps(files_content, sort_keys=True)
expected_digest = hashlib.sha256(package_str.encode()).hexdigest()

# Verify against stored digest
assert package['package_digest'] == expected_digest, "Digest mismatch!"
```

### Step 3: Verify Schema and Field Map

Validate schema:
- Load schema from `refs.schema`
- Verify it's valid JSON Schema
- Check all required fields defined

Validate field map:
- Load field map from `refs.field_map`
- Verify all schema fields mapped
- Verify no duplicate mappings
- Verify downstream layer fields covered

### Step 4: Verify No Dropped Pointers

Check for pointer integrity:
- All `refs` resolve to existing files
- No circular refs
- No orphaned profiles (referenced but not used)
- All required profile sections present

### Step 5: Verify Package Reaches ValidatedRequest

Verify U0 produces `ValidatedRequest` with:
```python
ValidatedRequest(
    app_payload=payload,           # Original ingress
    field_map=field_map,            # Preserved mappings
    package_digest=package_digest,  # Verified digest
    profile_refs=package['refs']     # All refs available
)
```

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `verification_passed` | bool | Overall result |
| `refs_status` | Dict[str, bool] | Per-ref verification |
| `digest_valid` | bool | Digest verification result |
| `schema_valid` | bool | Schema validation result |
| `field_map_valid` | bool | Field map validation result |
| `pointers_intact` | bool | Pointer integrity result |
| `errors` | List[str] | Any verification failures |

## Blocking Conditions

This skill **BLOCKS** when:
- Required ref missing from package
- Referenced file does not exist
- Package digest mismatch
- Schema validation fails
- Field map incomplete
- Dropped pointers detected
- `ValidatedRequest` would be incomplete

## Required Receipt Path

Verification receipt (optional for passing, required for failures):
```
artifacts/governance/verification_receipts/<timestamp>_<app_name>_package.json
```

Receipt includes:
- Verification results for each step
- Any errors found
- Recommended fixes

## Acceptance Criteria

- [ ] All required refs present
- [ ] All referenced files exist
- [ ] Package digest validates
- [ ] Schema is valid JSON Schema
- [ ] Field map covers all required fields
- [ ] No dropped pointers
- [ ] `ValidatedRequest.app_payload` would be complete

## Classification Categories Used

- `APPS_DECLARATIVE_CONFIG` — Package and profiles
- `GENERIC_CORE_RUNTIME` — Core consumption interface
- `APPS_TEST` — Verification tests

## Related

- Workflow: `/u0-customize-app` (verification step)
- Skill: `u0-app-customization` (creates packages this skill verifies)
