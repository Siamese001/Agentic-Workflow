"""W5 — governed PA: core assemble_prompt + section slot BOM."""

from __future__ import annotations

import os
from types import SimpleNamespace

import pytest

from agentic_core.runtime.contracts.final_evidence_contract import (
    EvidenceItem,
    FinalEvidenceContract,
    SUPPORT_STATUS_PASS,
)
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.route_contract import RouteContract
from apps_rg.runtime.bindings.pa_binding import pa_compose_apps_rg
from apps_rg.runtime.spine.governed_pa_compose import (
    GOVERNED_PA_MODE_SECTION_BOM,
    governed_pa_compose_enabled,
    runtime_fec_to_orchestrator_contract,
    runtime_route_to_orchestrator_route,
    section_slot_bom_from_compiled,
)


def _route() -> RouteContract:
    return RouteContract(
        request_id="req-w5",
        run_id="run-w5",
        app_id="apps_rg",
        trace_id="trace-w5",
        route_id="R3_SIMPLE_GROUNDED_READ",
        l3_required=False,
        grounding_required=True,
        model_generation_required=True,
        write_authority_present=False,
        l5_certification_ref="test:valid:w6",
        route_family="evidence_grounded_generation",
        execution_form="single_step",
        route_digest="a" * 64,
        hmac_sig="b" * 64,
    )


def _plan() -> L1PlanContract:
    return L1PlanContract(
        request_id="req-w5",
        run_id="run-w5",
        app_id="apps_rg",
        trace_id="trace-w5",
        grounding_required=True,
        model_generation_required=True,
        l5_certification_ref="test:valid:w6",
        profile_manifest_digest="c" * 64,
        task_spec={"generation_mode": "strategic_tailor"},
        query_spec={"target": {"company": "Acme", "role": "VP", "level": "EXECUTIVE"}},
    )


def _fec() -> FinalEvidenceContract:
    return FinalEvidenceContract(
        request_id="req-w5",
        run_id="run-w5",
        app_id="apps_rg",
        trace_id="trace-w5",
        l5_certification_ref="test:valid:w6",
        support_status=SUPPORT_STATUS_PASS,
        support_target_met=True,
        final_evidence_digest="d" * 64,
        evidence_items=(
            EvidenceItem(
                source="fact:bul_001",
                content="Delivered governed agentic platforms.",
                source_type="proof_pool",
            ),
        ),
    )


def _vr() -> SimpleNamespace:
    return SimpleNamespace(
        request_id="req-w5",
        run_id="run-w5",
        app_id="apps_rg",
        trace_id="trace-w5",
        tenant_id="tenant-w5",
        l5_certification_ref="test:valid:w6",
        app_payload={},
        replay_key="replay-w5",
    )


def test_governed_pa_compose_enabled_by_default() -> None:
    assert governed_pa_compose_enabled() is True


def test_runtime_fec_adapter_builds_orchestrator_contract() -> None:
    orch = runtime_fec_to_orchestrator_contract(
        _fec(),
        route=_route(),
        plan=_plan(),
    )
    assert orch.contract_id.startswith("fec-")
    assert orch.must_use


def test_runtime_route_to_orchestrator_forwards_l5_cert_ref() -> None:
    orch = runtime_route_to_orchestrator_route(_route())
    assert orch.l5_certification_ref == "test:valid:w6"


def test_pa_compose_apps_rg_uses_core_pipeline(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    import agentic_core.prompt_governance.prompt_assembly.pipeline as pipeline_mod

    monkeypatch.delenv("APPS_RG_GOVERNED_PA_SKIP", raising=False)
    with caplog.at_level("WARNING", logger=pipeline_mod._logger.name):
        artifact = pa_compose_apps_rg(_route(), _plan(), _fec(), _vr())
    assert artifact.compilation_hash
    assert any("pa_manifest:" in ref for ref in artifact.gate_verdict_refs)
    assert any("pa_hmac:" in ref for ref in artifact.gate_verdict_refs)
    assert not any("L5CertRefViolation" in r.message for r in caplog.records)


def test_legacy_pa_when_governed_pa_skipped(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_GOVERNED_PA_SKIP", "1")
    artifact = pa_compose_apps_rg(_route(), _plan(), _fec(), _vr())
    assert artifact.compilation_hash
    assert not any("pa_manifest:" in ref for ref in artifact.gate_verdict_refs)


def test_section_slot_bom_from_compiled_shape() -> None:
    payload = SimpleNamespace(
        slot_id="S0",
        authority_class=SimpleNamespace(name="SYSTEM_AUTHORITY"),
        content_hash="abc123",
        source_tag=None,
    )
    art = SimpleNamespace(
        template_id="executive_summary.generate_scratch_v1",
        prompt_hash="hash123",
        canonical_slot_order=["S0", "I0", "C0"],
        slot_payloads=[payload],
        component_hash_map=None,
        provider_render_manifest={"model": "retired_provider"},
    )
    compiled = SimpleNamespace(
        section_id="executive_summary",
        apps_rg_prompt_template_ref="apps_rg/prompt_assembly/templates/x.yaml",
        artifact=art,
    )
    bom = section_slot_bom_from_compiled(compiled)
    assert bom["governed_pa_mode"] == GOVERNED_PA_MODE_SECTION_BOM
    assert bom["slot_payloads"][0]["slot_id"] == "S0"
    assert bom["core_assemble_prompt_invoked"] is False
