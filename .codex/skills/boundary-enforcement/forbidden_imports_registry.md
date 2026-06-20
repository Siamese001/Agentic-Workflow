# Forbidden Imports Registry

Authoritative list of forbidden import patterns and their canonical replacements.

## Registry

| Forbidden Import | Reason | Canonical Alternative |
|---|---|---|
| `structure_blueprint.ssot` | Archived — use constants | Use inline constants or `config/` layer |
| `base_agents.timeout_decorator` | Wrong location | `agentic_core.L0_routing.utils.timeout_decorator` |
| `from archives.*` | Archive graveyard | Find canonical location in `agentic_core/` or `apps_*/` |
| Runtime `import X` inside functions (structural) | Circular import risk | Module-level import only |

## Adding to This Registry

When a new forbidden pattern is identified:
1. Add row to the table above
2. Document the CI gate that enforces it (if any)
3. Update `ops_scripts/ci/check_anti_patterns.py` if programmatic detection is needed
