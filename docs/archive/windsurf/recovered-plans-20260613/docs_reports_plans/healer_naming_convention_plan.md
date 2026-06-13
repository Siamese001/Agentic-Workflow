# Healer Naming Convention Plan

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Objective

Ensure all healer agents used in `execute_ssot.py` have "Healer" explicitly in their class names,
consistent with the `{Domain}ValidatorAgent` / `{Domain}HealerAgent` naming convention.

## Scope: N=6 files

### Files to CREATE (backward-compat shims per §26)
1. `agentic_core/L5_safety/reasoning/FileClassificationHealerAgent.py`
2. `agentic_core/L5_safety/reasoning/HierarchyHealerAgent.py`
3. `agentic_core/L5_safety/reasoning/GravityLeakHealerAgent.py`
4. `agentic_core/L5_safety/reasoning/FilesystemSSOTHealerAgent.py`

### Files to EDIT
5. `agentic_core/L0_routing/scripts/execute_ssot.py`
   - `_get_l5_agent_roster()` lines 382-405: update imports + return tuple
   - Destructuring assignment lines 5459-5470: update variable names
   - `agents` dict lines 5472-5482: update values

### Files to CREATE (test)
6. `tests/unit/agentic_core/L0_routing/scripts/test_healer_naming_convention.py`

## Rationale

- **Shim strategy**: 100+ files reference the old names. Renaming all would be an unbounded
  scope change. Instead, create new canonically-named shim files (imports only, per §26)
  and update `execute_ssot.py` to use the new names. Old files remain untouched for backward compat.
- **Not renamed**: `ArchitectureGovernorAgent` — dual-purpose (governor, not pure healer).
  `ArchitectureGovernorValidatorAgent.py` already exists as the pure validator.
- **Not renamed**: `state_mgr.update_agent()` string labels — display names, separate concern,
  risk of breaking dashboard tests.

## Rename Mapping

| Old Name | New Canonical Name | Role in execute_ssot |
|---|---|---|
| `FileClassificationAgent` | `FileClassificationHealerAgent` | Healer (file classification repairs) |
| `HierarchyAgent` | `HierarchyHealerAgent` | Healer (directory structure repairs) |
| `GravityLeakRepairAgent` | `GravityLeakHealerAgent` | Healer (layer inversion repairs) |
| `FilesystemSSOTReconcilerAgent` | `FilesystemSSOTHealerAgent` | Healer (filesystem drift reconciliation) |

## Shim Structure (per §26)

```python
"""<NewName> - canonical healer name alias for <OldName>."""
from agentic_core.L5_safety.reasoning.<OldModule> import <OldClass> as <NewClass>
__all__ = ["<NewClass>"]
```

## Acceptance Criteria

1. `execute_ssot.py._get_l5_agent_roster()` returns tuple using new canonical names
2. All 4 shim files import cleanly
3. New invariant test passes: verifies roster uses canonical healer names
4. Full `python -m pytest -q --color=no` passes

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

