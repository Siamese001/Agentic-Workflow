"""W6 — governed L2 seal + ExitEvalPipeline + RuntimeExhaustBundle."""

from __future__ import annotations

import os
from types import SimpleNamespace

import pytest

from agentic_core.runtime.contracts.compiled_prompt_artifact import (
    CompiledPromptArtifact,
    PromptBlock,
)
from agentic_core.runtime.contracts.final_evidence_contract import (
    FinalEvidenceContract,
    SUPPORT_STATUS_PASS,
)
from agentic_core.runtime.contracts.origin import Origin
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from apps_rg.runtime.bindings.exit_binding import exit_finalize_apps_rg
from apps_rg.runtime.bindings.l2_binding_adapter import l2_execute_apps_rg
from apps_rg.runtime.spine.exit_artifacts import build_exit_disposition_receipt_for_section
from apps_rg.runtime.spine.governed_l2_exit_compose import (
    GOVERNED_EXIT_SPINE_MARKER,
    governed_l2_exit_enabled,
    governed_l2_seal_integrated,
)


def _cpa() -> CompiledPromptArtifact:
    return CompiledPromptArtifact(
        request_id="req-w6-l2",
        run_id="run-w6-l2",
        app_id="apps_rg",
        trace_id="trace-w6-l2",
        prompt_blocks=(
            PromptBlock(role="system", content="sys", block_index=0, origin=Origin.SYSTEM_INTERNAL),
            PromptBlock(role="user", content="user", block_index=1, origin=Origin.USER_INTENT),
        ),
        system_preamble="sys",
        user_instruction="user",
        assembly_timestamp="2026-05-23T00:00:00Z",
        target_model="qwen",
        target_provider="vllm",
        evidence_digest="ev-digest",
        compilation_hash="comp-hash-w6",
        l5_certification_ref="test:valid:w6",
    )


def _fec() -> FinalEvidenceContract:
    return FinalEvidenceContract(
        request_id="req-w6-l2",
        run_id="run-w6-l2",
        app_id="apps_rg",
        trace_id="trace-w6-l2",
        l5_certification_ref="test:valid:w6",
        support_status=SUPPORT_STATUS_PASS,
        final_evidence_digest="fec-digest",
    )


def _sealed() -> SealedL2Artifact:
    return SealedL2Artifact(
        request_id="req-w6-exit",
        run_id="run-w6-exit",
        app_id="apps_rg",
        trace_id="trace-w6-exit",
        execution_status="completed",
        generated_content='{"ok": true}',
        compilation_hash="comp-exit-w6",
        l5_certification_ref="test:valid:w6",
    )


def test_governed_l2_exit_enabled_by_default() -> None:
    assert governed_l2_exit_enabled() is True


def test_governed_l2_seal_stamps_marker(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_L2_FORCE_STUB", "1")
    sealed = governed_l2_seal_integrated(_cpa())
    assert GOVERNED_EXIT_SPINE_MARKER in tuple(sealed.gate_verdict_refs or ())


def test_l2_execute_uses_governed_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_L2_FORCE_STUB", "1")
    sealed = l2_execute_apps_rg(_cpa())
    assert GOVERNED_EXIT_SPINE_MARKER in tuple(sealed.gate_verdict_refs or ())


def test_exit_finalize_runs_spine_eval_and_exhaust(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPS_RG_GOVERNED_L2_EXIT_SKIP", raising=False)
    result = exit_finalize_apps_rg(_sealed(), fec=_fec(), target_company="Acme", target_role="VP")
    bundle = getattr(result, "_governed_integrated_exit_bundle", None)
    assert bundle is not None
    assert bundle.x3_code
    exhaust = bundle.exhaust_bundle
    assert exhaust.created_after_exit is True
    assert exhaust.current_run_closed is True
    assert exhaust.exit_disposition_ref


def test_legacy_exit_when_governed_skip(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_GOVERNED_L2_EXIT_SKIP", "1")
    result = exit_finalize_apps_rg(_sealed(), fec=_fec())
    assert getattr(result, "_governed_integrated_exit_bundle", None) is None


def test_section_exit_disposition_receipt_single_x3_field(tmp_path) -> None:
    import json

    art = tmp_path / "lane"
    art.mkdir()
    (art / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3_ALLOW", "pass": True}),
        encoding="utf-8",
    )
    (art / "sealed_l2_artifact.json").write_text("{}", encoding="utf-8")
    edr = build_exit_disposition_receipt_for_section(
        section_id="executive_summary",
        runtime_payload={"run_id": "r1", "sealed_l2_artifact_ref": "sealed_l2_artifact.json"},
        artifact_dir=art,
    )
    x3 = edr.get("x3_disposition")
    assert isinstance(x3, dict)
    assert edr.get("x3_code") == x3.get("x3_code")
