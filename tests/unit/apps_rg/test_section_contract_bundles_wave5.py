"""Wave 5: section front-spine and downstream runtime bundles stay separate."""
from __future__ import annotations

from dataclasses import fields

from apps_rg.runtime.spine import front_contracts
from apps_rg.runtime.spine.section_contract_bundles import (
    FRONT_SPINE_CONTRACTS,
    SectionFrontSpineBridge,
    SectionRunContractBundle,
)
from apps_rg.runtime import spine_contracts


DOWNSTREAM_FIELD_NAMES = {
    "evidence_contract",
    "final_evidence_contract",
    "compiled_prompt",
    "compiled_prompt_artifact",
    "sealed_artifact",
    "sealed_l2_artifact",
    "section_exit_receipt",
    "exit_disposition_receipt",
    "x3_disposition",
    "runtime_exhaust_bundle",
}


def test_front_contracts_reexports_canonical_section_front_bridge() -> None:
    assert front_contracts.SectionFrontSpineBridge is SectionFrontSpineBridge


def test_section_front_spine_bridge_has_no_downstream_runtime_fields() -> None:
    field_names = {field.name for field in fields(SectionFrontSpineBridge)}
    assert field_names.isdisjoint(DOWNSTREAM_FIELD_NAMES)


def test_section_front_spine_bridge_emits_only_front_contracts() -> None:
    bridge = SectionFrontSpineBridge(
        section_id="executive_summary",
        validated_request=object(),
        l1_plan=object(),
        route=object(),
    )
    assert tuple(bridge.contracts_emitted()) == FRONT_SPINE_CONTRACTS
    assert bridge.contracts_emitted() == {
        "ValidatedRequest": True,
        "L1PlanContract": True,
        "RouteContract": True,
    }


def test_section_run_contract_bundle_owns_downstream_runtime_fields() -> None:
    field_names = {field.name for field in fields(SectionRunContractBundle)}
    assert {
        "evidence_contract",
        "compiled_prompt",
        "sealed_artifact",
        "section_exit_receipt",
        "x3_disposition",
    }.issubset(field_names)

    empty = SectionRunContractBundle()
    assert empty.runtime_complete() is False
    assert empty.contracts_emitted() == {
        "FinalEvidenceContract": False,
        "CompiledPromptArtifact": False,
        "SealedL2Artifact": False,
        "ExitDispositionReceipt": False,
        "X3Disposition": False,
    }


def test_section_and_full_paths_share_core_contract_vocabulary() -> None:
    assert SectionRunContractBundle.__annotations__["evidence_contract"].startswith(
        "FinalEvidenceContract"
    )
    assert spine_contracts.X3Disposition.__module__ == (
        "agentic_core.runtime.contracts.x3_disposition"
    )
