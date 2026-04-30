"""
Engines module for apps_underwriting_ai.

Lazy-load pattern (PEP 562) — eagerly importing ``underwriting_engine`` here
created a circular dependency through
``..validators.contradiction_validator → ..engines.document_reconciliation_engine``
because Python would re-enter ``engines/__init__.py`` while ``validators``
was still partially loaded.

By moving the imports into ``__getattr__``, the package import is cheap and
the heavy modules are loaded on first attribute access. Test files that do
``from apps_underwriting_ai.engines import UnderwritingEngine`` continue to
work — they just trigger the lazy load on the first access.

Fix landed: apps-svp-plus-hardening-7c4e3a Wave A (2026-04-30).
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover -- imports only for type checkers
    from .decision_packet_assembler import DecisionPacketAssembler
    from .document_reconciliation_engine import (
        Contradiction,
        DocumentReconciliationEngine,
        ReconciliationResult,
    )
    from .evidence_register_engine import EvidenceRegisterEngine
    from .feature_derivation_engine import FeatureDerivationEngine
    from .underwriting_engine import UnderwritingEngine, UnderwritingResult


_LAZY_EXPORTS: dict[str, tuple[str, str]] = {
    "DecisionPacketAssembler": (".decision_packet_assembler", "DecisionPacketAssembler"),
    "Contradiction": (".document_reconciliation_engine", "Contradiction"),
    "DocumentReconciliationEngine": (".document_reconciliation_engine", "DocumentReconciliationEngine"),
    "ReconciliationResult": (".document_reconciliation_engine", "ReconciliationResult"),
    "EvidenceRegisterEngine": (".evidence_register_engine", "EvidenceRegisterEngine"),
    "FeatureDerivationEngine": (".feature_derivation_engine", "FeatureDerivationEngine"),
    "UnderwritingEngine": (".underwriting_engine", "UnderwritingEngine"),
    "UnderwritingResult": (".underwriting_engine", "UnderwritingResult"),
}


def __getattr__(name: str) -> Any:
    if name not in _LAZY_EXPORTS:
        raise AttributeError(f"module 'apps_underwriting_ai.engines' has no attribute {name!r}")
    submodule, attr = _LAZY_EXPORTS[name]
    from importlib import import_module

    mod = import_module(submodule, package=__name__)
    value = getattr(mod, attr)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(_LAZY_EXPORTS))


__all__ = list(_LAZY_EXPORTS)
