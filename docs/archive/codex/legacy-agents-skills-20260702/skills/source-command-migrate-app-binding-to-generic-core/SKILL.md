---
name: "source-command-migrate-app-binding-to-generic-core"
description: "|"
---

# source-command-migrate-app-binding-to-generic-core

Use this skill when the user asks to run the migrated source command `migrate-app-binding-to-generic-core`.

## Command Template

# /migrate-app-binding-to-generic-core Workflow

## Slash-Command Purpose

Migrate a `TEMPORARY_THIN_ADAPTER` binding from `agentic_core/` to the target state: generic core engine consuming app-owned profile. This is the canonical procedure for W5 binding migration.

## Ordered Steps

### Step 1: Identify Binding

Specify the binding to migrate:

```python
binding_to_migrate = {
    'file': 'agentic_core/L0_routing/apps_lic_l0_binding.py',
    'app_name': 'apps_lic',
    'layer': 'L0',
    'current_status': 'TEMPORARY_THIN_ADAPTER',
    'target_status': 'GENERIC_READY'
}
```

Verify binding exists and has current migration receipt.

### Step 2: Extract App Policy

Analyze binding to extract app-specific behavior:

```python
# Read binding file
binding_content = read_file(binding_to_migrate['file'])

# Extract app-specific logic
app_policy = {
    'route_selection_rules': extract_route_rules(binding_content),
    'hardcoded_routes': extract_hardcoded_routes(binding_content),
    'app_specific_conditions': extract_conditions(binding_content),
    'gate_references': extract_gate_refs(binding_content)
}

# Classify extracted logic
for rule in app_policy['route_selection_rules']:
    if 'apps_lic' in rule:
        rule['classification'] = 'APP_SPECIFIC'
        rule['migration_target'] = 'apps_lic route profile'
```

### Step 3: Create App Profile

Create declarative profile in `apps_*/config/domain_contract/`:

**For L0 routing migration:**
```yaml
# apps_lic/config/domain_contract/l0_route_profile.yaml
profile_version: "1.0"
profile_digest: "sha256:..."

# Migrated from apps_lic_l0_binding.py
route_policy:
  default_route: "R1_STANDARD"
  
  conditional_routes:
    # Was: if app_id == "apps_lic" and payload.type == "managed_draft"
    - condition: "payload.type == 'managed_draft'"
      route: "R4_MANAGED_DRAFT"
      gate_profile: "final_draft_pre_publish"
      
    # Was: if app_id == "apps_lic" and payload.priority == "urgent"
    - condition: "payload.priority == 'urgent'"
      route: "R2_EXPEDITED"
      gate_profile: "urgent_review"

cache_policies:
  r1a_exact:
    bypass_conditions: []
  r1b_semantic:
    bypass_conditions: []
    
final_draft_routes:
  - "R4_MANAGED_DRAFT"
  - "R3R4_MANAGED_RESEARCH_THEN_DRAFT"
```

**For Exit migration:**
```yaml
# apps_lic/config/domain_contract/exit_profile.yaml
profile_version: "1.0"

exit_gates:
  # Migrated from apps_lic_exit_binding.py
  - gate_id: "G21_CONTENT_SAFETY"
    required: true
    threshold: 0.85
    rubric: "apps_lic/config/domain_contract/rubrics/content_safety.yaml"
    
  - gate_id: "G22_BRAND_VOICE"
    required: true
    threshold: 0.75
    
forbidden_actions:
  - action: "linkedin_send"
    exception_conditions: []
  - action: "email_outbox_send"
    exception_conditions: ["user_consented", "exit_profile.approved"]
```

### Step 4: Extend Generic Core Engine

Create or modify generic engine:

```python
# agentic_core/L0_routing/package_driven_l0_binding.py

class PackageDrivenRouteSelector:
    """Generic L0 routing using app profiles."""
    
    def select_route(self, validated_request: ValidatedRequest) -> RouteContract:
        """Select route using app profile, not hardcoded logic."""
        # Load app profile from package
        route_profile = load_yaml(
            validated_request.profile_refs['route_profile']
        )
        
        # Evaluate conditions (generic, not app-specific)
        for conditional in route_profile.get('conditional_routes', []):
            if self._evaluate_condition(
                conditional['condition'], 
                validated_request.app_payload
            ):
                return RouteContract(
                    route=conditional['route'],
                    gate_profile=conditional.get('gate_profile')
                )
        
        # Default route
        return RouteContract(route=route_profile['default_route'])
    
    def _evaluate_condition(self, condition: str, payload: dict) -> bool:
        """Generic condition evaluation (safe subset)."""
        # Safe evaluation - no arbitrary code execution
        return evaluate_safe_expression(condition, payload)
```

### Step 5: Replace Binding with Generic Call

Update call sites to use generic engine:

**Before:**
```python
# Direct binding call
from apps_lic.runtime.bindings.l0_binding import select_route
route = select_route(app_id='apps_lic', payload=payload)
```

**After:**
```python
# Generic engine + app profile
from agentic_core.L0_routing.package_driven_l0_binding import PackageDrivenRouteSelector

validated = u0_validate(payload, app_name='apps_lic')
selector = PackageDrivenRouteSelector()
route = selector.select_route(validated)  # Uses profile internally
```

### Step 6: Prove Behavior Unchanged

Create comprehensive tests:

