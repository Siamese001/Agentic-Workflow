"""apps-test-model: CONTRACT SPINE."""
from __future__ import annotations

import pytest

from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    AppsRgIngressPayload,
    RequestEnvelope,
)
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact

from apps_rg.runtime.bindings.c0_binding import c0_retrieve_apps_rg
from apps_rg.runtime.bindings.exit_binding import exit_finalize_apps_rg
from apps_rg.runtime.bindings.l0_binding import l0_route_apps_rg
from apps_rg.runtime.bindings.l1_binding import l1_plan_apps_rg
from apps_rg.runtime.bindings.l2_binding import l2_execute_apps_rg
from apps_rg.runtime.bindings.pa_binding import pa_compose_apps_rg
from apps_rg.runtime.bindings.u0_binding import u0_validate_apps_rg

pytestmark = pytest.mark.apps_test_model("CONTRACT SPINE")


def _envelope() -> RequestEnvelope:
    payload = AppsRgIngressPayload(
        target_company="Acme Robotics",
        target_role="Director of AI Platforms",
        target_level="EXECUTIVE",
        source_resume_text="Built AI platforms, led cloud migrations, and managed ML teams.",
        job_description_text="Lead AI platform strategy, governance, model operations, and cloud delivery.",
        user_constraints={
            "fact_check_required": True,
            "provenance_required": True,
            "citation_required": True,
            "briefing_text": "Run-specific briefing: prioritize AI platform governance and delivery impact.",
        },
        idempotency_key="apps-rg-l5-runtime-contract",
    )
    return RequestEnvelope(
        payload=payload,
        request_id="req-l5-runtime-contract",
        run_id="run-l5-runtime-contract",
        trace_id="trace-l5-runtime-contract",
        tenant_id="apps_rg",
        replay_key="replay-l5-runtime-contract",
    )


def _plain_sealed(**overrides: object) -> SealedL2Artifact:
    base = {
        "request_id": "req-l5-negative",
        "run_id": "run-l5-negative",
        "app_id": "apps_rg",
        "trace_id": "trace-l5-negative",
        "execution_status": "completed",
        "generated_content": '{"ok": true}',
        "compilation_hash": "a" * 64,
        "replay_key": "replay-l5-negative",
        "l5_certification_ref": "l5:apps_rg:u0:negative",
    }
    base.update(overrides)
    return SealedL2Artifact(**base)


def test_u0_to_exit_emits_one_l5_packet_and_exit_consumes_it(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_L2_FORCE_STUB", "1")
    monkeypatch.setenv("APPS_RG_TEST_HARNESS", "1")
    monkeypatch.setenv("APPS_RG_C0_DENSE_SPARSE_MANDATORY", "0")
    monkeypatch.setenv("APPS_RG_C0_SPARSE_ENABLED", "0")
    monkeypatch.setenv("CHROMA_PERSIST_DIR", "")

    validated = u0_validate_apps_rg(_envelope())
    assert validated.l5_certification_ref != "test:valid:w6"
    assert str(validated.l5_certification_ref).startswith("l5:apps_rg:u0:")

    plan = l1_plan_apps_rg(validated)
    route = l0_route_apps_rg(plan)
    fec = c0_retrieve_apps_rg(route, validated, chromadb_path=None)
    prompt = pa_compose_apps_rg(route, plan, fec, validated)
    sealed = l2_execute_apps_rg(prompt)

    assert sealed.l5_certification_status == "L5_CERTIFIED"
    assert sealed.l5_certification_packet_ref.startswith("l5_packet:")
    assert len(sealed.l5_certification_packet_digest) == 64
    assert sealed.gate_verdict_refs.count(sealed.l5_certification_packet_ref) == 0
    assert sum(1 for value in (sealed.l5_certification_packet_ref,) if value.startswith("l5_packet:")) == 1

    exit_result = exit_finalize_apps_rg(
        sealed,
        prompt,
        fec=fec,
        target_company="Acme Robotics",
        target_role="Director of AI Platforms",
    )
    l5_gates = [gate for gate in exit_result.disposition.gate_results if gate.gate_id == "G_L5_CERTIFICATION"]
    assert len(l5_gates) == 1
    assert l5_gates[0].verdict.value == "PASS"

    if exit_result.disposition.outcome_authorized:
        assert len(exit_result.cache_write_proposals) == 1
        assert (
            exit_result.cache_write_proposals[0].l5_certification_packet_digest
            == sealed.l5_certification_packet_digest
        )


def test_missing_l5_packet_blocks_exit_and_cache_proposals() -> None:
    result = exit_finalize_apps_rg(_plain_sealed(), fec=None)

    assert result.disposition.outcome_authorized is False
    assert result.cache_write_proposals == ()
    assert any(gate.gate_id == "G_L5_CERTIFICATION" and gate.verdict.value == "FAIL" for gate in result.disposition.gate_results)


def test_l5_not_certified_blocks_exit_and_cache_proposals() -> None:
    result = exit_finalize_apps_rg(
        _plain_sealed(
            l5_certification_packet_ref="l5_packet:bad",
            l5_certification_packet_digest="b" * 64,
            l5_certification_status="L5_NOT_CERTIFIED",
        ),
        fec=None,
    )

    assert result.disposition.outcome_authorized is False
    assert result.cache_write_proposals == ()
    assert "L5_NOT_CERTIFIED" in result.disposition.blocking_reason


def test_placeholder_cert_ref_blocks_governed_exit_even_with_packet_fields() -> None:
    result = exit_finalize_apps_rg(
        _plain_sealed(
            l5_certification_ref="test:valid:w6",
            l5_certification_packet_ref="l5_packet:test",
            l5_certification_packet_digest="c" * 64,
            l5_certification_status="L5_CERTIFIED",
        ),
        fec=None,
    )

    assert result.disposition.outcome_authorized is False
    assert result.cache_write_proposals == ()
    assert "placeholder" in result.disposition.blocking_reason
