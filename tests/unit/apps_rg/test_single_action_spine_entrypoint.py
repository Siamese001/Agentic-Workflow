"""Route-neutral spine entrypoint — old R4 module path deleted; cache preflight enforced."""
from __future__ import annotations

import importlib
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_old_r4_module_not_importable() -> None:
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module(
            "agentic_core.runtime.entrypoints.integrated_r4_deterministic_pipeline_run"
        )


def test_new_spine_module_importable() -> None:
    mod = importlib.import_module(
        "agentic_core.runtime.entrypoints.integrated_single_action_spine_run"
    )
    assert hasattr(mod, "run_integrated_single_action_spine")
    assert mod.ROUTE_FAMILY == "R4_SINGLE_ACTION"


def test_apps_rg_production_requires_cache_preflight_evidence(tmp_path: Path) -> None:
    from agentic_core.runtime.entrypoints.integrated_single_action_spine_run import (
        run_integrated_single_action_spine,
    )

    result = run_integrated_single_action_spine(
        raw_request={"jd_payload": {"title": "t", "description": "d"}},
        app_name="apps_rg",
        artifact_dir=tmp_path,
    )
    assert "CACHE_PREFLIGHT" in (result.fault or "")


def test_direct_spine_without_cache_fails_product_proof(tmp_path: Path) -> None:
    from agentic_core.runtime.entrypoints.integrated_single_action_spine_run import (
        run_integrated_single_action_spine,
    )
    from apps_rg.runtime.integrated_product_proof_gate import validate_integrated_product_proof

    with patch(
        "agentic_core.runtime.l2_recipe_resolver.resolve_l2_recipe"
    ) as mock_resolve:
        mock_resolve.return_value = MagicMock(return_value={"status": "ok"})
        run_integrated_single_action_spine(
            raw_request={
                "jd_payload": {"title": "Role", "description": "desc"},
                "jd_hash": "a",
                "brief_hash": "b",
                "resume_hash": "c",
            },
            app_name="apps_rg",
            artifact_dir=tmp_path,
            _test_mode=True,
        )

    result = validate_integrated_product_proof(tmp_path)
    assert result.status == "FAIL"
    assert "cache_preflight_evidence_missing" in result.decisive_reason


