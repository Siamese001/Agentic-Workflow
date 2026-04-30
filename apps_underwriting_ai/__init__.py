"""
Apps Underwriting AI - Domain app for commercial credit underwriting.

Public surface re-exports the domain types and the top-level engine so that
``from apps_underwriting_ai import UnderwritingEngine, BankingPackage`` works
without callers having to know the internal module layout. Heavy types load
lazily via PEP 562 ``__getattr__`` to keep the import-time cost low and to
avoid eagerly entering the engines/validators packages (which previously
caused a circular import — see Wave A 2026-04-30).
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

__version__ = "1.0.0"


if TYPE_CHECKING:  # pragma: no cover -- type-checker imports only
    from apps_underwriting_ai.engines import (
        DecisionPacketAssembler,
        DocumentReconciliationEngine,
        EvidenceRegisterEngine,
        FeatureDerivationEngine,
        UnderwritingEngine,
        UnderwritingResult,
    )
    from apps_underwriting_ai.types import (
        AuditTrace,
        BankingPackage,
        BorrowerProfile,
        CalculatedMetrics,
        CapacityFeatures,
        CollateralFeatures,
        CollateralPackage,
        CollateralRules,
        CollateralType,
        CompositeFeatures,
        CreditFeatures,
        CreditPackage,
        DecisionConstraints,
        DecisionMemo,
        DecisionPacket,
        DocumentPackage,
        EvidenceRegister,
        ExternalSignals,
        FinancialPackage,
        FinancialPeriod,
        OwnerInfo,
        PolicyContext,
        RelationshipContext,
        RequestedStructure,
        RiskFeatures,
        UnderwritingRequest,
    )


# Re-exports: name → (qualified module, attribute).
_LAZY_EXPORTS: dict[str, tuple[str, str]] = {
    # Engines
    "DecisionPacketAssembler": ("apps_underwriting_ai.engines", "DecisionPacketAssembler"),
    "DocumentReconciliationEngine": ("apps_underwriting_ai.engines", "DocumentReconciliationEngine"),
    "EvidenceRegisterEngine": ("apps_underwriting_ai.engines", "EvidenceRegisterEngine"),
    "FeatureDerivationEngine": ("apps_underwriting_ai.engines", "FeatureDerivationEngine"),
    "UnderwritingEngine": ("apps_underwriting_ai.engines", "UnderwritingEngine"),
    "UnderwritingResult": ("apps_underwriting_ai.engines", "UnderwritingResult"),
    # Domain types — re-exported from apps_underwriting_ai.types.
    "AuditTrace": ("apps_underwriting_ai.types", "AuditTrace"),
    "BankingPackage": ("apps_underwriting_ai.types", "BankingPackage"),
    "BorrowerProfile": ("apps_underwriting_ai.types", "BorrowerProfile"),
    "CalculatedMetrics": ("apps_underwriting_ai.types", "CalculatedMetrics"),
    "CapacityFeatures": ("apps_underwriting_ai.types", "CapacityFeatures"),
    "CollateralFeatures": ("apps_underwriting_ai.types", "CollateralFeatures"),
    "CollateralPackage": ("apps_underwriting_ai.types", "CollateralPackage"),
    "CollateralRules": ("apps_underwriting_ai.types", "CollateralRules"),
    "CollateralType": ("apps_underwriting_ai.types", "CollateralType"),
    "CompositeFeatures": ("apps_underwriting_ai.types", "CompositeFeatures"),
    "CreditFeatures": ("apps_underwriting_ai.types", "CreditFeatures"),
    "CreditPackage": ("apps_underwriting_ai.types", "CreditPackage"),
    "DecisionConstraints": ("apps_underwriting_ai.types", "DecisionConstraints"),
    "DecisionMemo": ("apps_underwriting_ai.types", "DecisionMemo"),
    "DecisionPacket": ("apps_underwriting_ai.types", "DecisionPacket"),
    "DocumentPackage": ("apps_underwriting_ai.types", "DocumentPackage"),
    "EvidenceRegister": ("apps_underwriting_ai.types", "EvidenceRegister"),
    "ExternalSignals": ("apps_underwriting_ai.types", "ExternalSignals"),
    "FinancialPackage": ("apps_underwriting_ai.types", "FinancialPackage"),
    "FinancialPeriod": ("apps_underwriting_ai.types", "FinancialPeriod"),
    "OwnerInfo": ("apps_underwriting_ai.types", "OwnerInfo"),
    "PolicyContext": ("apps_underwriting_ai.types", "PolicyContext"),
    "RelationshipContext": ("apps_underwriting_ai.types", "RelationshipContext"),
    "RequestedStructure": ("apps_underwriting_ai.types", "RequestedStructure"),
    "RiskFeatures": ("apps_underwriting_ai.types", "RiskFeatures"),
    "UnderwritingRequest": ("apps_underwriting_ai.types", "UnderwritingRequest"),
}


def __getattr__(name: str) -> Any:
    if name not in _LAZY_EXPORTS:
        raise AttributeError(f"module 'apps_underwriting_ai' has no attribute {name!r}")
    qualified_module, attr = _LAZY_EXPORTS[name]
    from importlib import import_module

    mod = import_module(qualified_module)
    value = getattr(mod, attr)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(_LAZY_EXPORTS))


__all__ = list(_LAZY_EXPORTS)
