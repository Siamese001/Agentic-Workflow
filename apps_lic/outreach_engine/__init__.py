"""ADR-082 W6.P6.2 compat shim. Canonical: apps_lic.engines.outreach. Remove 2026-05-17."""
from __future__ import annotations
import importlib
import sys
import warnings

warnings.warn(
    "apps_lic.outreach_engine has moved to apps_lic.engines.outreach (ADR-082). "
    "This compat shim will be removed 2026-05-17.",
    DeprecationWarning,
    stacklevel=2,
)

_target = importlib.import_module("apps_lic.engines.outreach")
sys.modules[__name__] = _target