def test_r1a_hit_skips_generation_spine(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    import apps_rg.cache.whole_run_entrypoint_preflight as preflight_mod
    import apps_rg.runtime.orchestration.canonical_dispatch as cd
    from apps_rg.cache.whole_run_entrypoint_preflight import (
        ENTRYPOINT_CANONICAL_DISPATCH,
        WholeRunCachePreflightOutcome,
    )

    called: list[str] = []

    def _fake_spine(**kwargs):  # noqa: ANN003
        called.append("spine")
        raise AssertionError("spine must not run on cache hit")

    hit = WholeRunCachePreflightOutcome(
        entrypoint=ENTRYPOINT_CANONICAL_DISPATCH,
        r1a_hit=True,
        r1a_artifact_dir=str(tmp_path / "r1a_hit"),
        generation_required=False,
    )
    monkeypatch.setattr(cd, "run_integrated_single_action_spine", _fake_spine)
    monkeypatch.setattr(
        cd, "build_raw_request_for_r4", lambda **kwargs: {"jd_payload": {"title": "t"}, "resume_hash": "h"}
    )
    monkeypatch.setattr(cd, "_default_artifact_dir", lambda _a: tmp_path / "art")
    monkeypatch.setattr(preflight_mod, "run_whole_run_cache_preflight", lambda **kwargs: hit)

    out = cd.run_canonical_apps_rg_from_cli_primitives(
        target_company="Acme",
        target_role="Engineer",
        jd="inline jd text long enough",
        manual_brief="brief",
    )
    assert called == []
    assert out.get("generation_skipped") is True


def test_cache_miss_invokes_spine_once(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import apps_rg.cache.whole_run_entrypoint_preflight as preflight_mod
    import apps_rg.runtime.orchestration.canonical_dispatch as cd
    from apps_rg.cache.whole_run_entrypoint_preflight import (
        ENTRYPOINT_CANONICAL_DISPATCH,
        WholeRunCachePreflightOutcome,
    )

    calls: list[dict] = []

    def _fake_spine(**kwargs):  # noqa: ANN003
        calls.append(kwargs)
        return type(
            "R",
            (),
            {
                "fault": "",
                "x3_disposition": "X3_ALLOW",
                "run_id": "run-1",
                "request_id": "req-1",
                "terminal_r5": False,
                "artifact_dir": kwargs["artifact_dir"],
            },
        )()

    miss = WholeRunCachePreflightOutcome(
        entrypoint=ENTRYPOINT_CANONICAL_DISPATCH,
        generation_required=True,
    )
    monkeypatch.setattr(cd, "run_integrated_single_action_spine", _fake_spine)
    monkeypatch.setattr(
        cd, "build_raw_request_for_r4", lambda **kwargs: {"jd_payload": {"title": "t"}, "resume_hash": "h"}
    )
    monkeypatch.setattr(preflight_mod, "run_whole_run_cache_preflight", lambda **kwargs: miss)
    monkeypatch.setattr(cd, "_default_artifact_dir", lambda _a: tmp_path)
    monkeypatch.setattr(cd, "emit_integrated_run_bundle_index", lambda *a, **k: None)
    monkeypatch.setattr(cd, "_augment_integrated_manifest_with_apps_rg_docx", lambda _a: None)
    monkeypatch.setattr(cd, "_augment_r4_run_manifest_for_apps_rg_l2_fault", lambda *a, **k: None)
    monkeypatch.setattr(preflight_mod, "maybe_ingest_r1b_post_exit", lambda **k: None)

    cd.run_canonical_apps_rg_from_cli_primitives(
        target_company="Acme",
        target_role="Engineer",
        jd="inline jd text long enough",
        manual_brief="brief",
        artifact_dir=str(tmp_path),
    )
    assert len(calls) == 1
    assert calls[0]["cache_preflight_evidence"]["generation_spine_invocation_allowed"] is True
    assert (tmp_path / "whole_run_cache_preflight_miss.json").is_file()


def test_section_path_invokes_integrated_spine_with_section_scope(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    import apps_rg.runtime.orchestration.canonical_dispatch as cd
    from agentic_core.runtime.entrypoints.integrated_single_action_spine_run import (
        ROUTE_ID,
        SingleActionSpineRunResult,
    )

    calls: list[dict] = []

    def _fake_spine(**kwargs):  # noqa: ANN003
        calls.append(kwargs)
        return SingleActionSpineRunResult(
            run_id="core-run-section",
            request_id="core-req-section",
            route_id=ROUTE_ID,
            x3_disposition="EXIT_OK",
            terminal_r5=False,
            terminal_r5_reason="",
            artifact_dir=tmp_path,
            fault="",
            l2_result={
                "step_results": [
                    {
                        "section_result": {
                            "outcome_authorized": True,
                            "executive_summary_cli_output_text": "SECTION_OK",
                        }
                    }
                ]
            },
        )

    monkeypatch.setattr(
        "agentic_core.runtime.entrypoints.integrated_single_action_spine_run.run_integrated_single_action_spine",
        _fake_spine,
    )
    monkeypatch.setattr(cd, "_apps_rg_u0_runtime_package_fields", lambda: {})
    cd.run_canonical_apps_rg_from_cli_primitives(
        target_company="Acme",
        target_role="Engineer",
        section="executive_summary",
        jd="jd",
        manual_brief="brief",
        artifact_dir=str(tmp_path),
    )
    assert len(calls) == 1
    assert calls[0]["app_name"] == "apps_rg"
    assert calls[0]["raw_request"]["execution_scope"] == "section"
    assert calls[0]["raw_request"]["section_id"] == "executive_summary"
    assert calls[0]["cache_preflight_evidence"]["cache_preflight_completed"] is True


def test_section_path_uses_nested_section_x3_block_not_wrapper_exit_ok(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    import apps_rg.runtime.orchestration.canonical_dispatch as cd
    from agentic_core.runtime.entrypoints.integrated_single_action_spine_run import (
        ROUTE_ID,
        SingleActionSpineRunResult,
    )

    def _fake_spine(**kwargs):  # noqa: ANN003
        return SingleActionSpineRunResult(
            run_id="core-run-section",
            request_id="core-req-section",
            route_id=ROUTE_ID,
            x3_disposition="EXIT_OK",
            terminal_r5=False,
            terminal_r5_reason="",
            artifact_dir=kwargs["artifact_dir"],
            fault="",
            l2_result={
                "step_results": [
                    {
                        "status": "blocked",
                        "section_result": {
                            "section_id": "headline",
                            "exit_status": "error",
                            "outcome_authorized": False,
                            "x3_disposition": "X3_BLOCK",
                        },
                    }
                ]
            },
        )

    monkeypatch.setattr(
        "agentic_core.runtime.entrypoints.integrated_single_action_spine_run.run_integrated_single_action_spine",
        _fake_spine,
    )
    monkeypatch.setattr(cd, "_apps_rg_u0_runtime_package_fields", lambda: {})

    result = cd.run_canonical_apps_rg_from_cli_primitives(
        target_company="Anthropic",
        target_role="Manager of Applied AI Architecture, Partnerships",
        section="headline",
        jd="jd",
        manual_brief="brief",
        artifact_dir=str(tmp_path),
    )

    assert result["exit_status"] == "error"
    assert result["outcome_authorized"] is False
    assert result["x3_disposition"] == "X3_BLOCK"
    assert result["fault"] == ""
    assert result["section_result_blocked"] is True
