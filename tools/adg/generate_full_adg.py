"""Compatibility shim for ADG generator migration.

Deprecated: use ``tools.generate.generate_full_adg`` (canonical). Accessing
``main`` or ``generate_full_adg`` on this module emits ``DeprecationWarning``
once per attribute resolution (importing the module alone is silent).

Migration:
    OLD: from tools.adg.generate_full_adg import main
    NEW: from tools.generate.generate_full_adg import main
"""

from __future__ import annotations

import warnings
from importlib import import_module
from typing import Any

__all__ = ("main", "generate_full_adg")


def __getattr__(name: str) -> Any:
    if name not in __all__:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    warnings.warn(
        "tools.adg.generate_full_adg is deprecated. "
        "Use tools.generate.generate_full_adg instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    mod = import_module("tools.generate.generate_full_adg")
    return getattr(mod, name)


if __name__ == "__main__":
    # CLI backward compatibility — direct import avoids DeprecationWarning noise.
    from tools.generate.generate_full_adg import main

    main()
