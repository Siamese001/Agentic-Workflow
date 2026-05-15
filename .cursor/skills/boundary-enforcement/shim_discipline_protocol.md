# Shim Discipline Protocol

When relocating any Python module or changing canonical import paths.

## Required Steps

1. **Create backward compatibility** — create `_shim.py` or `_compat.py` that re-exports from the new canonical location
2. **Document deprecation** — add `DeprecationWarning` with a minimum 90-day removal timeline
3. **Update references** — coordinate changes across all dependent files (use ADG fan-in to find them)
4. **Test compatibility** — verify both old and new import paths work during the transition period
5. **Schedule removal** — shim MUST be removed after the deprecation period (no permanent shims)

## Shim Requirements

- Must import from canonical location and re-export
- Must include `DeprecationWarning` with explicit timeline
- Must document canonical alternative in module docstring
- Must have a removal plan with a target date

## Forbidden

- Moving or renaming symbols without a shim
- Creating undocumented shims
- Silent breaking changes (no deprecation warning)
- Permanent shims without a removal plan

## Evidence Format

```
## SHIM_CREATED
**Old path**: old_module.SomeClass
**New path**: new_location.canonical_module.SomeClass
**Shim file**: old_module/_shim.py
**Deprecation warning**: added with timeline 90 days
**Removal target**: <date>
**ADG fan-in callers updated**: N
```
