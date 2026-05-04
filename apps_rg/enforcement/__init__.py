"""ADR-082 W8.P8.1 compat shim. Canonical: apps_rg.validators.enforcement. Remove 2026-05-17."""
from __future__ import annotations
import importlib
import sys
import warnings

warnings.warn(
    "apps_rg.enforcement has moved to apps_rg.validators.enforcement (ADR-082). "
    "This compat shim will be removed 2026-05-17.",
    DeprecationWarning,
    stacklevel=2,
)

_target = importlib.import_module("apps_rg.validators.enforcement")
sys.modules[__name__] = _target
