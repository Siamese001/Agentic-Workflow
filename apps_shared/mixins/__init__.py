"""ADR-082 W9.P9.2 compat shim. Canonical: apps_shared.utils.mixins. Remove 2026-05-17."""
from __future__ import annotations
import importlib
import sys
import warnings

warnings.warn(
    "apps_shared.mixins has moved to apps_shared.utils.mixins (ADR-082). "
    "This compat shim will be removed 2026-05-17.",
    DeprecationWarning,
    stacklevel=2,
)

_target = importlib.import_module("apps_shared.utils.mixins")
sys.modules[__name__] = _target
