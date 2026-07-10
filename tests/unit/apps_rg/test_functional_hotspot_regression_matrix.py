"""apps-test-model: APP CONTRACT.

Regression matrices for apps_rg functional hotspots found during local-main verification.
"""
from __future__ import annotations

import json
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from agentic_core.runtime.contracts.route_contract import RouteContract
from apps_rg.fact_inventory import p2_graph_skills_accelerated_closeout as closeout_mod
from apps_rg.l2_recipe.r4_modular_proof_verification import (
    verify_recorded_modular_r4_proof_bundle,
)
from apps_rg.runtime.bindings import l0_l3_otel_spans as span_mod
from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES


def _route() -> RouteContract:
    return RouteContract(
        request_id="req-hotspot",
        run_id="run-hotspot",
        app_id="apps_rg",
        trace_id="trace-hotspot",
        route_id="R4_MANAGED_DRAFT",
        execution_form="managed_workflow",
        l3_required=True,
        grounding_required=True,
        model_generation_required=True,
        write_authority_present=False,
        route_digest="cafe" * 16,
        l5_certification_ref="test:valid:hotspot",
    )


def test_span_digest_ignores_timestamp_but_not_semantic_fields() -> None:
    base = {
        "span_kind": "l0.route_decision",
        "trace_id": "trace-hotspot",
        "route_id": "R4_MANAGED_DRAFT",
        "timestamp": "2026-07-09T10:00:00+00:00",
    }
    replay = {**base, "timestamp": "2026-07-09T10:00:01+00:00"}
    changed_route = {**replay, "route_id": "R4_OTHER"}

    assert span_mod._digest(base) == span_mod._digest(replay)
    assert span_mod._digest(base) != span_mod._digest(changed_route)


def test_l0_span_ref_is_replay_stable_while_timestamp_refreshes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    timestamps = iter(
        (
            datetime(2026, 7, 9, 10, 0, 0, tzinfo=timezone.utc),
            datetime(2026, 7, 9, 10, 0, 1, tzinfo=timezone.utc),
        )
    )

    class _Clock:
        @classmethod
        def now(cls, _tz: object) -> datetime:
            return next(timestamps)

    monkeypatch.setattr(span_mod, "datetime", _Clock)
    first = span_mod.emit_l0_route_span(_route())
    second = span_mod.emit_l0_route_span(_route())

    assert first is not None and second is not None
    assert first["payload"]["timestamp"] != second["payload"]["timestamp"]
    assert first["payload_digest"] == second["payload_digest"]
    assert first["span_ref"] == second["span_ref"]


def test_l3_span_digest_changes_with_orchestration_identity() -> None:
    route = _route()
    baseline = span_mod.emit_l3_orchestration_span(
        route=route,
        workflow_id="workflow-a",
        dag_id="dag-a",
    )
    changed_workflow = span_mod.emit_l3_orchestration_span(
        route=route,
        workflow_id="workflow-b",
        dag_id="dag-a",
    )
    changed_route = span_mod.emit_l3_orchestration_span(
        route=replace(route, route_id="R4_RETRY"),
        workflow_id="workflow-a",
        dag_id="dag-a",
    )

    assert baseline is not None and changed_workflow is not None and changed_route is not None
    assert baseline["payload_digest"] != changed_workflow["payload_digest"]
    assert baseline["payload_digest"] != changed_route["payload_digest"]


def test_span_emitters_fail_soft_when_route_access_raises() -> None:
    class _ExplodingRoute:
        @property
        def app_id(self) -> str:
            raise RuntimeError("route unavailable")

    assert span_mod.emit_l0_route_span(_ExplodingRoute()) is None  # type: ignore[arg-type]
    assert (
        span_mod.emit_l3_orchestration_span(
            route=_ExplodingRoute(),  # type: ignore[arg-type]
            workflow_id="workflow",
            dag_id="dag",
        )
        is None
    )


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _build_r4_run(
    repo_root: Path,
    *,
    schema_version: str,
    lanes: tuple[str, ...],
    include_section_refs: bool = True,
) -> tuple[str, Path]:
    run_id = "r4-hotspot"
    run_dir = repo_root / "artifacts" / "apps_rg" / "runs" / run_id
    _write_json(run_dir / "r4_run_manifest.json", {"x3_disposition": "X3D", "l2_fault": ""})
    _write_json(run_dir / "outputs" / "generated_resume.json", {"resume": {}})
    _write_json(
        run_dir / "apps_rg_output_manifest.json",
        {
            "apps_rg_generation_status": "REAL_RESUME",
            "full_resume_generated": True,
            "required_artifacts": {"generated_resume_json": "verified"},
        },
    )
    receipt: dict[str, Any] = {
        "apps_rg_r4_generation_mode": "modular_section_lanes",
        "decisive_status": "PASS",
        "final_schema_valid": True,
        "failure_reason": "",
    }
    if include_section_refs:
        receipt["section_output_refs"] = {lane: f"outputs/{lane}.json" for lane in lanes}
    _write_json(run_dir / "modular_r4" / "generate_resume_step_receipt.json", receipt)
    _write_json(
        run_dir / "modular_r4" / "section_provider_calls.json",
        {
            "schema_version": schema_version,
            "locked_sections_provider_calls_detected": False,
            "real_lane_invocation_attempted": True,
            "decisive_status": "PASS",
            "recipe_lane_policy": {"fatal_lane_failures": []},
            "records": [
                {
                    "section_lane": lane,
                    "generation_status": "REAL_LLM",
                    "provider_call_attempted": True,
                }
                for lane in lanes
            ],
        },
    )
    _write_json(
        run_dir / "modular_r4" / "outputs" / "rg_output_merge_receipt.json",
        {"schema_valid": True, "ok": True},
    )
    _write_json(
        run_dir / "modular_r4" / "rg_output_schema_validation_receipt.json",
        {"final_schema_valid": True},
    )
    return run_id, run_dir


