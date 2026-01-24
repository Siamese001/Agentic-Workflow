# Legacy Archive

This folder contains deprecated/legacy code that has been moved from active `apps_shared/base_agents/` during the core standardization migration.

## Migration Completed (Jan 23, 2026)

The following core interfaces have been migrated to `agentic_core/utils/core_extensions/`:

- `CanonBaseAgentInterface` → `agentic_core/utils/core_extensions/canon_base_agent_interface.py`

## Updated Import References

All import references across the repository have been updated:
- `from apps_shared.base_agents.canon_base_agent_interface` → `from agentic_core.utils.core_extensions.canon_base_agent_interface`

## Validation

- ✅ Specialist agents (HOP1ProfileAnalysisAgent) initialize correctly
- ✅ Core interfaces import from new location
- ✅ Zero-loss migration completed

## Status

This folder is preserved for historical reference only. Active development should use the new `agentic_core` locations.
