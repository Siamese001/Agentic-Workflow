"""Compatibility exports for runtime ADG app-route contracts.

The canonical implementation lives in
``agentic_core.L6_system_learning.runtime_adg.app_route_contracts``.  This
module preserves the older top-level import path used by runtime-cert tooling
and tests.
"""

from __future__ import annotations

from agentic_core.L6_system_learning.runtime_adg.app_route_contracts import (
    AppRouteContract,
    BUILD_TIME_COMPILER_CONTRACTS,
    BUILD_TIME_COMPILER_FORBIDDEN_CONTRACTS,
    CertificationLevel,
    ContractSpanBinding,
    PhaseAStatus,
    R3_FORBIDDEN_CONTRACTS,
    R3_GROUNDED_READ_CONTRACTS,
    RequiredAttribute,
    RouteShape,
    build_build_time_compiler_contract,
    build_formal_exception_contract,
    build_r3_grounded_read_contract,
)

__all__ = [
    "AppRouteContract",
    "BUILD_TIME_COMPILER_CONTRACTS",
    "BUILD_TIME_COMPILER_FORBIDDEN_CONTRACTS",
    "CertificationLevel",
    "ContractSpanBinding",
    "PhaseAStatus",
    "R3_FORBIDDEN_CONTRACTS",
    "R3_GROUNDED_READ_CONTRACTS",
    "RequiredAttribute",
    "RouteShape",
    "build_build_time_compiler_contract",
    "build_formal_exception_contract",
    "build_r3_grounded_read_contract",
]
