"""apps_rg.contracts — canonical declarative ingress contracts for apps_rg.

These contracts describe the JSON shape apps_rg emits at U0 ingress. They are
versioned (v1, v2, ...) and digest-bound. apps_rg has NO runtime authority —
these contracts carry only declarative configuration: identity, source refs,
target context, generation intent, capability requirements, profile manifest
references, quality thresholds, output requirements, and provenance
requirements.

Plan: .windsurf/plans/apps-rg-u0-reflection-harness-79d032.md
"""
from __future__ import annotations

from apps_rg.contracts.apps_rg_ingress_contract_v1 import (
    APPS_RG_INGRESS_CONTRACT_VERSION,
    AppsRgIngressContractV1,
    GenerationMode,
)

__all__ = [
    "APPS_RG_INGRESS_CONTRACT_VERSION",
    "AppsRgIngressContractV1",
    "GenerationMode",
]
