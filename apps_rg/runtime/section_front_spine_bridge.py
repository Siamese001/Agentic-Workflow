"""Section front-spine bridge — compatibility re-export (pa-exec-flowchart-gap W2).

Product SSOT: ``apps_rg.runtime.spine.front_contracts`` (U0→L1→L0 before proof_pool).
This module exists so plan/CI paths and receipts can reference a stable filename.
Do not import from section lanes; use ``load_section_proof_for_lane`` or ``front_contracts``.
"""
from __future__ import annotations

from apps_rg.runtime.spine.front_contracts import (
    DOWNSTREAM_MISSING_CANONICAL_CONTRACTS,
    FRONT_SPINE_CONTRACTS,
    OBSERVED_CHAIN_WITH_FRONT_BRIDGE,
    SectionFrontSpineBridge,
    SectionFrontSpinePreconditionError,
    activate_fixture_dev_bypass,
    assert_proof_pool_front_spine_preconditions,
    build_section_front_spine_from_args,
    build_section_front_spine_receipt,
    deactivate_fixture_dev_bypass,
    emit_section_front_spine_receipts,
    fixture_dev_bypass_active,
    product_visible_kill_switch_enabled,
)

__all__ = [
    "DOWNSTREAM_MISSING_CANONICAL_CONTRACTS",
    "FRONT_SPINE_CONTRACTS",
    "OBSERVED_CHAIN_WITH_FRONT_BRIDGE",
    "SectionFrontSpineBridge",
    "SectionFrontSpinePreconditionError",
    "activate_fixture_dev_bypass",
    "assert_proof_pool_front_spine_preconditions",
    "build_section_front_spine_from_args",
    "build_section_front_spine_receipt",
    "deactivate_fixture_dev_bypass",
    "emit_section_front_spine_receipts",
    "fixture_dev_bypass_active",
    "product_visible_kill_switch_enabled",
]
