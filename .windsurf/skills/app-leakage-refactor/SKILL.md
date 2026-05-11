---
skill_id: app-leakage-refactor
version: "1.0"
tier: 2
description: |
  Detect app-specific logic in agentic_core and migrate it to apps_* 
  profiles and generic core engines.
---

# App Leakage Refactor Skill

## Purpose

Detect app-specific logic in `agentic_core/` and guide its migration to `apps_*/` profiles and generic core engines. This is the canonical procedure for moving from `CORE_APP_SPECIFIC_LEAKAGE` or `TEMPORARY_THIN_ADAPTER` to `GENERIC_READY`.

## When to Use

Invoke this skill when:
- Detecting `CORE_APP_SPECIFIC_LEAKAGE` in audit
- Migrating `TEMPORARY_THIN_ADAPTER` to generic
- `/migrate-app-binding-to-generic-core` workflow triggered
- W5 binding migration wave
- Refactoring app-specific code out of core

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `leakage_file` | str | Yes | Path to file with app-specific logic |
| `app_name` | str | Yes | App the logic belongs to (e.g., "apps_lic") |
| `target_generic_engine` | str | Yes | Generic core file to extend |

## Steps

### Step 1: Detect App-Specific Logic

Identify app-specific patterns:

```python
LEAKAGE_PATTERNS = [
    r'if\s+app_id\s*==\s*["\']apps_\w+["\']',  # App ID branching
    r'["\']apps_\w+["\']\s*:\s*',  # App-specific dict keys
    r'APPS_\w+_\w+\s*=\s*\[',  # App-specific constants
    r'def\s+\w+_apps_\w+\(',  # App-prefixed functions
]
```

Classify what was found:
- Route logic → Move to L0 route profile
- Cache policy → Move to cache policy profile
- Exit gates → Move to Exit profile
- Judge thresholds → Move to threshold profile
- L6 policy → Move to meta-feedback profile

### Step 2: Move Behavior to App Profile

Extract app-specific behavior to `apps_*/config/domain_contract/`:

**Before (in core):**
```python
# agentic_core/L0_routing/route_selector.py - LEAKAGE!
if app_id == "apps_lic":
    return "R4_MANAGED_DRAFT"
elif app_id == "apps_rg":
    return "R1_RESUME_GENERATION"
```

**After (app profile):**
```yaml
# apps_lic/config/domain_contract/l0_route_profile.yaml
route_policy:
  default_route: "R1_STANDARD"
  conditional_routes:
    - condition: "payload.type == 'managed_draft'"
      route: "R4_MANAGED_DRAFT"
```

### Step 3: Create or Extend Generic Core Engine

Create/modify generic engine that consumes profiles:

```python
# agentic_core/L0_routing/package_driven_l0_binding.py
class PackageDrivenRouteSelector:
    def select_route(self, validated_request: ValidatedRequest) -> RouteContract:
        # Generic: reads from app profile
        route_profile = load_profile(
            validated_request.profile_refs['route_profile']
        )
        
        # Generic evaluation of conditions
        for conditional in route_profile['conditional_routes']:
            if evaluate_condition(conditional['condition'], validated_request):
                return RouteContract(route=conditional['route'])
        
        return RouteContract(route=route_profile['default_route'])
```

### Step 4: Replace Binding with Package-Driven Interpretation

Replace old binding with generic call:

**Before:**
```python
# Old temporary adapter
from agentic_core.L0_routing.apps_lic_l0_binding import select_route
route = select_route(app_id, payload)
```

**After:**
```python
# Generic engine + app profile
from agentic_core.L0_routing.package_driven_l0_binding import PackageDrivenRouteSelector
selector = PackageDrivenRouteSelector()
route = selector.select_route(validated_request)  # Uses app profile internally
```

### Step 5: Prove Behavior Unchanged with Tests

Create tests verifying migration preserved behavior:

```python
# tests/_apps_contract/test_apps_lic_route_migration.py
def test_route_selection_unchanged_after_migration():
    # Given same input
    payload = create_test_payload(type='managed_draft')
    
    # When routed through generic engine + app profile
    validated = u0_validate(payload, app_name='apps_lic')
    route = PackageDrivenRouteSelector().select_route(validated)
    
    # Then behavior matches pre-migration
    assert route.route == "R4_MANAGED_DRAFT"
```

### Step 6: Write Migration Receipt

Document the migration:

```json
{
  "receipt_version": "1.0",
  "migration_id": "uuid",
  "timestamp": "2026-05-11T12:00:00Z",
  "original_binding": "agentic_core/L0_routing/apps_lic_l0_binding.py",
  "target_state": "GENERIC_READY",
  "generic_engine": "agentic_core/L0_routing/package_driven_l0_binding.py",
  "app_profile_created": "apps_lic/config/domain_contract/l0_route_profile.yaml",
  "tests_added": [
    "tests/_apps_contract/test_apps_lic_route_migration.py"
  ],
  "behavior_preserved": true,
  "binding_deleted": true,
  "verification_command": "pytest tests/_apps_contract/test_apps_lic_route_migration.py -v"
}
```

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `app_profile_created` | str | Path to new app profile |
| `generic_engine_modified` | str | Path to modified generic engine |
| `old_binding_deleted` | bool | Whether binding was removed |
| `migration_receipt_path` | str | Path to written receipt |
| `tests_created` | List[str] | Migration verification tests |

## Blocking Conditions

This skill **BLOCKS** when:
- App profile not created
- Generic engine not extended
- Behavior not preserved (tests fail)
- Migration receipt not written
- Old binding not deleted after migration
- No test coverage for migrated behavior

## Required Receipt Path

Migration receipt:
```
artifacts/governance/migration_receipts/<timestamp>_<app_name>_<layer>_migration.json
```

## Acceptance Criteria

- [ ] App-specific logic identified and classified
- [ ] App profile created in `apps_*/config/domain_contract/`
- [ ] Generic core engine created or extended
- [ ] Core binding replaced with generic call
- [ ] Tests prove behavior unchanged
- [ ] Old binding deleted
- [ ] Migration receipt written
- [ ] `/core-boundary-audit` passes post-migration

## Classification Categories Used

- `TEMPORARY_THIN_ADAPTER` → `GENERIC_READY` (migration target)
- `CORE_APP_SPECIFIC_LEAKAGE` → Must migrate
- `APPS_DECLARATIVE_CONFIG` — Created profiles
- `GENERIC_CORE_RUNTIME` — Generic engines

## Related

- Workflow: `/migrate-app-binding-to-generic-core`
- Skill: `core-boundary-audit` (detects what needs migration)
- Skill: `u0-app-customization` (creates app profiles)
