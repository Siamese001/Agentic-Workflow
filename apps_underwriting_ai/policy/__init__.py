"""ADR-082 W7.extra compat shim. Canonical: apps_underwriting_ai.validators.policy. Remove 2026-05-17."""
from __future__ import annotations
import importlib
import sys
import warnings

warnings.warn(
    "apps_underwriting_ai.policy has moved to apps_underwriting_ai.validators.policy (ADR-082). "
    "This compat shim will be removed 2026-05-17.",
    DeprecationWarning,
    stacklevel=2,
)

_target = importlib.import_module("apps_underwriting_ai.validators.policy")
sys.modules[__name__] = _target