def test_r4_phase1_v1_uses_its_recorded_lane_set(tmp_path: Path) -> None:
    lanes = ("headline", "competencies")
    run_id, _ = _build_r4_run(
        tmp_path,
        schema_version="section_provider_calls.phase1.v1",
        lanes=lanes,
    )

    assert verify_recorded_modular_r4_proof_bundle(repo_root=tmp_path, run_id=run_id) == []


def test_r4_phase1_v2_requires_the_current_generated_lane_set(tmp_path: Path) -> None:
    run_id, _ = _build_r4_run(
        tmp_path,
        schema_version="section_provider_calls.phase1.v2",
        lanes=("headline", "competencies"),
    )

    errs = verify_recorded_modular_r4_proof_bundle(repo_root=tmp_path, run_id=run_id)

    assert f"section_lane_record_count_expected_{len(GENERATED_LANES)}" in errs


def test_r4_phase1_v1_without_recorded_refs_falls_back_to_current_lanes(tmp_path: Path) -> None:
    run_id, _ = _build_r4_run(
        tmp_path,
        schema_version="section_provider_calls.phase1.v1",
        lanes=("headline",),
        include_section_refs=False,
    )

    errs = verify_recorded_modular_r4_proof_bundle(repo_root=tmp_path, run_id=run_id)

    assert f"section_lane_record_count_expected_{len(GENERATED_LANES)}" in errs


def test_r4_phase1_v2_rejects_pass_with_fatal_lane_failures(tmp_path: Path) -> None:
    lanes = tuple(GENERATED_LANES)
    run_id, run_dir = _build_r4_run(
        tmp_path,
        schema_version="section_provider_calls.phase1.v2",
        lanes=lanes,
    )
    calls_path = run_dir / "modular_r4" / "section_provider_calls.json"
    calls = json.loads(calls_path.read_text(encoding="utf-8"))
    calls["recipe_lane_policy"]["fatal_lane_failures"] = [lanes[0]]
    _write_json(calls_path, calls)

    errs = verify_recorded_modular_r4_proof_bundle(repo_root=tmp_path, run_id=run_id)

    assert "section_calls_PASS_with_fatal_lane_failures" in errs


def test_r4_rejects_mocked_or_unattempted_recorded_lanes(tmp_path: Path) -> None:
    run_id, run_dir = _build_r4_run(
        tmp_path,
        schema_version="section_provider_calls.phase1.v1",
        lanes=("headline", "competencies"),
    )
    calls_path = run_dir / "modular_r4" / "section_provider_calls.json"
    calls = json.loads(calls_path.read_text(encoding="utf-8"))
    calls["records"][0]["generation_status"] = "MOCKED"
    calls["records"][1]["provider_call_attempted"] = False
    _write_json(calls_path, calls)

    errs = verify_recorded_modular_r4_proof_bundle(repo_root=tmp_path, run_id=run_id)

    assert "MOCKED_lane_count_nonzero:1" in errs
    assert "provider_call_attempted_false:competencies" in errs


def test_r4_detects_legacy_envelope_and_silent_fallback_evidence(tmp_path: Path) -> None:
    run_id, run_dir = _build_r4_run(
        tmp_path,
        schema_version="section_provider_calls.phase1.v1",
        lanes=("headline",),
    )
    (run_dir / "runtime_trace_snapshot.json").write_text(
        'run_apps_rg_l2_envelope\n{"silent_provider_fallback": true}',
        encoding="utf-8",
    )

    errs = verify_recorded_modular_r4_proof_bundle(repo_root=tmp_path, run_id=run_id)

    assert "legacy_l2_envelope_artifact_evidence:runtime_trace_snapshot.json" in errs
    assert "silent_fallback_marker_in:runtime_trace_snapshot.json" in errs


