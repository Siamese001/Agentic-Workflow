"""
Validators module for apps_underwriting_ai.

Lazy-load pattern (PEP 562) — same fix as ``engines/__init__.py``. Eager
imports of ``contradiction_validator`` create a circular dependency through
``..engines.document_reconciliation_engine`` because the engines package's
``__init__`` chain pulls in ``underwriting_engine``, which then re-enters
this validators package while it's still partially loaded.

Fix landed: apps-svp-plus-hardening-7c4e3a Wave A (2026-04-30).
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover -- type-checker imports only
    from .authority_limit_validator import AuthorityLimitValidator, AuthorityResult
    from .compliance_validator import ComplianceResult, ComplianceValidator
    from .contradiction_validator import ContradictionValidator
    from .document_completeness_validator import (
        CompletenessResult,
        DocumentCompletenessValidator,
    )
    from .forbidden_feature_checker import (
        ForbiddenCheckResult,
        ForbiddenFeatureChecker,
    )
    from .stale_data_validator import StaleDataValidator


_LAZY_EXPORTS: dict[str, tuple[str, str]] = {
    "AuthorityLimitValidator": (".authority_limit_validator", "AuthorityLimitValidator"),
    "AuthorityResult": (".authority_limit_validator", "AuthorityResult"),
    "ComplianceResult": (".compliance_validator", "ComplianceResult"),
    "ComplianceValidator": (".compliance_validator", "ComplianceValidator"),
    "ContradictionValidator": (".contradiction_validator", "ContradictionValidator"),
    "CompletenessResult": (".document_completeness_validator", "CompletenessResult"),
    "DocumentCompletenessValidator": (".document_completeness_validator", "DocumentCompletenessValidator"),
    "ForbiddenCheckResult": (".forbidden_feature_checker", "ForbiddenCheckResult"),
    "ForbiddenFeatureChecker": (".forbidden_feature_checker", "ForbiddenFeatureChecker"),
    "StaleDataValidator": (".stale_data_validator", "StaleDataValidator"),
}


def __getattr__(name: str) -> Any:
    if name not in _LAZY_EXPORTS:
        raise AttributeError(f"module 'apps_underwriting_ai.validators' has no attribute {name!r}")
    submodule, attr = _LAZY_EXPORTS[name]
    from importlib import import_module

    mod = import_module(submodule, package=__name__)
    value = getattr(mod, attr)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(_LAZY_EXPORTS))


__all__ = list(_LAZY_EXPORTS)
