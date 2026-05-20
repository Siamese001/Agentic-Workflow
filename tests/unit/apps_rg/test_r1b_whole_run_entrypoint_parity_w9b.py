"""W9b — whole-run cache preflight parity across canonical entrypoints."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from apps_rg.cache.r1b_models import HistoricalIntentRecord, HistoricalOutputChunk
from apps_rg.cache.r1b_store import R1BSemanticCacheStore
from apps_rg.cache.whole_run_entrypoint_preflight import (
    ENTRYPOINT_CANONICAL_DISPATCH,
    ENTRYPOINT_TEST_WHOLE_RUN_HARNESS,
    PREFLIGHT_ORDER,
    build_cache_hit_dispatch_result,
    build_entrypoint_audit_matrix,
    run_whole_run_cache_preflight,
)


def _seed(store: R1BSemanticCacheStore) -> None:
    repo = Path(__file__).resolve().parents[3]
    w7 = repo / "artifacts" / "apps_rg" / "r1b_semantic_cache" / "w7_fixtures"
    intent = json.loads((w7 / "historical_intent_record_admissible.json").read_text(encoding="utf-8"))
    chunks = json.loads((w7 / "historical_output_chunks_admissible.json").read_text(encoding="utf-8"))
    store.write_intent(HistoricalIntentRecord.from_dict(intent))
    for row in chunks:
        store.write_chunk(HistoricalOutputChunk.from_dict(row))


def _req() -> dict:
    return {
        "target_company": "Synthetic Enterprise Corp.",
        "target_role": "SVP Engineering",
        "generation_mode": "strategic_tailor",
        "resume_hash": "fixture_resume_digest",
        "jd_hash": "fixture_jd_digest",
        "brief_hash": "fixture_brief_digest",
    }


def test_audit_matrix_canonical_paths_wired() -> None:
    matrix = {row["entrypoint"]: row for row in build_entrypoint_audit_matrix()}
    assert matrix[ENTRYPOINT_CANONICAL_DISPATCH]["status"] == "wired_w9b"
    assert matrix[ENTRYPOINT_TEST_WHOLE_RUN_HARNESS]["status"] == "test_harness_only"
    assert matrix[ENTRYPOINT_CANONICAL_DISPATCH]["uses_r1a"] is True
    assert matrix[ENTRYPOINT_CANONICAL_DISPATCH]["uses_r1b"] is True


def test_production_preflight_accepted_hit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = R1BSemanticCacheStore(tmp_path)
    _seed(store)
    monkeypatch.setenv("SEMANTIC_CACHE_D2_ENABLED", "1")
    monkeypatch.setenv("APPS_RG_R1B_CACHE_ROOT", str(store.root))
    pf = run_whole_run_cache_preflight(
        entrypoint=ENTRYPOINT_CANONICAL_DISPATCH,
        raw_request=_req(),
        target_company="Synthetic Enterprise Corp.",
        target_role="SVP Engineering",
        artifact_dir=tmp_path / "art",
        runs_dir=tmp_path,
        policy_hash="prompt_profile_w7_v1",
        blueprint_hash="gate_profile_w7_v1",
    )
    assert pf.r1b_hit is True
    assert pf.generation_required is False
    dr = build_cache_hit_dispatch_result(pf)
    assert dr["generation_skipped"] is True
    assert dr["exit_bypassed"] is False
    assert dr["c0_fact_vectors_consulted"] is False


def test_production_preflight_miss_fallthrough(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = R1BSemanticCacheStore(tmp_path)
    _seed(store)
    monkeypatch.setenv("SEMANTIC_CACHE_D2_ENABLED", "1")
    monkeypatch.setenv("APPS_RG_R1B_CACHE_ROOT", str(store.root))
    pf = run_whole_run_cache_preflight(
        entrypoint=ENTRYPOINT_CANONICAL_DISPATCH,
        raw_request={"target_company": "X", "target_role": "Y", "resume_hash": "a", "jd_hash": "b"},
        target_company="X",
        target_role="Y",
        runs_dir=tmp_path,
    )
    assert pf.r1b_hit is False
    assert pf.generation_required is True


def test_section_lane_skips_whole_run_preflight() -> None:
    pf = run_whole_run_cache_preflight(
        entrypoint=ENTRYPOINT_CANONICAL_DISPATCH,
        raw_request=_req(),
        target_company="Acme",
        target_role="VP",
        section="headline",
    )
    assert pf.section_lane is True
    assert pf.generation_required is True
    assert pf.r1b_hit is False


def test_canonical_dispatch_invokes_preflight_before_pipeline(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from apps_rg.runtime.orchestration import canonical_dispatch as cd

    order: list[str] = []

    def fake_preflight(**kwargs):
        from apps_rg.cache.whole_run_entrypoint_preflight import WholeRunCachePreflightOutcome

        order.append("PREFLIGHT")
        return WholeRunCachePreflightOutcome(
            entrypoint=str(kwargs.get("entrypoint") or ""),
            generation_required=True,
        )

    def fake_pipeline(**kwargs):
        order.append("PIPELINE")
        return type(
            "R",
            (),
            {
                "fault": "",
                "x3_disposition": "X3_ALLOW",
                "run_id": "r1",
                "request_id": "req1",
                "terminal_r5": False,
            },
        )()

    monkeypatch.setattr(cd, "run_integrated_single_action_spine", fake_pipeline)
    monkeypatch.setattr(
        "apps_rg.cache.whole_run_entrypoint_preflight.run_whole_run_cache_preflight",
        fake_preflight,
    )

    with patch.object(cd, "build_raw_request_for_r4", return_value=_req()):
        with patch.object(cd, "_default_artifact_dir", return_value=tmp_path / "art"):
            with patch.object(cd, "emit_integrated_run_bundle_index", lambda *a, **k: None):
                with patch.object(cd, "_augment_integrated_manifest_with_apps_rg_docx", lambda *a, **k: None):
                    with patch.object(cd, "_augment_r4_run_manifest_for_apps_rg_l2_fault", lambda *a, **k: None):
                        cd.run_canonical_apps_rg_from_cli_primitives(
                            target_company="Synthetic Enterprise Corp.",
                            target_role="SVP Engineering",
                            jd="",
                            manual_brief="",
                            resume_path="",
                        )

    assert "PREFLIGHT" in order
    assert "PIPELINE" in order
    assert order.index("PREFLIGHT") < order.index("PIPELINE")


def test_canonical_dispatch_r1b_hit_skips_pipeline(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from apps_rg.runtime.orchestration import canonical_dispatch as cd

    monkeypatch.setenv("SEMANTIC_CACHE_D2_ENABLED", "1")
    monkeypatch.setenv("APPS_RG_POLICY_HASH", "prompt_profile_w7_v1")
    monkeypatch.setenv("APPS_RG_BLUEPRINT_HASH", "gate_profile_w7_v1")
    store = R1BSemanticCacheStore(tmp_path / "r1b_store")
    _seed(store)
    monkeypatch.setenv("APPS_RG_R1B_CACHE_ROOT", str(store.root))

    pipeline_called: list[bool] = []

    def fake_pipeline(**kwargs):
        pipeline_called.append(True)
        raise AssertionError("pipeline should not run")

    monkeypatch.setattr(cd, "run_integrated_single_action_spine", fake_pipeline)

    with patch.object(cd, "build_raw_request_for_r4", return_value=_req()):
        with patch.object(cd, "_default_artifact_dir", return_value=tmp_path / "art"):
            result = cd.run_canonical_apps_rg_from_cli_primitives(
                target_company="Synthetic Enterprise Corp.",
                target_role="SVP Engineering",
            )

    assert not pipeline_called
    assert result.get("generation_skipped") is True
    cp = result.get("cache_preflight")
    if isinstance(cp, dict):
        assert cp.get("cache_result") == "r1b_hit"
    else:
        assert cp == "r1b_hit"


def test_preflight_order_constant() -> None:
    assert PREFLIGHT_ORDER[0] == "R1A_EXACT_CACHE"
    assert PREFLIGHT_ORDER[1] == "R1B_SEMANTIC_ROLE_TARGET_RUN"
