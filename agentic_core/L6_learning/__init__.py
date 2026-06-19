"""DEPRECATED — ``agentic_core.L6_learning`` moved to
``agentic_core.L6_system_learning.future_run_promotion`` (ADR-105).

This module is a backward-compatibility shim: it forwards the package's public
symbols and submodules to the new canonical location and emits a
``DeprecationWarning``. Update imports before the **2026-06-29 sunset**, after
which this shim is removed.

    OLD: from agentic_core.L6_learning import PromotionGauntlet
    OLD: from agentic_core.L6_learning.promotion_gauntlet import PromotionGauntlet
    NEW: from agentic_core.L6_system_learning.future_run_promotion import PromotionGauntlet
"""
import sys as _sys
import warnings as _warnings

from agentic_core.L6_system_learning import future_run_promotion as _new
from agentic_core.L6_system_learning.future_run_promotion import (  # noqa: F401
    completed_run_evaluator as _completed_run_evaluator,
    rca_synthesizer as _rca_synthesizer,
    future_run_proposal_builder as _future_run_proposal_builder,
    promotion_gauntlet as _promotion_gauntlet,
    types as _types,
)

_warnings.warn(
    "agentic_core.L6_learning has moved to "
    "agentic_core.L6_system_learning.future_run_promotion (ADR-105); "
    "update imports before the 2026-06-29 sunset.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = list(getattr(_new, "__all__", []))

# Re-export the public symbol vocabulary from the new package without a star import.
for _public_name in __all__:
    globals()[_public_name] = getattr(_new, _public_name)

# Register the legacy dotted submodule paths so existing
# `from agentic_core.L6_learning.<sub> import X` imports keep resolving.
for _legacy_name, _module in (
    ("completed_run_evaluator", _completed_run_evaluator),
    ("rca_synthesizer", _rca_synthesizer),
    ("future_run_proposal_builder", _future_run_proposal_builder),
    ("promotion_gauntlet", _promotion_gauntlet),
    ("types", _types),
):
    _sys.modules[f"{__name__}.{_legacy_name}"] = _module