```python
# tests/_apps_contract/test_apps_lic_l0_migration.py

class TestAppsLicL0Migration:
    """Verify L0 routing behavior preserved after migration."""
    
    def test_managed_draft_route_unchanged(self):
        """Was: if type == 'managed_draft' -> R4_MANAGED_DRAFT"""
        payload = create_payload(type='managed_draft', priority='normal')
        
        # New path: generic engine + app profile
        validated = u0_validate(payload, app_name='apps_lic')
        route = PackageDrivenRouteSelector().select_route(validated)
        
        assert route.route == "R4_MANAGED_DRAFT"
        assert route.gate_profile == "final_draft_pre_publish"
    
    def test_urgent_route_unchanged(self):
        """Was: if priority == 'urgent' -> R2_EXPEDITED"""
        payload = create_payload(type='standard', priority='urgent')
        
        validated = u0_validate(payload, app_name='apps_lic')
        route = PackageDrivenRouteSelector().select_route(validated)
        
        assert route.route == "R2_EXPEDITED"
    
    def test_default_route_unchanged(self):
        """Was: else -> R1_STANDARD"""
        payload = create_payload(type='standard', priority='normal')
        
        validated = u0_validate(payload, app_name='apps_lic')
        route = PackageDrivenRouteSelector().select_route(validated)
        
        assert route.route == "R1_STANDARD"
    
    def test_all_original_conditions_covered(self):
        """Ensure no conditions dropped during migration."""
        original_conditions = load_original_conditions(
            'agentic_core/L0_routing/apps_lic_l0_binding.py'
        )
        profile_conditions = load_profile_conditions(
            'apps_lic/config/domain_contract/l0_route_profile.yaml'
        )
        
        assert set(original_conditions) == set(profile_conditions)
```

Run tests:
```bash
python -m pytest tests/_apps_contract/test_apps_lic_l0_migration.py -v
```

### Step 7: Write Migration Receipt

Document the completed migration:

```json
{
  "receipt_version": "1.0",
  "workflow": "/migrate-app-binding-to-generic-core",
  "migration_id": "<uuid>",
  "timestamp": "<ISO8601>",
  
  "original_binding": {
    "file": "agentic_core/L0_routing/apps_lic_l0_binding.py",
    "layer": "L0",
    "app": "apps_lic",
    "classification": "TEMPORARY_THIN_ADAPTER"
  },
  
  "target_state": {
    "classification": "GENERIC_READY",
    "generic_engine": "agentic_core/L0_routing/package_driven_l0_binding.py",
    "app_profile": "apps_lic/config/domain_contract/l0_route_profile.yaml"
  },
  
  "files_created": [
    "apps_lic/config/domain_contract/l0_route_profile.yaml",
    "tests/_apps_contract/test_apps_lic_l0_migration.py"
  ],
  
  "files_modified": [
    "agentic_core/L0_routing/package_driven_l0_binding.py"
  ],
  
  "files_deleted": [
    "agentic_core/L0_routing/apps_lic_l0_binding.py"
  ],
  
  "verification": {
    "tests_created": 4,
    "tests_passing": 4,
    "behavior_preserved": true,
    "boundary_audit_passed": true
  },
  
  "known_gaps": [],
  
  "acceptance_criteria": [
    "App profile created and valid",
    "Generic engine extended",
    "Original binding deleted",
    "All tests passing",
    "Boundary audit clean"
  ]
}
```

## Files Inspected

| File Pattern | Purpose |
|--------------|---------|
| `agentic_core/**/apps_*_*.py` | Bindings to migrate |
| `apps_*/config/domain_contract/` | Profile destination |
| `agentic_core/**/package_driven_*.py` | Generic engines |
| `tests/_apps_contract/` | Migration tests |
| `artifacts/governance/migration_receipts/` | Existing receipts |

## Classification Categories

Categories applied during migration:

- `TEMPORARY_THIN_ADAPTER` → `GENERIC_READY` (source → target)
- `CORE_APP_SPECIFIC_LEAKAGE` → Must migrate
- `APPS_DECLARATIVE_CONFIG` — Created profiles
- `GENERIC_CORE_RUNTIME` — Generic engines
- `GENERIC_INFRASTRUCTURE` — Infrastructure
- `MIGRATION_REQUIRED` — Documented for tracking
- `TEST_ALLOWED` — Migration verification tests

## Expected Receipt

Path:
```
artifacts/governance/migration_receipts/<timestamp>_<app>_<layer>_migration.json
```

## Stop Conditions

This workflow **STOPS** when:

- Original binding not found
- Migration receipt not current
- App profile creation fails
- Generic engine extension fails
- Tests fail (behavior not preserved)
- Boundary audit fails post-migration
- User explicitly cancels

## Success Criteria

- [ ] App-specific logic identified and extracted
- [ ] App profile created in `apps_*/config/domain_contract/`
- [ ] Generic core engine created or extended
- [ ] Original binding replaced with generic call
- [ ] Comprehensive tests prove behavior unchanged
- [ ] All tests passing
- [ ] Original binding deleted
- [ ] Migration receipt written
- [ ] `/core-boundary-audit` passes

## Output

```
MIGRATE_APP_BINDING: app=<app>, layer=<layer>, outcome=success, receipt=<path>
```

## Related

- Skill: `app-leakage-refactor`
- Skill: `u0-app-customization` (profile creation)
- Skill: `core-boundary-audit` (post-migration verification)
- Workflow: `/core-boundary-audit`
- Plan W5: Binding migration wave

## MANUAL MIGRATION REQUIRED

Migrated from source command `migrate-app-binding-to-generic-core` into a Codex skill. Invoke it as `$source-command-migrate-app-binding-to-generic-core` and manually rewrite any slash-command behavior that depended on provider-specific runtime expansion.

Review unsupported command metadata manually: `slash_command`, `tier`, `version`, `workflow_id`.
