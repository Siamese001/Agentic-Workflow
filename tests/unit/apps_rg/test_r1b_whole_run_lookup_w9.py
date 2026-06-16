"""W9 — whole-run R1B preflight lookup, compatibility, fallthrough."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from apps_rg.cache.r1b_constants import CACHE_GRAIN_ROLE_TARGET_RUN, C0_FACT_VECTORS_COLLECTION
from apps_rg.cache.r1b_store import R1BSemanticCacheStore
from apps_rg.cache.r1b_whole_run_preflight import (
    PREFLIGHT_ORDER,
    execute_whole_run_r1b_preflight,
)
from tests.unit.apps_rg.r1b_fixture_builders import (
    r1b_match_request,
    seed_admissible_r1b_store,
)


def _seed_admissible(store: R1BSemanticCacheStore) -> None:
    seed_admissible_r1b_store(store)


def _match_request() -> dict:
    return r1b_match_request()


def test_preflight_order_constant() -> None:
    assert PREFLIGHT_ORDER[0] == "R1A_EXACT_CACHE"
    assert PREFLIGHT_ORDER[1] == "R1B_SEMANTIC_ROLE_TARGET_RUN"
    assert PREFLIGHT_ORDER[2] == "NORMAL_GENERATION"


def test_accepted_hit_on_matching_intent(tmp_path: Path) -> None:
    store = R1BSemanticCacheStore(tmp_path)
    _seed_admissible(store)
    result = execute_whole_run_r1b_preflight(
        raw_request=_match_request(),
        runs_dir=tmp_path,
        similarity_threshold=0.5,
        prompt_profile_hash="prompt_profile_w7_v1",
        gate_profile_hash="gate_profile_w7_v1",
    )
    assert result.r1b_hit is True
    assert result.outcome == "r1b_hit"
    assert result.cache_grain == CACHE_GRAIN_ROLE_TARGET_RUN
    assert result.terminal_packet is not None
    assert result.terminal_packet.get("no_l2_execution_assertion") is True
    assert result.terminal_packet.get("exit_bypassed") is False
    assert result.c0_fact_vectors_consulted is False


def test_semantic_miss_fallthrough(tmp_path: Path) -> None:
    store = R1BSemanticCacheStore(tmp_path)
    _seed_admissible(store)
    result = execute_whole_run_r1b_preflight(
        raw_request={"target_company": "Other", "target_role": "Role", "resume_hash": "a", "jd_hash": "b"},
        runs_dir=tmp_path,
        similarity_threshold=0.99,
    )
    assert result.r1b_hit is False
    assert result.generation_required is True
    assert result.outcome == "r1b_miss"


def test_profile_mismatch_inadmissible_not_hit(tmp_path: Path) -> None:
    store = R1BSemanticCacheStore(tmp_path)
    _seed_admissible(store)
    result = execute_whole_run_r1b_preflight(
        raw_request=_match_request(),
        runs_dir=tmp_path,
        similarity_threshold=0.5,
        prompt_profile_hash="wrong_profile",
        gate_profile_hash="wrong_gate",
    )
    assert result.r1b_hit is False
    assert result.generation_required is True
    assert result.outcome in ("r1b_miss", "r1b_inadmissible_only")


def test_child_chunks_inspected_not_independent_lookup(tmp_path: Path) -> None:
    store = R1BSemanticCacheStore(tmp_path)
    _seed_admissible(store)
    result = execute_whole_run_r1b_preflight(
        raw_request=_match_request(),
        runs_dir=tmp_path,
        similarity_threshold=0.5,
        prompt_profile_hash="prompt_profile_w7_v1",
        gate_profile_hash="gate_profile_w7_v1",
    )
    assert result.child_chunk_inspection is not None
    assert result.child_chunk_inspection["independent_chunk_lookup_performed"] is False
    for row in result.child_chunk_inspection["chunks_inspected"]:
        assert row["used_as_lookup_key"] is False
        assert row["independent_cache_identity"] is False


def test_r1b_not_c0_fact_vectors(tmp_path: Path) -> None:
    store = R1BSemanticCacheStore(tmp_path)
    _seed_admissible(store)
    result = execute_whole_run_r1b_preflight(
        raw_request=_match_request(),
        runs_dir=tmp_path,
        similarity_threshold=0.5,
        prompt_profile_hash="prompt_profile_w7_v1",
        gate_profile_hash="gate_profile_w7_v1",
    )
    assert result.c0_fact_vectors_consulted is False
    assert C0_FACT_VECTORS_COLLECTION == "fact_vectors"
    assert result.probe is not None
    assert result.probe.get("not_c0_fact_vectors") is True


def test_main_r1a_before_r1b_order(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from tests.helpers import whole_run_spine_harness as harness

    order: list[str] = []

    monkeypatch.setenv("SEMANTIC_CACHE_D2_ENABLED", "1")
    monkeypatch.setattr(
        "apps_rg.cache.whole_run_entrypoint_preflight._semantic_cache_r1b_enabled",
        lambda: True,
    )
    monkeypatch.setattr(
        "agentic_core.runtime.entrypoints.integrated_single_action_spine_run.run_integrated_single_action_spine",
        lambda **k: order.append("PIPELINE") or _fake_outcome(tmp_path),
    )
    monkeypatch.setattr("apps_rg.cache.r1a_adapter.stamp_r1a_cache", lambda *a, **k: None)
    monkeypatch.setattr(
        "tests.helpers.whole_run_spine_harness.emit_integrated_run_bundle_index",
        lambda *a, **k: None,
    )

    def fake_r1b(**kwargs):
        order.append("R1B")
        from apps_rg.cache.r1b_whole_run_preflight import WholeRunR1BPreflightResult

        return WholeRunR1BPreflightResult(
            outcome="r1b_miss",
            r1b_hit=False,
            lookup_anchor="HistoricalIntentRecord.request_intent_vector",
            cache_grain=CACHE_GRAIN_ROLE_TARGET_RUN,
            generation_required=True,
        )

    with patch(
        "apps_rg.cache.whole_run_entrypoint_preflight.check_r1a_cache",
        lambda *a, **k: order.append("R1A") or None,
    ):
        with patch(
            "apps_rg.cache.whole_run_entrypoint_preflight.execute_whole_run_r1b_preflight",
            fake_r1b,
        ):
            with patch(
                "apps_rg.enforcement.cli_prerequisite_gate.check_apps_rg_cli_prerequisites",
                lambda **k: None,
            ):
                with patch(
                    "apps_rg.runtime.orchestration.canonical_dispatch.build_raw_request_for_r4",
                    lambda **k: _match_request(),
                ):
                    args = type("A", (), {"target_company": "Synthetic Enterprise Corp.", "target_role": "SVP Engineering", "target_level": "", "jd": "", "manual_brief": "", "resume": "", "generation_mode": "strategic_tailor", "tenant_id": "t"})()
                    with pytest.raises(SystemExit):
                        harness.run_whole_run_spine_harness(args, runs_dir=tmp_path, artifact_dir_override=tmp_path / "art")

    assert order.index("R1A") < order.index("R1B")
    assert order.index("R1B") < order.index("PIPELINE")


def _fake_outcome(tmp_path: Path):
    from types import SimpleNamespace

    art = tmp_path / "art"
    art.mkdir(exist_ok=True)
    return SimpleNamespace(
        run_id="run1",
        artifact_dir=art,
        fault="",
        terminal_r5=False,
    )


def test_main_r1b_hit_skips_pipeline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from tests.helpers import whole_run_spine_harness as harness

    monkeypatch.setattr(
        "tests.helpers.whole_run_spine_harness.emit_integrated_run_bundle_index",
        lambda *a, **k: None,
    )
    monkeypatch.setenv("SEMANTIC_CACHE_D2_ENABLED", "1")
    monkeypatch.setattr(
        "apps_rg.cache.whole_run_entrypoint_preflight._semantic_cache_r1b_enabled",
        lambda: True,
    )
    pipeline_called: list[bool] = []

    def fake_pipeline(**kwargs):
        pipeline_called.append(True)
        return _fake_outcome(tmp_path)

    monkeypatch.setattr(
        "agentic_core.runtime.entrypoints.integrated_single_action_spine_run.run_integrated_single_action_spine",
        fake_pipeline,
    )

    def fake_r1b(**kwargs):
        from apps_rg.cache.r1b_whole_run_preflight import WholeRunR1BPreflightResult

        return WholeRunR1BPreflightResult(
            outcome="r1b_hit",
            r1b_hit=True,
            lookup_anchor="HistoricalIntentRecord.request_intent_vector",
            cache_grain=CACHE_GRAIN_ROLE_TARGET_RUN,
            terminal_packet={"exit_bypassed": False},
        )

    def fake_whole_preflight(**kwargs):
        from apps_rg.cache.whole_run_entrypoint_preflight import WholeRunCachePreflightOutcome

        r1b = fake_r1b(**kwargs)
        return WholeRunCachePreflightOutcome(
            entrypoint=str(kwargs.get("entrypoint") or ""),
            r1b_result=r1b,
            generation_required=False,
        )

    with patch(
        "tests.helpers.whole_run_spine_harness.run_whole_run_cache_preflight",
        fake_whole_preflight,
    ):
        with patch(
            "apps_rg.cache.r1b_whole_run_preflight.write_r1b_preflight_receipt",
            lambda *a, **k: None,
        ):
            with patch(
                "apps_rg.enforcement.cli_prerequisite_gate.check_apps_rg_cli_prerequisites",
                lambda **k: None,
            ):
                with patch(
                    "apps_rg.runtime.orchestration.canonical_dispatch.build_raw_request_for_r4",
                    lambda **k: _match_request(),
                ):
                    args = type("A", (), {"target_company": "Synthetic Enterprise Corp.", "target_role": "SVP Engineering", "target_level": "", "jd": "", "manual_brief": "", "resume": "", "generation_mode": "strategic_tailor", "tenant_id": "t"})()
                    with pytest.raises(SystemExit) as exc:
                        harness.run_whole_run_spine_harness(args, runs_dir=tmp_path)
    assert exc.value.code == 0
    assert not pipeline_called
