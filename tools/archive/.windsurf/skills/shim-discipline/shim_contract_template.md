# Shim Contract Template

Every backward-compatibility shim file MUST follow this template exactly.
Deviation from this template = non-compliant shim.

---

## Template

```python
"""
DEPRECATED: Use `<canonical.module.path>` instead.

This shim maintains backward compatibility for consumers importing from
`<old.module.path>`. It will be removed after all consumers have migrated
to the canonical location.

Canonical location: <canonical.module.path>
Old location (this file): <old.module.path>
Migration guide: Replace `from <old.module.path> import X`
                 with     `from <canonical.module.path> import X`

SHIM EXPIRY: after all consumers migrated (target: <milestone or date>)
"""
# DEPRECATED — see docstring above

from <canonical.module.path> import (  # noqa: F401  (re-export)
    SymbolOne,
    SymbolTwo,
    SymbolThree,
)

__all__ = [
    "SymbolOne",
    "SymbolTwo",
    "SymbolThree",
]
```

---

## Compliance Checklist

Before committing a new shim file, verify ALL of the following:

- [ ] Module docstring starts with `DEPRECATED: Use \`<canonical>\` instead`
- [ ] Canonical import path is correct and resolvable
- [ ] `__all__` re-exports ALL symbols that the old path exported
- [ ] `# noqa: F401` on import line (re-exports are intentional)
- [ ] `SHIM EXPIRY` comment present with milestone or date
- [ ] A test file exists asserting the shim re-exports the canonical symbol:

```python
# tests/unit_min_deps/test_<name>_shim_contract.py

def test_shim_reexports_canonical():
    """Shim re-exports the canonical symbol unchanged."""
    from <old.module.path> import SymbolOne as ShimSymbol
    from <canonical.module.path> import SymbolOne as CanonicalSymbol
    assert ShimSymbol is CanonicalSymbol, (
        "Shim must re-export the exact canonical symbol, not a copy"
    )
```

- [ ] Test is in `tests/unit_min_deps/` (fast, no side-effect imports)
- [ ] Test passes before canonical move is committed

---

## Anti-Patterns (FORBIDDEN)

```python
# FORBIDDEN: Shim that copies logic instead of re-exporting
def SymbolOne(*args, **kwargs):
    # duplicated logic here
    ...

# FORBIDDEN: Shim without DEPRECATED docstring
from canonical.path import SymbolOne  # no docstring explaining why

# FORBIDDEN: Shim with __all__ missing symbols
from canonical.path import SymbolOne, SymbolTwo
__all__ = ["SymbolOne"]  # SymbolTwo missing!

# FORBIDDEN: Shim without expiry annotation
from canonical.path import SymbolOne  # no SHIM EXPIRY comment
```
