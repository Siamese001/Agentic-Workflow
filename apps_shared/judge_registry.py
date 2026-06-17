"""Judge promotion registry — tracks stub vs real judge implementations.

Plan: `.claude/plans/apps-eval-harness-residual-a2d9c7.md` W5.P1.

Purpose
-------
Parent continuation plan landed 4 LLM-judge stubs at canonical import
paths. Each stub declares ``IS_STUB = True``. This registry resolves
the importable module for a given ``(app_id, dim_name)`` and reports
whether the judge is still a stub or has been promoted to a real
implementation.

CI and operators consult this registry to decide when a judge
flipping from stub to real requires Author-Gate review (score-band
changes, calibration-budget impact, etc.).

Authority
---------
READ-ONLY. The registry does not execute judges; it inspects modules.
"""

from __future__ import annotations

import importlib
import logging
from dataclasses import dataclass
from types import ModuleType
from typing import Dict, Mapping, Optional, Tuple

Logger = logging.getLogger(__name__)


# Canonical (app_id, dim_name) -> dotted module path for the judge.
# Matches the `check_app_domain_harness_parity` gate expectations.
JUDGE_IMPORT_PATHS: Dict[Tuple[str, str], str] = {
    ("apps_rg", "executive_positioning"): "apps_rg.engines.judges.executive_positioning_judge",
    ("apps_lic", "response_likelihood"): "apps_lic.engines.judges.response_likelihood_judge",
    ("apps_lic", "brand_voice"): "apps_lic.engines.judges.brand_voice_judge",
}


@dataclass(frozen=True)
class JudgeStatus:
    app_id: str
    dim_name: str
    import_path: str
    importable: bool
    is_stub: bool
    error: str = ""


def _probe_module(import_path: str) -> Tuple[Optional[ModuleType], str]:
    try:
        mod = importlib.import_module(import_path)
    except (ImportError, ModuleNotFoundError) as exc:
        return None, f"{type(exc).__name__}: {exc}"
    return mod, ""


def _module_is_stub(module: ModuleType) -> bool:
    """A judge is stub iff module defines ``IS_STUB = True``."""
    return bool(getattr(module, "IS_STUB", False))


def resolve_judge(app_id: str, dim_name: str) -> JudgeStatus:
    """Resolve the judge status for (app_id, dim_name)."""
    key = (app_id, dim_name)
    path = JUDGE_IMPORT_PATHS.get(key)
    if path is None:
        return JudgeStatus(
            app_id=app_id,
            dim_name=dim_name,
            import_path="",
            importable=False,
            is_stub=False,
            error="unregistered (app_id, dim_name)",
        )
    module, error = _probe_module(path)
    if module is None:
        return JudgeStatus(
            app_id=app_id,
            dim_name=dim_name,
            import_path=path,
            importable=False,
            is_stub=False,
            error=error,
        )
    return JudgeStatus(
        app_id=app_id,
        dim_name=dim_name,
        import_path=path,
        importable=True,
        is_stub=_module_is_stub(module),
        error="",
    )


def registered_judges() -> Mapping[Tuple[str, str], str]:
    """Snapshot of the canonical (app_id, dim_name) -> import path map."""
    return dict(JUDGE_IMPORT_PATHS)


def stub_count() -> int:
    """Count of currently-stub judges across the registry."""
    return sum(
        1
        for (app_id, dim_name) in JUDGE_IMPORT_PATHS
        if resolve_judge(app_id, dim_name).is_stub
    )


def promoted_count() -> int:
    """Count of importable, non-stub (promoted) judges."""
    total = 0
    for (app_id, dim_name) in JUDGE_IMPORT_PATHS:
        status = resolve_judge(app_id, dim_name)
        if status.importable and not status.is_stub:
            total += 1
    return total


__all__ = [
    "JUDGE_IMPORT_PATHS",
    "JudgeStatus",
    "promoted_count",
    "registered_judges",
    "resolve_judge",
    "stub_count",
]