def _stub_closeout_waves(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    for name in (
        "REBASELINE_JSON",
        "W1A_JSON",
        "W2_JSON",
        "W3_JSON",
        "W4_JSON",
        "W5_JSON",
        "W6_JSON",
        "W7_JSON",
        "W8_JSON",
        "W10_JSON",
    ):
        monkeypatch.setattr(closeout_mod, name, tmp_path / f"{name.lower()}.json")
    monkeypatch.setattr(closeout_mod, "CLOSEOUT_JSON", tmp_path / "closeout.json")
    monkeypatch.setattr(closeout_mod, "CLOSEOUT_MD", tmp_path / "closeout.md")
    monkeypatch.setattr(closeout_mod, "W9_JSON", tmp_path / "w9.json")
    monkeypatch.setattr(closeout_mod, "_write_json", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(closeout_mod._wg, "write_text", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(closeout_mod, "write_p2_rebaseline", lambda **_kwargs: {})
    monkeypatch.setattr(
        closeout_mod,
        "write_p2_w1a_all_sections",
        lambda **_kwargs: {
            "all_sections_default_to_augmented_skills_graph": True,
            "broad_skills_ledger_used_as_authority_anywhere": False,
        },
    )
    for name in (
        "write_p2_w2_c03_binding",
        "write_p2_w3_infrastructure",
        "write_p2_w4_x2",
        "write_p2_w5_pa",
        "write_p2_w6_repair",
        "write_p2_w7_x1d",
        "write_p2_w8_validators",
    ):
        monkeypatch.setattr(closeout_mod, name, lambda **_kwargs: {})
    monkeypatch.setattr(
        closeout_mod,
        "write_p2_w10_audit",
        lambda **_kwargs: {"package_audit_status": "PASS"},
    )
    monkeypatch.setattr(
        "apps_rg.fact_inventory.competencies_graph_skills_proof_pool.write_p2_w1a_default_graph_authority_receipt",
        lambda **_kwargs: {"receipt_json": "receipt.json"},
    )


def test_closeout_preserves_valid_w9_without_refresh(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _stub_closeout_waves(monkeypatch, tmp_path)
    original = {"schema": "canonical_live_section_proofs_p2_w9_v1", "sections": {"headline": {"status": "PASS"}}}
    closeout_mod.W9_JSON.write_text(json.dumps(original), encoding="utf-8")
    refresh_calls: list[bool] = []

    def _refresh(**kwargs: Any) -> dict[str, Any]:
        refresh_calls.append(bool(kwargs["run_live"]))
        return {"w9": {"sections": {"unexpected": {"status": "PASS"}}}}

    monkeypatch.setattr(closeout_mod, "write_p2_w9_live_matrix_closeout", _refresh)

    out = closeout_mod.run_full_closeout(repo_root=tmp_path, skip_live=True)

    assert refresh_calls == []
    assert out["live_proof_summary"] == original


@pytest.mark.parametrize("invalid_sections", [None, [], "not-an-object"])
def test_closeout_refreshes_malformed_preserved_w9(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    invalid_sections: object,
) -> None:
    _stub_closeout_waves(monkeypatch, tmp_path)
    closeout_mod.W9_JSON.write_text(
        json.dumps({"schema": "canonical_live_section_proofs_p2_w9_v1", "sections": invalid_sections}),
        encoding="utf-8",
    )
    refreshed = {"sections": {"headline": {"status": "PASS"}}}
    refresh_calls: list[bool] = []

    def _refresh(**kwargs: Any) -> dict[str, Any]:
        refresh_calls.append(bool(kwargs["run_live"]))
        return {"w9": refreshed}

    monkeypatch.setattr(closeout_mod, "write_p2_w9_live_matrix_closeout", _refresh)

    out = closeout_mod.run_full_closeout(repo_root=tmp_path, skip_live=True)

    assert refresh_calls == [False]
    assert out["live_proof_summary"] == refreshed


def test_closeout_refreshes_w9_when_preservation_is_disabled(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _stub_closeout_waves(monkeypatch, tmp_path)
    closeout_mod.W9_JSON.write_text(
        json.dumps({"sections": {"headline": {"status": "PASS"}}}),
        encoding="utf-8",
    )
    refresh_calls: list[bool] = []

    def _refresh(**kwargs: Any) -> dict[str, Any]:
        refresh_calls.append(bool(kwargs["run_live"]))
        return {"w9": {"sections": {}}}

    monkeypatch.setattr(closeout_mod, "write_p2_w9_live_matrix_closeout", _refresh)

    closeout_mod.run_full_closeout(
        repo_root=tmp_path,
        skip_live=True,
        preserve_w9_live_matrix=False,
    )

    assert refresh_calls == [False]


def test_missing_recorded_r4_run_fails_closed(tmp_path: Path) -> None:
    errs = verify_recorded_modular_r4_proof_bundle(repo_root=tmp_path, run_id="missing")

    assert len(errs) == 1
    assert errs[0].startswith("missing_proof_run_dir:")
