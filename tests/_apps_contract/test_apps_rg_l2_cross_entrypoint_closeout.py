"""Contract tests for apps_rg canonical L2 cross-entrypoint closeout."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from agentic_core.runtime.contracts.compiled_prompt_artifact import CompiledPromptArtifact
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact


def _cpa() -> CompiledPromptArtifact:
    return CompiledPromptArtifact(
        request_id="req-l2-closeout",
        run_id="run-l2-closeout",
        app_id="apps_rg",
        trace_id="trace-l2-closeout",
        tenant_id="tenant-l2-closeout",
        system_preamble="system",
        user_instruction="user",
        target_provider="external_claude",
        target_model="claude-sonnet-4-20250514",
        evidence_digest="a" * 64,
        compilation_hash="b" * 64,
        replay_key="replay-l2-closeout",
        l5_certification_ref="test:valid:w6",
    )


def _sealed(*, canonical: bool) -> SealedL2Artifact:
    return SealedL2Artifact(
        request_id="req-l2-closeout",
        run_id="run-l2-closeout",
        app_id="apps_rg",
        trace_id="trace-l2-closeout",
        execution_status="completed",
        compilation_hash="c" * 64,
        audit_manifest_ref="l2_receipt_bundle.json" if canonical else "",
        sovereign_execution_receipt="l2_packet:abc" if canonical else "",
        state_diff_authorized=False,
        is_uwg_write_authority=False,
        l5_certification_ref="test:valid:w6",
    )


def test_product_binding_delegates_signed_upstream_authority(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    from apps_rg.runtime.bindings import l2_authorized_runtime
    from apps_rg.runtime.bindings.l2_binding_adapter import _l2_execute_apps_rg_core

    observed: dict[str, Any] = {}

    def fake_run(prompt: Any, route: Any, request: Any, **kwargs: Any) -> SealedL2Artifact:
        observed.update(prompt=prompt, route=route, request=request, kwargs=kwargs)
        return _sealed(canonical=True)

    monkeypatch.delenv("APPS_RG_L2_FORCE_STUB", raising=False)
    monkeypatch.delenv("APPS_RG_L2_DEV_LEGACY_PACKAGE", raising=False)
    monkeypatch.setattr(l2_authorized_runtime, "run_apps_rg_authorized_l2", fake_run)
    route = object()
    request = object()
    result = _l2_execute_apps_rg_core(
        _cpa(),
        route_contract=route,
        validated_request=request,
        artifact_dir=str(tmp_path),
        product_mode=True,
    )

    assert result.execution_status == "completed"
    assert observed["route"] is route
    assert observed["request"] is request
    assert observed["kwargs"]["artifact_dir"] == str(tmp_path)


def test_product_binding_missing_authority_is_provider_free_rejection(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    from apps_rg.runtime.bindings.l2_binding_adapter import _l2_execute_apps_rg_core

    monkeypatch.delenv("APPS_RG_L2_FORCE_STUB", raising=False)
    monkeypatch.delenv("APPS_RG_L2_DEV_LEGACY_PACKAGE", raising=False)
    sealed = _l2_execute_apps_rg_core(
        _cpa(),
        artifact_dir=str(tmp_path),
        product_mode=True,
    )

    assert sealed.execution_status == "rejected"
    assert sealed.provider_receipts == ()
    assert sealed.model_call_refs == ()
    bundle = json.loads((tmp_path / "l2_receipt_bundle.json").read_text(encoding="utf-8"))
    assert bundle["provider_invoked"] is False
    assert bundle["state_diff_authorized"] is False


def test_governed_marker_distinguishes_canonical_authority_from_stub() -> None:
    from apps_rg.runtime.spine.governed_l2_exit_compose import (
        CANONICAL_L2_AUTHORITY_MARKER,
        GOVERNED_EXIT_SPINE_MARKER,
        _stamp_sealed_governed_marker,
    )

    canonical = _stamp_sealed_governed_marker(_sealed(canonical=True))
    compatibility = _stamp_sealed_governed_marker(_sealed(canonical=False))

    assert GOVERNED_EXIT_SPINE_MARKER in canonical.gate_verdict_refs
    assert CANONICAL_L2_AUTHORITY_MARKER in canonical.gate_verdict_refs
    assert GOVERNED_EXIT_SPINE_MARKER in compatibility.gate_verdict_refs
    assert CANONICAL_L2_AUTHORITY_MARKER not in compatibility.gate_verdict_refs


def test_section_product_path_uses_canonical_two_phase_lifecycle(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    from apps_rg.runtime import section_l2_authority
    from apps_rg.runtime import section_l2_lane_integration as integration
    from apps_rg.runtime import graph_skills_run_artifacts
    from apps_rg.runtime.spine import section_x3_finalize, spine_span_emit

    (tmp_path / "compiled_prompt_artifact.json").write_text("{}", encoding="utf-8")
    calls: list[str] = []

    def fake_prepare(*args: Any, **kwargs: Any) -> dict[str, Any]:
        calls.append("prepare")
        return {"packet_digest": "abc"}

    def fake_finalize(*args: Any, **kwargs: Any) -> dict[str, Path]:
        calls.append("finalize")
        return {
            "sealed_l2_artifact": tmp_path / "sealed_l2_artifact.json",
            "l2_spine_receipt": tmp_path / "l2_spine_receipt.json",
            "l2_handoff_receipt": tmp_path / "l2_handoff_receipt.json",
        }

    monkeypatch.setattr(section_l2_authority, "prepare_section_l2_authority", fake_prepare)
    monkeypatch.setattr(section_l2_authority, "finalize_section_l2_authority", fake_finalize)
    monkeypatch.setattr(spine_span_emit, "emit_spine_span_event", lambda *a, **k: None)
    monkeypatch.setattr(
        graph_skills_run_artifacts,
        "persist_graph_skills_lane_artifacts",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        section_x3_finalize,
        "finalize_section_spine_exit_after_sealed_l2",
        lambda *a, **k: None,
    )

    runtime_payload = {
        "product_visible": True,
        "section_fec_bridge": {"route_contract_ref": "route_contract.json"},
    }
    integration.prepare_section_l2_before_provider(
        tmp_path,
        "headline",
        runtime_payload,
        provider_lane="external_claude",
        model_lane="claude-sonnet-4-20250514",
    )
    integration.finalize_section_l2_after_output(
        tmp_path,
        "headline",
        runtime_payload,
    )
    assert calls == ["prepare", "finalize"]


def test_section_handoff_never_treats_unknown_token_usage_as_pass() -> None:
    from apps_rg.runtime.section_l2_authority import _build_handoff_receipt

    packet = SimpleNamespace(
        packet_signature="sig",
        packet_digest="packet",
        prompt_hash="prompt",
        replay_key="replay",
        canonical_provider="anthropic",
        target_model="claude-sonnet-4-20250514",
        budget={"max_tokens": 4096},
        final_evidence_contract_ref="fec",
    )
    receipt = _build_handoff_receipt(
        section_id="headline",
        packet=packet,
        provider_request={
            "provider": "anthropic",
            "model": "claude-sonnet-4-20250514",
        },
        provider_response={},
        output_exists=True,
        tokens_used=0,
        tokens_observed=False,
        runtime_payload={
            "canonical_l2_prompt_hash": "prompt",
            "canonical_l2_replay_key": "replay",
            "provider_lane": "anthropic",
            "model_lane": "claude-sonnet-4-20250514",
        },
    )
    assert receipt["handoff_status"] == "FAIL"
    assert receipt["checks"]["token_usage_observed"] is False
    assert receipt["tokens_emitted"] is None
    assert receipt["unknown_never_pass"] is True


def test_apps_eval_requires_and_indexes_canonical_l2_receipts() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    contract = json.loads(
        (repo_root / "apps_eval" / "registries" / "apps_rg_lane_contract.json").read_text(
            encoding="utf-8"
        )
    )
    required = set(contract["required_lane_artifact_roles"]["L2"])
    expected = {
        "l2_execution_packet",
        "frozen_execution_context",
        "prep_receipt",
        "validation_receipt",
        "attempt_receipt",
        "seal_receipt",
        "l2_receipt_bundle",
        "sealed_l2_artifact",
        "l2_handoff_receipt",
    }
    assert expected <= required

    from apps_eval.adapters import apps_rg as adapter

    for role, filename in {
        "l2_execution_packet": "l2_execution_packet.json",
        "l2_receipt_bundle": "l2_receipt_bundle.json",
        "sealed_l2_artifact": "sealed_l2_artifact.json",
        "l2_handoff_receipt": "l2_handoff_receipt.json",
    }.items():
        assert adapter._LANE_ARTIFACT_ROLE_BY_NAME[filename] == role
